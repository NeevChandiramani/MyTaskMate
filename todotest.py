import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import time

# Connexion à la base de données SQLite
conn = sqlite3.connect('todo_list.db')
cursor = conn.cursor()

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_description TEXT NOT NULL,
    due_date TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL,
    priority TEXT CHECK( priority IN ('low', 'medium', 'high') ) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
''')
conn.commit()

# Fonctions pour la gestion des utilisateurs
def create_user(username, password_hash):
    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password_hash):
    cursor.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password_hash))
    return cursor.fetchone() is not None

# Fonctions pour la gestion des tâches
def add_task(user_id, description, due_date, priority):
    cursor.execute('INSERT INTO tasks (user_id, task_description, due_date, is_completed, priority) VALUES (?, ?, ?, ?, ?)',
                   (user_id, description, due_date, False, priority))
    conn.commit()

def update_task(task_id, description, due_date, priority):
    cursor.execute('UPDATE tasks SET task_description = ?, due_date = ?, priority = ? WHERE task_id = ?',
                   (description, due_date, priority, task_id))
    conn.commit()

def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
    conn.commit()

def mark_task_completed(task_id):
    cursor.execute('UPDATE tasks SET is_completed = TRUE WHERE task_id = ?', (task_id,))
    conn.commit()

def get_tasks(user_id):
    cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

# Classe d'ordonnancement pour gérer les états des tâches
class TaskScheduler:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def run(self):
        while True:
            now = datetime.now()
            for task in self.tasks:
                due_date = datetime.strptime(task[3], '%Y-%m-%d')
                if now > due_date and not task[4]:
                    print(f"Task {task[2]} is overdue!")
            time.sleep(60)  # Vérifie toutes les minutes

# Interface graphique avec tkinter
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")
        self.current_user = None

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12))

        self.login_frame = ttk.Frame(root)
        self.login_frame.pack(padx=10, pady=10)

        self.username_label = ttk.Label(self.login_frame, text="Username")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = ttk.Label(self.login_frame, text="Password")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.create_account_button = ttk.Button(self.login_frame, text="Create Account", command=self.create_account)
        self.create_account_button.grid(row=3, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if login_user(username, password):
            cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
            self.current_user = cursor.fetchone()[0]
            self.show_main_frame()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def create_account(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if create_user(username, password):
            messagebox.showinfo("Account Created", "Your account has been created successfully")
        else:
            messagebox.showerror("Account Creation Failed", "Username already exists")

    def show_main_frame(self):
        self.login_frame.pack_forget()
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)

        self.task_listbox = tk.Listbox(self.main_frame, height=15, width=50, font=("Helvetica", 12))
        self.task_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        self.refresh_tasks()

        self.add_task_button = ttk.Button(self.main_frame, text="Add Task", command=self.add_task)
        self.add_task_button.grid(row=1, column=0, pady=5)

        self.mark_completed_button = ttk.Button(self.main_frame, text="Mark as Completed", command=self.mark_completed)
        self.mark_completed_button.grid(row=1, column=1, pady=5)

        self.logout_button = ttk.Button(self.main_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=1, column=2, pady=5)

    def refresh_tasks(self):
        self.task_listbox.delete(0, tk.END)
        tasks = get_tasks(self.current_user)
        for task in tasks:
            task_text = f"{task[2]} - Due: {task[3]} - Priority: {task[5]}"
            if task[4]:
                task_text += " - Completed"
                self.task_listbox.insert(tk.END, task_text)
                self.task_listbox.itemconfig(tk.END, {'fg': 'gray'})
            elif task[5] == 'high':
                self.task_listbox.insert(tk.END, task_text)
                self.task_listbox.itemconfig(tk.END, {'fg': 'red'})
            else:
                self.task_listbox.insert(tk.END, task_text)

    def add_task(self):
        task_window = tk.Toplevel(self.root)
        task_window.title("Add Task")

        description_label = ttk.Label(task_window, text="Task Description")
        description_label.grid(row=0, column=0, padx=5, pady=5)
        description_entry = ttk.Entry(task_window)
        description_entry.grid(row=0, column=1, padx=5, pady=5)

        due_date_label = ttk.Label(task_window, text="Due Date (YYYY-MM-DD)")
        due_date_label.grid(row=1, column=0, padx=5, pady=5)
        due_date_entry = ttk.Entry(task_window)
        due_date_entry.grid(row=1, column=1, padx=5, pady=5)

        priority_label = ttk.Label(task_window, text="Priority (low, medium, high)")
        priority_label.grid(row=2, column=0, padx=5, pady=5)
        priority_entry = ttk.Entry(task_window)
        priority_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_task():
            description = description_entry.get()
            due_date = due_date_entry.get()
            priority = priority_entry.get()
            add_task(self.current_user, description, due_date, priority)
            self.refresh_tasks()
            task_window.destroy()

        save_button = ttk.Button(task_window, text="Save Task", command=save_task)
        save_button.grid(row=3, column=0, columnspan=2, pady=10)

    def mark_completed(self):
        selected_task_index = self.task_listbox.curselection()
        if not selected_task_index:
            messagebox.showwarning("No Selection", "Please select a task to mark as completed")
            return

        selected_task_index = selected_task_index[0]
        tasks = get_tasks(self.current_user)
        task_id = tasks[selected_task_index][0]
        mark_task_completed(task_id)
        self.refresh_tasks()

    def logout(self):
        self.main_frame.pack_forget()
        self.login_frame.pack()
        self.current_user = None

# Lancer l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)

    # Démarrer le planificateur de tâches dans un thread séparé
    scheduler = TaskScheduler()
    scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
    scheduler_thread.start()

    root.mainloop()
