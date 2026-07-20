from flask import Flask, render_template, send_file, abort
import os

app = Flask(__name__)

# Dossier contenant vos fichiers PDF d'attestation
# Changez "attestations" par le nom exact de votre dossier si nécessaire
PDF_FOLDER = os.path.join(os.getcwd(), "attestations")

@app.route('/candidat/<nom>/<prenom>')
def profil_candidat(nom, prenom):
    """
    Affiche la page de félicitations personnalisée pour le candidat.
    """
    return render_template('candidat.html', nom=nom, prenom=prenom)

@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """
    Gère le téléchargement direct du fichier PDF avec notification.
    """
    # Nettoyage du nom de fichier pour éviter les erreurs d'encodage d'URL
    safe_filename = os.path.basename(nom_complet)
    pdf_path = os.path.join(PDF_FOLDER, safe_filename)
    
    # Vérification si le fichier PDF existe bien dans votre dossier
    if not os.path.exists(pdf_path):
        return f"Erreur : Le fichier '{safe_filename}' est introuvable dans le dossier des attestations.", 404

    try:
        # Envoi du fichier en mode attachement strict pour déclencher le téléchargement direct
        response = send_file(
            pdf_path, 
            mimetype='application/pdf',
            as_attachment=True, 
            download_name=safe_filename
        )
        
        # En-têtes HTTP spécifiques pour forcer le gestionnaire d'Android à afficher la flèche de progression
        response.headers["Content-Description"] = "File Transfer"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    except Exception as e:
        return f"Une erreur est survenue lors du téléchargement : {str(e)}", 500

# Lancement de l'application en local
if __name__ == '__main__':
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    app.run(debug=True, port=5000)
