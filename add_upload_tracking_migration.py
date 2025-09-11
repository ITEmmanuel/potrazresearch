#!/usr/bin/env python3
"""
Database migration to add upload tracking fields to Document model
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add academi_uploaded and academi_upload_time columns to documents table"""
    
    # Path to the database file
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(document)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'academi_uploaded' not in columns:
            migrations_needed.append("ALTER TABLE document ADD COLUMN academi_uploaded BOOLEAN DEFAULT 0")
            
        if 'academi_upload_time' not in columns:
            migrations_needed.append("ALTER TABLE document ADD COLUMN academi_upload_time DATETIME")
        
        if not migrations_needed:
            print("✅ Database is already up to date!")
            return True
            
        # Execute migrations
        for migration in migrations_needed:
            print(f"🔄 Executing: {migration}")
            cursor.execute(migration)
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(document)")
        columns = cursor.fetchall()
        print("\n📋 Updated document table structure:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("🚀 Starting database migration...")
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed! You can now restart your Flask application.")
    else:
        print("\n❌ Migration failed! Please check the error messages above.")
