from pathlib import Path
from datetime import datetime, date, time, timedelta
import json
import csv
import os
import time
import platform
from db_manager import (
    create_db,
    ajouter_utilisateurs,
    afficher_utilisateurs,
    supprimer_utilisateur)



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
    except KeyboardInterrupt:
        pass


# Fonction pour supprimer une question de la liste
def suppresion():
    print("Suppression")
    h = int(input("Numéro de la question : ")) - 1
    print(liste[h]['question'])
    try:
        del liste[h]
        print("Question supprimée.")
        input("Appuyez sur Entrée pour continuer...")
    except IndexError as e:
        print(f"Il n'y a aucune donnée à supprimer {e}")
        input("Appuyez sur Entrée pour continuer...")


# Fonction pour ajouter une réponse à une question
def reponse():
    try:
        h = int(input("Numéro de la question : ")) - 1
        print(liste[h]["question"])
        yu = input("Réponse : ")
        liste[h]["reponse"] = yu
        print(f"La question est : {liste[h]['question']}, réponse : {liste[h]['reponse']}")
        input("Appuyez sur Entrée pour continuer...")
    except IndexError as e:
        print(f"Aucune réponse à afficher {e}")
        input("Appuyez sur Entrée pour continuer...")


# Fonction pour saisir une valeur booléenne
def repbool():
    try:
        h = int(input("Numéro de la question : ")) - 1
        print(liste[h]["question"])
        valeur = input("Valeur booléenne (True/False) : ")
        if valeur == "True" or valeur == "False":
            liste[h]["type"] = valeur
            print(liste)
            input("Appuyez sur Entrée pour continuer...")
        else:
            print("Erreur")
            input("Appuyez sur Entrée pour continuer...")
    except IndexError as e:
        print(f"Aucune valeur booléenne à afficher {e}")
        input("Appuyez sur Entrée pour continuer...")


# Fonction pour afficher toutes les questions/réponses
def rep():
    print("Récapitulatif")
    print("_______________")
    if not liste:
        print("Aucune donnée")
        input("Appuyez sur Entrée pour continuer...")
    else:
        print(f"{'N°':<5} {'Question':<20} {'Réponse':<10} {'Type':<10} {'Commentaire':<20} {'Date':<10}")
        for i, ligne in enumerate(liste, 1):
            print(f"{i:<5} {ligne['question']:<20} {ligne['reponse']:<10} {ligne['type']:<10} {ligne['commentaire']:<20} {ligne['date']:<10}")
        
        input("Appuyez sur Entrée pour continuer...")


# Fonction pour ajouter un commentaire à une question
def libre():
    libres = input("Votre commentaire : ")
    h = int(input("Numéro de la question : ")) - 1
    liste[h]["commentaire"] = libres



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
        input("Appuyez sur Entrée pour continuer...")
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

def sauvegarder_csv(liste):
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
        nomcsv = input("Nom du fichier CSV : ")

        fichier = dossier / f"{nomcsv}.csv"

        # Ouvre le fichier en mode écriture
        with open(fichier, mode='w', newline='', encoding="utf-8") as f:
            # Si la liste n'est pas vide, on utilise la première ligne pour les en-têtes (les clés du dictionnaire)
            if liste:
                writer = csv.DictWriter(f, fieldnames=liste[0].keys())
                writer.writeheader()  # Écriture des en-têtes (les clés du dictionnaire)
                
                # Écriture des lignes de données
                for ligne in liste:
                    writer.writerow(ligne)

        print("CSV créé ici :", fichier)
        input("Appuyez sur Entrée pour continuer...")
    except PermissionError:
        print("Permission refusée")
    except OSError as e:
        print("Erreur système :", e)
    except Exception as e:
        print(e)



# Menu principal
while True:
    try :
        delterm()
        print("======== Menu Principal ========\n")
        a=input("/1 Enregistre votre question\n/2 Afficher le reacap\n/3 Enregistre votre progression\n\nChosisez une option a effectuer : (1/2/3)")
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
            print("Choisissez votre mode de sauvegarde : 1.txt, 2.json, 3.charger_json, 4.CSV, 5.DB")
            sauvegarde=input("Votre choix (1-5) : ")
            if sauvegarde == "1" :
                print("fichier sauvegarder en .txt")
                txt()
                input("Appuyez sur Entrée pour continuer...")
            elif sauvegarde == "2":
                print("fichier sauvegarder en .json")
                sauvegarder_json(liste)
            elif sauvegarde == "3":
                liste=charger_json()
            elif sauvegarde == "4":
                sauvegarder_csv(liste)
            elif sauvegarde == "5":
                if not liste:
                    print("Attention : La liste est vide. Ajoutez des questions (Menu 1) avant de sauvegarder.")
                else:
                    create_db()
                    ajouter_utilisateurs(liste)
                    print(f"{len(liste)} données sauvegardées en base de données.")

                tt=input("Tapez 'affiche' pour voir, 'suppr' pour supprimer l'ID 1, ou Entrée pour quitter : ").strip().lower()
                if tt == "affiche":
                    afficher_utilisateurs()
                    input("Appuyez sur Entrée pour continuer...")
                if tt == "suppr":
                    supprimer_utilisateur(1)
                    afficher_utilisateurs()
                    input("Appuyez sur Entrée pour continuer...")
    except KeyboardInterrupt:
        print("\nFermeture du programme...")
        break
