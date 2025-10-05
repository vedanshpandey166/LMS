import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import sys
import os
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import sqlite3
import secrets

class MaintenancePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Housekeeping - Maintenance")
        self.root.geometry("800x600")
        
        self.center_window(self.root)
        self.db_name = "library.db"
        self.setup_database()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill="both")

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))

        home_button = ttk.Button(top_frame, text="Home", command=self.go_home)
        home_button.pack(side="right")
        
        title_label = ttk.Label(top_frame, text="Housekeeping", font=("Helvetica", 16, "bold"))
        title_label.pack(side="left")

        sections_frame = ttk.Frame(main_frame)
        sections_frame.pack(expand=True, fill="both", pady=10)
        sections_frame.columnconfigure(1, weight=1) 

        style = ttk.Style()
        style.configure('Action.TButton', font=('Helvetica', 11), padding=(10, 8))

        # --- A. User Management Section ---
        user_label = ttk.Label(sections_frame, text="User Management", font=("Helvetica", 12, "bold"))
        user_label.grid(row=0, column=0, sticky="w", padx=5, pady=(10,5))
        
        user_add_button = ttk.Button(sections_frame, text="Add", style='Action.TButton', command=lambda: self.show_user_management_popup(mode='new'))
        user_add_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        user_update_button = ttk.Button(sections_frame, text="Update", style='Action.TButton', command=lambda: self.show_user_management_popup(mode='existing'))
        user_update_button.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # --- B. Membership Section ---
        membership_label = ttk.Label(sections_frame, text="Membership", font=("Helvetica", 12, "bold"))
        membership_label.grid(row=2, column=0, sticky="w", padx=5, pady=(20,5))
        
        membership_add_button = ttk.Button(
            sections_frame, text="Add", style='Action.TButton', command=self.show_add_membership_popup)
        membership_add_button.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        membership_update_button = ttk.Button(
            sections_frame, text="Update", style='Action.TButton', command=self.show_update_membership_popup)
        membership_update_button.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # --- C. Books/Movies Section ---
        items_label = ttk.Label(sections_frame, text="Books/Movies", font=("Helvetica", 12, "bold"))
        items_label.grid(row=4, column=0, sticky="w", padx=5, pady=(20,5))

        items_add_button = ttk.Button(
            sections_frame, text="Add", style='Action.TButton', command=self.show_add_item_popup)
        items_add_button.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        
        items_update_button = ttk.Button(
            sections_frame, text="Update", style='Action.TButton', command=self.show_update_item_popup)
        items_update_button.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", side="bottom", pady=(10, 0))

        logout_button = ttk.Button(bottom_frame, text="Log Out", command=self.logout)
        logout_button.pack(side="right")

    def setup_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                contact_no TEXT,
                contact_address TEXT,
                aadhaar_card_no TEXT,
                status TEXT NOT NULL,
                role TEXT NOT NULL
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Memberships (
                member_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                membership_duration TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Items (
                serial_no TEXT PRIMARY KEY,
                item_type TEXT NOT NULL,
                item_name TEXT NOT NULL,
                creator TEXT NOT NULL,
                procurement_date TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL 
            )''')
        conn.commit()
        conn.close()

    # --- User Management Methods ---
    def show_user_management_popup(self, mode='new'):
        popup = tk.Toplevel(self.root)
        popup.title("User Management")
        popup.geometry("450x400")
        self.center_window(popup)
        popup.transient(self.root)
        popup.grab_set()

        form_frame = ttk.Frame(popup, padding="20")
        form_frame.pack(expand=True, fill="both")
        form_frame.columnconfigure(1, weight=1)

        mode_var = tk.StringVar(value=mode)
        entries = {}
        
        labels = ["User ID", "Name", "Contact No.", "Contact Address", "Aadhaar Card No"]
        for i, text in enumerate(labels):
            ttk.Label(form_frame, text=text).grid(row=i+1, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(form_frame)
            entry.grid(row=i+1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
            entries[text.replace(" ", "_").lower().replace(".", "")] = entry

        status_var = tk.StringVar(value="active")
        role_var = tk.StringVar(value="user")

        def toggle_mode(*args):
            user_id_entry = entries['user_id']
            if mode_var.get() == "new":
                user_id = f"USER-{datetime.now().strftime('%y%m%d')}-{secrets.token_hex(4).upper()}"
                user_id_entry.config(state="normal")
                user_id_entry.delete(0, tk.END)
                user_id_entry.insert(0, user_id)
                user_id_entry.config(state="readonly")
                for key, entry in entries.items():
                    if key != 'user_id': entry.config(state="normal"); entry.delete(0, tk.END)
            else:
                for key, entry in entries.items():
                    entry.config(state="normal"); entry.delete(0, tk.END)
                    if key != 'user_id': entry.config(state="readonly")

        mode_var.trace("w", toggle_mode)

        mode_frame = ttk.Frame(form_frame)
        ttk.Radiobutton(mode_frame, text="New User", variable=mode_var, value="new").pack(side="left")
        ttk.Radiobutton(mode_frame, text="Existing User", variable=mode_var, value="existing").pack(side="left", padx=10)
        mode_frame.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        fetch_button = ttk.Button(form_frame, text="Fetch", command=lambda: self.fetch_user_details(popup, entries))
        fetch_button.grid(row=1, column=2, sticky="e", padx=5)
        
        status_frame = ttk.Frame(form_frame)
        ttk.Radiobutton(status_frame, text="Active", variable=status_var, value="active").pack(side="left")
        ttk.Radiobutton(status_frame, text="Inactive", variable=status_var, value="inactive").pack(side="left", padx=10)
        ttk.Label(form_frame, text="Status").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        status_frame.grid(row=6, column=1, columnspan=2, sticky="w")
        
        role_frame = ttk.Frame(form_frame)
        ttk.Radiobutton(role_frame, text="User", variable=role_var, value="user").pack(side="left")
        ttk.Radiobutton(role_frame, text="Admin", variable=role_var, value="admin").pack(side="left", padx=10)
        ttk.Label(form_frame, text="Role").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        role_frame.grid(row=7, column=1, columnspan=2, sticky="w")

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=(20, 0))
        ttk.Button(btn_frame, text="Confirm", command=lambda: self.handle_user_confirmation(popup, mode_var.get(), entries, status_var, role_var)).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=10)
        
        toggle_mode()

    def fetch_user_details(self, popup, entries):
        user_id = entries['user_id'].get()
        if not user_id: return

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name, contact_no, contact_address, aadhaar_card_no FROM Users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        for key, entry in entries.items():
            if key != 'user_id':
                entry.config(state="normal"); entry.delete(0, tk.END)

        if result:
            entries['name'].insert(0, result[0]); entries['contact_no'].insert(0, result[1] or "")
            entries['contact_address'].insert(0, result[2] or ""); entries['aadhaar_card_no'].insert(0, result[3] or "")
        else:
            messagebox.showerror("Not Found", f"No user found with ID: {user_id}", parent=popup)
        
        for key, entry in entries.items():
            if key != 'user_id': entry.config(state="readonly")

    def handle_user_confirmation(self, popup, mode, entries, status_var, role_var):
        values = {key: entry.get() for key, entry in entries.items()}
        status = status_var.get()
        role = role_var.get()

        if not (values['user_id'] and values['name']):
            messagebox.showerror("Validation Error", "User ID and Name are required.", parent=popup)
            return

        if mode == "new":
            contact_no = values['contact_no']
            if contact_no and not (contact_no.isdigit() and len(contact_no) == 10):
                messagebox.showerror("Validation Error", "Contact No. must be a 10-digit number.", parent=popup)
                return

            aadhaar_no = values['aadhaar_card_no']
            if aadhaar_no and not (aadhaar_no.isdigit() and len(aadhaar_no) == 12):
                messagebox.showerror("Validation Error", "Aadhaar Card No. must be a 12-digit number.", parent=popup)
                return
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            if mode == "new":
                password = secrets.token_hex(8)
                cursor.execute("""
                    INSERT INTO Users (user_id, name, password, contact_no, contact_address, aadhaar_card_no, status, role) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,(values['user_id'], values['name'], password, values['contact_no'], values['contact_address'], values['aadhaar_card_no'], status, role))
                messagebox.showinfo("User Added", f"User created successfully.\n\nPassword: {password}\n\nPlease save this password securely.", parent=popup)
            else:
                cursor.execute("UPDATE Users SET status=?, role=? WHERE user_id=?", (status, role, values['user_id']))
                messagebox.showinfo("Success", "User updated successfully.", parent=popup)
            
            conn.commit()
            popup.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Database Error", "This User ID already exists.", parent=popup)
        finally:
            conn.close()

    # --- Membership Methods ---
    def show_add_membership_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Membership")
        popup.geometry("500x450")
        self.center_window(popup)
        popup.transient(self.root)
        popup.grab_set()

        form_frame = ttk.Frame(popup, padding="20")
        form_frame.pack(expand=True, fill="both")
        form_frame.columnconfigure(1, weight=1)
        
        entries = {}
        labels = ["Membership ID", "User ID", "Name", "Contact No.", "Contact Address", "Aadhaar Card No", "Start Date", "End Date"]
        for i, text in enumerate(labels):
             ttk.Label(form_frame, text=text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
             entry = ttk.Entry(form_frame, state="readonly")
             entry.grid(row=i, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
             entries[text.replace(" ", "_").lower().replace(".", "")] = entry
        
        entries['user_id'].config(state="normal"); entries['start_date'].config(state="normal")
        entries['start_date'].insert(0, date.today().strftime('%Y-%m-%d'))
        
        member_id = f"MEM-{datetime.now().strftime('%y%m%d')}-{secrets.token_hex(5).upper()}"
        entries['membership_id'].config(state="normal"); entries['membership_id'].insert(0, member_id); entries['membership_id'].config(state="readonly")

        ttk.Button(form_frame, text="Fetch User", command=lambda: self.fetch_user_for_membership(popup, entries)).grid(row=1, column=2, padx=5)

        membership_var = tk.StringVar()
        def update_end_date(*args):
            try:
                start_dt = datetime.strptime(entries['start_date'].get(), '%Y-%m-%d').date()
                duration = membership_var.get()
                end_dt = None
                if duration == "6m": end_dt = start_dt + relativedelta(months=+6)
                elif duration == "1y": end_dt = start_dt + relativedelta(years=+1)
                elif duration == "2y": end_dt = start_dt + relativedelta(years=+2)
                
                if end_dt:
                    entries['end_date'].config(state="normal"); entries['end_date'].delete(0, tk.END)
                    entries['end_date'].insert(0, end_dt.strftime('%Y-%m-%d')); entries['end_date'].config(state="readonly")
            except ValueError: pass
        membership_var.trace("w", update_end_date)
        
        ttk.Label(form_frame, text="Membership").grid(row=len(labels), column=0, sticky="w", padx=5, pady=10)
        radio_frame = ttk.Frame(form_frame)
        radio_frame.grid(row=len(labels), column=1, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(radio_frame, text="Six Months", variable=membership_var, value="6m").pack(side="left")
        ttk.Radiobutton(radio_frame, text="One Year", variable=membership_var, value="1y").pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Two Years", variable=membership_var, value="2y").pack(side="left", padx=5)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(labels)+1, column=0, columnspan=3, pady=(20,0))
        ttk.Button(btn_frame, text="Confirm", command=lambda: self.handle_add_membership_confirmation(popup, entries, membership_var)).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=10)

    def fetch_user_for_membership(self, popup, entries):
        user_id = entries['user_id'].get()
        if not user_id: return
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name, contact_no, contact_address, aadhaar_card_no FROM Users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        for key in ['name', 'contact_no', 'contact_address', 'aadhaar_card_no']:
            entries[key].config(state="normal"); entries[key].delete(0, tk.END)

        if result:
            entries['name'].insert(0, result[0]); entries['contact_no'].insert(0, result[1] or "")
            entries['contact_address'].insert(0, result[2] or ""); entries['aadhaar_card_no'].insert(0, result[3] or "")
        else:
            messagebox.showerror("Not Found", f"No user found with ID: {user_id}", parent=popup)
        
        for key in ['name', 'contact_no', 'contact_address', 'aadhaar_card_no']:
            entries[key].config(state="readonly")
        
    def handle_add_membership_confirmation(self, popup, entries, membership_var):
        values = {key: entry.get() for key, entry in entries.items()}
        duration = membership_var.get()
        
        if not (values['user_id'] and values['name'] and values['start_date'] and values['end_date'] and duration):
            messagebox.showerror("Validation Error", "Please fetch a user and select a membership duration.", parent=popup)
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Memberships VALUES (?, ?, ?, ?, ?)",
                           (values['membership_id'], values['user_id'], values['start_date'], values['end_date'], duration))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Membership created successfully!", parent=popup)
            popup.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Database Error", "This User already has a membership or Member ID conflict.", parent=popup)

    def show_update_membership_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Update Membership")
        popup.geometry("500x400")
        self.center_window(popup)
        popup.transient(self.root)
        popup.grab_set()

        form_frame = ttk.Frame(popup, padding="20")
        form_frame.pack(expand=True, fill="both")
        form_frame.columnconfigure(1, weight=1)

        entries = {}
        labels = ["Membership No.", "User ID", "Name", "Start Date", "End Date"]
        for i, text in enumerate(labels):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(form_frame, state="readonly")
            entry.grid(row=i, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
            entries[text.replace(" ", "_").lower().replace(".", "")] = entry
        
        entries['membership_no'].config(state="normal")
        
        fetch_button = ttk.Button(form_frame, text="Fetch Details", command=lambda: self.fetch_member_details(popup, entries))
        fetch_button.grid(row=0, column=2, padx=5, pady=5)

        update_var = tk.StringVar()
        ttk.Label(form_frame, text="Membership Extn:").grid(row=5, column=0, sticky="w", padx=5, pady=10)
        ext_frame = ttk.Frame(form_frame)
        ext_frame.grid(row=5, column=1, columnspan=2, sticky="ew")
        ttk.Radiobutton(ext_frame, text="Six Months", variable=update_var, value="ext_6m").pack(side="left")
        ttk.Radiobutton(ext_frame, text="One Year", variable=update_var, value="ext_1y").pack(side="left", padx=10)
        ttk.Radiobutton(ext_frame, text="Two Years", variable=update_var, value="ext_2y").pack(side="left")

        ttk.Label(form_frame, text="Membership Remove:").grid(row=6, column=0, sticky="w", padx=5, pady=10)
        ttk.Radiobutton(form_frame, text="Yes, remove", variable=update_var, value="remove").grid(row=6, column=1, sticky="w")

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=(20,0))
        ttk.Button(btn_frame, text="Confirm", 
            command=lambda: self.handle_update_membership_confirmation(popup, entries['membership_no'].get(), update_var.get(), entries['end_date'].get())).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=10)

    def fetch_member_details(self, popup, entries):
        member_id = entries['membership_no'].get()
        if not member_id: return
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        query = """
            SELECT m.user_id, u.name, m.start_date, m.end_date 
            FROM Memberships m JOIN Users u ON m.user_id = u.user_id 
            WHERE m.member_id = ? """
        cursor.execute(query, (member_id,))
        result = cursor.fetchone()
        conn.close()

        for key in ['user_id', 'name', 'start_date', 'end_date']:
            entries[key].config(state="normal"); entries[key].delete(0, tk.END)

        if result:
            entries['user_id'].insert(0, result[0]); entries['name'].insert(0, result[1])
            entries['start_date'].insert(0, result[2]); entries['end_date'].insert(0, result[3])
        else:
            messagebox.showerror("Not Found", f"No membership found with number: {member_id}", parent=popup)

        for key in ['user_id', 'name', 'start_date', 'end_date']:
            entries[key].config(state="readonly")
    
    def handle_update_membership_confirmation(self, popup, member_id, action, current_end_date_str):
        if not member_id or not action: return

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        message = ""
        if action == "remove":
            if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove membership {member_id}?", parent=popup):
                cursor.execute("DELETE FROM Memberships WHERE member_id=?", (member_id,))
                message = "Membership removed."
            else: conn.close(); return
        else:
            try:
                current_end_date = datetime.strptime(current_end_date_str, '%Y-%m-%d').date()
                new_end_date = None
                if action == "ext_6m": new_end_date = current_end_date + relativedelta(months=+6)
                elif action == "ext_1y": new_end_date = current_end_date + relativedelta(years=+1)
                elif action == "ext_2y": new_end_date = current_end_date + relativedelta(years=+2)
                
                cursor.execute("UPDATE Memberships SET end_date=? WHERE member_id=?", (new_end_date.strftime('%Y-%m-%d'), member_id))
                message = "Membership extended."
            except (ValueError, TypeError):
                messagebox.showerror("Error", "Invalid end date. Cannot extend.", parent=popup)
                conn.close(); return
        conn.commit()
        conn.close()
        if message: messagebox.showinfo("Success", message, parent=popup)
        popup.destroy()

    # --- Item (Book/Movie) Methods ---
    def show_add_item_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Book/Movie")
        popup.geometry("400x320")
        self.center_window(popup)
        popup.transient(self.root)
        popup.grab_set()

        form_frame = ttk.Frame(popup, padding="20")
        form_frame.pack(expand=True, fill="both")
        form_frame.columnconfigure(1, weight=1)

        item_type_var = tk.StringVar(value="Book")
        serial_entry = ttk.Entry(form_frame, state="readonly")
        name_entry = ttk.Entry(form_frame)
        creator_entry = ttk.Entry(form_frame)
        date_entry = ttk.Entry(form_frame)
        qty_entry = ttk.Entry(form_frame)
        
        def update_serial_no(*args):
            prefix = "B" if item_type_var.get() == "Book" else "M"
            new_serial = f"{prefix}-{datetime.now().strftime('%y%m%d')}-{secrets.token_hex(5).upper()}"
            serial_entry.config(state="normal"); serial_entry.delete(0, tk.END)
            serial_entry.insert(0, new_serial); serial_entry.config(state="readonly")

        item_type_var.trace("w", update_serial_no)

        radio_frame = ttk.Frame(form_frame)
        ttk.Radiobutton(radio_frame, text="Book", variable=item_type_var, value="Book").pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Movie", variable=item_type_var, value="Movie").pack(side="left", padx=5)
        radio_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ttk.Label(form_frame, text="Serial No.").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        serial_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(form_frame, text="Book/Movie Name").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        name_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(form_frame, text="Author/Creator").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        creator_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date of Procurement").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        date_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        date_entry.insert(0, date.today().strftime('%Y-%m-%d'))

        ttk.Label(form_frame, text="Quantity/Copies").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        qty_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        qty_entry.insert(0, "1")
        
        update_serial_no()

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(20,0))
        ttk.Button(btn_frame, text="Confirm", 
            command=lambda: self.handle_add_item_confirmation(popup, item_type_var, serial_entry, name_entry, creator_entry, date_entry, qty_entry)).pack(side="left")
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=10)

    def handle_add_item_confirmation(self, popup, item_type_var, serial_entry, name_entry, creator_entry, date_entry, qty_entry):
        serial_no = serial_entry.get(); name = name_entry.get(); creator = creator_entry.get(); qty = qty_entry.get()
        if not (name and creator and serial_no and qty):
            messagebox.showerror("Validation Error", "All fields are required.", parent=popup)
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Items VALUES (?, ?, ?, ?, ?, ?, ?)", 
                (serial_no, item_type_var.get(), name, creator, date_entry.get(), int(qty), "available"))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"{item_type_var.get()} added successfully!", parent=popup)
            popup.destroy()
        except Exception as e: messagebox.showerror("Database Error", f"An error occurred: {e}", parent=popup)

    def show_update_item_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Update Book/Movie")
        popup.geometry("450x340")
        self.center_window(popup)
        popup.transient(self.root)
        popup.grab_set()

        form_frame = ttk.Frame(popup, padding="20")
        form_frame.pack(expand=True, fill="both")
        form_frame.columnconfigure(1, weight=1)

        item_type_var = tk.StringVar(); status_var = tk.StringVar()
        status_options = ["available", "unavailable", "removed", "on repair", "to replace"]

        ttk.Label(form_frame, text="Serial No").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        serial_entry = ttk.Entry(form_frame)
        serial_entry.grid(row=0, column=1, sticky="ew")

        radio_frame = ttk.Frame(form_frame)
        ttk.Radiobutton(radio_frame, text="Book", variable=item_type_var, value="Book", state="disabled").pack(side="left")
        ttk.Radiobutton(radio_frame, text="Movie", variable=item_type_var, value="Movie", state="disabled").pack(side="left", padx=10)
        radio_frame.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(form_frame, text="Book/Movie Name").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        name_entry = ttk.Entry(form_frame, state="readonly")
        name_entry.grid(row=2, column=1, sticky="ew")
        
        ttk.Label(form_frame, text="Author/Creator").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        creator_entry = ttk.Entry(form_frame, state="readonly")
        creator_entry.grid(row=3, column=1, sticky="ew")

        ttk.Label(form_frame, text="Status").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        status_dropdown = ttk.Combobox(form_frame, textvariable=status_var, values=status_options, state="readonly")
        status_dropdown.grid(row=4, column=1, sticky="ew")

        ttk.Label(form_frame, text="Date").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        date_entry = ttk.Entry(form_frame, state="readonly")
        date_entry.grid(row=5, column=1, sticky="ew")

        fetch_button = ttk.Button(form_frame, text="Fetch Details", command=lambda: self.fetch_item_details(popup, serial_entry.get(), item_type_var, name_entry, creator_entry, status_dropdown, date_entry))
        fetch_button.grid(row=0, column=2, padx=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=(20,0))
        ttk.Button(btn_frame, text="Confirm", command=lambda: self.handle_update_item_confirmation(popup, serial_entry.get(), status_var.get())).pack(side="left")
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=10)

    def fetch_item_details(self, popup, serial_no, item_type_var, name_entry, creator_entry, status_dropdown, date_entry):
        if not serial_no: return
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT item_type, item_name, creator, procurement_date, status FROM Items WHERE serial_no=?", (serial_no,))
        result = cursor.fetchone()
        conn.close()

        for entry in [name_entry, creator_entry, date_entry]:
            entry.config(state="normal"); entry.delete(0, tk.END); entry.config(state="readonly")
        item_type_var.set(""); status_dropdown.set("")

        if result:
            item_type, item_name, creator, proc_date, status = result
            item_type_var.set(item_type); status_dropdown.set(status)
            name_entry.config(state="normal"); name_entry.insert(0, item_name); name_entry.config(state="readonly")
            creator_entry.config(state="normal"); creator_entry.insert(0, creator); creator_entry.config(state="readonly")
            date_entry.config(state="normal"); date_entry.insert(0, proc_date); date_entry.config(state="readonly")
        else:
            messagebox.showerror("Not Found", f"No item found with Serial No: {serial_no}", parent=popup)

    def handle_update_item_confirmation(self, popup, serial_no, new_status):
        if not (serial_no and new_status): return
            
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Items SET status=? WHERE serial_no=?", (new_status, serial_no))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Item status updated successfully.", parent=popup)
            popup.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}", parent=popup)


    # --- General Methods ---
    def go_home(self):
        dashboard_path = r"C:\Users\vedan\Desktop\LMS\admin_dashboard.py"
        if not os.path.exists(dashboard_path):
            messagebox.showerror("Error", f"Could not find the dashboard script at:\n{dashboard_path}")
            return
        try:
            subprocess.Popen([sys.executable, dashboard_path])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open dashboard script:\n{e}")
        
    def logout(self):
        if messagebox.askokcancel("Log Out", "Are you sure you want to log out?"):
            self.root.destroy()

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    root = tk.Tk()
    app = MaintenancePage(root)
    root.mainloop()

