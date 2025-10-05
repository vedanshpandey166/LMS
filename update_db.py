import sqlite3
import os

# This script will add the 'fulfilled_date' column to your 'Requests' table.

DB_PATH = "library.db"

def update_schema():
    """Connects to the database and adds the required column."""

    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found.")
        print("Please make sure this script is in the same folder as your database.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # This command adds the new column to the Requests table
        cursor.execute("ALTER TABLE Requests ADD COLUMN fulfilled_date TEXT")

        conn.commit()
        conn.close()

        print("✅ Success! The 'fulfilled_date' column has been added to the Requests table.")
        print("You can now delete this script ('update_db.py').")

    except sqlite3.OperationalError as e:
        # This will catch the error if the column already exists
        if "duplicate column name" in str(e):
            print("✅ The 'fulfilled_date' column already exists. No changes were needed.")
        else:
            print(f"An unexpected database error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_schema()