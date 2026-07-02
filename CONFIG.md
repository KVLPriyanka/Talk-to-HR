HR PORTAL - MySQL CLI Setup Guide
===================================

CHANGES MADE:
✓ Removed all Streamlit dependencies
✓ Replaced SQLite with MySQL (mysql-connector-python)
✓ Created CLI-based menu interface
✓ Updated requirements.txt

MYSQL CONNECTION CONFIGURATION:
File: hr.py (Lines 12-18)

DB_CONFIG = {
    "host": "localhost",        # Change if MySQL is on a different server
    "user": "root",             # Change to your MySQL username
    "password": "",             # Add your MySQL password here
    "database": "hr_portal",    # Database name (created automatically)
    "port": 3306                # Default MySQL port
}

SETUP STEPS:
============

1. Install Dependencies:
   pip install -r requirements.txt

2. Set Up MySQL Database:
   python setup_mysql.py
   (This creates the database and default tables)

3. Configure Connection (if needed):
   - Edit hr.py and modify DB_CONFIG with your MySQL credentials
   - Default assumes: localhost, root user, no password

4. Run the Application:
   python hr.py

DEFAULT CREDENTIALS:
===================
HR Account:
   Email: hr@portal.com
   Password: hrpass123

FEATURES:
=========
✓ Login/Registration
✓ Password Reset
✓ Applicant Dashboard (Submit & View Tickets)
✓ HR Dashboard (Manage Users & Tickets)
✓ Session Management
✓ User Active/Inactive Toggle

CLI INTERFACE:
==============
Main Menu:
  1. Login
  2. Sign Up (New Applicants)
  3. Forgot Password
  4. Exit

Applicant Menu:
  1. Submit New Feedback/Complaint
  2. View My Submissions
  3. Logout

HR Menu:
  1. Manage User Access
  2. View & Update Tickets
  3. Logout

TROUBLESHOOTING:
================
❌ "Cannot connect to MySQL server"
   → Ensure MySQL is installed and running
   → Check host, user, password in DB_CONFIG

❌ "Database does not exist"
   → Run: python setup_mysql.py

❌ "Access denied for user"
   → Update MySQL password in DB_CONFIG
   → Ensure MySQL user exists

QUICK MYSQL SETUP (Windows):
=============================
1. Install MySQL: https://dev.mysql.com/downloads/mysql/
2. Start MySQL: net start MySQL80 (or your version)
3. Connect: mysql -u root -p
4. Run setup_mysql.py

FILES INCLUDED:
===============
- hr.py              → Main application (MySQL + CLI)
- setup_mysql.py     → Database initialization script
- requirements.txt   → Python dependencies
