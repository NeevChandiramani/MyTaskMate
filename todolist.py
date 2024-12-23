import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview
import hashlib
from datetime import datetime

# Database setup
def init_db():
    with sqlite3.connect("todo_app.db") as conn:
        cursor = conn.cursor()
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_description TEXT NOT NULL,
                due_date TEXT,
                is_completed BOOLEAN DEFAULT 0,
                priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

# User management
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        with sqlite3.connect("todo_app.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                           (username, hash_password(password)))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    with sqlite3.connect("todo_app.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ? AND password_hash = ?",
                       (username, hash_password(password)))
        result = cursor.fetchone()
        return result[0] if result else None

# Task management
def add_task(user_id, description, due_date, priority):
    with sqlite3.connect("todo_app.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (user_id, task_description, due_date, priority) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, description, due_date, priority))
        conn.commit()

def get_tasks(user_id, filter_by=None, order_by=None):
    with sqlite3.connect("todo_app.db") as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM tasks WHERE user_id = ?"
        if filter_by:
            query += f" AND {filter_by}"
        if order_by:
            query += f" ORDER BY {order_by}"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()

def update_task(task_id, **kwargs):
    with sqlite3.connect("todo_app.db") as conn:
        cursor = conn.cursor()
        for key, value in kwargs.items():
            cursor.execute(f"UPDATE tasks SET {key} = ? WHERE task_id = ?", (value, task_id))
        conn.commit()

def delete_task(task_id):
    with sqlite3.connect("todo_app.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        conn.commit()

# GUI setup
class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")
        self.user_id = None
        self.setup_login_page()

    def setup_login_page(self):
        self.clear_frame()

        Label(self.root, text="Username:").pack()
        self.username_entry = Entry(self.root)
        self.username_entry.pack()

        Label(self.root, text="Password:").pack()
        self.password_entry = Entry(self.root, show="*")
        self.password_entry.pack()

        Button(self.root, text="Login", command=self.login).pack()
        Button(self.root, text="Register", command=self.register).pack()

    def setup_main_page(self):
        self.clear_frame()

        Button(self.root, text="Add Task", command=self.add_task_popup).pack()
        self.tree = Treeview(self.root, columns=("Description", "Due Date", "Priority", "Completed"), show="headings")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Completed", text="Completed")
        self.tree.pack(fill=BOTH, expand=True)

        self.load_tasks()

    def load_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        tasks = get_tasks(self.user_id)
        for task in tasks:
            self.tree.insert("", "end", values=(task[2], task[3], task[5], "Yes" if task[4] else "No"))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.user_id = login_user(username, password)
        if self.user_id:
            self.setup_main_page()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if register_user(username, password):
            messagebox.showinfo("Success", "Account created successfully")
        else:
            messagebox.showerror("Error", "Username already exists")

    def add_task_popup(self):
        popup = Toplevel(self.root)
        popup.title("Add Task")

        Label(popup, text="Description:").pack()
        description_entry = Entry(popup)
        description_entry.pack()

        Label(popup, text="Due Date (YYYY-MM-DD):").pack()
        due_date_entry = Entry(popup)
        due_date_entry.pack()

        Label(popup, text="Priority:").pack()
        priority_var = StringVar(value="medium")
        for priority in ["low", "medium", "high"]:
            Radiobutton(popup, text=priority.capitalize(), variable=priority_var, value=priority).pack()

        def save_task():
            description = description_entry.get()
            due_date = due_date_entry.get()
            priority = priority_var.get()
            try:
                datetime.strptime(due_date, "%Y-%m-%d")  # Validate date format
                add_task(self.user_id, description, due_date, priority)
                popup.destroy()
                self.load_tasks()
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")

        Button(popup, text="Save", command=save_task).pack()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Initialize application
if __name__ == "__main__":
    init_db()
    root = Tk()
    app = ToDoApp(root)
    root.mainloop()
