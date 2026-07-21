from flask import Flask, render_template, request, send_file
import os
import qrcode
import io
import base64
import urllib.parse
import unicodedata  # Requis pour la gestion automatique des accents

app = Flask(__name__)

# Configuration du dossier contenant vos fichiers PDF
PDF_FOLDER = os.path.join(os.getcwd(), "attestations")

def supprimer_accents_et_nettoyer(texte):
    """
    Transforme 'EXAUCÉ' en 'EXAUCE', met tout en majuscules
    et supprime les doubles espaces invisibles.
    """
    if not texte:
        return ""
    # Décode les %20 et autres caractères d'URL
    texte_decode = urllib.parse.unquote(texte)
    # Supprime les accents de manière universelle
    texte_sans_accent = ''.join(c for c in unicodedata.normalize('NFD', texte_decode) if unicodedata.category(c) != 'Mn')
    # Met en majuscules et nettoie les espaces superflus au début, au milieu et à la fin
    return " ".join(texte_sans_accent.upper().split())


@app.route('/', methods=['GET', 'POST'])
def generateur_qr():
    """Gère le formulaire et génère un QR code masqué en Base64."""
    qr_base64 = None
    nom_complet = ""

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        nom_complet = f"{nom} {prenom}"

        # Masquage en Base64 pour cacher le nom dans l'URL
        nom_masque = base64.b64encode(nom.encode('utf-8')).decode('utf-8')
        prenom_masque = base64.b64encode(prenom.encode('utf-8')).decode('utf-8')

        domaine_actuel = request.host
        lien_candidat = f"https://{domaine_actuel}/candidat?n={nom_masque}&p={prenom_masque}"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('formulaire.html', qr_base64=qr_base64, nom_complet=nom_complet)


@app.route('/candidat')
def profil_candidat():
    """Décode les paramètres masqués pour afficher proprement la page candidat.html."""
    n_encode = request.args.get('n', '')
    p_encode = request.args.get('p', '')

    nom_decode = ""
    prenom_decode = ""

    try:
        if n_encode:
            nom_decode = base64.b64decode(n_encode).decode('utf-8').strip()
        if p_encode:
            prenom_decode = base64.b64decode(p_encode).decode('utf-8').strip()
    except Exception:
        nom_decode = n_encode
        prenom_decode = p_encode

    return render_template('candidat.html', nom=nom_decode, prenom=prenom_decode)


# =========================================================================
# ROUTE DE TÉLÉCHARGEMENT ULTRA-INTELLIGENTE (Compatible Accents/Espaces)
# =========================================================================
@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """Fouille le serveur en ignorant les différences d'accents et de casse."""
    # Préparation du nom demandé par l'utilisateur (nettoyé et sans accent)
    nom_cible = supprimer_accents_et_nettoyer(nom_complet)
    if nom_cible.endswith('.PDF'):
        nom_cible = nom_cible[:-4] # On retire temporairement le .PDF pour la comparaison

    chemin_fichier_trouve = None
    nom_reel_fichier = ""

    # Liste des dossiers à scanner sur Vercel
    dossiers_a_scanner = [PDF_FOLDER, os.path.join(os.getcwd(), "static")]

    # On parcourt les dossiers pour trouver une correspondance magique sans accent
    for dossier in dossiers_a_scanner:
        if os.path.exists(dossier):
            for element in os.listdir(dossier):
                # On nettoie temporairement le nom du fichier trouvé sur le disque pour le tester
                nom_fichier_disque = supprimer_accents_et_nettoyer(element)
                if nom_fichier_disque.endswith('.PDF'):
                    nom_fichier_disque = nom_fichier_disque[:-4]

                # Si le nom correspond (qu'il y ait eu un accent ou non à l'origine !)
                if nom_fichier_disque == nom_cible:
                    chemin_fichier_trouve = os.path.join(dossier, element)
                    nom_reel_fichier = element
                    break
        if chemin_fichier_trouve:
            break

    # Si le fichier reste introuvable malgré la recherche approfondie
    if not chemin_fichier_trouve:
        nom_affiche = supprimer_accents_et_nettoyer(nom_complet)
        return f"""
        <html>
            <body style="font-family:sans-serif; text-align:center; margin-top:50px; padding:20px;">
                <h2 style="color:#d32f2f;">⚠️ Attestation introuvable</h2>
                <p>Le fichier PDF pour <b>{nom_affiche}</b> n'existe pas sous ce nom sur le serveur Vercel.</p>
                <p>Veuillez vérifier l'orthographe exacte (lettres et espaces) du fichier sur votre GitHub.</p>
                <br>
                <a href="javascript:history.back()" style="color:#1d70b8; font-weight:bold; text-decoration:none;">⬅️ Retourner à la page précédente</a>
            </body>
        </html>
        """, 404

    # Envoi sécurisé du vrai fichier PDF d'origine (1.41 Mo)
    return send_file(
        chemin_fichier_trouve, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name=nom_reel_fichier
    )


if __name__ == '__main__':
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    app.run(debug=True, port=5000)
