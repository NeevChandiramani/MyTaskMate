
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import threading
import time

# La fonction "connect()" permet de se connecter à la base de donnée
conn = sqlite3.connect('todolist.db')

# La fonction "cursor()"" permet d'intéragir avec la base de donnée et d'utiliser les différentes requêtes SQL
cursor = conn.cursor()

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS utilisateur (
    utilisateur_id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifiant TEXT UNIQUE NOT NULL,       
    mdp TEXT NOT NULL
)
''')

# "NOT NULL" indique que la valeur ne peut pas être nul
# "AUTOINCREMENT" génère automatiquement une valeur unique pour chaque enregistrement
cursor.execute('''
CREATE TABLE IF NOT EXISTS taches (
    tache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    tache TEXT NOT NULL,
    description TEXTE,
    echeance TEXT NOT NULL,
    est_completee BOOLEAN NOT NULL,
    priorite TEXT CHECK( priorite IN ('Faible', 'Moyenne', 'Haute') ) NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur (utilisateur_id)
)
''')

# La fonction "commit()" permet d'enregistrer les modifications faites sur la base de donnée
conn.commit()

# Fonctions pour la gestion des utilisateurs
def nouveau_compte(nom_identifiant, mot_de_passe):
    """str, str -> bool
    Crée un compte utilisateur dans la base de donnée"""
    try:
        cursor.execute('INSERT INTO utilisateur (identifiant, mdp) VALUES (?, ?)', (nom_identifiant, mot_de_passe))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# La fonction "fetchone()" prend le 1er enregistrement, ici elle vérifie si il y a bien un enregistrement
def se_connecter(nom_identifiant, mot_de_passe):
    """str, str -> bool
    Vérifie si l'utilisateur est enregistré dans la base de donnée"""
    cursor.execute('SELECT * FROM utilisateur WHERE identifiant = ? AND mdp = ?', (nom_identifiant, mot_de_passe))
    return cursor.fetchone() is not None


# Fonctions pour la gestion des tâches
def ajouter_tache(id_utilisateur, nom_tache, date_echeance, prio):
    """int, str, str, str -> None
    Ajoute une tâche à la base de donnée"""
    cursor.execute('INSERT INTO taches (utilisateur_id, tache, echeance, est_completee, priorite) VALUES (?, ?, ?, ?, ?)',
                   (id_utilisateur, nom_tache, date_echeance, False, prio))
    conn.commit()

def maj_tache(description_tache, prio, nom_tache):
    """str, str, str, int -> None
    Met à jour une tâche existante dans la base de donnée"""
    cursor.execute('UPDATE taches SET description = ?, priorite = ? WHERE tache = ?',
                   (description_tache, prio, nom_tache))
    conn.commit()


def supprimer_tache(id_tache):
    """int -> None
    Supprime une tâche de la base de donnée"""
    cursor.execute('DELETE FROM taches WHERE tache_id = ?', (id_tache,))
    conn.commit()


def marquer_tache_complete(id_tache):
    """int -> None
    Marque une tâche comme complétée dans la base de donnée"""
    cursor.execute('UPDATE taches SET est_completee = TRUE WHERE tache_id = ?', (id_tache,))
    conn.commit()


def obtenir_taches(id_utilisateur):
    """int -> list
    Récupère toutes les tâches d'un utilisateur"""
    cursor.execute('SELECT * FROM taches WHERE utilisateur_id = ?', (id_utilisateur,))
    return cursor.fetchall()


# Classe d'ordonnancement pour gérer les états des tâches
class Planificateur:
    def __init__(self):
        self.taches = []


    def ajouter_tache(self, task):
        """list -> None
        Ajoute une tâche à la liste des tâches"""
        self.taches.append(task)


    def run(self):
        """Planificateur -> None
        Vérifie si une tâche est expirée toutes les minutes"""
        while True:
            for tache in self.taches:
                echeance = datetime.strptime(tache[4], '%Y-%m-%d')
                if datetime.now() > echeance and not tache[4]:
                    messagebox.showerror("La tâche a expiré")
            # Vérifie toutes les minutes avec le time.sleep
            time.sleep(60)



# Interface graphique avec tkinter
class Todolist:
    def __init__(self, principale):
        self.principale = principale
        self.principale.title("La todo list de M. Picard")
        self.utilisateur_actuel = None

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12))


        self.fenetre_connexion = ttk.Frame(principale)
        self.fenetre_connexion.pack(padx=10, pady=10)

        self.identifiant_label = ttk.Label(self.fenetre_connexion, text="Identifiant")
        self.identifiant_label.grid(row=0, column=0, padx=5, pady=5)
        self.identifiant_entry = ttk.Entry(self.fenetre_connexion)
        self.identifiant_entry.grid(row=0, column=1, padx=5, pady=5)

        self.mdp_label = ttk.Label(self.fenetre_connexion, text="Mot de passe")
        self.mdp_label.grid(row=1, column=0, padx=5, pady=5)
        self.mdp_entry = ttk.Entry(self.fenetre_connexion, show="*")
        self.mdp_entry.grid(row=1, column=1, padx=5, pady=5)

        self.connexion_button = ttk.Button(self.fenetre_connexion, text="Se connecter", command=self.connexion)
        self.connexion_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.creer_compte_button = ttk.Button(self.fenetre_connexion, text="Créer un compte", command=self.créer_compte)
        self.creer_compte_button.grid(row=3, column=0, columnspan=2, pady=10)


    def connexion(self):
        """Todolist -> None
        Vérifie les informations de connexion et affiche la fenêtre principale si les informations sont correctes"""
        identifiant = self.identifiant_entry.get()
        mdp = self.mdp_entry.get()
        if se_connecter(identifiant, mdp):
            cursor.execute('SELECT utilisateur_id FROM utilisateur WHERE identifiant = ?', (identifiant,))
            self.utilisateur_actuel = cursor.fetchone()[0]
            self.montrer_fenetre_principale()
        else:
            messagebox.showerror("Connection échouée", "L'identifiant ou le mot de passe est incorrect")


    def créer_compte(self):
        """Todolist -> None
        Crée un compte utilisateur et affiche un message de confirmation"""
        identifiant = self.identifiant_entry.get()
        mdp = self.mdp_entry.get()
        if nouveau_compte(identifiant, mdp):
            messagebox.showinfo("Compte créé", "Votre compte a été créé avec succès")
        else:
            messagebox.showerror("Création échouée", "L'identifiant est déjà enregistré")


    def montrer_fenetre_principale(self):
        """Todolist -> None
        Affiche la fenêtre principale de l'application"""
        self.fenetre_connexion.pack_forget()
        self.fenetre_princiaple = ttk.Frame(self.principale)
        self.fenetre_princiaple.pack(padx=10, pady=10)

        self.taches_listbox = tk.Listbox(self.fenetre_princiaple, height=15, width=50, font=("Helvetica", 12))
        self.taches_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        self.rafraichir_taches()

        self.ajouter_tache_button = ttk.Button(self.fenetre_princiaple, text = "Ajouter une tâche", command = self.ajouter_tache)
        self.ajouter_tache_button.grid(row=1, column=0, pady=5)

        self.completer_button = ttk.Button(self.fenetre_princiaple, text = "Marquer comme complêtée", command = self.marquer_completee)
        self.completer_button.grid(row = 1, column = 1, pady = 5)

        self.deco_button = ttk.Button(self.fenetre_princiaple, text = "Se déconnecter", command = self.deconnecter)
        self.deco_button.grid(row = 2, column = 1, pady = 5)

        self.supprimer_button = ttk.Button(self.fenetre_princiaple, text = "Supprimer la tâche", command = self.supprimer_tache)
        self.supprimer_button.grid(row = 2, column = 0, pady = 5)

        # self.modifier_tache_button = ttk.Button(self.fenetre_princiaple, text = "Modifier la tâche", command = self.modif_tache)
        # self.modifier_tache_button.grid(row = 3, column = 0, pady = 5)


    def rafraichir_taches(self):
        """Todolist -> None
        Met à jour la liste des tâches affichées dans la fenêtre principale"""
        self.taches_listbox.delete(0, tk.END)
        taches = obtenir_taches(self.utilisateur_actuel)
        for tache in taches:
            text_tache = f"{tache[2]} - Échéance: {tache[4]} - Priorité: {tache[6]}"   ## ex échéance 01-01-2001 ou alors 1er janvier 2001
            if tache[5]:
                text_tache += " - Terminée"
                self.taches_listbox.insert(tk.END, text_tache)
                self.taches_listbox.itemconfig(tk.END, {'fg': 'gray'})
            elif tache[6] == 'Faible' :
                self.taches_listbox.insert(tk.END, text_tache)
                self.taches_listbox.itemconfig(tk.END, {'fg': 'green'})
            elif tache[6] == 'Moyenne' :
                self.taches_listbox.insert(tk.END, text_tache)
                self.taches_listbox.itemconfig(tk.END, {'fg': 'orange'})
            elif tache[6] == 'Haute':
                self.taches_listbox.insert(tk.END, text_tache)
                self.taches_listbox.itemconfig(tk.END, {'fg': 'red'})
            else:
                self.taches_listbox.insert(tk.END, text_tache)


    def ajouter_tache(self) :
        """Todolist -> None
        Affiche une fenêtre pour ajouter une nouvelle tâche"""
        fenetre_tache = tk.Toplevel(principale)
        fenetre_tache.title("Ajouter une tâche")

        nom_tache_label = ttk.Label(fenetre_tache, text="Nom de la tâche")
        nom_tache_label.grid(row=0, column=0, padx=5, pady=5)
        nom_tache_entry = ttk.Entry(fenetre_tache)
        nom_tache_entry.grid(row=0, column=1, padx=5, pady=5)

        echeance_label = ttk.Label(fenetre_tache, text="Date limite (JJ-MM-AAAA)")
        echeance_label.grid(row=1, column=0, padx=5, pady=5)
        echeance_entry = ttk.Entry(fenetre_tache)
        echeance_entry.grid(row=1, column=1, padx=5, pady=5)

        prio_label = ttk.Label(fenetre_tache, text="Priorité")
        prio_label.grid(row=2, column=0, padx=5, pady=5)

        choix_prio = tk.StringVar()
        prio_combobox = ttk.Combobox(fenetre_tache, textvariable = choix_prio)
        prio_combobox['values'] = ("Faible", "Moyenne", "Haute")
        prio_combobox.bind('Séléction', choix_prio.get())
        prio_combobox.grid(row = 2, column = 1, padx = 5, pady = 5)


        def enregistrer_tache() :
            """Todolist -> None
            Enregistre une nouvelle tâche dans la base de donnée"""
            nom_tache = nom_tache_entry.get()
            echeance = echeance_entry.get()
            priorite = choix_prio.get()
            ajouter_tache(self.utilisateur_actuel, nom_tache, echeance, priorite)
            self.rafraichir_taches()
            fenetre_tache.destroy()


        def annuler() :
            """Todolist -> None
            Ferme la fenêtre d'ajout de tâche"""
            fenetre_tache.destroy()

        boutton_enregistrement = ttk.Button(fenetre_tache, text = "Enregistrer la tâche", command = enregistrer_tache)
        boutton_enregistrement.grid(row = 3, column = 1, pady = 5)

        boutton_annuler = ttk.Button(fenetre_tache, text = "Annuler", command = annuler)
        boutton_annuler.grid(row = 3, column = 0, pady = 5)
    
    
    
    
    
    
    # def modif_tache(self) :

    #     tache_selectionnee = self.taches_listbox.curselection()

    #     if tache_selectionnee:
    #         tache_id = tache_selectionnee[0]
    #         tache_enregistree = tache_id
    #     else:
    #         messagebox.showwarning("Aucune sélection", "Choisissez une tâche à modifier")

    #     fenetre_modif = tk.Toplevel(principale)
    #     fenetre_modif.title("Modifier une tâche")

    #     description_label = ttk.Label(fenetre_modif, text = "Description de la tâche :")
    #     description_label.grid(row = 0, column = 0, pady = 5)
    #     description_entree = ttk.Entry(fenetre_modif)
    #     description_entree.grid(row = 1, rowspan = 3, column = 0, columnspan = 4, padx = 5, pady = 5)

    #     modif_prio_label= ttk.Label(fenetre_modif, text = "Priorité (menu déroulant)")
    #     modif_prio_label.grid(row = 4, column = 0, pady = 5)
        
    #     modif_prio = tk.StringVar()
    #     modif_prio_combobox = ttk.Combobox(fenetre_modif, textvariable = modif_prio)
    #     modif_prio_combobox['values'] = ("Faible", "Moyenne", "Haute")
    #     modif_prio_combobox.bind('Séléction', modif_prio.get())
    #     modif_prio_combobox.grid(row = 4, column = 1, padx = 5, pady = 5)


    #     def enregistrer_modif() :
    #         description = description_entree.get()
    #         priorite = modif_prio.get()
    #         maj_tache(description, priorite, tache_enregistree)
    #         self.rafraichir_taches()
    #         fenetre_modif.destroy()


    #     def annuler_modif() :
    #         fenetre_modif.destroy()

    #     boutton_enregistrement = ttk.Button(fenetre_modif, text = "Enregistrer la tâche", command = enregistrer_modif)
    #     boutton_enregistrement.grid(row = 5, column = 1, pady = 5, padx = 5)

    #     boutton_annuler = ttk.Button(fenetre_modif, text = "Annuler", command = annuler_modif)
    #     boutton_annuler.grid(row = 5, column = 0, pady = 5, padx = 5)


    def marquer_completee(self):
        """Todolist -> None
        Marque une tâche comme complétée dans la base de donnée"""
        tache_selectionnee = self.taches_listbox.curselection()
        if not tache_selectionnee:
            messagebox.showwarning("Aucune séléction", "Choisissez une tâche à marquer comme complétée")
            return
        tache_selectionnee = tache_selectionnee[0]
        taches = obtenir_taches(self.utilisateur_actuel)
        tache_id = taches[tache_selectionnee][0]
        marquer_tache_complete(tache_id)
        self.rafraichir_taches()


    def supprimer_tache(self):
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


    def deconnecter(self):
        """Todolist -> None
        Déconnecte l'utilisateur et affiche la fenêtre de connexion"""
        self.fenetre_princiaple.pack_forget()
        self.fenetre_connexion.pack()
        self.utilisateur_actuel = None

# Lancer l'application
if __name__ == "__main__":
    principale = ttk.Window(themename="darkly")
    todolist = Todolist(principale)

    # Démarrer le planificateur de tâches dans un thread séparé
    scheduler = Planificateur()
    scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
    scheduler_thread.start()

    principale.mainloop()
