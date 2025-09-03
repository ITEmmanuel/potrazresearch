#!/usr/bin/env python3
"""
Migration script to add original_filename column to Document table
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Document

def add_original_filename_column():
    """Add original_filename column to Document table"""

    app = create_app()

    with app.app_context():
        print("Adding original_filename column to Document table...")

        try:
            # Check if the column already exists
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('document')
            column_names = [col['name'] for col in columns]

            if 'original_filename' in column_names:
                print("✅ original_filename column already exists!")
                return

            # Add the column using raw SQL (MySQL/SQLite compatible)
            with db.engine.connect() as conn:
                # Check database type for syntax compatibility
                if 'mysql' in str(db.engine.url):
                    # MySQL syntax
                    conn.execute(db.text("ALTER TABLE document ADD COLUMN original_filename VARCHAR(255) NOT NULL DEFAULT ''"))
                else:
                    # SQLite syntax
                    conn.execute(db.text("ALTER TABLE document ADD COLUMN original_filename VARCHAR(255) NOT NULL DEFAULT ''"))
                conn.commit()

            print("✅ Successfully added original_filename column to Document table")

        except Exception as e:
            print(f"❌ Error adding column: {str(e)}")
            # Try to create all tables if the table doesn't exist at all
            try:
                db.create_all()
                print("✅ Created all tables including the new column")
            except Exception as e2:
                print(f"❌ Error creating tables: {str(e2)}")
                sys.exit(1)

def main():
    """Main function"""
    try:
        add_original_filename_column()
        print("\n🎉 Database migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

