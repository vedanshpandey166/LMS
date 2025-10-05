Library Management System (LMS)
A desktop-based application built with Python's Tkinter GUI toolkit and SQLite for managing a library's collection of books and movies, memberships, and transactions. The system features separate interfaces and functionalities for administrators and regular users.

Features
This application is divided into two main roles, each with a distinct set of features:

👤 Admin Features
Secure Login: Separate login for the administrator.

Comprehensive Reports: Access to master lists and system-wide reports:

Master List of all Books & Movies

Master List of all Memberships

View all Active Issues across the library

Track all Overdue Returns and calculate fines

Request Management: View and process all pending issue requests from users with the ability to Approve or Reject them. Approving a request automatically creates a transaction and updates the item's status.

👥 User Features
Secure Login: Individual user accounts with password protection.

Personalized Dashboard: A central hub for users to access library functions.

Item Availability: Check if a specific book or movie is available for borrowing.

Issue & Return:

Request to issue an available item. The request is sent to an admin for approval.

Return a borrowed item and handle any associated fines.

Personalized Reports: View reports filtered to show only their own activity:

My Active Issues

My Overdue Returns

My Approved Issue Requests (shows the date the admin fulfilled the request)

My Membership Details

Technology Stack
Language: Python

GUI Toolkit: Tkinter (Python's standard library)

Database: SQLite 3

Setup and Installation
Follow these steps to get the application running on your local machine.

1. Prerequisites
Python 3.x installed on your system.

2. Clone the Repository
Clone this repository to your local machine:

git clone https://github.com/vedanshpandey166/LMS.git

cd LMS

3. ⚠️ Important: Update File Paths
This is the most critical step. The Python scripts currently use hardcoded absolute file paths to navigate between different windows (e.g., from the login screen to the dashboard). You must update these paths to match the location where you cloned the repository on your system.

Example:
The original path in the code is C:\Users\vedan\Desktop\LMS - Copy\some_script.py. You need to find and replace all instances of this path with the correct path on your machine.

Look for and update the hardcoded paths in the following files:

login.py (in the open_dashboard function)

user_dashboard.py (in open_reports_page and open_transactions_page)

user_reports.py (in the go_to_dashboard function)

admin_reports.py (in the go_home function)

user_transaction.py (in the go_home function)

4. Database Setup
The library.db file is included in the repository. The application will use this file automatically. The first time you run the login.py script, it will ensure the necessary tables exist and create a default admin user if one isn't present.

Important: Before running the main application for the first time, you must update the database schema to support all features. Run the included update_db.py script from your terminal:

python update_db.py

This script adds the fulfilled_date column to the Requests table, which is essential for the admin approval workflow. It is safe to run multiple times but only needs to be run once.

5. Run the Application
The entry point for the application is the login.py script. To start the LMS, run the following command from your terminal in the project's root directory:

python login.py

How to Use
Admin Login
User ID: admin

Password: admin

User Login
Users are created and managed within the database. They can log in using the user_id and password stored in the Users table.

Basic Workflow
A user logs in and navigates to the Transactions page.

The user checks for a book's availability and submits an issue request.

The admin logs in and navigates to the Reports -> Pending Issue Requests page.

The admin selects the user's request and clicks Approve. This creates an official transaction and sets the fulfilled_date.

The user can now log back in and see the approved request with the fulfillment date in their Reports -> My Issue Requests section.

File Structure
login.py: Handles authentication for both admins and users. The main entry point.

admin_dashboard.py: The main dashboard for the administrator.

admin_reports.py: Displays all system-wide reports and handles the approval/rejection of user requests.

user_dashboard.py: The main dashboard for a logged-in user.

user_reports.py: Displays personalized reports for the logged-in user.

user_transaction.py: Handles user-facing transactions like checking availability, issuing requests, and returning items.

library.db: The SQLite database file containing all the application data.

update_db.py: A one-time script to update the database schema.

Future Improvements
[ ] Refactor Paths: Remove hardcoded absolute paths and use relative paths for better portability.

[ ] Admin CRUD: Add UI functionality for the admin to Create, Read, Update, and Delete users, books, and movies directly from the dashboard.

[ ] Password Hashing: Implement password hashing (e.g., with Werkzeug or hashlib) instead of storing plain text passwords for improved security.

[ ] UI/UX Enhancements: Improve the visual design and user experience of the application.
