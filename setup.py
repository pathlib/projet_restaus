from pathlib import Path


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


def suppresion():
    print("suppretion")
    print(liste)
    h=int(input("numeros de la question : "))
    try:
        del liste[h]
        print(liste,"supr")
    except IndexError:
        print("il n y a aucune donnée a suprimer")


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


def repbool():
    try:
        h=int(input("numeros de la question : "))
        print(liste[h])
        valeur=input("valeur booeene : ")
        if valeur == "True" or "False":
            g=liste[h]+valeur
            print (g)
        else:
            print("erreur")
    except IndexError:
         print("aucune valeur boleene a affiche")


def rep():
    print("recap")
    for reponse in liste:
        if None is liste:
            print("aucune donnee")
        else:
            print(reponse)


def affiche():
    for r in liste:
        print("recap")
        print(r)


def txt():
    try:
        fichier = Path("mon_fichier.txt")
        fichier.write_text(" ".join(liste), encoding="utf-8")
    except TypeError:
        print("La donnée n'est pas du texte")
    except PermissionError:
        print("Permission refusée")
    except FileNotFoundError:
        print("Dossier introuvable")
    except OSError as e:
        print("Erreur système :", e)

txt()

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
    elif a =="2":
         rep()
    elif a =="3":
        affiche()
    elif a =="4":
        print("save en .txt")
        txt()
