"""
MySQL Database Setup Script for HR Portal
Run this script before starting the application to set up the database.
"""

import mysql.connector
from mysql.connector import Error

def setup_mysql():
    """Create the MySQL database if it doesn't exist."""
    
    # Configuration for MySQL root connection
    config = {
        "host": "localhost",
        "user": "root",
        "password": "",  # Change this to your MySQL root password if you have one
        "port": 3306
    }
    
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("✓ Connected to MySQL server")
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS hr_portal")
        print("✓ Database 'hr_portal' created/verified")
        
        # Select the database
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
        
        conn.commit()
        print("\n✅ Database setup completed successfully!")
        print("\nDefault HR Account:")
        print("   Username: hr@portal.com")
        print("   Password: hrpass123")
        print("\nNext steps:")
        print("1. Update the DB_CONFIG in hr.py if your MySQL credentials differ")
        print("2. Run: python hr.py")
        
        cursor.close()
        conn.close()
        
    except Error as err:
        if err.errno == 2003:
            print("❌ Error: Cannot connect to MySQL server")
            print("   Make sure MySQL is installed and running")
            print("   Default MySQL: localhost:3306")
        elif err.errno == 1045:
            print("❌ Error: Access denied")
            print("   Check your MySQL username and password")
        else:
            print(f"❌ Error: {err}")
        return False
    
    return True


if __name__ == "__main__":
    print("="*70)
    print("  HR Portal - MySQL Database Setup")
    print("="*70)
    print()
    
    # Check if user wants to proceed with default credentials
    response = input("Do you want to proceed with setup? (yes/no): ").strip().lower()
    if response == "yes":
        setup_mysql()
    elif response == "no":
        print("Setup cancelled.")
    else:
        print("Invalid response. Setup cancelled.")
