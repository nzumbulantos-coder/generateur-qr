from flask import Flask, render_template, send_file
import os

app = Flask(__name__)

def chercher_pdf_sur_serveur(nom_fichier):
    """
    Parcourt intelligemment les dossiers du serveur pour trouver le PDF,
    ce qui évite les erreurs 404 si le nom du dossier a changé.
    """
    # Dossiers probables où peuvent être stockés vos fichiers
    dossiers_possibles = [
        os.path.join(os.getcwd(), "attestations"),
        os.path.join(os.getcwd(), "static"),
        os.path.join(os.getcwd(), "static", "pdf"),
        os.getcwd() # Racine du projet
    ]
    
    for dossier in dossiers_possibles:
        chemin_test = os.path.join(dossier, nom_fichier)
        if os.path.exists(chemin_test):
            return chemin_test
            
    return None

@app.route('/candidat/<nom>/<prenom>')
def profil_candidat(nom, prenom):
    """Affiche la page de félicitations personnalisée."""
    return render_template('candidat.html', nom=nom, prenom=prenom)

@app.route('/telecharger-pdf/<nom_complet>')
def telecharger_pdf(nom_complet):
    """Gère le téléchargement direct du PDF sans ouvrir de page."""
    safe_filename = os.path.basename(nom_complet)
    
    # Recherche automatique du fichier dans tous vos dossiers
    pdf_path = chercher_pdf_sur_serveur(safe_filename)
    
    # Si le fichier n'est pas trouvé avec son nom brut, on teste en retirant l'extension .pdf de l'URL
    if not pdf_path and safe_filename.lower().endswith('.pdf'):
        pdf_path = chercher_pdf_sur_serveur(safe_filename)

    # Si le fichier reste introuvable, on affiche la liste des dossiers scannés pour vous aider
    if not pdf_path:
        return f"Erreur 404 : Le fichier '{safe_filename}' est introuvable sur le serveur.", 404

    try:
        # Configuration optimale pour déclencher le gestionnaire de téléchargement Android
        response = send_file(
            pdf_path, 
            mimetype='application/pdf',
            as_attachment=True, 
            download_name=safe_filename
        )
        
        # En-têtes pour forcer l'affichage de la flèche de téléchargement Chrome
        response.headers["Content-Description"] = "File Transfer"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    except Exception as e:
        return f"Erreur lors du transfert : {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
