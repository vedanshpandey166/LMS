import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import sqlite3
from datetime import date, timedelta, datetime

class TransactionsPage:
    # --- MODIFIED ---
    # The constructor now accepts the logged-in user's ID
    def __init__(self, root, current_user_id):
        self.root = root
        self.window = tk.Toplevel(self.root)
        self.window.title("Transactions")
        self.window.geometry("600x400")
        
        self.center_window(self.window)
        self.db_name = "library.db"
        self.setup_database()
        
        # --- MODIFIED ---
        # The hardcoded user ID is removed and the passed one is used
        self.current_user_id = current_user_id 

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
            "Is book available?": self.show_book_availability_popup,
            "Issue book?": self.show_issue_book_popup,
            "Return book?": self.show_return_book_popup,
            "Pay Fine?": self.show_pay_fine_popup
        }

        for name, command in button_map.items():
            button = ttk.Button(transactions_frame, text=name, style='Action.TButton', command=command)
            button.pack(fill="x", pady=5)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", side="bottom")
        logout_button = ttk.Button(bottom_frame, text="Log Out", command=self.logout)
        logout_button.pack(side="right")
        
    def setup_database(self):
        # This function is correct and unchanged
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL,
                serial_no TEXT NOT NULL, issue_date TEXT NOT NULL, due_date TEXT NOT NULL,
                return_date TEXT, fine_paid REAL,
                FOREIGN KEY (user_id) REFERENCES Users(user_id),
                FOREIGN KEY (serial_no) REFERENCES Items(serial_no) ) ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL,
                serial_no TEXT NOT NULL, request_date TEXT NOT NULL, status TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users(user_id),
                FOREIGN KEY (serial_no) REFERENCES Items(serial_no) ) ''')
        conn.commit()
        conn.close()

    # --- All other functions (popups, database logic) are correct and unchanged ---
    # They will now use the correct `self.current_user_id`

    def show_book_availability_popup(self):
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
                self.show_issue_book_popup(book_details=item_details_dict)
            else:
                messagebox.showwarning("Not Available", "This item is not available for issue.", parent=results_popup)

        button_frame = ttk.Frame(popup_frame)
        button_frame.pack(pady=(20, 0))
        ttk.Button(button_frame, text="Cancel", command=results_popup.destroy).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Select to Issue", command=handle_issue_selection).pack(side="left", padx=10)

    def show_issue_book_popup(self, book_details=None):
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
            entries[text.replace("/", "_").replace(" ", "_").lower()] = entry
        
        if book_details:
            entries['serial_no'].insert(0, book_details['serial_no']); entries['serial_no'].config(state="readonly")
            entries['book_movie_name'].insert(0, book_details['name']); entries['book_movie_name'].config(state="readonly")
            entries['author_creator'].insert(0, book_details['creator']); entries['author_creator'].config(state="readonly")
        
        today = date.today()
        return_date = today + timedelta(days=15)
        entries['issue_date'].insert(0, today.strftime("%Y-%m-%d")); entries['issue_date'].config(state="readonly")
        entries['return_date'].insert(0, return_date.strftime("%Y-%m-%d")); entries['return_date'].config(state="readonly")
        entries['user_id'].insert(0, self.current_user_id); entries['user_id'].config(state="readonly")

        def handle_issue_confirmation():
            user_id = entries['user_id'].get()
            serial_no = entries['serial_no'].get()
            if not (user_id and serial_no):
                messagebox.showerror("Validation Error", "Item details are required.", parent=popup)
                return
            
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Requests (user_id, serial_no, request_date, status) VALUES (?, ?, ?, ?)", 
                               (user_id, serial_no, date.today().strftime("%Y-%m-%d"), 'pending'))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Your request has been submitted for admin approval.", parent=popup)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}", parent=popup)

        btn_frame = ttk.Frame(popup_frame)
        btn_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=(20, 0))
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Confirm Request", command=handle_issue_confirmation).pack(side="left", padx=10)

    def show_return_book_popup(self):
        popup = tk.Toplevel(self.window)
        popup.title("Return Book")
        popup.geometry("500x300")
        self.center_window(popup)
        popup.grab_set()

        popup_frame = ttk.Frame(popup, padding="20")
        popup_frame.pack(expand=True, fill="both")
        popup_frame.columnconfigure(1, weight=1)

        ttk.Label(popup_frame, text="Return Book", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT I.item_name, T.serial_no 
            FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no 
            WHERE T.user_id = ? AND T.return_date IS NULL
        """, (self.current_user_id,))
        issued_items = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()

        entries = {}
        def on_book_select(event):
            book_name = entries['book_movie_name'].get()
            serial_no = issued_items.get(book_name)
            if not serial_no: return
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT I.creator, T.issue_date, T.due_date 
                FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no 
                WHERE T.serial_no = ? AND T.user_id = ? AND T.return_date IS NULL
            """, (serial_no, self.current_user_id))
            result = cursor.fetchone()
            conn.close()

            if result:
                entries['serial_no'].config(state='normal'); entries['serial_no'].delete(0, tk.END); entries['serial_no'].insert(0, serial_no); entries['serial_no'].config(state='readonly')
                entries['author_creator'].config(state='normal'); entries['author_creator'].delete(0, tk.END); entries['author_creator'].insert(0, result[0]); entries['author_creator'].config(state='readonly')
                entries['issue_date'].config(state='normal'); entries['issue_date'].delete(0, tk.END); entries['issue_date'].insert(0, result[1]); entries['issue_date'].config(state='readonly')
                entries['due_date'].config(state='normal'); entries['due_date'].delete(0, tk.END); entries['due_date'].insert(0, result[2]); entries['due_date'].config(state='readonly')
        
        labels = ["Book/Movie Name", "Author/Creator", "Serial No", "Issue Date", "Due Date"]
        for i, text in enumerate(labels):
            ttk.Label(popup_frame, text=text).grid(row=i+1, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(popup_frame, state='readonly') if text != "Book/Movie Name" else ttk.Combobox(popup_frame, values=list(issued_items.keys()))
            entry.grid(row=i+1, column=1, sticky="ew", padx=5, pady=5)
            if text == "Book/Movie Name": entry.bind("<<ComboboxSelected>>", on_book_select)
            entries[text.replace("/", "_").replace(" ", "_").lower()] = entry

        def handle_return_confirmation():
            if not entries['serial_no'].get(): return
            
            due_date_str = entries['due_date'].get()
            due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            days_overdue = (date.today() - due_date_obj).days
            fine = max(0, days_overdue * 50)
            
            return_details = {
                "serial_no": entries['serial_no'].get(), "book_name": entries['book_movie_name'].get(),
                "author": entries['author_creator'].get(), "issue_date": entries['issue_date'].get(),
                "return_date": due_date_str, "actual_return_date": date.today().strftime("%Y-%m-%d"),
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
            # If called directly without details, fetch overdue items.
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            today_str = date.today().isoformat()
            cursor.execute("""
                SELECT T.serial_no, I.item_name, I.creator, T.issue_date, T.due_date
                FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no
                WHERE T.user_id = ? AND T.return_date IS NULL AND T.due_date < ?
            """, (self.current_user_id, today_str))
            overdue_item = cursor.fetchone()
            conn.close()

            if not overdue_item:
                messagebox.showinfo("No Fines", "You have no overdue items with pending fines.")
                return

            due_date_obj = datetime.strptime(overdue_item[4], "%Y-%m-%d").date()
            days_overdue = (date.today() - due_date_obj).days
            fine = max(0, days_overdue * 50)
            
            return_details = {
                "serial_no": overdue_item[0], "book_name": overdue_item[1], "author": overdue_item[2],
                "issue_date": overdue_item[3], "return_date": overdue_item[4],
                "actual_return_date": date.today().strftime("%Y-%m-%d"), "fine_calculated": f"{fine:.2f}"
            }

        popup = tk.Toplevel(self.window)
        popup.title("Pay Fine")
        popup.geometry("500x450")
        self.center_window(popup)
        popup.grab_set()

        popup_frame = ttk.Frame(popup, padding="20")
        popup_frame.pack(expand=True, fill="both")

        ttk.Label(popup_frame, text="Pay Fine", font=("Helvetica", 14, "bold")).pack(pady=(0,20))
        
        labels_and_keys = [
            ("Book Name", "book_name"), ("Author", "author"), ("Serial No", "serial_no"),
            ("Issue Date", "issue_date"), ("Return Date", "return_date"), 
            ("Actual Return Date", "actual_return_date"), ("Fine Calculated", "fine_calculated")
        ]
        
        for label_text, key in labels_and_keys:
            frame = ttk.Frame(popup_frame)
            frame.pack(fill="x", pady=2)
            ttk.Label(frame, text=f"{label_text}:", width=20).pack(side="left")
            entry = ttk.Entry(frame); entry.insert(0, return_details.get(key, "")); entry.config(state="readonly")
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
                """, (return_details['actual_return_date'], fine_amount, return_details['serial_no'], self.current_user_id))
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

    def go_home(self):
        # --- MODIFIED --- Correct path and passes user_id back
        dashboard_path = r"C:\Users\vedan\Desktop\LMS - Copy\user_dashboard.py"
        if not os.path.exists(dashboard_path):
            messagebox.showerror("Error", f"Could not find dashboard script at:\n{dashboard_path}")
            return
        try:
            subprocess.Popen([sys.executable, dashboard_path, self.current_user_id])
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

# --- MODIFIED ---
# This block now captures the user_id passed from the dashboard script
if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        root = tk.Tk()
        root.withdraw() 
        app = TransactionsPage(root, user_id)
        root.mainloop()
    else:
        messagebox.showerror("Authentication Error", "No User ID specified. Please launch from the dashboard.")