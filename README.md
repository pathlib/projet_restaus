Projet Restau - Reconditionnement de Matériel Informatique
Description du Projet

Le projet Restau a pour objectif de centraliser et structurer les informations relatives aux Restos du Cœur, dans le but de les exploiter via une interface graphique (GUI) dédiée à un logiciel de reconditionnement de matériel informatique. Il vise à faciliter la gestion des données et à permettre une exploitation simple et intuitive des informations.

Le projet fonctionne comme une base de données légère, facilement maintenable et conçue pour s’intégrer sans difficulté dans une application existante ou en développement.

Le projet est volontairement minimaliste pour garantir une bonne lisibilité du code et permettre une évolution progressive en fonction des besoins futurs, notamment avec l’intégration de diverses technologies et modules.

Fonctionnalités
1. Gestion des informations des Restos du Cœur

Centralisation et structuration des données relatives aux Restos du Cœur.

Facilité d'ajout, modification et suppression des informations.

2. Interface graphique (GUI)

Développement d’une interface graphique pour la gestion et l’affichage des données.

L'interface permet une interaction utilisateur simplifiée avec les données.

3. Reconditionnement de Matériel Informatique

Gestion de l’historique des machines reconditionnées.

Suivi des étapes de reconditionnement de chaque machine.

4. Modules Utilisateur et Droits

Gestion des utilisateurs et des droits d’accès.

Module d’authentification pour contrôler les accès à certaines fonctionnalités de l’application.

5. Tableaux récapitulatifs

Génération de tableaux récapitulatifs pour un suivi détaillé des activités.

Export des données au format CSV et autres formats compatibles.

Technologies Utilisées

Le projet utilise plusieurs bibliothèques et outils Python pour sa mise en œuvre. Voici une liste des principales technologies employées :

Pathlib : Gestion des chemins de fichiers et répertoires de manière sécurisée et lisible.

PDF : Génération de rapports en format PDF pour la documentation et les rapports d’activités.

SQLite : Base de données légère pour stocker et gérer les informations relatives aux Restos du Cœur et aux machines reconditionnées.

PySide6 : Framework pour le développement de l’interface graphique (GUI).

Datetime : Gestion des dates et heures pour le suivi des événements (par exemple, date de reconditionnement, date d’ajout des machines).

JSON : Manipulation des données en format JSON pour la sérialisation des informations.

CSV : Export des données sous format CSV pour permettre leur exploitation en dehors de l’application.

Structure du Projet

La structure du projet est organisée de manière à permettre une évolution progressive et facile à maintenir. Voici un aperçu de l'architecture des fichiers :

Projet_Restau/
│
├── src/                   # Code source principal
│   ├── gui/               # Interface graphique (PySide6)
│   ├── models/            # Gestion des modèles de données (Base de données, machines, utilisateurs)
│   ├── utils/             # Utilitaires et fonctions génériques (Pathlib, CSV, JSON)
│   └── main.py            # Point d'entrée du programme
│
├── data/                  # Fichiers de données (SQLite, CSV, JSON)
│   ├── historique.csv     # Historique des machines reconditionnées
│   └── utilisateurs.json  # Liste des utilisateurs et droits d’accès
│
├── docs/                  # Documentation technique et guides
│   └── README.md          # Ce fichier README
│
└── requirements.txt       # Liste des dépendances

Installation
Prérequis

Python 3.7 ou supérieur

Bibliothèques Python : PySide6, sqlite3, pandas, matplotlib (si nécessaire pour l'affichage graphique), etc.

Installation des dépendances

Pour installer les dépendances nécessaires à l'exécution du projet, il suffit d'exécuter la commande suivante dans ton terminal :

pip install -r requirements.txt

Lancer l'application

Assure-toi que toutes les dépendances sont installées.

Lance l’application avec la commande :

python src/main.py


Cela démarrera l’interface graphique et te permettra de commencer à interagir avec l’application.

Utilisation
Ajouter une machine

L'utilisateur peut entrer les informations relatives à une machine (nom, type, date de reconditionnement, etc.).

Ces données sont enregistrées dans une base de données SQLite, et un historique des machines reconditionnées est généré.

Gérer les utilisateurs

Un administrateur peut ajouter ou supprimer des utilisateurs et leur attribuer des droits d’accès.

Un module d’authentification permet de contrôler l'accès à certaines fonctionnalités sensibles.

Exporter les données

Les données peuvent être exportées sous plusieurs formats :

CSV : Export des données dans un format compatible pour une utilisation avec Excel ou d'autres outils de gestion de données.

PDF : Génération de rapports PDF pour la documentation des activités.

Fonctionnalités à venir

Le projet est actuellement en développement, et plusieurs fonctionnalités sont prévues dans les prochaines versions :

Module de recherche avancée pour les machines.

Rapports statistiques sur les reconditionnements (graphiques et résumés).

Améliorations de l'interface graphique avec des éléments plus interactifs.

Contribuer

Le projet est en cours, et les contributions sont les bienvenues ! Si tu souhaites participer à son développement, voici quelques étapes pour commencer :

Fork le projet.

Crée une branche pour ta fonctionnalité : git checkout -b feature-nouvelle-fonctionnalite.

Fais tes modifications et commit tes changements.

Ouvre une pull request pour que ton code soit examiné et fusionné.

Licence

Ce projet est sous licence MIT. Tu peux librement utiliser, modifier et distribuer le code, tout en respectant les termes de cette licence.

Ce README devrait maintenant donner une vision claire de ton projet, de ses fonctionnalités, de son installation et de son utilisation. Assure-toi d'adapter les sections au fur et à mesure que ton projet évolue, surtout pour ajouter des détails spécifiques à ton développement en cours.
