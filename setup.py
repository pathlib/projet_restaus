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
    print("supretion")
    print(liste)
    h=int(input("numeros de la question : "))
    try:
        del liste[h]
        print(liste,"supr")
    except IndexError:
        print("il n y a aucune donnée a suprimer")
   

def reponse():
   h=int(input("numeros de la question : "))
   print(liste[h])
   yu=input("reponse : ")
   v=liste[h]+yu
   liste[h]=v
   print(liste)

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
         print("aucune valeur ")

def rep():
    print("recap")
    for reponse in liste:
        if None is liste:
            print("aucune donnee")
        else:
            print(reponse)


while True:
    a=input("action 1/action 2 : ")
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