import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os
import subprocess
from datetime import date

# --- Configuration ---
DB_PATH = "library.db" 

class ReportsPage:
    def __init__(self, root, current_user_id):
        self.root = root
        self.user_id = current_user_id
        self.root.title(f"User Reports - {self.user_id}")
        self.root.geometry("450x450")
        self.center_window(self.root)
        self.root.resizable(False, False)

        # Style configuration
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('Report.TButton', font=('Helvetica', 12), padding=(10, 10))
        style.configure('Logout.TButton', font=('Helvetica', 10, 'bold'))
        style.configure('Home.TButton', font=('Helvetica', 10))

        main_frame = ttk.Frame(self.root, padding="20 20 20 10", style='TFrame')
        main_frame.pack(expand=True, fill="both")
        
        top_bar_frame = ttk.Frame(main_frame, style='TFrame')
        top_bar_frame.pack(fill='x', pady=(0, 20))

        title_label = ttk.Label(top_bar_frame, text="Available Reports", font=("Helvetica", 20, "bold"))
        title_label.pack(side="left")

        home_button = ttk.Button(
            top_bar_frame, 
            text="Home", 
            command=self.go_to_dashboard, 
            style='Home.TButton'
        )
        home_button.pack(side="right")

        reports_frame = ttk.Frame(main_frame, style='TFrame')
        reports_frame.pack(expand=True, fill="x")

        report_options = {
            "My Active Issues": self.show_active_issues,
            "My Overdue Returns": self.show_overdue_returns,
            "My Issue Requests": self.show_pending_requests,
            "My Membership Details": self.show_master_memberships,
            "Master List of Books": self.show_master_books,
            "Master List of Movies": self.show_master_movies,
        }
        
        for text, command in report_options.items():
            button = ttk.Button(reports_frame, text=text, command=command, style='Report.TButton')
            button.pack(fill='x', pady=4)

        bottom_frame = ttk.Frame(main_frame, style='TFrame', padding="0 10 0 0")
        bottom_frame.pack(fill="x", side="bottom")
        logout_button = ttk.Button(bottom_frame, text="Log Out", command=self.log_out, style='Logout.TButton')
        logout_button.pack(side="right")

    def go_to_dashboard(self):
        dashboard_path = r"C:\Users\vedan\Desktop\LMS - Copy\user_dashboard.py"
        if not os.path.exists(dashboard_path):
            messagebox.showerror("Error", f"Could not find the dashboard script at:\n{dashboard_path}")
            return
            
        try:
            command = [sys.executable, dashboard_path, self.user_id]
            subprocess.Popen(command)
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open dashboard script:\n{e}")

    def _display_report(self, title, columns, query, params=(), window_size="1000x400"):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query, params)
            data = cursor.fetchall()
            conn.close()

            if not data:
                messagebox.showinfo("No Records Found", f"You have no records to display for '{title}'.")
                return

            report_win = tk.Toplevel(self.root)
            report_win.title(title)
            report_win.geometry(window_size)
            self.center_window(report_win)

            tree = ttk.Treeview(report_win, columns=list(columns.keys()), show="headings")
            tree.pack(expand=True, fill='both', padx=10, pady=10)

            for col_id, (col_text, col_width) in columns.items():
                tree.heading(col_id, text=col_text)
                tree.column(col_id, width=col_width, anchor='w')
            
            for row in data:
                tree.insert("", "end", values=row)

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}\n\nPlease check your database schema.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def show_master_memberships(self):
        columns = { "mid": ("Membership Id", 120), "name": ("Name of Member", 150), "contact": ("Contact Number", 120), "address": ("Contact Address", 200), "aadhar": ("Aadhar Card No", 120), "start": ("Start Date", 120), "end": ("End Date", 120), "status": ("Status", 100), "fine": ("Amount Pending(Fine)", 120) }
        query = "SELECT M.member_id, U.name, U.contact_no, U.contact_address, U.aadhaar_card_no, M.start_date, M.end_date, U.status, 'N/A' as pending_fine FROM Memberships M JOIN Users U ON M.user_id = U.user_id WHERE M.user_id = ?"
        self._display_report("My Membership Details", columns, query, params=(self.user_id,), window_size="1200x400")

    def show_active_issues(self):
        columns = { "serial": ("Serial No Book/Movie", 150), "name": ("Name of Book/Movie", 250), "mid": ("Membership Id", 150), "issue": ("Date of Issue", 120), "due": ("Date of return", 120) }
        query = "SELECT T.serial_no, I.item_name, M.member_id, T.issue_date, T.due_date FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no JOIN Memberships M ON T.user_id = M.user_id WHERE (T.return_date IS NULL OR T.return_date = '') AND T.user_id = ?"
        self._display_report("My Active Issues", columns, query, params=(self.user_id,))

    def show_overdue_returns(self):
        columns = { "serial": ("Serial No Book", 150), "name": ("Name of Book", 250), "mid": ("Membership Id", 150), "issue": ("Date of Issue", 120), "due": ("Date of return", 120), "fine": ("Fine Calculations", 120) }
        today_str = date.today().isoformat()
        query = f"SELECT T.serial_no, I.item_name, M.member_id, T.issue_date, T.due_date, CAST((julianday('{today_str}') - julianday(T.due_date)) * 5 AS INTEGER) AS fine FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no JOIN Memberships M ON T.user_id = M.user_id WHERE (T.return_date IS NULL OR T.return_date = '') AND T.due_date < ? AND T.user_id = ?"
        self._display_report("My Overdue Returns", columns, query, params=(today_str, self.user_id))

    def show_pending_requests(self):
        """
        Shows approved requests and the date they were fulfilled by an admin.
        """
        columns = { "mid": ("Membership Id", 150), "name": ("Name of Book/Movie", 250), "req_date": ("Requested Date", 150), "ful_date": ("Request Fulfilled Date", 150) }
        
        # --- UPDATED ---
        # This query now selects the actual 'fulfilled_date' from the Requests table.
        # It will display the date set by the admin upon approval.
        query = """
            SELECT M.member_id, I.item_name, R.request_date, R.fulfilled_date
            FROM Requests R
            JOIN Items I ON R.serial_no = I.serial_no
            JOIN Memberships M ON R.user_id = M.user_id
            WHERE R.status = 'approved' AND R.user_id = ?
        """
        self._display_report("My Issue Requests", columns, query, params=(self.user_id,))

    def show_master_books(self):
        columns = { "serial": ("Serial No", 80), "name": ("Name of Book", 250), "author": ("Author Name", 180), "category": ("Category", 120), "status": ("Status", 100), "cost": ("Cost", 80), "proc_date": ("Procurement Date", 120) }
        query = "SELECT serial_no, item_name, creator, 'N/A', status, 'N/A', procurement_date FROM Items WHERE item_type = 'Book'"
        self._display_report("Master List of Books", columns, query)

    def show_master_movies(self):
        columns = { "serial": ("Serial No", 80), "name": ("Name of Movie", 250), "director": ("Director Name", 180), "category": ("Category", 120), "status": ("Status", 100), "cost": ("Cost", 80), "proc_date": ("Procurement Date", 120) }
        query = "SELECT serial_no, item_name, creator, 'N/A', status, 'N/A', procurement_date FROM Items WHERE item_type = 'Movie'"
        self._display_report("Master List of Movies", columns, query)
        
    def log_out(self):
        self.root.destroy()

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        current_user_id = sys.argv[1]
        root = tk.Tk()
        app = ReportsPage(root, current_user_id)
        root.mainloop()
    else:
        messagebox.showerror("Authentication Error", "No user ID provided. Please log in to access this page.")