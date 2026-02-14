import sqlite3

def ajouter_donnees(cursor, question):
    """Ajouter une question dans la base de données."""
    cursor.execute("INSERT INTO user (question) VALUES (?)", (question,))
    print("Question ajoutée avec succès.")

def afficher_donnees(cursor):
    """Afficher toutes les questions de la base de données."""
    cursor.execute("SELECT * FROM user")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"- {row[0]}")
    else:
        print("Aucune donnée à afficher.")

def supprimer_donnees(cursor, question):
    """Supprimer une question de la base de données."""
    cursor.execute("DELETE FROM user WHERE question = ?", (question,))
    if cursor.rowcount > 0:
        print(f"Question '{question}' supprimée avec succès.")
    else:
        print(f"Aucune question trouvée avec le texte '{question}'.")

def menu():
    """Afficher le menu principal."""
    print("\n--- Menu ---")
    print("1. Ajouter une question")
    print("2. Afficher toutes les questions")
    print("3. Supprimer une question")
    print("4. Quitter")

def base_de_donne():
    """Fonction principale pour gérer la base de données et les options utilisateur."""
    # Connexion à la base de données (création si elle n'existe pas)
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()

    # Créer la table si elle n'existe pas
    cursor.execute("CREATE TABLE IF NOT EXISTS user (question TEXT)")

    while True:
        menu()  # Afficher le menu
        choix = input("Choisissez une option : ")

        if choix == "1":
            question = input("Entrez la question à ajouter : ")
            ajouter_donnees(cursor, question)
            conn.commit()

        elif choix == "2":
            print("\n--- Liste des questions ---")
            afficher_donnees(cursor)

        elif choix == "3":
            question = input("Entrez la question à supprimer : ")
            supprimer_donnees(cursor, question)
            conn.commit()

        elif choix == "4":
            print("Au revoir !")
            break  # Quitter la boucle

        else:
            print("Option invalide, veuillez réessayer.")

    # Fermer la connexion à la base de données
    conn.close()

# Lancer le programme
base_de_donne()
