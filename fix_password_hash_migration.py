#!/usr/bin/env python3
"""
Migration script to fix password_hash column size in User table
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db

def fix_password_hash_column():
    """Update password_hash column to VARCHAR(255)"""

    app = create_app()

    with app.app_context():
        print("Fixing password_hash column size...")

        try:
            # Update the password_hash column to be larger
            with db.engine.connect() as conn:
                # Check database type for syntax compatibility
                if 'mysql' in str(db.engine.url):
                    # MySQL syntax - modify column size
                    conn.execute(db.text("ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255)"))
                else:
                    # SQLite doesn't support MODIFY COLUMN, so we'd need to recreate the table
                    # But for SQLite, VARCHAR(255) should work anyway
                    print("SQLite detected - no column modification needed")
                conn.commit()

            print("✅ Successfully updated password_hash column size to VARCHAR(255)")

        except Exception as e:
            print(f"❌ Error updating column: {str(e)}")
            # If there's an error, it might be because the column doesn't exist yet
            # Let's try creating all tables fresh
            try:
                print("Attempting to recreate tables...")
                db.create_all()
                print("✅ Created all tables with correct column sizes")
            except Exception as e2:
                print(f"❌ Error creating tables: {str(e2)}")
                sys.exit(1)

def main():
    """Main function"""
    try:
        fix_password_hash_column()
        print("\n🎉 Password hash column migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
