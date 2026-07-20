from flask import Flask, render_template, request, send_file
import os
import qrcode
import io
import base64
import urllib.parse  # Permet de supprimer définitivement les %20

app = Flask(__name__)

# Configuration du dossier des fichiers PDF
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
        # Utilisation de la méthode sécurisée de Flask pour passer les variables sans casser l'URL
        lien_candidat = f"https://{domaine_actuel}/candidat/{nom}/{prenom}"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('formulaire.html', qr_base64=qr_base64, nom_complet=nom_complet)


@app.route('/candidat/<nom>/<prenom>')
def profil_candidat(nom, prenom):
    """Affiche la page de félicitations en nettoyant le %20 pour l'affichage visuel."""
    # Décodage des caractères URL pour l'affichage propre à l'écran
    nom_propre = urllib.parse.unquote(nom)
    prenom_propre = urllib.parse.unquote(prenom)
    return render_template('candidat.html', nom=nom_propre, prenom=prenom_propre)


@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """Télécharge le fichier en nettoyant le nom pour éviter le Not Found."""
    # Transformation de "ASELE%20LIKAKA" en "ASELE LIKAKA"
    nom_fichier_propre = urllib.parse.unquote(nom_complet)
    
    # Recherche dans le dossier des attestations
    pdf_path = os.path.join(PDF_FOLDER, nom_fichier_propre)
    
    # Recherche de secours dans le dossier static
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.getcwd(), "static", nom_fichier_propre)

    if not os.path.exists(pdf_path):
        return f"Erreur 404 : Le fichier '{nom_fichier_propre}' reste introuvable sur le serveur.", 404

    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    app.run(debug=True, port=5000)
