
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
    echeance TEXT NOT NULL,
    est_completee BOOLEAN NOT NULL,
    priorité TEXT CHECK( priorité IN ('Faible', 'Moyenne', 'Haute') ) NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur (utilisateur_id)
)
''')

# La fonction "commit()" permet d'enregistrer les modifications faites sur la base de donnée
conn.commit()

# Fonctions pour la gestion des utilisateurs
def créer_compte(nom_identifiant, mot_de_passe):
    """str, str -> bool
    Crée un compte utilisateur dans la base de donnée
    """
    try:
        cursor.execute('INSERT INTO utilisateur (identifiant, mdp) VALUES (?, ?)', (nom_identifiant, mot_de_passe))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# La fonction "fetchone()" prend le 1er enregistrement, ici elle vérifie si il y a bien un enregistrement
def se_connecter(nom_identifiant, mot_de_passe):
    """str, str -> bool
    Vérifie si l'utilisateur est enregistré dans la base de donnée
    """
    cursor.execute('SELECT * FROM utilisateur WHERE identifiant = ? AND mdp = ?', (nom_identifiant, mot_de_passe))
    return cursor.fetchone() is not None


# Fonctions pour la gestion des tâches
def ajouter_tache(id_utilisateur, nom_tache, date_echeance, prio):
    """int, str, str, str -> None
    Ajoute une tâche à la base de donnée
    """
    cursor.execute('INSERT INTO taches (utilisateur_id, tache, echeance, est_completee, priorité) VALUES (?, ?, ?, ?, ?)',
                   (id_utilisateur, nom_tache, date_echeance, False, prio))
    conn.commit()


def maj_tache(nom_tache, date_echeance, prio, id_tache):
    cursor.execute('UPDATE taches SET tache = ?, echeance = ?, priorité = ? WHERE tache_id = ?',
                   (nom_tache, date_echeance, prio, id_tache))
    conn.commit()


def supprimer_tache(id_tache):
    cursor.execute('DELETE FROM taches WHERE tache_id = ?', (id_tache,))
    conn.commit()


def marquer_tache_complete(id_tache):
    cursor.execute('UPDATE taches SET est_completee = TRUE WHERE tache_id = ?', (id_tache,))
    conn.commit()


def get_tasks(id_utilisateur):
    cursor.execute('SELECT * FROM taches WHERE utilisateur_id = ?', (id_utilisateur,))
    return cursor.fetchall()


# Classe d'ordonnancement pour gérer les états des tâches
class Planificateur:
    def __init__(self):
        self.tasks = []


    def ajouter_tache(self, task):
        self.tasks.append(task)


    def run(self):
        while True:
            for task in self.tasks:
                due_date = datetime.strptime(task[3], '%Y-%m-%d')
                if datetime.now() > due_date and not task[4]:
                    print(f"La tâche {task[2]} est expirée!")
            # Vérifie toutes les minutes avec le time.sleep
            time.sleep(60)



# Interface graphique avec tkinter
class Todolist:
    def __init__(self, principale):
        self.principale = principale
        self.principale.title("To do list tg3 code créa michoucroute dans la boutique les gars")
        self.current_user = None

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12))


        self.login_frame = ttk.Frame(principale)
        self.login_frame.pack(padx=10, pady=10)

        self.identifiant_label = ttk.Label(self.login_frame, text="Identifiant")
        self.identifiant_label.grid(row=0, column=0, padx=5, pady=5)
        self.identifiant_entry = ttk.Entry(self.login_frame)
        self.identifiant_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = ttk.Label(self.login_frame, text="Mot de passe")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ttk.Button(self.login_frame, text="Se connecter", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.créer_compte_button = ttk.Button(self.login_frame, text="Créer un compte", command=self.créer_compte)
        self.créer_compte_button.grid(row=3, column=0, columnspan=2, pady=10)


    def login(self):
        identifiant = self.identifiant_entry.get()
        password = self.password_entry.get()
        if se_connecter(identifiant, password):
            cursor.execute('SELECT utilisateur_id FROM utilisateur WHERE identifiant = ?', (identifiant,))
            self.current_user = cursor.fetchone()[0]
            self.show_main_frame()
        else:
            messagebox.showerror("Connection échouée", "L'identifiant ou le mot de passe est incorrect")


    def créer_compte(self):
        identifiant = self.identifiant_entry.get()
        password = self.password_entry.get()
        if créer_compte(identifiant, password):
            messagebox.showinfo("Compte créé", "Votre compte a été créé avec succès")
        else:
            messagebox.showerror("Création échouée", "L'identifiant est déjà enregistré")


    def show_main_frame(self):
        self.login_frame.pack_forget()
        self.main_frame = ttk.Frame(self.principale)
        self.main_frame.pack(padx=10, pady=10)

        self.task_listbox = tk.Listbox(self.main_frame, height=15, width=50, font=("Helvetica", 12))
        self.task_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        self.refresh_tasks()

        self.ajouter_tache_button = ttk.Button(self.main_frame, text="Ajouter une tâche", command = self.ajouter_tache)
        self.ajouter_tache_button.grid(row=1, column=0, pady=5)

        self.complete_button = ttk.Button(self.main_frame, text = "Marquer comme complêtée", command = self.mark_completed)
        self.complete_button.grid(row = 1, column = 1, pady = 5)

        self.deco_button = ttk.Button(self.main_frame, text = "Se déconnecter", command = self.deconnecter)
        self.deco_button.grid(row = 2, column = 1, pady = 5)

        self.supprimer_button = ttk.Button(self.main_frame, text ="Supprimer la tâche", command = self.supprimer_tache)
        self.supprimer_button.grid(row = 2, column = 0, pady = 5)


    def refresh_tasks(self):
        self.task_listbox.delete(0, tk.END)
        tasks = get_tasks(self.current_user)
        for task in tasks:
            task_text = f"{task[2]} - Échéance: {task[3]} - Priorité: {task[5]}"
            if task[4]:
                task_text += " - Completed"
                self.task_listbox.insert(tk.END, task_text)
                self.task_listbox.itemconfig(tk.END, {'fg': 'gray'})
            elif task[5] == 'Faible' :
                self.task_listbox.insert(tk.END, task_text)
                self.task_listbox.itemconfig(tk.END, {'fg': 'green'})
            elif task[5] == 'Moyenne' :
                self.task_listbox.insert(tk.END, task_text)
                self.task_listbox.itemconfig(tk.END, {'fg': 'orange'})
            elif task[5] == 'Haute':
                self.task_listbox.insert(tk.END, task_text)
                self.task_listbox.itemconfig(tk.END, {'fg': 'red'})
            else:
                self.task_listbox.insert(tk.END, task_text)


    def ajouter_tache(self):
        fenetre_tache = tk.Toplevel(principale)
        fenetre_tache.title("Ajouter une tâche")

        description_label = ttk.Label(fenetre_tache, text="Nom de la tâche")
        description_label.grid(row=0, column=0, padx=5, pady=5)
        description_entry = ttk.Entry(fenetre_tache)
        description_entry.grid(row=0, column=1, padx=5, pady=5)

        due_date_label = ttk.Label(fenetre_tache, text="Date limite (JJ-MM-AAAA)")
        due_date_label.grid(row=1, column=0, padx=5, pady=5)
        due_date_entry = ttk.Entry(fenetre_tache)
        due_date_entry.grid(row=1, column=1, padx=5, pady=5)


        prio_label = ttk.Label(fenetre_tache, text="Priorité")
        prio_label.grid(row=2, column=0, padx=5, pady=5)

        choix_prio = tk.StringVar()
        combobox = ttk.Combobox(fenetre_tache, textvariable = choix_prio)
        combobox['values'] = ("Faible", "Moyenne", "Haute")
        combobox.bind('Séléction', choix_prio.get())
        combobox.grid(row = 2, column = 1, padx = 5, pady = 5)


        def enregistrer_tache():
            description = description_entry.get()
            due_date = due_date_entry.get()
            priorité = None
            if choix_prio.get() == 'Faible' :
                priorité = 'Faible'
            elif choix_prio.get() == 'Moyenne' :
                priorité = 'Moyenne'
            elif choix_prio.get() == 'Haute' :
                priorité = 'Haute'
            if priorité is not None :      
                ajouter_tache(self.current_user, description, due_date, priorité)
                self.refresh_tasks()
                fenetre_tache.destroy()


        def annuler() :
            fenetre_tache.destroy()

        boutton_enregistrement = ttk.Button(fenetre_tache, text = "Enregistrer la tâche", command = enregistrer_tache)
        boutton_enregistrement.grid(row = 3, column = 1, pady = 5)

        boutton_annuler = ttk.Button(fenetre_tache, text = "Annuler", command = annuler)
        boutton_annuler.grid(row = 3, column = 0, pady = 5)


    def mark_completed(self):
        tache_selectionnee = self.task_listbox.curselection()
        if not tache_selectionnee:
            messagebox.showwarning("Aucune séléction", "Choisissez une tâche à marquer comme complétée")
            return
        tache_selectionnee = tache_selectionnee[0]
        tasks = get_tasks(self.current_user)
        task_id = tasks[tache_selectionnee][0]
        marquer_tache_complete(task_id)
        self.refresh_tasks()


    def supprimer_tache(self):
        tache_selectionnee = self.task_listbox.curselection()
        tache_selectionnee = tache_selectionnee[0]
        tasks = get_tasks(self.current_user)
        task_id = tasks[tache_selectionnee][0]
        supprimer_tache(task_id)
        self.refresh_tasks()


    def deconnecter(self):
        self.main_frame.pack_forget()
        self.login_frame.pack()
        self.current_user = None

# Lancer l'application
if __name__ == "__main__":
    principale = ttk.Window(themename="darkly")
    todolist = Todolist(principale)

    # Démarrer le planificateur de tâches dans un thread séparé
    scheduler = Planificateur()
    scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
    scheduler_thread.start()

    principale.mainloop()
