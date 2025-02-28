

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import threading
import time

# La fonction "connect()" permet de se connecter à la base de donnée
conn = sqlite3.connect("todolist.db")

# La fonction "cursor()"" permet d'intéragir avec la base de donnée et d'utiliser les différentes requêtes SQL
cursor = conn.cursor()

# Création des tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS utilisateur (
    utilisateur_id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifiant TEXT UNIQUE NOT NULL,       
    mdp TEXT NOT NULL
)
""")

# "NOT NULL" indique que la valeur ne peut pas être nul
# "AUTOINCREMENT" génère automatiquement une valeur unique pour chaque enregistrement
cursor.execute("""
CREATE TABLE IF NOT EXISTS taches (
    tache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    tache TEXT NOT NULL,
    description TEXTE NOT NULL,
    echeance DATE NOT NULL,
    est_completee BOOLEAN NOT NULL,
    priorite TEXT CHECK( priorite IN ("Faible", "Moyenne", "Haute") ) NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur (utilisateur_id)
)
""")

# La fonction "commit()" permet d'enregistrer les modifications faites sur la base de donnée
conn.commit()

# Fonctions pour la gestion des utilisateurs
def nouveau_compte(nom_identifiant, mot_de_passe) :
    """str, str -> bool
    Crée un compte utilisateur dans la base de donnée"""
    try:
        cursor.execute("INSERT INTO utilisateur (identifiant, mdp) VALUES (?, ?)", (nom_identifiant, mot_de_passe))
        conn.commit()
        return True
    # Permet de vérifier que les veleur de nom_identifiant et mot_de_passe ne sont pas vides
    except sqlite3.IntegrityError :
        return False


# La fonction "fetchone()" prend le 1er enregistrement, ici elle vérifie si il y a bien un enregistrement
def se_connecter(nom_identifiant, mot_de_passe) :
    """str, str -> bool
    Vérifie si l'utilisateur est enregistré dans la base de donnée"""
    cursor.execute("SELECT * FROM utilisateur WHERE identifiant = ? AND mdp = ?", (nom_identifiant, mot_de_passe))
    return cursor.fetchone() is not None


# Fonctions pour la gestion des tâches
def ajouter_tache(id_utilisateur, nom_tache,description_tache, date_echeance, prio) :
    """int, str, str, str -> None
    Ajoute une tâche à la base de donnée"""
    cursor.execute("INSERT INTO taches (utilisateur_id, tache, description, echeance, est_completee, priorite) VALUES (?, ?, ?, ?, ?, ?)",
                   (id_utilisateur, nom_tache, description_tache, date_echeance, False, prio))
    conn.commit()


# def maj_tache(description_tache,prio, id_tache) :
#     """str, str, str, int -> None
#     Met à jour une tâche existante dans la base de donnée"""
#     cursor.execute("UPDATE taches SET description = ?, priorite = ? WHERE tache_id = ?", (description_tache, prio, id_tache))
#     conn.commit()


def supprimer_tache(id_tache) :
    """int -> None
    Supprime une tâche de la base de donnée"""
    cursor.execute("DELETE FROM taches WHERE tache_id = ?", (id_tache,))
    conn.commit()


def marquer_tache_complete(id_tache) :
    """int -> None
    Marque une tâche comme complétée dans la base de donnée"""
    cursor.execute("UPDATE taches SET est_completee = TRUE WHERE tache_id = ?", (id_tache,))
    conn.commit()


def obtenir_taches(id_utilisateur) :
    """int -> list
    Récupère toutes les tâches d'un utilisateur"""
    cursor.execute("SELECT * FROM taches WHERE utilisateur_id = ?", (id_utilisateur,))
    # La fonction fetchall() retourne tous les enregistrements de la commande sql précédente
    return cursor.fetchall()



# Classe d'ordonnancement pour gérer les états des tâches
class Planificateur :
    def __init__(self) :
        self.taches = []


    def ajouter_tache(self, tache) :
        """list -> None
        Ajoute une tâche à la liste des tâches"""
        self.taches.append(tache)


    def run(self) :
        """Planificateur -> None
        Vérifie si une tâche est expirée toutes les minutes"""
        while True :
            for tache in self.taches :
                # La fonction strptime permet de convertir une chaîne de caractère en une date
                echeance = datetime.strptime(tache[4], '%d-%m-%Y') 
                if datetime.now() > echeance :
                    # La fonction showwarning() permet d'afficher une fenêtre d'avertissement personnalisée
                    messagebox.showwarning("La tâche a expiré")
            # Vérifie toutes les minutes avec le time.sleep
            time.sleep(60)



# Interface graphique avec tkinter
class Todolist :
    def __init__(self, principale) :
        # Permet de définir la fenêtre principale
        self.principale = principale
        self.principale.title("Todolist Tg3 code créateur M. Picard dans la boutique les gars")
        self.utilisateur_actuel = None

        self.style = ttk.Style()
        self.style.configure("TLabel", font = ("Helvetica", 12))
        self.style.configure("TButton", font = ("Helvetica", 12))

        # La classe Frame du module ttk permet de définir une fenêtre, qui viendra ce placer au dessus de la fenêtre principale
        self.fenetre_connexion = ttk.Frame(principale)
        self.fenetre_connexion.pack(padx = 10, pady = 10)

        # La classe Label du module ttk permet de définir une chaîne de caractère affichable
        self.identifiant_texte = ttk.Label(self.fenetre_connexion, text = "Identifiant")
        self.identifiant_texte.grid(row = 0, column = 0, padx = 5, pady = 5)
        # La classe Entry du module ttk permet à l'utilisateur d'entrer une chaîne de caractère
        self.identifiant_entree = ttk.Entry(self.fenetre_connexion)
        self.identifiant_entree.grid(row = 0, column = 1, padx = 5, pady = 5)

        self.mdp_texte = ttk.Label(self.fenetre_connexion, text = "Mot de passe")
        self.mdp_texte.grid(row = 1, column = 0, padx = 5, pady = 5)
        self.mdp_entree = ttk.Entry(self.fenetre_connexion, show = "*")
        self.mdp_entree.grid(row = 1, column = 1, padx = 5, pady = 5)

        # La classe Button du module ttk permet de créer une zone clickable qui exécutera une commande
        self.connexion_bouton = ttk.Button(self.fenetre_connexion, text = "Se connecter", command = self.connexion)
        self.connexion_bouton.grid(row = 2, column=0, columnspan=2, pady = 10)

        self.creer_compte_bouton = ttk.Button(self.fenetre_connexion, text = "Créer un compte", command = self.créer_compte)
        self.creer_compte_bouton.grid(row = 3, column = 0, columnspan = 2, pady = 10)


    def connexion(self) :
        """Todolist -> None
        Vérifie les informations de connexion et affiche la fenêtre principale si les informations sont correctes"""
        identifiant = self.identifiant_entree.get()
        mdp = self.mdp_entree.get()
        if se_connecter(identifiant, mdp) :
            cursor.execute("SELECT utilisateur_id FROM utilisateur WHERE identifiant = ?", (identifiant,))
            self.utilisateur_actuel = cursor.fetchone()[0]
            self.montrer_fenetre_principale()
        else :
            # La fonction showerror() permet d'afficher une fenêtre d'erreur personnalisée
            messagebox.showerror("Connection échouée", "L'identifiant ou le mot de passe est incorrect")


    def créer_compte(self) :
        """Todolist -> None
        Crée un compte utilisateur et affiche un message de confirmation"""
        identifiant = self.identifiant_entree.get()
        mdp = self.mdp_entree.get()
        if nouveau_compte(identifiant, mdp) :
            # La fonction showinfo() permet d'afficher une fenêtre d'information personnalisée
            messagebox.showinfo("Compte créé", "Votre compte a été créé avec succès")
        else:
            messagebox.showerror("Création échouée", "L'identifiant est déjà enregistré")


    def montrer_fenetre_principale(self) :
        """Todolist -> None
        Affiche la fenêtre principale de l'application"""
        # La fonction pack_forget() permet de supprimer une fenêtre affichée à l'écran
        self.fenetre_connexion.pack_forget()
        self.fenetre_principale = ttk.Frame(self.principale)
        self.fenetre_principale.pack(padx = 10, pady = 10)

        # La classe Listbox du module ttk permet de créer une liste d'information
        self.taches_listbox = tk.Listbox(self.fenetre_principale, height = 15, width = 50, font = ("Helvetica", 12))
        self.taches_listbox.grid(row = 0, column = 0, columnspan = 3, padx = 5, pady = 5)

        self.rafraichir_taches()

        self.ajouter_tache_bouton = ttk.Button(self.fenetre_principale, text = "Ajouter une tâche", command = self.ajouter_tache)
        self.ajouter_tache_bouton.grid(row = 1, column = 0, pady = 5)

        self.completer_bouton = ttk.Button(self.fenetre_principale, text = "Marquer comme complêtée", command = self.marquer_completee)
        self.completer_bouton.grid(row = 1, column = 1, pady = 5)

        self.deco_bouton = ttk.Button(self.fenetre_principale, text = "Se déconnecter", command = self.deconnecter)
        self.deco_bouton.grid(row = 3, column = 0, pady = 5)

        self.supprimer_bouton = ttk.Button(self.fenetre_principale, text = "Supprimer la tâche", command = self.supprimer_tache)
        self.supprimer_bouton.grid(row = 2, column = 0, pady = 5)

        self.description_bouton = ttk.Button(self.fenetre_principale, text = "Description de la tâche", command = self.description_tache)
        self.description_bouton.grid(row = 2, column = 1, padx = 5, pady = 5) 

        # self.modifier_tache_bouton = ttk.Button(self.fenetre_principale, text = "Modifier la tâche", command = self.modif_tache)
        # self.modifier_tache_bouton.grid(row = 3, column = 0, pady = 5)


    def rafraichir_taches(self) :
        """Todolist -> None
        Met à jour la liste des tâches affichées dans la fenêtre principale"""
        self.taches_listbox.delete(0, tk.END)
        taches = obtenir_taches(self.utilisateur_actuel)
        for tache in taches :
            text_tache = f"{tache[2]} - Échéance: {tache[4]} - Priorité: {tache[6]}"
            if tache[5] :
                text_tache += " - Terminée"
                self.taches_listbox.insert(tk.END, text_tache)
                self.taches_listbox.itemconfig(tk.END, {"fg": "gray"})
            elif tache[6] == "Faible" :
                self.taches_listbox.insert(tk.END, text_tache)
                self.taches_listbox.itemconfig(tk.END, {"fg": "green"})
            elif tache[6] == "Moyenne" :
                self.taches_listbox.insert(tk.END, text_tache)
                self.taches_listbox.itemconfig(tk.END, {"fg": "orange"})
            elif tache[6] == "Haute" :
                self.taches_listbox.insert(tk.END, text_tache)
                self.taches_listbox.itemconfig(tk.END, {"fg": "red"})
            else :
                self.taches_listbox.insert(tk.END, text_tache)


    def ajouter_tache(self) :
        """Todolist -> None
        Affiche une fenêtre pour ajouter une nouvelle tâche"""
        fenetre_tache = tk.Toplevel(principale)
        fenetre_tache.title("Ajouter une tâche")

        nom_tache_texte = ttk.Label(fenetre_tache, text = "Nom de la tâche")
        nom_tache_texte.grid(row = 0, column = 0, padx = 5, pady = 5)
        nom_tache_entree = ttk.Entry(fenetre_tache)
        nom_tache_entree.grid(row = 0, column = 1, padx = 5, pady = 5)

        description_tache_texte = ttk.Label(fenetre_tache, text = "Description de la tâche")
        description_tache_texte.grid(row = 1, column = 0, padx = 5, pady = 5)
        description_tache_entree = ttk.Entry(fenetre_tache)
        description_tache_entree.grid(row = 1, column = 1, padx = 5, pady = 5)

        echeance_texte = ttk.Label(fenetre_tache, text = "Date limite (JJ-MM-AAAA)")
        echeance_texte.grid(row = 2, column = 0, padx = 5, pady = 5)
        echeance_entree = ttk.Entry(fenetre_tache)
        echeance_entree.grid(row = 2, column = 1, padx = 5, pady = 5)

        prio_texte = ttk.Label(fenetre_tache, text = "Priorité")
        prio_texte.grid(row = 3, column = 0, padx = 5, pady = 5)

        # La class Stringvar permet de vérifier l'état d'un widget à une variable
        choix_prio = tk.StringVar()
        # La class Combobox permet de créer un widget de sélection
        prio_combobox = ttk.Combobox(fenetre_tache, textvariable = choix_prio)
        prio_combobox["values"] = ("Faible", "Moyenne", "Haute")
        prio_combobox.bind("Séléction", choix_prio.get())
        prio_combobox.grid(row = 3, column = 1, padx = 5, pady = 5)

        def date_valide(date) :
            """Todolist -> Bool
            Vérifie si la date est valide"""
            try :
                datetime.strptime(date, "%d-%m-%Y")
                return True
            except ValueError :
                messagebox.showwarning("Date invalide", "Veuillez rentrer une date valide")
                return False

        def enregistrer_tache() :
            """Todolist -> None
            Enregistre une nouvelle tâche dans la base de donnée"""
            nom_tache = nom_tache_entree.get()
            description = description_tache_entree.get()
            echeance = echeance_entree.get()
            priorite = choix_prio.get()
            if not date_valide(echeance) :
                return
            ajouter_tache(self.utilisateur_actuel, nom_tache, description, echeance, priorite)
            self.rafraichir_taches()
            # La fonction destroy() permet d'enlever une fenêtre affichée à l'écran
            fenetre_tache.destroy()

        def annuler() :
            """Todolist -> None
            Ferme la fenêtre d'ajout de tâche"""
            fenetre_tache.destroy()

        bouton_enregistrement = ttk.Button(fenetre_tache, text = "Enregistrer la tâche", command = enregistrer_tache)
        bouton_enregistrement.grid(row = 4, column = 1, padx = 5, pady = 5)

        bouton_annuler = ttk.Button(fenetre_tache, text = "Annuler", command = annuler)
        bouton_annuler.grid(row = 4, column = 0, padx = 5, pady = 5)
    
    
    """Les fonctions commentées ne fonctionnent pas."""
    
    
    # def modif_tache(self) :
    #     """Todolist -> None
    #     Modifie la description et la priorité d'une tâche"""
    #     tache_selectionnee = self.taches_listbox.curselection()
    #     if not tache_selectionee :
    #         messagebox.showwarning("Aucune sélection", "Choisissez une tâche à modifier")
    #     taches = obtenir_taches(self.utilisateur_actuel)
    #     tache_id = taches[tache_selectionnee][0]
    #     tache_enregistree = tache_id

    #     fenetre_modif = tk.Toplevel(principale)
    #     fenetre_modif.title("Modifier une tâche")

    #     modif_description_texte = ttk.Label(fenetre_modif, text = "Description de la tâche :")
    #     modif_description_texte.grid(row = 0, column = 0, pady = 5)
    #     modif_description_entree = ttk.Entry(fenetre_modif)
    #     modif_description_entree.grid(row = 1, rowspan = 3, column = 0, columnspan = 4, padx = 5, pady = 5)

    #     modif_prio_texte= ttk.Label(fenetre_modif, text = "Priorité")
    #     modif_prio_texte.grid(row = 4, column = 0, pady = 5)
        
    #     modif_prio = tk.StringVar()
    #     modif_prio_combobox = ttk.Combobox(fenetre_modif, textvariable = modif_prio)
    #     modif_prio_combobox["values"] = ("Faible", "Moyenne", "Haute")
    #     modif_prio_combobox.bind("Séléction", modif_prio.get())
    #     modif_prio_combobox.grid(row = 4, column = 1, padx = 5, pady = 5)

    #     def enregistrer_modif() :
    #         """Todolist -> None
    #         Enregistre les modifications de la tâche"""
    #         description = modif_description_entree.get()
    #         priorite = modif_prio.get()
    #         maj_tache(description, priorite, tache_enregistree)
    #         self.rafraichir_taches()
    #         fenetre_modif.destroy()

    #     def annuler_modif() :
    #         """Todolist -> None
    #         Annule la modification de la tâche"""
    #         fenetre_modif.destroy()

    #     bouton_enregistrement = ttk.Button(fenetre_modif, text = "Enregistrer la tâche", command = enregistrer_modif)
    #     bouton_enregistrement.grid(row = 5, column = 1, pady = 5, padx = 5)

    #     bouton_annuler = ttk.Button(fenetre_modif, text = "Annuler", command = annuler_modif)
    #     bouton_annuler.grid(row = 5, column = 0, pady = 5, padx = 5)


    def description_tache(self) :
        """Todolist -> None
        Voir la description d'une tâche"""
        tache_selectionnee = self.taches_listbox.curselection()
        if not tache_selectionnee :
            messagebox.showwarning("Aucune séléction", "Choisissez une tâche pour voir sa déscription")
            return
        tache_selectionnee = tache_selectionnee[0]
        taches = obtenir_taches(self.utilisateur_actuel)
        description = taches[tache_selectionnee][3]

        fenetre_description = tk.Toplevel(principale)
        fenetre_description.geometry("300x250")
        fenetre_description.title("Description de la tâche")

        description_texte = ttk.Label(fenetre_description, text = description, wraplength = 250)
        description_texte.grid(row = 0, column = 0,padx = 10, pady = 20)

        def retour() :
            """Todolist -> None
            Ferme la fenêtre de description"""
            fenetre_description.destroy()

        bouton_retour = ttk.Button(fenetre_description, text = "Retour", command = retour)
        bouton_retour.grid(row = 2, column = 0, padx = 5, pady = 5)


    def marquer_completee(self) :
        """Todolist -> None
        Marque une tâche comme complétée dans la base de donnée"""
        tache_selectionnee = self.taches_listbox.curselection()
        if not tache_selectionnee :
            messagebox.showwarning("Aucune séléction", "Choisissez une tâche à marquer comme complétée")
            return
        tache_selectionnee = tache_selectionnee[0]
        taches = obtenir_taches(self.utilisateur_actuel)
        tache_id = taches[tache_selectionnee][0]
        marquer_tache_complete(tache_id)
        self.rafraichir_taches()


    def supprimer_tache(self) :
        """Todolist -> None
        Supprime une tâche de la base de donnée"""
        tache_selectionnee = self.taches_listbox.curselection()
        if not tache_selectionnee:
            messagebox.showwarning("Aucune séléction", "Choisissez une tâche à supprimer")
            return
        tache_selectionnee = tache_selectionnee[0]
        taches = obtenir_taches(self.utilisateur_actuel)
        tache_id = taches[tache_selectionnee][0]
        supprimer_tache(tache_id)
        self.rafraichir_taches()


    def deconnecter(self) :
        """Todolist -> None
        Déconnecte l'utilisateur et affiche la fenêtre de connexion"""
        self.fenetre_principale.pack_forget()
        self.fenetre_connexion.pack()
        self.utilisateur_actuel = None


# Lancer l'application
if __name__ == "__main__":
    principale = ttk.Window(themename = "darkly")
    todolist = Todolist(principale)

    # Démarrer le planificateur de tâches dans un thread séparé
    planificateur = Planificateur()
    planificateur_thread = threading.Thread(target = planificateur.run, daemon = True)
    planificateur_thread.start()

    principale.mainloop()
