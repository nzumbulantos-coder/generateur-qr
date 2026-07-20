from flask import Flask, render_template, request, send_file
import os
import qrcode
import io
import base64

app = Flask(__name__)

# Configuration du dossier des fichiers PDF
PDF_FOLDER = os.path.join(os.getcwd(), "attestations")

@app.route('/', methods=['GET', 'POST'])
def generateur_qr():
    """
    Gère le formulaire.html et génère un QR code avec un chemin dynamique 
    qui s'adapte automatiquement à votre vrai site web actuel.
    """
    qr_base64 = None
    nom_complet = ""

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        nom_complet = f"{nom} {prenom}"

        # Détection dynamique du domaine (Vercel ou local) pour éviter l'erreur 404
        domaine_actuel = request.host
        lien_candidat = f"https://{domaine_actuel}/candidat/{nom}/{prenom}"

        # Génération de l'image du QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Encodage en base64 pour l'affichage HTML
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('formulaire.html', qr_base64=qr_base64, nom_complet=nom_complet)


@app.route('/candidat/<nom>/<prenom>')
def profil_candidat(nom, prenom):
    """Affiche la page de félicitations du candidat."""
    return render_template('candidat.html', nom=nom, prenom=prenom)


@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """Télécharge directement le fichier PDF associé au candidat."""
    pdf_path = os.path.join(PDF_FOLDER, nom_complet)
    
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.getcwd(), "static", nom_complet)

    if not os.path.exists(pdf_path):
        return f"Erreur 404 : Le fichier '{nom_complet}' est introuvable.", 404

    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    app.run(debug=True, port=5000)