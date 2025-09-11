#!/usr/bin/env python3
"""
MySQL migration to add upload tracking fields to Document model
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_mysql_database():
    """Add academi_uploaded and academi_upload_time columns to document table in MySQL"""
    
    # Get MySQL connection details from environment
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = int(os.environ.get('MYSQL_PORT', '3306'))
    mysql_user = os.environ.get('MYSQL_USER', 'potplag')
    mysql_password = os.environ.get('MYSQL_PASSWORD', 'potplag_secure_password_123')
    mysql_database = os.environ.get('MYSQL_DATABASE', 'potplag')
    
    try:
        # Connect to MySQL database
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Check if columns already exist
        cursor.execute("DESCRIBE document")
        columns = [column[0] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'academi_uploaded' not in columns:
            migrations_needed.append("ALTER TABLE document ADD COLUMN academi_uploaded BOOLEAN DEFAULT FALSE")
            
        if 'academi_upload_time' not in columns:
            migrations_needed.append("ALTER TABLE document ADD COLUMN academi_upload_time DATETIME NULL")
        
        if not migrations_needed:
            print("✅ MySQL database is already up to date!")
            return True
            
        # Execute migrations
        for migration in migrations_needed:
            print(f"🔄 Executing: {migration}")
            cursor.execute(migration)
        
        # Commit changes
        connection.commit()
        print("✅ MySQL database migration completed successfully!")
        
        # Show updated table structure
        cursor.execute("DESCRIBE document")
        columns = cursor.fetchall()
        print("\n📋 Updated document table structure:")
        for column in columns:
            print(f"  - {column[0]} ({column[1]})")
        
        return True
        
    except Exception as e:
        print(f"❌ MySQL migration failed: {str(e)}")
        return False
        
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    print("🚀 Starting MySQL database migration...")
    success = migrate_mysql_database()
    
    if success:
        print("\n✅ Migration completed! You can now restart your Flask application.")
    else:
        print("\n❌ Migration failed! Please check the error messages above.")
