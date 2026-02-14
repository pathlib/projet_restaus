import sqlite3

def ajouter_donnees(cursor, question):
    cursor.execute("INSERT INTO user (question) VALUES (?)", (question,))

def afficher_donnees(cursor):
    cursor.execute("SELECT * FROM user")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"- {row[0]}")
    else:
        print("Aucune donnée à afficher.")

def supprimer_donnees(cursor, question):
    cursor.execute("DELETE FROM user WHERE question = ?", (question,))
    if cursor.rowcount > 0:
        print(f"Question '{question}' supprimée avec succès.")
    else:
        print(f"Aucune question trouvée avec le texte '{question}'.")

def menu():
    print("\n--- Menu ---")
    print("1. Ajouter une question")
    print("2. Afficher toutes les questions")
    print("3. Supprimer une question")
    print("4. Quitter")

def base_de_donne():
    # Connexion à la base de données
    curs = sqlite3.connect("mabase.db")  # Nom du fichier de la base de données
    cursor = curs.cursor()

    # Création de la table (si elle n'existe pas déjà)
    cursor.execute("CREATE TABLE IF NOT EXISTS user (question TEXT)")

    while True:
        menu()  # Afficher le menu
        choix = input("Choisissez une option : ")

        if choix == "1":
            question = input("Entrez la question à ajouter : ")
            ajouter_donnees(cursor, question)
            curs.commit()
            print("Question ajoutée avec succès.")

        elif choix == "2":
            print("\n--- Liste des questions ---")
            afficher_donnees(cursor)

        elif choix == "3":
            question = input("Entrez la question à supprimer : ")
            supprimer_donnees(cursor, question)
            curs.commit()

        elif choix == "4":
            print("Au revoir !")
            break  # Quitter la boucle et fermer le programme

        else:
            print("Option invalide, veuillez réessayer.")

    # Fermeture de la connexion
    curs.close()

# Lancer le programme
base_de_donne()
