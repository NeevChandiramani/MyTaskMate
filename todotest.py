import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Listbox, END
from datetime import datetime
import threading
import time
from PIL import Image, ImageTk

# La fonction "connect()" permet de se connecter à la base de donnée
conn = sqlite3.connect('todo_list.db')

# La fonction "cursor()"" permet d'intéragir avec la base de donnée et d'utiliser les différentes requêtes SQL
cursor = conn.cursor()

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS utilisateur (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifiant TEXT UNIQUE NOT NULL,
    mdp TEXT NOT NULL
)
''')

# "NOT NULL" indique que la valeur ne peut pas être nul
# "AUTOINCREMENT" génère automatiquement une valeur unique pour chaque enregistrement
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_description TEXT NOT NULL,
    due_date TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL,
    priority TEXT CHECK( priority IN ('low', 'medium', 'high') ) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES utilisateur (user_id)
)
''')

# La fonction "commit()" permet d'enregistrer les modifications faites sur la base de donnée
conn.commit()

# Fonctions pour la gestion des utilisateurs
def créer_compte(identifiant, mdp):
    try:
        cursor.execute('INSERT INTO utilisateur (identifiant, mdp) VALUES (?, ?)', (identifiant, mdp))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# La fonction "fetchone()" prend le 1er enregistrement, ici elle vérifie si il y a bien un enregistrement
def se_connecter(identifiant, mdp):
    cursor.execute('SELECT * FROM utilisateur WHERE identifiant = ? AND mdp = ?', (identifiant, mdp))
    return cursor.fetchone() is not None

# Fonctions pour la gestion des tâches
def ajouter_tache(user_id, description, due_date, priority):
    cursor.execute('INSERT INTO tasks (user_id, task_description, due_date, is_completed, priority) VALUES (?, ?, ?, ?, ?)',
                   (user_id, description, due_date, False, priority))
    conn.commit()

def get_tasks(user_id):
    cursor.execute('SELECT * FROM tasks WHERE user_id = ? AND is_completed = ?', (user_id, False))
    return cursor.fetchall()

def marquer_tache_complete(task_id):
    cursor.execute('UPDATE tasks SET is_completed = ? WHERE task_id = ?', (True, task_id))
    conn.commit()

def supprimer_tache(task_id):
    cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
    conn.commit()

class Planificateur:
    def run(self):
        while True:
            time.sleep(1)
            # Logique de planification ici

class Todolist:
    def __init__(self, root):
        self.root = root
        self.current_user = None

        # Configuration du style
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12))
        style.configure('TLabel', font=('Helvetica', 12))

        # Création du cadre de connexion
        self.login_frame = ttk.Frame(root)
        self.login_frame.pack(padx=10, pady=10)

        ttk.Label(self.login_frame, text="Identifiant:").grid(row=0, column=0, padx=5, pady=5)
        self.identifiant_entry = ttk.Entry(self.login_frame)
        self.identifiant_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Mot de passe:").grid(row=1, column=0, padx=5, pady=5)
        self.mdp_entry = ttk.Entry(self.login_frame, show="*")
        self.mdp_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.login_frame, text="Se connecter", command=self.login).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(self.login_frame, text="Créer un compte", command=self.create_account).grid(row=3, column=0, columnspan=2, pady=5)

        # Création du cadre principal
        self.main_frame = ttk.Frame(root)
        self.task_listbox = Listbox(self.main_frame, width=50)
        self.task_listbox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        ttk.Button(self.main_frame, text="Ajouter une tâche", command=self.add_task).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Marquer comme complétée", command=self.mark_completed).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Supprimer la tâche", command=self.supprimer_tache).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Se déconnecter", command=self.logout).grid(row=2, column=1, padx=5, pady=5)

    def login(self):
        identifiant = self.identifiant_entry.get()
        mdp = self.mdp_entry.get()
        if se_connecter(identifiant, mdp):
            self.current_user = identifiant
            self.login_frame.pack_forget()
            self.main_frame.pack()
            self.refresh_tasks()
        else:
            messagebox.showerror("Erreur de connexion", "Identifiant ou mot de passe incorrect")

    def create_account(self):
        identifiant = self.identifiant_entry.get()
        mdp = self.mdp_entry.get()
        if créer_compte(identifiant, mdp):
            messagebox.showinfo("Succès", "Compte créé avec succès")
        else:
            messagebox.showerror("Erreur", "Impossible de créer le compte")

    def refresh_tasks(self):
        if hasattr(self, 'task_listbox'):
            self.task_listbox.delete(0, END)
            tasks = get_tasks(self.current_user)
            for task in tasks:
                self.task_listbox.insert(END, f"{task[2]} - Date d'échéance (JJ-MM-AAAA): {task[3]} - Priorité: {task[5]}")

    def add_task(self):
        fenetre_tache = ttk.Toplevel(self.root)
        fenetre_tache.title("Ajouter une tâche")

        ttk.Label(fenetre_tache, text="Description:").grid(row=0, column=0, padx=5, pady=5)
        description_entry = ttk.Entry(fenetre_tache, width=40)
        description_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(fenetre_tache, text="Date d'échéance:").grid(row=1, column=0, padx=5, pady=5)
        due_date_entry = ttk.Entry(fenetre_tache, width=40)
        due_date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(fenetre_tache, text="Priorité (low, medium, high):").grid(row=2, column=0, padx=5, pady=5)
        priority_entry = ttk.Entry(fenetre_tache, width=40)
        priority_entry.grid(row=2, column=1, padx=5, pady=5)

        def enregistrer_tache():
            description = description_entry.get()
            due_date = due_date_entry.get()
            priority = priority_entry.get()
            ajouter_tache(self.current_user, description, due_date, priority)
            self.refresh_tasks()
            fenetre_tache.destroy()

        def annuler():
            fenetre_tache.destroy()

        boutton_enregistrement = ttk.Button(fenetre_tache, text="Enregistrer la tâche", command=enregistrer_tache)
        boutton_enregistrement.grid(row=3, column=1, pady=5)

        boutton_annuler = ttk.Button(fenetre_tache, text="Annuler", command=annuler)
        boutton_annuler.grid(row=3, column=0, pady=5)

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

    def logout(self):
        self.main_frame.pack_forget()
        self.login_frame.pack()
        self.current_user = None

# Lancer l'application
if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    todolist = Todolist(app)

    # Démarrer le planificateur de tâches dans un thread séparé
    scheduler = Planificateur()
    scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
    scheduler_thread.start()

    app.mainloop()

