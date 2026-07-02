import mysql.connector
import hashlib
import secrets
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Tuple, List

# ============================================================================
# MySQL Configuration
# ============================================================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",  # Your MySQL password
    "database": "hr_portal",
    "port": 3306
}

# ============================================================================
# Database Connection Helper
# ============================================================================
def get_db_connection():
    """Create and return a MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        if err.errno == 2003:
            print(f"❌ Error: Cannot connect to MySQL server at {DB_CONFIG['host']}")
            print("   Make sure MySQL is running and the credentials are correct.")
        else:
            print(f"❌ Database Error: {err}")
        sys.exit(1)


# ============================================================================
# Database Initialization
# ============================================================================
def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    c = conn.cursor()

    # Create users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            mobile_number VARCHAR(20),
            employee_id VARCHAR(100),
            is_active INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create tickets table
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            type VARCHAR(50) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            description LONGTEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'Pending Review',
            hr_notes LONGTEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # Create sessions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            username VARCHAR(255) PRIMARY KEY,
            token VARCHAR(255) NOT NULL,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    conn.commit()

    # Check if default HR user exists
    c.execute("SELECT username FROM users WHERE username=%s", ("hr@portal.com",))
    if not c.fetchone():
        hashed_pw = hashlib.sha256("hrpass123".encode()).hexdigest()
        c.execute("""
            INSERT INTO users
            (username, password, role, full_name, mobile_number, employee_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """, ("hr@portal.com", hashed_pw, "HR", "HR Administrator", "9999999999", "HR001"))
        conn.commit()
        print("✓ Default HR account created: hr@portal.com / hrpass123")

    c.close()
    conn.close()


# ============================================================================
# Authentication Functions
# ============================================================================
def make_hashes(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login(username: str, password: str) -> Optional[Tuple]:
    """Verify login credentials. Returns (role, full_name, is_active) or None."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT role, full_name, is_active
        FROM users
        WHERE username=%s AND password=%s
    """, (username, make_hashes(password)))
    row = c.fetchone()
    c.close()
    conn.close()
    return row


def register_user(username: str, password: str, full_name: str, 
                  mobile_number: str, employee_id: str) -> bool:
    """Register a new applicant user."""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO users
            (username, password, role, full_name, mobile_number, employee_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """, (username, make_hashes(password), "Applicant", full_name, mobile_number, employee_id))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry
            return False
        raise
    finally:
        c.close()
        conn.close()


def reset_password(username: str, employee_id: str, mobile_number: str, 
                   new_password: str) -> bool:
    """Reset user password with verification."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT username
        FROM users
        WHERE username=%s AND employee_id=%s AND mobile_number=%s AND is_active=1
    """, (username, employee_id, mobile_number))
    
    row = c.fetchone()
    if not row:
        c.close()
        conn.close()
        return False

    c.execute("UPDATE users SET password=%s WHERE username=%s", 
              (make_hashes(new_password), username))
    conn.commit()
    c.close()
    conn.close()
    return True


def is_user_active(username: str) -> bool:
    """Check if user is active."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT is_active FROM users WHERE username=%s", (username,))
    row = c.fetchone()
    c.close()
    conn.close()
    return bool(row[0]) if row else False


# ============================================================================
# Session Management
# ============================================================================
def create_session(username: str) -> str:
    """Create a session token for the user."""
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE username=%s", (username,))
    c.execute("""
        INSERT INTO sessions (username, token, expires_at) 
        VALUES (%s, %s, %s)
    """, (username, token, expires_at))
    conn.commit()
    c.close()
    conn.close()
    return token


def clear_session(username: str):
    """Clear session for logout."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE username=%s", (username,))
    conn.commit()
    c.close()
    conn.close()


# ============================================================================
# Ticket Management
# ============================================================================
def create_ticket(username: str, form_type: str, subject: str, description: str) -> int:
    """Create a new ticket."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO tickets
        (username, type, subject, description, status, hr_notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (username, form_type, subject, description, "Pending Review", "No response yet"))
    conn.commit()
    ticket_id = c.lastrowid
    c.close()
    conn.close()
    return ticket_id


def get_ticket_by_id(ticket_id: int) -> Optional[Tuple]:
    """Get ticket details by ID."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, username, type, subject, description, status, hr_notes, timestamp
        FROM tickets
        WHERE id=%s
    """, (ticket_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row


def update_ticket(ticket_id: int, status: str, notes: str):
    """Update ticket status and notes."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE tickets 
        SET status=%s, hr_notes=%s 
        WHERE id=%s
    """, (status, notes, ticket_id))
    conn.commit()
    c.close()
    conn.close()


def get_user_tickets(username: str) -> List[Tuple]:
    """Get all tickets for a specific user."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, timestamp, type, subject, description, status, hr_notes
        FROM tickets
        WHERE username=%s
        ORDER BY id DESC
    """, (username,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def get_all_tickets() -> List[Tuple]:
    """Get all tickets (for HR)."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, username, type, subject, status, timestamp
        FROM tickets
        ORDER BY id DESC
    """)
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


# ============================================================================
# User Management (HR Only)
# ============================================================================
def get_all_users() -> List[Tuple]:
    """Get all users (for HR)."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT username, full_name, employee_id, mobile_number, role, is_active
        FROM users
        ORDER BY username
    """)
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def set_user_active(username: str, active: bool):
    """Set user active/inactive status."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_active=%s WHERE username=%s", 
              (1 if active else 0, username))
    conn.commit()
    c.close()
    conn.close()


# ============================================================================
# CLI Menu Functions
# ============================================================================
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def applicant_menu(username: str, full_name: str):
    """Applicant dashboard menu."""
    while True:
        print_header(f"APPLICANT DASHBOARD - {full_name}")
        print("1. Submit New Feedback/Complaint")
        print("2. View My Submissions")
        print("3. Logout")
        print()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            clear_screen()
            print_header("Submit New Request")
            
            print("Form Categories:")
            print("  1. Feedback")
            print("  2. Complaint")
            print("  3. Suggestion")
            print()
            
            form_choice = input("Select category (1-3): ").strip()
            form_types = {"1": "Feedback", "2": "Complaint", "3": "Suggestion"}
            form_type = form_types.get(form_choice, "Feedback")
            
            subject = input("Subject Heading: ").strip()
            if not subject:
                print("❌ Subject cannot be empty.")
                input("Press Enter to continue...")
                continue
            
            description = input("Detailed Information (press Enter twice to finish):\n")
            if not description:
                print("❌ Description cannot be empty.")
                input("Press Enter to continue...")
                continue
            
            ticket_id = create_ticket(username, form_type, subject, description)
            print(f"\n✅ Form submitted successfully! Ticket ID: {ticket_id}")
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "2":
            clear_screen()
            print_header("Your Submission History")
            
            tickets = get_user_tickets(username)
            if not tickets:
                print("ℹ️  You haven't submitted any tickets yet.")
            else:
                for idx, (tid, timestamp, form_type, subject, desc, status, notes) in enumerate(tickets, 1):
                    print(f"\n{idx}. Ticket #{tid}")
                    print(f"   Submitted: {timestamp}")
                    print(f"   Type: {form_type}")
                    print(f"   Subject: {subject}")
                    print(f"   Status: {status}")
                    print(f"   HR Response: {notes if notes else 'Pending'}")
                    print("-" * 70)
            
            input("\nPress Enter to continue...")
            clear_screen()
        
        elif choice == "3":
            clear_session(username)
            print("✅ Logged out successfully.")
            return "logout"
        
        else:
            print("❌ Invalid choice. Please try again.")
            input("Press Enter to continue...")
            clear_screen()


def hr_menu(username: str, full_name: str):
    """HR dashboard menu."""
    while True:
        print_header(f"HR MANAGEMENT PANEL - {full_name}")
        print("1. Manage User Access")
        print("2. View & Update Tickets")
        print("3. Logout")
        print()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            clear_screen()
            print_header("Manage User Access")
            
            users = get_all_users()
            if not users:
                print("ℹ️  No users found.")
            else:
                for idx, (user, name, empid, mobile, role, is_active) in enumerate(users, 1):
                    status = "✓ Active" if is_active else "✗ Inactive"
                    print(f"{idx}. {user:30} {name:30} {role:15} {status}")
                
                print("\n" + "-" * 70)
                target_user = input("\nEnter username to toggle: ").strip().lower()
                
                # Find the user
                user_found = None
                for user, name, empid, mobile, role, is_active in users:
                    if user.lower() == target_user:
                        user_found = (user, is_active)
                        break
                
                if user_found:
                    new_status = "activate" if not user_found[1] else "deactivate"
                    confirm = input(f"\nConfirm to {new_status} {user_found[0]}? (yes/no): ").strip().lower()
                    if confirm == "yes":
                        set_user_active(user_found[0], not user_found[1])
                        print(f"✅ User {new_status.capitalize()}d successfully.")
                else:
                    print("❌ User not found.")
            
            input("\nPress Enter to continue...")
            clear_screen()
        
        elif choice == "2":
            clear_screen()
            print_header("Ticket Master List")
            
            tickets = get_all_tickets()
            if not tickets:
                print("ℹ️  No tickets submitted yet.")
            else:
                for idx, (tid, user, form_type, subject, status, timestamp) in enumerate(tickets, 1):
                    print(f"{idx}. Ticket #{tid} | {user:25} | {form_type:12} | {status:20} | {timestamp}")
                
                print("\n" + "-" * 70)
                ticket_id = input("\nEnter Ticket ID to review: ").strip()
                
                try:
                    ticket_id = int(ticket_id)
                    ticket = get_ticket_by_id(ticket_id)
                    
                    if ticket:
                        tid, user, form_type, subject, desc, status, notes, timestamp = ticket
                        clear_screen()
                        print_header(f"Review Ticket #{tid}")
                        
                        print(f"Submitted By: {user}")
                        print(f"Category: {form_type}")
                        print(f"Subject: {subject}")
                        print(f"Submitted On: {timestamp}")
                        print(f"Current Status: {status}")
                        print("\nApplicant's Message:")
                        print("-" * 70)
                        print(desc)
                        print("-" * 70)
                        
                        print("\nUpdate Ticket:")
                        print("  1. Pending Review")
                        print("  2. Action Taken")
                        print("  3. Resolved")
                        new_status_choice = input("\nSelect new status (1-3): ").strip()
                        status_map = {"1": "Pending Review", "2": "Action Taken", "3": "Resolved"}
                        new_status = status_map.get(new_status_choice, status)
                        
                        new_notes = input("\nAdd HR Response / Resolution Notes:\n")
                        
                        if new_notes:
                            update_ticket(ticket_id, new_status, new_notes)
                            print(f"\n✅ Ticket #{ticket_id} updated successfully.")
                        else:
                            print("⚠️  No changes made.")
                    else:
                        print("❌ Ticket not found.")
                except ValueError:
                    print("❌ Invalid ticket ID.")
            
            input("\nPress Enter to continue...")
            clear_screen()
        
        elif choice == "3":
            clear_session(username)
            print("✅ Logged out successfully.")
            return "logout"
        
        else:
            print("❌ Invalid choice. Please try again.")
            input("Press Enter to continue...")
            clear_screen()


def main():
    """Main application entry point."""
    clear_screen()
    init_db()
    
    while True:
        print_header("HR PORTAL - LOGIN")
        print("1. Login")
        print("2. Sign Up (New Applicants)")
        print("3. Forgot Password")
        print("4. Exit")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        clear_screen()
        
        if choice == "1":
            print_header("Login to Your Account")
            username = input("Email / Username: ").strip().lower()
            password = input("Password: ").strip()
            
            user_info = check_login(username, password)
            if user_info:
                role, full_name, is_active = user_info
                if not is_active:
                    print("❌ Your account is inactive. Contact HR.")
                    input("Press Enter to continue...")
                    clear_screen()
                    continue
                
                print(f"✅ Welcome, {full_name}!")
                input("Press Enter to continue...")
                clear_screen()
                
                if role == "Applicant":
                    result = applicant_menu(username, full_name)
                    if result == "logout":
                        input("Press Enter to continue...")
                        clear_screen()
                elif role == "HR":
                    result = hr_menu(username, full_name)
                    if result == "logout":
                        input("Press Enter to continue...")
                        clear_screen()
            else:
                print("❌ Incorrect username or password.")
                print("   Default HR: hr@portal.com / hrpass123")
                input("Press Enter to continue...")
                clear_screen()
        
        elif choice == "2":
            print_header("Create an Applicant Profile")
            full_name = input("Full Name: ").strip()
            username = input("Email Address (Username): ").strip().lower()
            mobile_number = input("Mobile Number: ").strip()
            employee_id = input("Employee ID: ").strip()
            password = input("Create Password: ").strip()
            
            if not all([full_name, username, mobile_number, employee_id, password]):
                print("❌ Please fill out all fields.")
            elif not mobile_number.isdigit() or len(mobile_number) != 10:
                print("❌ Mobile number must be exactly 10 digits.")
            else:
                if register_user(username, password, full_name, mobile_number, employee_id):
                    print("🎉 Account created successfully! Now log in from the Login tab.")
                else:
                    print("❌ An account with this email already exists.")
            
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "3":
            print_header("Reset Your Password")
            username = input("Username / Email: ").strip().lower()
            employee_id = input("Employee ID: ").strip()
            mobile_number = input("Mobile Number: ").strip()
            new_password = input("New Password: ").strip()
            confirm_password = input("Confirm New Password: ").strip()
            
            if not all([username, employee_id, mobile_number, new_password, confirm_password]):
                print("❌ Please fill out all fields.")
            elif new_password != confirm_password:
                print("❌ Passwords do not match.")
            else:
                if reset_password(username, employee_id, mobile_number, new_password):
                    print("✅ Password reset successfully. You can now log in.")
                else:
                    print("❌ Invalid details or inactive account.")
            
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "4":
            print("👋 Thank you for using HR Portal. Goodbye!")
            sys.exit(0)
        
        else:
            print("❌ Invalid choice. Please try again.")
            input("Press Enter to continue...")
            clear_screen()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application closed.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
