liste = []

def math():
    question = input("Entrez un nombre : ")
    a=liste.append(question)
    return a


def ert():
    h=int(input("numeros de la question : "))
    print(liste[h])
    yu=input("reponse")
    v=liste[h]+yu
    print(v)


while True:
    math()
    print(liste)
    ert()
