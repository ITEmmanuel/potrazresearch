#!/usr/bin/env python3
"""
MySQL Setup Script for POTPLAG Application
This script helps set up the MySQL database and user for the potplag application
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def run_mysql_command(command, password, user="root", host="localhost"):
    """Run a MySQL command using the mysql CLI"""
    mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    
    # Build the mysql command
    cmd = [
        mysql_path,
        f"-u{user}",
        f"-p{password}",
        f"-h{host}",
        "-e", command
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def create_database_and_user(root_password):
    """Create the potplag database and user"""
    
    print("Creating potplag database...")
    
    # Create database
    success, output = run_mysql_command(
        "CREATE DATABASE IF NOT EXISTS potplag CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        root_password
    )
    
    if not success:
        print(f"❌ Error creating database: {output}")
        return False
        
    print("✅ Database 'potplag' created successfully")
    
    # Create user (you can change the password here)
    potplag_password = "potplag_secure_password_123"
    
    success, output = run_mysql_command(
        f"CREATE USER IF NOT EXISTS 'potplag'@'localhost' IDENTIFIED BY '{potplag_password}';",
        root_password
    )
    
    if not success:
        print(f"❌ Error creating user: {output}")
        return False
        
    print("✅ User 'potplag' created successfully")
    
    # Grant privileges
    success, output = run_mysql_command(
        "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX ON potplag.* TO 'potplag'@'localhost';",
        root_password
    )
    
    if not success:
        print(f"❌ Error granting privileges: {output}")
        return False
        
    print("✅ Privileges granted successfully")
    
    # Flush privileges
    success, output = run_mysql_command("FLUSH PRIVILEGES;", root_password)
    
    if not success:
        print(f"❌ Error flushing privileges: {output}")
        return False
        
    print("✅ Privileges flushed successfully")
    
    return potplag_password

def create_env_file(potplag_password):
    """Create a .env file with MySQL configuration"""
    
    env_content = f"""# MySQL Configuration for POTPLAG
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=potplag
MYSQL_PASSWORD={potplag_password}
MYSQL_DATABASE=potplag

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_ENV=development

# Admin Configuration
ADMIN_EMAIL=admin@potplag.com
ADMIN_PASSWORD=admin123
"""
    
    env_file_path = Path(".env")
    with open(env_file_path, "w") as f:
        f.write(env_content)
    
    print(f"✅ Created .env file at {env_file_path.absolute()}")
    return str(env_file_path.absolute())

def set_environment_variables(potplag_password):
    """Set environment variables for the current session"""
    
    os.environ['MYSQL_HOST'] = 'localhost'
    os.environ['MYSQL_PORT'] = '3306'
    os.environ['MYSQL_USER'] = 'potplag'
    os.environ['MYSQL_PASSWORD'] = potplag_password
    os.environ['MYSQL_DATABASE'] = 'potplag'
    
    print("✅ Environment variables set for current session")

def test_connection(potplag_password):
    """Test the connection with the new user"""
    
    success, output = run_mysql_command(
        "SELECT 'Connection successful!' as status;",
        potplag_password,
        user="potplag"
    )
    
    if success:
        print("✅ MySQL connection test successful!")
        return True
    else:
        print(f"❌ MySQL connection test failed: {output}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 POTPLAG MySQL Setup")
    print("=" * 50)
    
    # Get MySQL root password
    print("\nPlease enter your MySQL root password:")
    root_password = getpass.getpass("Root password: ")
    
    if not root_password:
        print("❌ Password cannot be empty!")
        sys.exit(1)
    
    # Test root connection first
    print("\n📡 Testing root connection...")
    success, output = run_mysql_command("SELECT 'Root connection successful!' as status;", root_password)
    
    if not success:
        print(f"❌ Failed to connect as root: {output}")
        print("Please check your MySQL root password and try again.")
        sys.exit(1)
    
    print("✅ Root connection successful!")
    
    # Create database and user
    print("\n🗃️ Setting up database and user...")
    potplag_password = create_database_and_user(root_password)
    
    if not potplag_password:
        print("❌ Failed to set up database and user!")
        sys.exit(1)
    
    # Create .env file
    print("\n📝 Creating environment configuration...")
    env_file = create_env_file(potplag_password)
    
    # Set environment variables
    set_environment_variables(potplag_password)
    
    # Test connection with new user
    print("\n🔗 Testing potplag user connection...")
    if not test_connection(potplag_password):
        sys.exit(1)
    
    print("\n🎉 MySQL setup completed successfully!")
    print("\n📋 Configuration Summary:")
    print(f"   Database: potplag")
    print(f"   User: potplag")
    print(f"   Password: {potplag_password}")
    print(f"   Host: localhost")
    print(f"   Port: 3306")
    print(f"   Environment file: {env_file}")
    
    print("\n⚠️  IMPORTANT SECURITY NOTE:")
    print("   - The database password is stored in the .env file")
    print("   - Make sure to add .env to your .gitignore file")
    print("   - Change the default admin password in production")
    
    print("\n🚀 Next steps:")
    print("   1. Run: python app.py")
    print("   2. Visit: http://localhost:5000")
    print("   3. Login with admin@potplag.com / admin123")

if __name__ == "__main__":
    main()
