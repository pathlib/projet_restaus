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
    del liste[h]
    print(liste,"supr")

def reponse():
   h=int(input("numeros de la question : "))
   print(liste[h])
   yu=input("reponse : ")
   v=liste[h]+yu
   liste[h]=v
   print(liste)

def repbool():
    h=int(input("numeros de la question : "))
    print(liste[h])
    
    
    



while True:
    question()
    print(liste)
    z=input("fin/supr : ")
    if z == "fin":
        reponse()
        print(liste)
        print(liste[0])
    elif z == "supr":
        suppresion()
