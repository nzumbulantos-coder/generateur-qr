from flask import Flask, render_template, request, send_file
import os
import qrcode
import io
import base64

app = Flask(__name__)

# CONFIGURATION : Mettez ici l'adresse exacte de votre site sur Vercel
VOTRE_DOMAINE_VERCEL = "qr-5txl.vercel.app"

# Configuration du dossier des fichiers PDF
PDF_FOLDER = os.path.join(os.getcwd(), "attestations")

@app.route('/', methods=['GET', 'POST'])
def generateur_qr():
    """
    Gère l'affichage et la soumission du fichier 'formulaire.html'
    pour créer les nouveaux candidats sans bousiller l'URL.
    """
    qr_base64 = None
    nom_complet = ""

    if request.method == 'POST':
        # Récupération et nettoyage strict des données reçues du formulaire
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        nom_complet = f"{nom} {prenom}"

        # CONSTRUCTION DU LIEN PARFAIT (Sans cryptage bizarre ni caractères parasites)
        lien_candidat = f"https://{VOTRE_DOMAINE_VERCEL}/candidat/{nom}/{prenom}"

        # Génération de l'image du QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Conversion de l'image en texte Base64 pour l'afficher dans formulaire.html
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('formulaire.html', qr_base64=qr_base64, nom_complet=nom_complet)


@app.route('/candidat/<nom>/<prenom>')
def profil_candidat(nom, prenom):
    """
    Affiche la page de félicitations ('candidat.html') pour le candidat.
    """
    return render_template('candidat.html', nom=nom, prenom=prenom)


@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """
    Télécharge directement le fichier PDF d'origine du candidat.
    """
    pdf_path = os.path.join(PDF_FOLDER, nom_complet)
    
    # Recherche de secours dans le dossier static si nécessaire
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.getcwd(), "static", nom_complet)

    if not os.path.exists(pdf_path):
        return f"Erreur 404 : Le fichier '{nom_complet}' est introuvable.", 404

    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    app.run(debug=True, port=5000)
