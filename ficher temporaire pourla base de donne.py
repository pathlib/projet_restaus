import sqlite3

def base_de_donne():
    # Connexion à la base de données
    curs = sqlite3.connect("mabase.db")  # Le nom du fichier de la base de données est 'mabase.db'
    cursor = curs.cursor()

    # Création de la table (si elle n'existe pas déjà)
    cursor.execute("CREATE TABLE IF NOT EXISTS user (question TEXT)")

    # Données à insérer
    listes = ["Quel est ton nom ?", "Quel est ton âge ?", "Où habites-tu ?"]
    # Sélectionner uniquement la première question
    liste = listes[0]

    # Insertion de la première question dans la table
    cursor.execute("INSERT INTO user (question) VALUES (?)", (liste,))

    # Sauvegarder les changements
    curs.commit()

    # Afficher le contenu de la table pour vérifier l'insertion
    cursor.execute("SELECT * FROM user")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # Fermeture de la connexion
    curs.close()

base_de_donne()
