from pathlib import Path
from datetime import datetime, date, time, timedelta
import json
import csv

liste = []
def afficher_heure():
    maintenant = datetime.now()
    date_str = maintenant.strftime("%d/%m/%Y")
    heure_str = maintenant.strftime("%H:%M:%S")
    print("Date :", date_str)
    print("Heure :", heure_str)
    return f"{date_str} {heure_str}"


def question():
    try:
        question = input("Entrez une question : ")
        if question =="":
            raise KeyboardInterrupt
        liste.append({"question": question , "reponse": None, "type": "normale", "date": afficher_heure()})
    except KeyboardInterrupt:
        pass


def suppresion():
    print("suppretion")
    print(liste)
    h=int(input("numeros de la question : "))
    try:
        del liste[h]
        print(liste,"supr")
    except IndexError as e :
        print(f"il n y a aucune donnée a suprimer {e}")


def reponse():
   try:
       h=int(input("numeros de la question : "))
       print(liste[h])
       yu=input("reponse : ")
       liste[h]["reponse"]=yu
       print(liste)
   except IndexError as e:
       print(f"aucune reponse a affiche {e}")


def repbool():
    try:
        h=int(input("numeros de la question : "))
        print(liste[h]["question"])
        valeur=input("valeur booeene : ")
        if valeur == "True" or valeur == "False":
            liste[h]["type"]=valeur
            print(liste)
        else:
            print("erreur")
    except IndexError as e:
         print(f"aucune valeur boleene a affiche {e}")


def rep():
    print("recap")
    if not liste:
        print("aucune donnée")
    else:
        print(f"{'Nom':<10} {'Âge':<5} {'Ville':<10}")
        for ligne in liste:
            print(f"{ligne['question']:<10} {ligne['reponse']:<5} {ligne['type']:<10} {ligne['date']}")








def libre():
    libres=input()
    liste.append(f"commentaire{libres}")


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
        nomjson=input("")

        fichier = dossier / f"{nomjson}.json"

        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(liste, f, indent=4, ensure_ascii=False)

        print("JSON créé ici :", fichier)

    except PermissionError:
        print("Permission refusée")
    except OSError as e:
        print("Erreur système :", e)
    except Exception as e:
        print(e)


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


def creer_csv(nom_fichier, liste):
    """
    Crée un fichier CSV avec les données fournies.
    
    :param nom_fichier: Le nom du fichier CSV à créer (ex. 'personnes.csv')
    :param liste: Liste de dictionnaires contenant les lignes de données (ex. [{'Nom': 'Alice', 'Âge': 30}, ...])
    """
    # Si la liste est vide, afficher un message
    if not liste:
        print("La liste est vide.")
        return
    
    # Extraire les clés du premier dictionnaire pour les utiliser comme en-têtes de colonnes
    champs = liste[0].keys()

    # Ouvrir le fichier CSV en mode écriture
    with open(nom_fichier, mode='w', newline='') as fichier_csv:
        writer = csv.DictWriter(fichier_csv, fieldnames=champs)
        writer.writeheader()  # Écrire les en-têtes
        writer.writerows(liste)  # Écrire les lignes de données

    print(f"Fichier '{nom_fichier}' créé avec succès.")

# Appel de la fonction
creer_csv("personnes.csv", liste)


while True:
    print("========menue principale=========")
    a=input("1 enregistre votre question/2 afficher le reacap/3 enregistre votre progression: ")
    if a == "1":
        question()
        print(liste)
        z=input("fin/supr/bool/libre : ")
        if z == "fin":
            reponse()

            print(liste[0])
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
            nomcsv=input("")
            creer_csv(nomcsv,liste)
            
