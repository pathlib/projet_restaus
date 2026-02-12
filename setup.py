from pathlib import Path
from datetime import datetime, date, time, timedelta


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
        a=liste.append({"question": question , "reponse": None, "type": "normale", "date": afficher_heure()})
        return a
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
        if valeur == "True" or "False":
            liste[h]["type"]=valeur
            print(liste)
        else:
            print("erreur")
    except IndexError as e:
         print(f"aucune valeur boleene a affiche {e}")


def rep():
    print("recap")
    for reponse in liste:
        if None is liste:
            print("aucune donnee")
        else:
            print(reponse)

def libre():
    libres=input()
    liste.append(f"commentaire{libre}")


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

        fichier = dossier / "donnees.json"

        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(liste, f, indent=4, ensure_ascii=False)

        print("JSON créé ici :", fichier)

    except PermissionError:
        print("Permission refusée")
    except OSError as e:
        print("Erreur système :", e)


while True:
    a=input("action 1/action 2/action3 : ")
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
        sauvegarde=input(".txt,json,pdf,word")
        if sauvegarde == "1" :
            print("fichier sauvegarder en .txt")
            txt()
        elif sauvegarde == "2":
            print("fichier sauvegarder en .json")
            sauvegarder_json(liste)
