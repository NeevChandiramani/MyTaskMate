import sqlite3
from todoapp import (
    nouveau_compte, se_connecter, ajouter_tache, obtenir_taches,
    marquer_tache_complete, supprimer_tache
)


## Vérifier de pas avoir de base de données avant d'éxécuter ce fichier



# Connexion à la base de données
conn = sqlite3.connect('test_todolist.db')
cursor = conn.cursor()

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS utilisateur (
    utilisateur_id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifiant TEXT UNIQUE NOT NULL,
    mdp TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS taches (
    tache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    tache TEXT NOT NULL,
    description TEXT,
    echeance TEXT NOT NULL,
    est_completee BOOLEAN NOT NULL,
    priorite TEXT CHECK( priorite IN ('Faible', 'Moyenne', 'Haute') ) NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur (utilisateur_id)
)
''')

conn.commit()

# Test des fonctionnalités
def test_fonctions():
    # Création d'un compte
    if nouveau_compte('testuser', 'password'):
        print("Compte créé")

    # Connexion
    user_id = se_connecter('testuser', 'password')
    if user_id:
        print("Connexion réussie")

    # Ajout d'une tâche
    ajouter_tache(user_id, 'Faire les courses','monoprix', '2025-03-01', 'Moyenne')
    print("Tâche ajoutée")

    # Récupération des tâches
    taches = obtenir_taches(user_id)
    if taches:
        print("Tâches récupérées")

    # Marquer comme complétée
    tache_id = taches[0][0]  # Premier élément de la première tâche
    marquer_tache_complete(tache_id)
    print("Tâche complétée")

    
    # Suppression de la tâche
    supprimer_tache(tache_id)
    print("Tâche supprimée")

    # Vérification qu'il ne reste plus de tâches
    if not obtenir_taches(user_id):
        print("Toutes les tâches supprimées")

test_fonctions()

# Fermeture de la connexion
conn.close()



