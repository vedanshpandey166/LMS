import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import sqlite3
from datetime import date, timedelta, datetime

class AdminTransactionsPage:
    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(self.root)
        self.window.title("Administrator - Transactions")
        self.window.geometry("600x400")
        
        self.center_window(self.window)
        self.db_name = "library.db"

        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(expand=True, fill="both")

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x")

        home_button = ttk.Button(top_frame, text="Home", command=self.go_home)
        home_button.pack(side="right")
        
        title_label = ttk.Label(top_frame, text="Transactions", font=("Helvetica", 14, "bold"))
        title_label.pack(side="left")

        transactions_frame = ttk.Frame(main_frame)
        transactions_frame.pack(expand=True, fill="both", pady=20)

        style = ttk.Style()
        style.configure('Action.TButton', font=('Helvetica', 12), padding=10)
        
        button_map = {
            "Is Item Available?": self.show_item_availability_popup,
            "Issue Item": self.show_issue_item_popup,
            "Return Item": self.show_return_item_popup,
            "Pay Fine": self.show_pay_fine_popup # Placeholder, as it's part of the return flow
        }

        for name, command in button_map.items():
            button = ttk.Button(transactions_frame, text=name, style='Action.TButton', command=command)
            button.pack(fill="x", pady=5)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", side="bottom")
        logout_button = ttk.Button(bottom_frame, text="Log Out", command=self.logout)
        logout_button.pack(side="right")

    # --- Search and Issue Workflow ---
    def show_item_availability_popup(self):
        # This function is identical to the user version, as admins also need to search the catalog
        popup = tk.Toplevel(self.window)
        popup.title("Item Availability Search")
        popup.geometry("500x200")
        self.center_window(popup)
        popup.grab_set()

        popup_frame = ttk.Frame(popup, padding="20")
        popup_frame.pack(expand=True, fill="both")
        popup_frame.columnconfigure(1, weight=1)

        title_label = ttk.Label(popup_frame, text="Item Availability", font=("Helvetica", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT item_name FROM Items ORDER BY item_name")
        item_names = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT creator FROM Items ORDER BY creator")
        creator_names = [row[0] for row in cursor.fetchall()]
        conn.close()

        def on_search(search_type, value):
            if value:
                popup.destroy()
                self.show_search_results_popup(search_type, value)

        ttk.Label(popup_frame, text="Book/Movie Name", font=("Helvetica", 11)).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        item_name_combo = ttk.Combobox(popup_frame, values=item_names)
        item_name_combo.grid(row=1, column=1, sticky="ew", pady=5)
        
        ttk.Label(popup_frame, text="Author/Creator", font=("Helvetica", 11)).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        creator_combo = ttk.Combobox(popup_frame, values=creator_names)
        creator_combo.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Button(popup_frame, text="Search by Name", command=lambda: on_search('item_name', item_name_combo.get())).grid(row=1, column=2, padx=5)
        ttk.Button(popup_frame, text="Search by Creator", command=lambda: on_search('creator', creator_combo.get())).grid(row=2, column=2, padx=5)

    def show_search_results_popup(self, search_type, value):
        # Also identical to the user version
        results_popup = tk.Toplevel(self.window)
        results_popup.title("Search Results")
        results_popup.geometry("700x400")
        self.center_window(results_popup)
        results_popup.grab_set()

        popup_frame = ttk.Frame(results_popup, padding="20")
        popup_frame.pack(expand=True, fill="both")
        
        ttk.Label(popup_frame, text=f"Available Items for: {value}", font=("Helvetica", 14, "bold")).pack(pady=(0, 15))

        tree = ttk.Treeview(popup_frame, columns=("item_name", "creator", "serial", "available"), show="headings")
        tree.heading("item_name", text="Book/Movie Name"); tree.heading("creator", text="Author/Creator")
        tree.heading("serial", text="Serial Number"); tree.heading("available", text="Available")
        tree.pack(expand=True, fill="both")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        query = f"SELECT item_name, creator, serial_no, status FROM Items WHERE {search_type} = ?"
        cursor.execute(query, (value,))
        results = cursor.fetchall()
        conn.close()

        for item in results:
            availability = "Y" if item[3] == "available" else "N"
            tree.insert("", "end", values=(item[0], item[1], item[2], availability))

        def handle_issue_selection():
            selected_item_id = tree.focus()
            if not selected_item_id: return
            
            item_details_tree = tree.item(selected_item_id)
            values = item_details_tree.get("values")
            
            if values and values[3] == "Y":
                item_details_dict = {"name": values[0], "creator": values[1], "serial_no": values[2]}
                results_popup.destroy()
                self.show_issue_item_popup(item_details=item_details_dict)
            else:
                messagebox.showwarning("Not Available", "This item is not available for issue.", parent=results_popup)

        button_frame = ttk.Frame(popup_frame)
        button_frame.pack(pady=(20, 0))
        ttk.Button(button_frame, text="Cancel", command=results_popup.destroy).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Select to Issue", command=handle_issue_selection).pack(side="left", padx=10)

    def show_issue_item_popup(self, item_details=None):
        popup = tk.Toplevel(self.window)
        popup.title("Issue Item")
        popup.geometry("500x350")
        self.center_window(popup)
        popup.grab_set()

        popup_frame = ttk.Frame(popup, padding="20")
        popup_frame.pack(expand=True, fill="both")
        popup_frame.columnconfigure(1, weight=1)

        ttk.Label(popup_frame, text="Issue Item", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        labels = ["User ID", "Serial No", "Book/Movie Name", "Author/Creator", "Issue Date", "Return Date"]
        entries = {}
        for i, text in enumerate(labels):
            ttk.Label(popup_frame, text=text).grid(row=i+1, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(popup_frame)
            entry.grid(row=i+1, column=1, sticky="ew", padx=5, pady=5)
            # User ID is editable for admin
            if text not in ["User ID"]: entry.config(state="readonly")
            entries[text.replace("/", "_").replace(" ", "_").lower()] = entry
        
        if item_details:
            entries['serial_no'].config(state="normal"); entries['serial_no'].insert(0, item_details['serial_no']); entries['serial_no'].config(state="readonly")
            entries['book_movie_name'].config(state="normal"); entries['book_movie_name'].insert(0, item_details['name']); entries['book_movie_name'].config(state="readonly")
            entries['author_creator'].config(state="normal"); entries['author_creator'].insert(0, item_details['creator']); entries['author_creator'].config(state="readonly")
        
        today = date.today()
        return_date = today + timedelta(days=15)
        entries['issue_date'].config(state="normal"); entries['issue_date'].insert(0, today.strftime("%Y-%m-%d")); entries['issue_date'].config(state="readonly")
        entries['return_date'].config(state="normal"); entries['return_date'].insert(0, return_date.strftime("%Y-%m-%d")); entries['return_date'].config(state="readonly")

        def handle_issue_confirmation():
            user_id = entries['user_id'].get()
            serial_no = entries['serial_no'].get()
            if not (user_id and serial_no):
                messagebox.showerror("Validation Error", "User ID and Item details are required.", parent=popup)
                return
            
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Transactions (user_id, serial_no, issue_date, due_date) VALUES (?, ?, ?, ?)", 
                               (user_id, serial_no, entries['issue_date'].get(), entries['return_date'].get()))
                cursor.execute("UPDATE Items SET status = 'unavailable' WHERE serial_no = ?", (serial_no,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Item issued successfully!", parent=popup)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}", parent=popup)

        btn_frame = ttk.Frame(popup_frame)
        btn_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=(20, 0))
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Confirm Issue", command=handle_issue_confirmation).pack(side="left", padx=10)

    # --- Return and Fine Workflow ---
    def show_return_item_popup(self):
        popup = tk.Toplevel(self.window)
        popup.title("Return Item")
        popup.geometry("500x300")
        self.center_window(popup)
        popup.grab_set()

        popup_frame = ttk.Frame(popup, padding="20")
        popup_frame.pack(expand=True, fill="both")
        popup_frame.columnconfigure(1, weight=1)

        ttk.Label(popup_frame, text="Return Item", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT I.item_name, T.serial_no 
            FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no 
            WHERE T.return_date IS NULL
        """)
        issued_items = {f"{row[0]} ({row[1]})": row[1] for row in cursor.fetchall()}
        conn.close()

        entries = {}
        def on_item_select(event):
            # CORRECTED: Changed 'item_selection' to 'select_item' to match the key
            selection = entries['select_item'].get()
            serial_no = issued_items.get(selection)
            if not serial_no: return
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT I.creator, T.user_id, T.issue_date, T.due_date 
                FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no 
                WHERE T.serial_no = ? AND T.return_date IS NULL
            """, (serial_no,))
            result = cursor.fetchone()
            conn.close()

            if result:
                entries['serial_no'].config(state='normal'); entries['serial_no'].delete(0, tk.END); entries['serial_no'].insert(0, serial_no); entries['serial_no'].config(state='readonly')
                entries['user_id'].config(state='normal'); entries['user_id'].delete(0, tk.END); entries['user_id'].insert(0, result[1]); entries['user_id'].config(state='readonly')
                entries['issue_date'].config(state='normal'); entries['issue_date'].delete(0, tk.END); entries['issue_date'].insert(0, result[2]); entries['issue_date'].config(state='readonly')
                entries['due_date'].config(state='normal'); entries['due_date'].delete(0, tk.END); entries['due_date'].insert(0, result[3]); entries['due_date'].config(state='readonly')
        
        labels = ["Select Item", "User ID", "Serial No", "Issue Date", "Due Date"]
        for i, text in enumerate(labels):
            ttk.Label(popup_frame, text=text).grid(row=i+1, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(popup_frame, state='readonly') if text != "Select Item" else ttk.Combobox(popup_frame, values=list(issued_items.keys()))
            entry.grid(row=i+1, column=1, sticky="ew", padx=5, pady=5)
            if text == "Select Item": entry.bind("<<ComboboxSelected>>", on_item_select)
            entries[text.replace("/", "_").replace(" ", "_").lower()] = entry

        def handle_return_confirmation():
            if not entries['serial_no'].get(): return
            
            due_date_str = entries['due_date'].get()
            due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            days_overdue = (date.today() - due_date_obj).days
            fine = max(0, days_overdue * 50)
            
            return_details = {
                "user_id": entries['user_id'].get(),
                "serial_no": entries['serial_no'].get(),
                "issue_date": entries['issue_date'].get(),
                "due_date": due_date_str,
                "actual_return_date": date.today().strftime("%Y-%m-%d"),
                "fine_calculated": f"{fine:.2f}"
            }
            
            popup.destroy()
            self.show_pay_fine_popup(return_details)

        btn_frame = ttk.Frame(popup_frame)
        btn_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=(20,0))
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left")
        ttk.Button(btn_frame, text="Confirm Return", command=handle_return_confirmation).pack(side="left", padx=10)

    def show_pay_fine_popup(self, return_details=None):
        if not return_details: 
            messagebox.showinfo("Info", "This function is part of the return process.")
            return

        popup = tk.Toplevel(self.window)
        popup.title("Pay Fine")
        popup.geometry("500x450")
        self.center_window(popup)
        popup.grab_set()

        popup_frame = ttk.Frame(popup, padding="20")
        popup_frame.pack(expand=True, fill="both")

        ttk.Label(popup_frame, text="Pay Fine", font=("Helvetica", 14, "bold")).pack(pady=(0,20))
        
        for key, value in return_details.items():
            frame = ttk.Frame(popup_frame)
            frame.pack(fill="x", pady=2)
            ttk.Label(frame, text=f"{key.replace('_', ' ').title()}:", width=20).pack(side="left")
            entry = ttk.Entry(frame); entry.insert(0, value); entry.config(state="readonly")
            entry.pack(side="left", expand=True, fill="x")

        fine_paid_var = tk.BooleanVar()
        ttk.Checkbutton(popup_frame, text="Fine Paid", variable=fine_paid_var).pack(pady=10)

        def handle_fine_confirmation():
            fine_amount = float(return_details.get('fine_calculated', 0))
            if fine_amount > 0 and not fine_paid_var.get():
                messagebox.showerror("Payment Required", "A fine is pending. Please check 'Fine Paid'.", parent=popup)
                return
            
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Transactions SET return_date = ?, fine_paid = ? 
                    WHERE serial_no = ? AND user_id = ? AND return_date IS NULL
                """, (return_details['actual_return_date'], fine_amount, return_details['serial_no'], return_details['user_id']))
                cursor.execute("UPDATE Items SET status = 'available' WHERE serial_no = ?", (return_details['serial_no'],))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Return completed successfully!", parent=popup)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}", parent=popup)

        btn_frame = ttk.Frame(popup_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left")
        ttk.Button(btn_frame, text="Confirm", command=handle_fine_confirmation).pack(side="left", padx=10)

    # --- General Methods ---
    def go_home(self):
        dashboard_path = r"C:\Users\vedan\Desktop\LMS\admin_dashboard.py"
        if not os.path.exists(dashboard_path):
            messagebox.showerror("Error", f"Could not find dashboard script at:\n{dashboard_path}")
            return
        try:
            subprocess.Popen([sys.executable, dashboard_path])
            self.window.destroy()
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open dashboard script:\n{e}")

    def logout(self):
        if messagebox.askokcancel("Log Out", "Are you sure you want to log out?"):
            self.window.destroy()
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
    root.withdraw() 
    app = AdminTransactionsPage(root)
    root.mainloop()

