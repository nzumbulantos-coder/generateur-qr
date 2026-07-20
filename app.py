from flask import Flask, render_template, request, send_from_directory
import qrcode
import io
import base64
import urllib.parse
import os

app = Flask(__name__)

# 1. Page d'accueil : Formulaire simple
@app.route('/', methods=['GET', 'POST'])
def index():
    qr_base64 = None
    nom_complet = None
    
    if request.method == 'POST':
        nom = request.form['nom'].upper().strip()
        prenom = request.form['prenom'].upper().strip()
        nom_complet = f"{nom} {prenom}"
        
        # Encodage sécurisé des informations du candidat
        nom_encode = base64.b64encode(nom.encode('utf-8')).decode('utf-8')
        prenom_encode = base64.b64encode(prenom.encode('utf-8')).decode('utf-8')
        
        # CETTE LIGNE EST MAGIQUE : Elle détecte automatiquement l'adresse active (generateur-qr-5txl.vercel.app)
        # sans risque de coupure ou d'erreur d'écriture !
        host = request.host
        lien_candidat = f"https://{host}/candidat?n={nom_encode}&p={prenom_encode}"
        
        # Génération du QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('formulaire.html', qr_base64=qr_base64, nom_complet=nom_complet)

# 2. Page affichée lors du scan du QR Code
@app.route('/candidat')
def afficher_candidat():
    try:
        nom_encode = request.args.get('n', '')
        prenom_encode = request.args.get('p', '')
        
        nom = base64.b64decode(nom_encode.encode('utf-8')).decode('utf-8')
        prenom = base64.b64decode(prenom_encode.encode('utf-8')).decode('utf-8')
        
        return render_template('candidat.html', nom=nom, prenom=prenom)
    except Exception:
        return "Informations du candidat invalides ou corrompues", 400

# 3. Téléchargement intelligent (Compatible avec tous vos fichiers avec ou sans espaces/accents)
@app.route('/telecharger-pdf/<path:filename>')
def download_file(filename):
    clean_filename = urllib.parse.unquote(filename).strip()
    clean_filename = clean_filename.replace('É', 'E')
    
    try:
        return send_from_directory('static', clean_filename, as_attachment=True)
    except Exception:
        try:
            sans_espace_demande = clean_filename.replace(' ', '')
            for fichier_reel in os.listdir('static'):
                if fichier_reel.replace(' ', '').upper() == sans_espace_demande.upper():
                    return send_from_directory('static', fichier_reel, as_attachment=True)
            raise FileNotFoundError
        except Exception:
            return "Le fichier d'attestation demandé est introuvable sur le serveur.", 404

if __name__ == '__main__':
    app.run(debug=True, port=8080)
