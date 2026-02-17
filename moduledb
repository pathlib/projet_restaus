
import sqlite3
import os

# Chemin absolu pour garantir que la DB est créée au bon endroit (dans le même dossier que ce script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ma_base.db')

# Fonction pour créer la base de données'

def create_db():
    conn = sqlite3.connect(DB_PATH)  # Utilisation d'une seule base de données
    c = conn.cursor()

    # Création de la table si elle n'existe pas déjà
    c.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            reponse TEXT,
            type TEXT,
            commentaire TEXT,
            date TEXT
        )
    ''')

    # Sauvegarde des modifications
    conn.commit()
    conn.close()


# Fonction pour ajouter plusieurs entrées à la base de données à partir d'une liste de dictionnaires
def ajouter_utilisateurs(liste):
    conn = sqlite3.connect(DB_PATH)  # Utilisation de la même base de données
    c = conn.cursor()

    # Insertion de chaque entrée dans la base de données
    for utilisateur in liste:
        c.execute('''
            INSERT INTO utilisateurs (question, reponse, type, commentaire, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (utilisateur["question"], utilisateur["reponse"], utilisateur["type"], utilisateur["commentaire"], utilisateur["date"]))

    # Sauvegarde des modifications
    conn.commit()
    conn.close()


# Fonction pour afficher tous les utilisateurs (questions dans la base de données)
def afficher_utilisateurs():
    conn = sqlite3.connect(DB_PATH)  # Connexion à la bonne base de données
    c = conn.cursor()

    # Sélectionner toutes les questions
    c.execute('SELECT * FROM utilisateurs')
    utilisateurs = c.fetchall()

    if not utilisateurs:
        print("Aucune donnée trouvée dans la base de données.")
    else:
        # Affichage des utilisateurs
        for utilisateur in utilisateurs:
            print(f"ID: {utilisateur[0]}, Question: {utilisateur[1]}, Réponse: {utilisateur[2]}, Type: {utilisateur[3]}, Commentaire: {utilisateur[4]}, Date: {utilisateur[5]}")

    conn.close()


# Fonction pour supprimer une question de la base de données par ID
def supprimer_utilisateur(id_utilisateur):
    conn = sqlite3.connect(DB_PATH)  # Connexion à la bonne base de données
    c = conn.cursor()

    # Suppression de la question par ID
    c.execute('DELETE FROM utilisateurs WHERE id = ?', (id_utilisateur,))

    # Sauvegarde des modifications
    conn.commit()
    conn.close()
