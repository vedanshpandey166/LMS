import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class UserDashboard:
    # --- MODIFIED ---
    # The constructor now accepts and stores the user_id
    def __init__(self, root, current_user_id):
        self.root = root
        self.user_id = current_user_id  # Store the logged-in user's ID
        self.root.title(f"User Dashboard - Welcome {self.user_id}")
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

        reports_button = ttk.Button(
            menu_frame, 
            text="Reports", 
            style='TopMenu.TButton',
            command=self.open_reports_page
        )
        reports_button.pack(side="left", padx=5)

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

        product_details_label = ttk.Label(details_frame, text="Product Details", font=("Helvetica", 14, "bold"))
        product_details_label.pack(pady=(0, 10))

        columns = ("code_from", "code_to", "category")
        self.tree = ttk.Treeview(details_frame, columns=columns, show="headings")
        
        self.tree.heading("code_from", text="Code No From")
        self.tree.heading("code_to", text="Code No To")
        self.tree.heading("category", text="Category")
        
        self.tree.column("code_from", width=200, anchor='w')
        self.tree.column("code_to", width=200, anchor='w')
        self.tree.column("category", width=250, anchor='w')
        
        self.tree.pack(expand=True, fill='both')
        
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

        # Added command to the logout button
        logout_button = ttk.Button(bottom_frame, text="Log Out", command=self.root.destroy)
        logout_button.pack(side="right")
        
    def open_reports_page(self):
        """Launches the user reports script, PASSING THE USER ID."""
        reports_path = r"C:\Users\vedan\Desktop\LMS - Copy\user_reports.py"
        
        if not os.path.exists(reports_path):
            messagebox.showerror("Error", f"Could not find the reports script at:\n{reports_path}")
            return
            
        try:
            # --- MODIFIED ---
            # Pass the stored user_id to the reports script
            command = [sys.executable, reports_path, self.user_id]
            subprocess.Popen(command)
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open reports script:\n{e}")

    def open_transactions_page(self):
        """Launches the user transaction script, PASSING THE USER ID."""
        transactions_path = r"C:\Users\vedan\Desktop\LMS - COPY\user_transaction.py"
        
        if not os.path.exists(transactions_path):
            messagebox.showerror("Error", f"Could not find the transaction script at:\n{transactions_path}")
            return
            
        try:
            # --- MODIFIED ---
            # Pass the stored user_id to the transaction script as well
            command = [sys.executable, transactions_path, self.user_id]
            subprocess.Popen(command)
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to open transaction script:\n{e}")

    def center_window(self, window):
        """Helper function to center the window on the screen."""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')


# --- MODIFIED ---
# This block now captures the user_id passed from the login script
if __name__ == "__main__":
    if len(sys.argv) > 1:
        current_user_id = sys.argv[1]
        root = tk.Tk()
        app = UserDashboard(root, current_user_id)
        root.mainloop()
    else:
        # Fallback for running the file directly without logging in
        messagebox.showerror("Authentication Error", "No user ID provided. Please run from the login page.")