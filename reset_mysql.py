"""
MySQDB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",  # Changed from "" to "root"
    "database": "hr_portal",
    "port": 3306
}L Root Password Reset Script
For Windows with MySQL 5.7+
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def find_mysql_path():
    """Find MySQL installation path."""
    common_paths = [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin",
        r"C:\Program Files\MySQL\MySQL Server 5.7\bin",
        r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin",
        r"C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin",
    ]
    
    for path in common_paths:
        if Path(path).exists():
            return path
    
    return None

def reset_password():
    """Reset MySQL root password to 'root'."""
    
    print("="*70)
    print("  MySQL Root Password Reset")
    print("="*70)
    print()
    
    # Find MySQL path
    mysql_path = find_mysql_path()
    if not mysql_path:
        print("❌ Could not find MySQL installation")
        print("Common locations:")
        print("  - C:\\Program Files\\MySQL\\MySQL Server X.X\\bin")
        return False
    
    print(f"✓ Found MySQL at: {mysql_path}")
    print()
    
    # Step 1: Stop MySQL service
    print("Step 1: Stopping MySQL service...")
    try:
        result = subprocess.run(["net", "stop", "MySQL97"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ MySQL service stopped")
        else:
            print("⚠️  Service might already be stopped or different version")
    except Exception as e:
        print(f"⚠️  Could not stop service: {e}")
    
    time.sleep(2)
    
    # Step 2: Start MySQL with skip-grant-tables
    print("\nStep 2: Starting MySQL with --skip-grant-tables...")
    print("  (A window may open - let it run in background)")
    print()
    
    mysqld_path = os.path.join(mysql_path, "mysqld.exe")
    
    try:
        # Start mysqld with skip-grant-tables in background
        subprocess.Popen(
            [mysqld_path, "--skip-grant-tables"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✓ MySQL started with --skip-grant-tables")
        time.sleep(3)
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 3: Connect and reset password
    print("\nStep 3: Connecting and resetting password...")
    
    mysql_path_bin = os.path.join(mysql_path, "mysql.exe")
    
    # Create SQL commands
    sql_commands = """
    FLUSH PRIVILEGES;
    ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
    EXIT;
    """
    
    try:
        # Execute reset command
        process = subprocess.Popen(
            [mysql_path_bin, "-u", "root"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=sql_commands, timeout=5)
        
        if process.returncode == 0 or "ERROR" not in stderr:
            print("✓ Password reset successfully to: root")
        else:
            print(f"⚠️  {stderr}")
    except subprocess.TimeoutExpired:
        process.kill()
        print("✓ Command executed (timeout)")
    except FileNotFoundError:
        print(f"❌ mysql.exe not found at {mysql_path_bin}")
        return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    # Step 4: Stop and restart MySQL
    print("\nStep 4: Restarting MySQL service...")
    
    try:
        subprocess.run(["taskkill", "/IM", "mysqld.exe", "/F"], capture_output=True)
        time.sleep(2)
        
        result = subprocess.run(["net", "start", "MySQL97"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ MySQL service restarted")
        else:
            print("⚠️  Manual restart may be needed")
    except Exception as e:
        print(f"⚠️  {e}")
    
    time.sleep(2)
    
    # Step 5: Verify
    print("\nStep 5: Verifying new password...")
    
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"✓ Connection successful! MySQL version: {version[0]}")
        return True
    except Exception as e:
        print(f"❌ Could not verify: {e}")
        return False

def main():
    """Main function."""
    try:
        # Check if running as admin
        result = subprocess.run(["net", "session"], capture_output=True)
        if result.returncode != 0:
            print("⚠️  This script requires Administrator privileges!")
            print("Please run: Start > Command Prompt > Run as Administrator")
            print("Then run: python reset_mysql.py")
            sys.exit(1)
        
        success = reset_password()
        
        if success:
            print("\n" + "="*70)
            print("✅ PASSWORD RESET COMPLETE!")
            print("="*70)
            print("\nNew MySQL Credentials:")
            print("  Host: localhost")
            print("  User: root")
            print("  Password: root")
            print("\nUpdate hr.py with these credentials:")
            print("  1. Edit hr.py")
            print("  2. Change DB_CONFIG password from '' to 'root'")
            print("  3. Run: python hr.py")
        else:
            print("\n" + "="*70)
            print("❌ PASSWORD RESET FAILED")
            print("="*70)
            print("\nTry these alternatives:")
            print("1. Run Command Prompt as Administrator")
            print("2. Execute manually:")
            print("   cd C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin")
            print("   mysqld --skip-grant-tables")
            print("\n3. In another Admin Command Prompt:")
            print("   mysql -u root")
            print("   FLUSH PRIVILEGES;")
            print("   ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';")
            print("   EXIT;")
    
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
