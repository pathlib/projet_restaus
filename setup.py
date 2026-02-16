from pathlib import Path
from datetime import datetime, date, time, timedelta
import json
import csv
import os
import time
import platform
import sqlite3


liste = []

# Fonction pour vider l'écran
def delterm():
    time.sleep(1)
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


# Affichage de l'heure
def afficher_heure():
    maintenant = datetime.now()
    date_str = maintenant.strftime("%d/%m/%Y")
    heure_str = maintenant.strftime("%H:%M:%S")
    print("Date :", date_str)
    print("Heure :", heure_str)
    return f"{date_str} {heure_str}"


# Fonction pour saisir une question
def question():
    try:
        question = input("Entrez une question : ")
        if question == "":
            raise KeyboardInterrupt
        print(question)
        liste.append({"question": question, "reponse": "None", "type": "normale", "commentaire": "None", "date": afficher_heure()})
        delterm()
    except KeyboardInterrupt:
        pass


# Fonction pour supprimer une question de la liste
def suppresion():
    print("Suppression")
    h = int(input("Numéro de la question : "))
    print(liste[h]['question'])
    try:
        del liste[h]
        delterm()
    except IndexError as e:
        print(f"Il n'y a aucune donnée à supprimer {e}")


# Fonction pour ajouter une réponse à une question
def reponse():
    try:
        h = int(input("Numéro de la question : "))
        print(liste[h]["question"])
        yu = input("Réponse : ")
        liste[h]["reponse"] = yu
        print(f"La question est : {liste[h]['question']}, réponse : {liste[h]['reponse']}")
        delterm()
    except IndexError as e:
        print(f"Aucune réponse à afficher {e}")


# Fonction pour saisir une valeur booléenne
def repbool():
    try:
        h = int(input("Numéro de la question : "))
        print(liste[h]["question"])
        valeur = input("Valeur booléenne (True/False) : ")
        if valeur == "True" or valeur == "False":
            liste[h]["type"] = valeur
            print(liste)
            delterm()
        else:
            print("Erreur")
    except IndexError as e:
        print(f"Aucune valeur booléenne à afficher {e}")


# Fonction pour afficher toutes les questions/réponses
def rep():
    print("Récapitulatif")
    print("_______________")
    if not liste:
        print("Aucune donnée")
        return
    else:
        print(f"{'Question':<20} {'Réponse':<10} {'Type':<10} {'Commentaire':<20} {'Date':<10}")
        for ligne in liste:
            print(f"{ligne['question']:<20} {ligne['reponse']:<10} {ligne['type']:<10} {ligne['commentaire']:<20} {ligne['date']:<10}")
            y = input("Finish ? ")
            if y == "finish":
                delterm()


# Fonction pour ajouter un commentaire à une question
def libre():
    libres = input("Votre commentaire : ")
    h = int(input("Numéro de la question : "))
    liste[h]["commentaire"] = libres


# Création de la base de données SQLite
def create_db():
    conn = sqlite3.connect('ma_base.db')
    c = conn.cursor()

    # Création de la table si elle n'existe pas déjà
    c.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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


# Fonction pour ajouter une question à la base de données
def ajouter_utilisateur(question, reponse, type_, commentaire, date):
    conn = sqlite3.connect('ma_base.db')
    c = conn.cursor()

    # Insertion de la question dans la base de données
    c.execute('''
        INSERT INTO utilisateurs (question, reponse, type, commentaire, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (question, reponse, type_, commentaire, date))

    # Sauvegarde des modifications
    conn.commit()
    conn.close()


# Fonction pour afficher tous les utilisateurs (questions dans la base de données)
def afficher_utilisateurs():
    conn = sqlite3.connect('ma_base.db')
    c = conn.cursor()

    # Sélectionner toutes les questions
    c.execute('SELECT * FROM utilisateurs')
    utilisateurs = c.fetchall()

    # Affichage des utilisateurs
    for utilisateur in utilisateurs:
        print(utilisateur)

    conn.close()


# Fonction pour supprimer une question de la base de données par ID
def supprimer_utilisateur(id_utilisateur):
    conn = sqlite3.connect('ma_base.db')
    c = conn.cursor()

    # Suppression de la question par ID
    c.execute('DELETE FROM utilisateurs WHERE id = ?', (id_utilisateur,))

    # Sauvegarde des modifications
    conn.commit()
    conn.close()

def txt():
    try:
        home = Path.home()

        # Détecter le dossier Bureau / Desktop
        if (home / "Desktop").exists():
            bureau = home / "Desktop"
        elif (home / "Bureau").exists():
            bureau = home / "Bureau"
        else:
            # fallback : dossier utilisateur
            bureau = home

        # Créer le dossier
        dossier = bureau / "reconditionnement"
        dossier.mkdir(exist_ok=True)

        # Créer le fichier
        monfichier=input("")
        fichier = dossier / f"{monfichier}.txt"
        contenu = "\n".join(map(str, liste))
        fichier.write_text(contenu, encoding="utf-8")
        print("Dossier et fichier créés ici :", dossier)

    except PermissionError as e:
        print(f"Vous n'avez pas la permission d'écrire ici !{e}")
    except OSError as e:
        print(f"Erreur système : {e}")
    except Exception as e :
        print(e)
# Sauvegarder la liste en JSON


def sauvegarder_json(liste):
    try:
        home = Path.home()

        if (home / "Desktop").exists():
            bureau = home / "Desktop"
        elif (home / "Bureau").exists():
            bureau = home / "Bureau"
        else:
            bureau = home

        dossier = bureau / "reconditionnement"
        dossier.mkdir(exist_ok=True)
        nomjson = input("Nom du fichier JSON : ")

        fichier = dossier / f"{nomjson}.json"

        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(liste, f, indent=4, ensure_ascii=False)

        print("JSON créé ici :", fichier)
        delterm()
    except PermissionError:
        print("Permission refusée")
    except OSError as e:
        print("Erreur système :", e)
    except Exception as e:
        print(e)


# Charger les données depuis un fichier JSON
def charger_json():
    try:
        home = Path.home()

        if (home / "Desktop").exists():
            bureau = home / "Desktop"
        elif (home / "Bureau").exists():
            bureau = home / "Bureau"
        else:
            bureau = home

        dossier = bureau / "reconditionnement"

        nomjson = input("Nom du fichier à charger (sans .json) : ")
        fichier = dossier / f"{nomjson}.json"

        if not fichier.exists():
            print("Fichier introuvable.")
            return []

        with open(fichier, "r", encoding="utf-8") as f:
            liste = json.load(f)

        print("JSON chargé depuis :", fichier)
        return liste
    except json.JSONDecodeError:
        print("Erreur : fichier JSON invalide")
        return []
    except Exception as e:
        print("Erreur :", e)
        return []


# Menu principal
while True:
    delterm()
    print("======== Menu Principal ========")
    a=input("1 enregistre votre question/2 afficher le reacap/3 enregistre votre progression: ")
    if a == "1":
        question()
        z=input("fin/supr/bool/libre : ")
        if z == "fin":
            reponse()

            
        elif z == "supr":
           suppresion()
        elif z == "bool":
           repbool()
        elif z == "libre":
            libre()
    
    elif a =="2":
         rep()
    
    
    elif a =="3":
        print("choisiser votre mode de sauvegarde txt,json,pdf word ")
        sauvegarde=input(".txt,json,charger_json,CSV,pdf,word")
        if sauvegarde == "1" :
            print("fichier sauvegarder en .txt")
            txt()
        elif sauvegarde == "2":
            print("fichier sauvegarder en .json")
            sauvegarder_json(liste)
        elif sauvegarde == "3":
            liste=charger_json()
        elif sauvegarde == "4":
            nomcsv=input("nom du fichier")
            creer_csv(nomcsv,liste)
            
