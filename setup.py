
from pathlib import Path
from datetime import datetime

liste = []


def question():
    try:
        question = input("Entrez une question : ")
        if question =="":
            raise KeyboardInterrupt
        a=liste.append(question)
        return a
    except KeyboardInterrupt:
        pass
#ecriture des question

def suppresion():
    print("suppretion")
    print(liste)
    h=int(input("numeros de la question : "))
    try:
        del liste[h]
        print(liste,"supr")
    except IndexError:
        print("il n y a aucune donnée a suprimer")
#suppretion  des question

def reponse():
   try:
       h=int(input("numeros de la question : "))
       print(liste[h])
       yu=input("reponse : ")
       v=liste[h]+yu
       liste[h]=v
       print(liste)
   except IndexError:
       print("aucune reponse a affiche")
#ecriture des reponse 

def repbool():
    try:
        h=int(input("numeros de la question : "))
        print(liste[h])
        valeur=input("valeur booeene : ")
        if valeur == ["True","False"]:
            g=liste[h]+valeur
            print (g)
        else:
            print("erreur")
    except IndexError:
         print("aucune valeur boleene a affiche")
#creation des question en valeur booleene

def rep():
    print("recap")
    for reponse in liste:
        if None is liste:
            print("aucune donnee")
        else:
            print(reponse)
#recap du fichier txt

def affiche():
    for r in liste:
        print("recap")
        print(r)
#affichage pour la seconde page 

def libre():
    libres=input()
    liste.append("fcommentaire{libre}")
#note pour question libre

def txt():
    try:
        dossier = Path("dossier reconditionnement")
        dossier.mkdir(exist_ok=True)
        
        fichier = dossier / "mon_fichier.txt"
        fichier.write_text("Bonjour !", encoding="utf-8")
        
    except FileExistsError:
        print("Le dossier existe déjà !")
    except PermissionError:
        print("Vous n'avez pas la permission d'écrire ici !")
    except FileNotFoundError:
        print("Le chemin est invalide ou un dossier intermédiaire est manquant !")
    except OSError as e:
        print("Erreur système :", e)
  #generation du fichier txt      
    

def afficher_heure():
    """
    Affiche l'heure actuelle au format HH:MM:SS
    """
    try:
        maintenant = datetime.now()  # récupère la date et l'heure actuelles
        heure_str = maintenant.strftime("%H:%M:%S")  # formate en heure:minute:seconde
        print("Heure actuelle :", heure_str)
        return heure_str
    except Exception as e:
        # Attrape toute erreur inattendue
        print("Erreur lors de la récupération de l'heure :", e)
        return None


c=afficher_heure()
print(c)
liste.append(c)
#gestion de l heure

while True:
    a=input("action 1/action 2/action3 : ")
    if a == "1":
        question()
        print(liste)
        z=input("fin/supr/bool : ")
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
        affiche()
    elif a =="4":
        print("save en .txt")
        txt()
