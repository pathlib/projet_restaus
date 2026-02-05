liste = []

def generer_la_question():
    question = input("Entrez un nombre : ")
    a=liste.append(question)
    return a


def generer_la_reponse():
    h=int(input("numeros de la question : "))
    print(liste[h])
    yu=input("reponse")
    v=liste[h]+yu
    print(v)


while True:
    generer_la_question()
    print(liste)
    generer_la_reponse()
