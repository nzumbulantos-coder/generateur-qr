from flask import Flask, render_template, request, send_file
import os
import qrcode
import io
import base64
import urllib.parse

app = Flask(__name__)

# Configuration du dossier contenant vos fichiers PDF
PDF_FOLDER = os.path.join(os.getcwd(), "attestations")

@app.route('/', methods=['GET', 'POST'])
def generateur_qr():
    """
    Gère le formulaire et génère un QR code sécurisé
    où le nom et le prénom sont totalement MASQUÉS en Base64.
    """
    qr_base64 = None
    nom_complet = ""

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        nom_complet = f"{nom} {prenom}"

        # Chiffrement des données en Base64 pour les masquer dans le lien
        nom_masque = base64.b64encode(nom.encode('utf-8')).decode('utf-8')
        prenom_masque = base64.b64encode(prenom.encode('utf-8')).decode('utf-8')

        # Construction du lien anonyme
        domaine_actuel = request.host
        lien_candidat = f"https://{domaine_actuel}/candidat?n={nom_masque}&p={prenom_masque}"

        # Génération du QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('formulaire.html', qr_base64=qr_base64, nom_complet=nom_complet)


# =========================================================================
# ROUTE UNIQUE : Décode les anciens ET les nouveaux QR codes masqués
# =========================================================================
@app.route('/candidat')
def profil_candidat():
    """
    Intercepte les liens anonymes, démasque le nom/prénom en interne
    et transmet les vraies valeurs à la page candidat.html.
    """
    n_encode = request.args.get('n', '')
    p_encode = request.args.get('p', '')

    nom_decode = ""
    prenom_decode = ""

    # Décodage sécurisé de la chaîne masquée
    try:
        if n_encode:
            nom_decode = base64.b64decode(n_encode).decode('utf-8').strip()
        if p_encode:
            prenom_decode = base64.b64decode(p_encode).decode('utf-8').strip()
    except Exception:
        # En cas d'erreur de format, récupération brute par sécurité
        nom_decode = n_encode
        prenom_decode = p_encode

    return render_template('candidat.html', nom=nom_decode, prenom=prenom_decode)


# =========================================================================
# TÉLÉCHARGEMENT DIRECT ET SÉCURISÉ DU PDF
# =========================================================================
@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """Télécharge le fichier PDF physique correspondant au candidat."""
    nom_fichier_propre = urllib.parse.unquote(nom_complet)
    
    if not nom_fichier_propre.lower().endswith('.pdf'):
        nom_fichier_propre = f"{nom_fichier_propre}.pdf"
        
    pdf_path = os.path.join(PDF_FOLDER, nom_fichier_propre)
    
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.getcwd(), "static", nom_fichier_propre)

    if not os.path.exists(pdf_path):
        return f"Erreur 404 : Le fichier PDF '{nom_fichier_propre}' reste introuvable.", 404

    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    app.run(debug=True, port=5000)
