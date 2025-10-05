import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
import sys
import os

class LibraryLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Login")
        self.root.geometry("450x300")
        self.root.resizable(False, False)
        
        self.center_window()
        self.db_name = "library.db"
        self.setup_database_and_admin()

        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.create_login_widgets()

    def setup_database_and_admin(self):
        # This function is unchanged
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id TEXT PRIMARY KEY, name TEXT NOT NULL, password TEXT NOT NULL,
                contact_no TEXT, contact_address TEXT, aadhaar_card_no TEXT,
                status TEXT NOT NULL, role TEXT NOT NULL )''')
        cursor.execute("SELECT * FROM Users WHERE user_id = 'admin'")
        if cursor.fetchone() is None:
            admin_password = 'admin'
            cursor.execute("INSERT INTO Users (user_id, name, password, status, role) VALUES (?, ?, ?, ?, ?)",
                           ('admin', 'Administrator', admin_password, 'active', 'admin'))
            print("Default admin user ('admin'/'admin') created.")
        conn.commit()
        conn.close()

    def center_window(self):
        # This function is unchanged
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_login_widgets(self):
        # This function is unchanged
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill="both")
        title_label = ttk.Label(main_frame, text="Library Management System", font=("Helvetica", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        user_id_label = ttk.Label(main_frame, text="User ID:", font=("Helvetica", 12))
        user_id_label.grid(row=1, column=0, sticky="w", padx=(10, 5), pady=5)
        self.user_id_entry = ttk.Entry(main_frame, width=30, font=("Helvetica", 12))
        self.user_id_entry.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=5)
        password_label = ttk.Label(main_frame, text="Password:", font=("Helvetica", 12))
        password_label.grid(row=2, column=0, sticky="w", padx=(10, 5), pady=5)
        self.password_entry = ttk.Entry(main_frame, show="*", width=30, font=("Helvetica", 12))
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=5)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.root.destroy)
        cancel_button.pack(side="left", padx=10)
        login_button = ttk.Button(button_frame, text="Login", command=self.handle_login)
        login_button.pack(side="right", padx=10)
        main_frame.grid_columnconfigure(1, weight=1)

    def handle_login(self):
        # This function is unchanged
        login_id = self.user_id_entry.get()
        password = self.password_entry.get()
        if not login_id or not password:
            messagebox.showerror("Login Error", "User ID and Password cannot be empty.")
            return
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT password, role, name FROM Users WHERE user_id = ?", (login_id,))
        user_record = cursor.fetchone()
        conn.close()
        if user_record:
            stored_password, user_role, user_name = user_record
            if password == stored_password:
                messagebox.showinfo("Login Success", f"Welcome, {user_name}!")
                self.root.destroy()
                self.open_dashboard(user_role, login_id)
            else:
                messagebox.showerror("Login Failed", "Incorrect password.")
        else:
            messagebox.showerror("Login Failed", f"User ID '{login_id}' not found.")

    def open_dashboard(self, role, user_id):
        """Opens the correct dashboard, passing the user_id if not an admin."""
        command = [sys.executable]

        if role == 'admin':
            # --- CORRECTED PATH ---
            path = r"C:\Users\vedan\Desktop\LMS - Copy\admin_dashboard.py"
            script_name = "admin dashboard"
            command.append(path)
        else:
            # --- CORRECTED PATH ---
            path = r"C:\Users\vedan\Desktop\LMS - Copy\user_dashboard.py"
            script_name = "user dashboard"
            command.append(path)
            command.append(user_id)
        
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Could not find the {script_name} script at:\n{path}")
            return
        
        try:
            subprocess.Popen(command)
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open {script_name} script:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryLogin(root)
    root.mainloop()