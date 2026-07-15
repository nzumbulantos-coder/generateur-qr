from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2.extras import RealDictCursor
import qrcode
import os

app = Flask(__name__)

# On récupère proprement la configuration de la base de données depuis l'environnement
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        # En local ou si la variable n'est pas définie, on utilise par défaut le pooler Supabase
        return psycopg2.connect("postgresql://postgres:lvjj@://supabase.com")
    return psycopg2.connect(DATABASE_URL)

# 1. Page d'accueil : Formulaire d'ajout et liste des candidats
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        nom = request.form['nom'].upper()
        prenom = request.form['prenom'].upper()
        
        # Insertion dans Supabase et récupération immédiate de l'ID généré
        cursor.execute("INSERT INTO candidats (nom, prenom) VALUES (%s, %s) RETURNING id;", (nom, prenom))
        id_candidat = cursor.fetchone()['id']
        conn.commit()

        # Génération automatique du QR Code unique pointant vers votre lien Vercel
        lien_candidat = f"https://vercel.app{id_candidat}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(lien_candidat)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarde du QR code dans le dossier static
        if not os.path.exists('static'):
            os.makedirs('static')
        img.save(f"static/qr_{id_candidat}.png")

        cursor.close()
        conn.close()
        return redirect('/')

    # Récupération de tous les candidats pour les afficher dans le tableau
    cursor.execute("SELECT id, nom, prenom FROM candidats ORDER BY id DESC;")
    candidats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('formulaire.html', candidats=candidats)

# 2. Page affichée lors du scan du QR Code par un smartphone
@app.route('/candidat/<int:id_candidat>')
def afficher_candidat(id_candidat):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT nom, prenom FROM candidats WHERE id = %s;", (id_candidat,))
    candidat = cursor.fetchone()
    cursor.close()
    conn.close()

    if candidat:
        return render_template('candidat.html', nom=candidat['nom'], prenom=candidat['prenom'])
    return "Candidat introuvable", 404

if __name__ == '__main__':
    app.run(debug=True, port=8080)
