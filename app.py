from flask import Flask, render_template, request, render_template_string
import qrcode
import io
import base64

app = Flask(__name__)

# 1. Page d'accueil : Formulaire simple
@app.route('/', methods=['GET', 'POST'])
def index():
    qr_base64 = None
    nom_complet = None
    
    if request.method == 'POST':
        nom = request.form['nom'].upper()
        prenom = request.form['prenom'].upper()
        nom_complet = f"{nom} {prenom}"
        
        # On encode les informations du candidat directement dans l'URL du QR code !
        # Plus besoin de base de données pour se souvenir de lui.
        nom_encode = base64.b64encode(nom.encode('utf-8')).decode('utf-8')
        prenom_encode = base64.b64encode(prenom.encode('utf-8')).decode('utf-8')
        
        lien_candidat = f"https://generateur-qr-5txl.vercel.app/candidat?n={nom_encode}&p={prenom_encode}"
        
        # Génération du QR Code en mémoire vive
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Transformation de l'image en texte affichable instantanément sur la page
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('formulaire.html', qr_base64=qr_base64, nom_complet=nom_complet)

# 2. Page affichée lors du scan du QR Code (Décodage des infos en direct)
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

if __name__ == '__main__':
    app.run(debug=True, port=8080)
