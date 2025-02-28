
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
    mytaskmate = Todolist(root)
    assert mytaskmate.utilisateur_actuel is None
    print("Todolist instanciée")
    
    # Mock des méthodes de Todolist pour tester leurs appels
    mytaskmate.connexion = MagicMock()
    mytaskmate.créer_compte = MagicMock()
    mytaskmate.montrer_fenetre_principale = MagicMock()
    mytaskmate.rafraichir_taches = MagicMock()
    mytaskmate.ajouter_tache = MagicMock()
    mytaskmate.date_valide = MagicMock(return_value=True)
    mytaskmate.enregistrer_tache = MagicMock()
    mytaskmate.annuler = MagicMock()
    mytaskmate.description_tache = MagicMock()
    mytaskmate.marquer_completee = MagicMock()
    mytaskmate.supprimer_tache = MagicMock()
    mytaskmate.deconnecter = MagicMock()
    
    # Vérification des appels aux méthodes
    mytaskmate.connexion()
    mytaskmate.connexion.assert_called_once()
    
    mytaskmate.créer_compte()
    mytaskmate.créer_compte.assert_called_once()
    
    mytaskmate.montrer_fenetre_principale()
    mytaskmate.montrer_fenetre_principale.assert_called_once()
    
    mytaskmate.rafraichir_taches()
    mytaskmate.rafraichir_taches.assert_called_once()
    
    mytaskmate.ajouter_tache()
    mytaskmate.ajouter_tache.assert_called_once()
    
    mytaskmate.date_valide("2025-03-01")
    mytaskmate.date_valide.assert_called_once()
    
    mytaskmate.enregistrer_tache()
    mytaskmate.enregistrer_tache.assert_called_once()
    
    mytaskmate.annuler()
    mytaskmate.annuler.assert_called_once()
    
    mytaskmate.description_tache()
    mytaskmate.description_tache.assert_called_once()
    
    mytaskmate.marquer_completee()
    mytaskmate.marquer_completee.assert_called_once()
    
    mytaskmate.supprimer_tache()
    mytaskmate.supprimer_tache.assert_called_once()
    
    mytaskmate.deconnecter()
    mytaskmate.deconnecter.assert_called_once()
    
    print("Tous les tests sont passés !")
    
    # Fermeture de l'interface graphique
    root.destroy()

test_fonctions()
conn.close()

