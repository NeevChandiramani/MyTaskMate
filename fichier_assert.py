import sqlite3
from todoapp import (
    nouveau_compte, se_connecter, ajouter_tache, obtenir_taches,
    marquer_tache_complete, supprimer_tache, Planificateur, Todolist
)
import tkinter as tk

# Connexion à la base de données
test_db = 'test_todolist.db'
conn = sqlite3.connect(test_db)
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

def test_fonctions():
    print("Début des tests")
    
    # Test Planificateur
    planificateur = Planificateur()
    planificateur.ajouter_tache([1, "Test", "Desc", "2025-03-01", False, "Moyenne"])
    assert len(planificateur.taches) == 1
    print("Planificateur fonctionne")
    
    # Création d'un compte
    assert nouveau_compte('testuser', 'password')
    print("Compte créé")
    
    # Connexion
    user_id = se_connecter('testuser', 'password')
    assert user_id is not None
    print("Connexion réussie")
    
    # Ajout d'une tâche
    ajouter_tache(user_id, 'Faire les courses', 'Acheter du lait', '2025-03-01', 'Moyenne')
    taches = obtenir_taches(user_id)
    assert len(taches) > 0
    print("Tâche ajoutée")
    
    # Marquer comme complétée
    tache_id = taches[0][0]
    marquer_tache_complete(tache_id)
    print("Tâche complétée")
    
    # Suppression de la tâche
    supprimer_tache(tache_id)
    assert len(obtenir_taches(user_id)) == 0
    print("Tâche supprimée")
    
    # Tests sur Todolist (sans GUI)
    root = tk.Tk()
    app = Todolist(root)
    assert app.utilisateur_actuel is None
    print("Todolist instanciée")
    
    print("Tous les tests sont passés !")

test_fonctions()
conn.close()
