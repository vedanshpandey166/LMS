import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import sys
import os
import sqlite3
from datetime import date, datetime, timedelta

class ReportsPage:
    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(self.root)
        self.window.title("Administrator Reports")
        self.window.geometry("600x550")
        
        self.center_window(self.window)
        self.db_name = "library.db"

        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(expand=True, fill="both")

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x")

        home_button = ttk.Button(top_frame, text="Home", command=self.go_home)
        home_button.pack(side="right")

        reports_frame = ttk.Frame(main_frame)
        reports_frame.pack(expand=True, fill="both", pady=20)

        title_label = ttk.Label(reports_frame, text="Available Reports", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=(0, 20))

        style = ttk.Style()
        style.configure('Report.TButton', font=('Helvetica', 12), padding=10)
        
        report_buttons = {
            "Master List of Books": self.show_master_list_of_books,
            "Master List of Movies": self.show_master_list_of_movies,
            "Master List of Memberships": self.show_master_list_of_memberships,
            "Active Issues": self.show_active_issues,
            "Overdue returns": self.show_overdue_returns,
            "Pending Issue Requests": self.show_pending_issue_requests
        }

        for name, command in report_buttons.items():
            button = ttk.Button(reports_frame, text=name, style='Report.TButton', command=command)
            button.pack(fill="x", pady=4)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", side="bottom")
        logout_button = ttk.Button(bottom_frame, text="Log Out", command=self.logout)
        logout_button.pack(side="right")

    def show_pending_issue_requests(self):
        report_window = tk.Toplevel(self.window)
        report_window.title("Pending Issue Requests")
        report_window.geometry("900x400")
        self.center_window(report_window)
        report_window.grab_set()

        report_frame = ttk.Frame(report_window, padding="10")
        report_frame.pack(expand=True, fill="both")
        
        tree = self._create_treeview(report_frame,
            columns=("req_id", "user_id", "serial_no", "name", "req_date"),
            headings=("Request ID", "User ID", "Serial No.", "Item Name", "Requested Date"))
        
        def refresh_requests():
            for item in tree.get_children():
                tree.delete(item)
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT R.request_id, R.user_id, R.serial_no, I.item_name, R.request_date
                FROM Requests R JOIN Items I ON R.serial_no = I.serial_no
                WHERE R.status = 'pending'
            """)
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            conn.close()
        
        def handle_request(action):
            selected_item_id = tree.focus()
            if not selected_item_id:
                messagebox.showwarning("No Selection", "Please select a request to process.", parent=report_window)
                return
            
            item_details = tree.item(selected_item_id)['values']
            request_id, user_id, serial_no = item_details[0], item_details[1], item_details[2]

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            try:
                # This is inside the handle_request function in admin_reports.py

                if action == 'approve':
                    # --- TEMPORARY DEBUGGING CODE ---
                    # This block ONLY updates the request table.
                    today_str = date.today().strftime("%Y-%m-%d")
                    cursor.execute("""
                        UPDATE Requests 
                        SET status = 'approved', fulfilled_date = ? 
                        WHERE request_id = ?
                    """, (today_str, request_id))
                    
                    # This is a unique message so we know this code is running.
                    message = f"DEBUG: Request {request_id} was approved with date {today_str}."
                    
                else: # reject
                    cursor.execute("UPDATE Requests SET status = 'rejected' WHERE request_id = ?", (request_id,))
                    message = "Request rejected."
                
                conn.commit()
                messagebox.showinfo("Success", message, parent=report_window)
            except Exception as e:
                conn.rollback() # Rollback changes if an error occurs
                messagebox.showerror("Database Error", f"An error occurred: {e}", parent=report_window)
            finally:
                conn.close()
            
            refresh_requests()

        button_frame = ttk.Frame(report_frame)
        button_frame.pack(pady=10)
        approve_button = ttk.Button(button_frame, text="Approve Selected", command=lambda: handle_request('approve'))
        approve_button.pack(side="left", padx=10)
        reject_button = ttk.Button(button_frame, text="Reject Selected", command=lambda: handle_request('reject'))
        reject_button.pack(side="left", padx=10)

        refresh_requests()

    # --- Other functions are unchanged ---
    def show_master_list_of_books(self):
        report_window = tk.Toplevel(self.window); report_window.title("Master List of Books"); report_window.geometry("900x400"); self.center_window(report_window)
        tree = self._create_treeview(report_window, columns=("serial_no", "name", "author", "status", "procurement_date"), headings=("Serial No", "Name of Book", "Author Name", "Status", "Procurement Date"))
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor(); cursor.execute("SELECT serial_no, item_name, creator, status, procurement_date FROM Items WHERE item_type='Book'");
        for row in cursor.fetchall(): tree.insert("", "end", values=row)
        conn.close()

    def show_master_list_of_movies(self):
        report_window = tk.Toplevel(self.window); report_window.title("Master List of Movies"); report_window.geometry("900x400"); self.center_window(report_window)
        tree = self._create_treeview(report_window, columns=("serial_no", "name", "author", "status", "procurement_date"), headings=("Serial No", "Name of Movie", "Creator Name", "Status", "Procurement Date"))
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor(); cursor.execute("SELECT serial_no, item_name, creator, status, procurement_date FROM Items WHERE item_type='Movie'");
        for row in cursor.fetchall(): tree.insert("", "end", values=row)
        conn.close()

    def show_master_list_of_memberships(self):
        report_window = tk.Toplevel(self.window); report_window.title("Master List of All Memberships"); report_window.geometry("1100x400"); self.center_window(report_window)
        tree = self._create_treeview(report_window, columns=("mem_id", "user_id", "name", "contact_no", "start_date", "end_date", "status"), headings=("Membership ID", "User ID", "Name", "Contact No.", "Start Date", "End Date", "Status"))
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor(); cursor.execute("SELECT M.member_id, U.user_id, U.name, U.contact_no, M.start_date, M.end_date, U.status FROM Users U JOIN Memberships M ON U.user_id = U.user_id");
        for row in cursor.fetchall(): tree.insert("", "end", values=row)
        conn.close()

    def show_active_issues(self):
        report_window = tk.Toplevel(self.window); report_window.title("All Active Issues"); report_window.geometry("900x400"); self.center_window(report_window)
        tree = self._create_treeview(report_window, columns=("serial_no", "name", "user_id", "issue_date", "return_date"), headings=("Serial No.", "Name of Item", "User ID", "Date of Issue", "Due Date"))
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor(); cursor.execute("SELECT T.serial_no, I.item_name, T.user_id, T.issue_date, T.due_date FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no WHERE T.return_date IS NULL");
        for row in cursor.fetchall(): tree.insert("", "end", values=row)
        conn.close()

    def show_overdue_returns(self):
        report_window = tk.Toplevel(self.window); report_window.title("All Overdue Returns"); report_window.geometry("1000x400"); self.center_window(report_window)
        tree = self._create_treeview(report_window, columns=("serial_no", "name", "user_id", "issue_date", "return_date", "fine"), headings=("Serial No.", "Name of Item", "User ID", "Issue Date", "Due Date", "Fine"))
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor(); today_str = date.today().strftime("%Y-%m-%d")
        cursor.execute("SELECT T.serial_no, I.item_name, T.user_id, T.issue_date, T.due_date FROM Transactions T JOIN Items I ON T.serial_no = I.serial_no WHERE T.return_date IS NULL AND T.due_date < ?", (today_str,))
        for row in cursor.fetchall():
            due_date = datetime.strptime(row[4], "%Y-%m-%d").date()
            days_overdue = (date.today() - due_date).days
            fine = max(0, days_overdue * 50)
            tree.insert("", "end", values=(*row, f"Rs. {fine:.2f}"))
        conn.close()
    
    def _create_treeview(self, parent, columns, headings):
        report_frame = ttk.Frame(parent, padding="10"); report_frame.pack(expand=True, fill="both")
        tree = ttk.Treeview(report_frame, columns=columns, show="headings")
        for col, head in zip(columns, headings):
            tree.heading(col, text=head); tree.column(col, anchor='w', width=120)
        tree.pack(expand=True, fill='both')
        return tree

    def go_home(self):
        dashboard_path = r"C:\Users\vedan\Desktop\LMS - Copy\admin_dashboard.py" 
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
        window.update_idletasks(); width = window.winfo_width(); height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2); y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    app = ReportsPage(root)
    root.mainloop()