liste = []

def math():
    try:
        question = input("Entrez une question : ")
        if question =="":
            raise KeyboardInterrupt
        a=liste.append(question)
        return a
    except KeyboardInterrupt:
        pass
   

def ert():
   h=int(input("numeros de la question : "))
   print(liste[h])
   yu=input("reponse : ")
   v=liste[h]+yu
   liste[h]=v
   print(liste)

while True:
    math()
    print(liste)
    z=input("fin : ")
    if z == "fin":
        ert()
        print(liste)
    
