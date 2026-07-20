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
    """Gère le formulaire et génère le QR code dynamique."""
    qr_base64 = None
    nom_complet = ""

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        nom_complet = f"{nom} {prenom}"

        domaine_actuel = request.host
        # Conservation du nouveau format propre pour les futurs scans
        lien_candidat = f"https://{domaine_actuel}/candidat/{nom}/{prenom}"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('formulaire.html', qr_base64=qr_base64, nom_complet=nom_complet)


# =========================================================================
# ROUTE 1 : COMPATIBILITÉ ANCIENS QR CODES (/candidat?n=...&p=...)
# =========================================================================
@app.route('/candidat')
def profil_candidat_ancien():
    """
    Intercepte le format exact de vos anciens QR codes.
    Décode automatiquement le Base64 pour retrouver le nom et le prénom réels.
    """
    n_encode = request.args.get('n', '')
    p_encode = request.args.get('p', '')

    nom_decode = ""
    prenom_decode = ""

    # Décodage sécurisé du format Base64 d'origine
    try:
        if n_encode:
            nom_decode = base64.b64decode(n_encode).decode('utf-8').strip()
        if p_encode:
            prenom_decode = base64.b64decode(p_encode).decode('utf-8').strip()
    except Exception:
        # Si ce n'était pas du Base64, on récupère le texte brut par sécurité
        nom_decode = n_encode
        prenom_decode = p_encode

    return render_template('candidat.html', nom=nom_decode, prenom=prenom_decode)


# =========================================================================
# ROUTE 2 : NOUVEAUX CANDIDATS (/candidat/NOM/PRENOM)
# =========================================================================
@app.route('/candidat/<nom>/<prenom>')
def profil_candidat_nouveau(nom, prenom):
    """Affiche la page pour les nouveaux liens générés."""
    nom_propre = urllib.parse.unquote(nom)
    prenom_propre = urllib.parse.unquote(prenom)
    return render_template('candidat.html', nom=nom_propre, prenom=prenom_propre)


# =========================================================================
# TÉLÉCHARGEMENT UNIVERSEL DU PDF
# =========================================================================
@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """Télécharge le fichier en gérant les espaces et l'extension."""
    nom_fichier_propre = urllib.parse.unquote(nom_complet)
    
    if not nom_fichier_propre.lower().endswith('.pdf'):
        nom_fichier_propre = f"{nom_fichier_propre}.pdf"
        
    pdf_path = os.path.join(PDF_FOLDER, nom_fichier_propre)
    
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.getcwd(), "static", nom_fichier_propre)

    if not os.path.exists(pdf_path):
        return f"Erreur 404 : Le fichier PDF '{nom_fichier_propre}' reste introuvable sur le serveur.", 404

    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    app.run(debug=True, port=5000)
