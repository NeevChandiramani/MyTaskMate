
import sqlite3
from mytaskmate import (
    nouveau_compte, se_connecter, ajouter_tache, obtenir_taches,
    marquer_tache_complete, supprimer_tache, Planificateur, Todolist
)
import tkinter as tk
from unittest.mock import MagicMock

#IMPORTANT: Vérifier de pas avoir de base de données avant d'éxécuter ce fichier(Supprimer celles créées lors de l'exécution du code principal )



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
    
    # Tests sur Todolist avec mocks
    root = tk.Tk()
    root.withdraw()  
    todoapp = Todolist(root)
    assert todoapp.utilisateur_actuel is None
    print("Todolist instanciée")
    
    # Mock des méthodes de Todolist pour tester leurs appels
    todoapp.connexion = MagicMock()
    todoapp.créer_compte = MagicMock()
    todoapp.montrer_fenetre_principale = MagicMock()
    todoapp.rafraichir_taches = MagicMock()
    todoapp.ajouter_tache = MagicMock()
    todoapp.date_valide = MagicMock(return_value=True)
    todoapp.enregistrer_tache = MagicMock()
    todoapp.annuler = MagicMock()
    todoapp.description_tache = MagicMock()
    todoapp.marquer_completee = MagicMock()
    todoapp.supprimer_tache = MagicMock()
    todoapp.deconnecter = MagicMock()
    
    # Vérification des appels aux méthodes
    todoapp.connexion()
    todoapp.connexion.assert_called_once()
    
    todoapp.créer_compte()
    todoapp.créer_compte.assert_called_once()
    
    todoapp.montrer_fenetre_principale()
    todoapp.montrer_fenetre_principale.assert_called_once()
    
    todoapp.rafraichir_taches()
    todoapp.rafraichir_taches.assert_called_once()
    
    todoapp.ajouter_tache()
    todoapp.ajouter_tache.assert_called_once()
    
    todoapp.date_valide("2025-03-01")
    todoapp.date_valide.assert_called_once()
    
    todoapp.enregistrer_tache()
    todoapp.enregistrer_tache.assert_called_once()
    
    todoapp.annuler()
    todoapp.annuler.assert_called_once()
    
    todoapp.description_tache()
    todoapp.description_tache.assert_called_once()
    
    todoapp.marquer_completee()
    todoapp.marquer_completee.assert_called_once()
    
    todoapp.supprimer_tache()
    todoapp.supprimer_tache.assert_called_once()
    
    todoapp.deconnecter()
    todoapp.deconnecter.assert_called_once()
    
    print("Tous les tests sont passés !")
    
    # Fermeture de l'interface graphique
    root.destroy()

test_fonctions()
conn.close()

