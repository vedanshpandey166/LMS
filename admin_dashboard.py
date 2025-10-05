import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import sys
import os

class AdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard")
        self.root.geometry("800x500")
        
        self.center_window(self.root)

        # Main frame to hold all widgets
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill="both")

        # --- 1. Top Menu Bar ---
        menu_frame = ttk.Frame(main_frame)
        menu_frame.pack(fill="x", pady=(0, 10))
        
        style = ttk.Style()
        style.configure('TopMenu.TButton', font=('Helvetica', 11, 'bold'), padding=(10, 5))

        # Updated maintenance button with command
        maintenance_button = ttk.Button(
            menu_frame, 
            text="Maintenance", 
            style='TopMenu.TButton', 
            command=self.open_maintenance_page
        )
        maintenance_button.pack(side="left", padx=5)
        
        # Updated reports button with command
        reports_button = ttk.Button(
            menu_frame, 
            text="Reports", 
            style='TopMenu.TButton',
            command=self.open_reports_page
        )
        reports_button.pack(side="left", padx=5)

        # Updated transactions button with command
        transactions_button = ttk.Button(
            menu_frame, 
            text="Transactions", 
            style='TopMenu.TButton',
            command=self.open_transactions_page
        )
        transactions_button.pack(side="left", padx=5)

        # --- 2. Product Details Section ---
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(expand=True, fill="both", pady=10)

        # Title for the table
        product_details_label = ttk.Label(details_frame, text="Product Details", font=("Helvetica", 14, "bold"))
        product_details_label.pack(pady=(0, 10))

        # --- Create the Treeview (Table) ---
        columns = ("code_from", "code_to", "category")
        self.tree = ttk.Treeview(details_frame, columns=columns, show="headings")
        
        # Define headings from your blueprint
        self.tree.heading("code_from", text="Code No From")
        self.tree.heading("code_to", text="Code No To")
        self.tree.heading("category", text="Category")
        
        # Configure column widths for better appearance
        self.tree.column("code_from", width=200, anchor='w')
        self.tree.column("code_to", width=200, anchor='w')
        self.tree.column("category", width=250, anchor='w')
        
        self.tree.pack(expand=True, fill='both')
        
        # --- Insert the static data from your image ---
        # NOTE: This data is for visual layout purposes only for now.
        product_data = [
            ("SC(B/M)000001", "SC(B/M)000004", "Science"),
            ("EC(B/M)000001", "EC(B/M)000004", "Economics"),
            ("FC(B/M)000001", "FC(B/M)000004", "Fiction"),
            ("CH(B/M)000001", "CH(B/M)000004", "Children"),
            ("PD(B/M)000001", "PD(B/M)000004", "Personal Development")
        ]
        
        for item in product_data:
            self.tree.insert("", "end", values=item)

        # --- 3. Bottom Log Out Button ---
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=(10, 0))

        logout_button = ttk.Button(bottom_frame, text="Log Out", command=self.logout)
        logout_button.pack(side="right")
        
    def open_maintenance_page(self):
        """Launches the admin maintenance script and closes the current window."""
        maintenance_path = r"C:\Users\vedan\Desktop\LMS\admin_maintainance.py"
        
        if not os.path.exists(maintenance_path):
            messagebox.showerror("Error", f"Could not find the maintenance script at:\n{maintenance_path}")
            return
            
        try:
            subprocess.Popen([sys.executable, maintenance_path])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open maintenance script:\n{e}")

    def open_reports_page(self):
        """Launches the admin reports script and closes the current window."""
        reports_path = r"C:\Users\vedan\Desktop\LMS\admin_reports.py"
        
        if not os.path.exists(reports_path):
            messagebox.showerror("Error", f"Could not find the reports script at:\n{reports_path}")
            return
            
        try:
            subprocess.Popen([sys.executable, reports_path])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open reports script:\n{e}")

    def open_transactions_page(self):
        """Launches the admin transactions script and closes the current window."""
        transactions_path = r"C:\Users\vedan\Desktop\LMS\admin_transaction.py"
        
        if not os.path.exists(transactions_path):
            messagebox.showerror("Error", f"Could not find the transactions script at:\n{transactions_path}")
            return
            
        try:
            subprocess.Popen([sys.executable, transactions_path])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open transactions script:\n{e}")

    def logout(self):
        """Displays a confirmation and closes the application."""
        if messagebox.askokcancel("Log Out", "Are you sure you want to log out?"):
            self.root.destroy()

    def center_window(self, window):
        """Helper function to center the window on the screen."""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')


# This part allows you to run this file directly to see the UI
if __name__ == "__main__":
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()

