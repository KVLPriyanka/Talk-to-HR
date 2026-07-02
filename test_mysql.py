"""
MySQL Connection Tester and Configurator
Helps identify correct MySQL credentials
"""

import mysql.connector
from mysql.connector import Error
import sys

def test_connection(host, user, password, port=3306):
    """Test MySQL connection with given credentials."""
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        return True, f"✓ Connected! MySQL version: {version[0]}"
    except Error as err:
        if err.errno == 2003:
            return False, f"❌ Cannot reach MySQL server at {host}:{port}. Is it running?"
        elif err.errno == 1045:
            return False, f"❌ Access denied. Check username and password."
        elif err.errno == 1049:
            return False, f"❌ Database does not exist."
        else:
            return False, f"❌ Error: {err}"

def create_db_if_needed(host, user, password, port=3306):
    """Create database and tables."""
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS hr_portal")
        print("✓ Database 'hr_portal' created/verified")
        
        # Switch to database
        cursor.execute("USE hr_portal")
        
        # Create tables
        cursor.execute("""
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
        print("✓ Created 'users' table")
        
        cursor.execute("""
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
        print("✓ Created 'tickets' table")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                username VARCHAR(255) PRIMARY KEY,
                token VARCHAR(255) NOT NULL,
                expires_at DATETIME NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        print("✓ Created 'sessions' table")
        
        cursor.close()
        conn.close()
        return True, "Database setup completed"
    except Error as err:
        return False, f"Error creating database: {err}"

def main():
    print("="*70)
    print("  MySQL Connection Tester & Configurator")
    print("="*70)
    print()
    
    print("COMMON MYSQL CREDENTIALS TO TRY:")
    print("-" * 70)
    
    credentials = [
        ("localhost", "root", "", 3306),
        ("localhost", "root", "root", 3306),
        ("localhost", "root", "password", 3306),
        ("127.0.0.1", "root", "", 3306),
    ]
    
    successful_config = None
    
    for i, (host, user, pwd, port) in enumerate(credentials, 1):
        display_pwd = f"'{pwd}'" if pwd else "(empty)"
        print(f"\n{i}. Testing: host={host}, user={user}, password={display_pwd}")
        success, msg = test_connection(host, user, pwd, port)
        print(f"   {msg}")
        if success:
            successful_config = (host, user, pwd, port)
            break
    
    if not successful_config:
        print("\n" + "="*70)
        print("None of the common credentials worked.")
        print("="*70)
        print("\nPLEASE PROVIDE YOUR MYSQL CREDENTIALS MANUALLY:")
        print()
        
        host = input("MySQL Host [localhost]: ").strip() or "localhost"
        user = input("MySQL User [root]: ").strip() or "root"
        password = input("MySQL Password (press Enter for empty): ").strip()
        port_input = input("MySQL Port [3306]: ").strip()
        port = int(port_input) if port_input else 3306
        
        print(f"\nTesting connection with: {host}:{port} (user: {user})")
        success, msg = test_connection(host, user, password, port)
        print(msg)
        
        if success:
            successful_config = (host, user, password, port)
        else:
            print("\n❌ Failed to connect. Please check your MySQL installation and credentials.")
            sys.exit(1)
    
    if successful_config:
        print("\n" + "="*70)
        print("✅ CONNECTION SUCCESSFUL!")
        print("="*70)
        
        host, user, password, port = successful_config
        
        print(f"\nYour working configuration:")
        print(f"  Host: {host}")
        print(f"  User: {user}")
        print(f"  Password: {'(empty)' if not password else '(set)'}")
        print(f"  Port: {port}")
        
        # Update hr.py
        print("\nUpdating hr.py with your credentials...")
        
        with open("hr.py", "r") as f:
            content = f.read()
        
        # Find and replace DB_CONFIG
        old_config = f'''DB_CONFIG = {{
    "host": "localhost",
    "user": "root",
    "password": "",  # Change to your MySQL password
    "database": "hr_portal",
    "port": 3306
}}'''
        
        new_config = f'''DB_CONFIG = {{
    "host": "{host}",
    "user": "{user}",
    "password": "{password}",  # Your MySQL password
    "database": "hr_portal",
    "port": {port}
}}'''
        
        content = content.replace(old_config, new_config)
        
        with open("hr.py", "w") as f:
            f.write(content)
        
        print("✓ hr.py updated")
        
        # Create database and tables
        print("\nCreating database and tables...")
        success, msg = create_db_if_needed(host, user, password, port)
        print(msg)
        
        if success:
            print("\n" + "="*70)
            print("✅ ALL SETUP COMPLETE!")
            print("="*70)
            print("\nYou can now run: python hr.py")
        else:
            print(f"\n⚠️  {msg}")
            print("Try running again or check your permissions.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
