from flask import Flask, render_template, send_file
import os

app = Flask(__name__)

# Configuration du dossier contenant vos fichiers PDF
PDF_FOLDER = os.path.join(os.getcwd(), "attestations")

@app.route('/candidat/<nom>/<prenom>')
def profil_candidat(nom, prenom):
    """Affiche la page de félicitations."""
    return render_template('candidat.html', nom=nom, prenom=prenom)

@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """Force le téléchargement direct du fichier PDF."""
    safe_filename = os.path.basename(nom_complet)
    pdf_path = os.path.join(PDF_FOLDER, safe_filename)
    
    if not os.path.exists(pdf_path):
        return f"Erreur : Le fichier '{safe_filename}' est introuvable.", 404

    try:
        # On force le mode attachement pour le téléchargement direct
        response = send_file(
            pdf_path, 
            mimetype='application/pdf',
            as_attachment=True, 
            download_name=safe_filename
        )
        # Ajout d'en-têtes pour réveiller le gestionnaire de téléchargement d'Android
        response.headers["Content-Description"] = "File Transfer"
        response.headers["Transfer-Encoding"] = "chunked"
        return response
    except Exception as e:
        return f"Erreur : {str(e)}", 500

if __name__ == '__main__':
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    app.run(debug=True, port=5000)
