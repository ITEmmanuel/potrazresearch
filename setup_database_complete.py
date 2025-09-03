#!/usr/bin/env python3
"""
Complete database setup script for POTPLAG Application
This script creates tables, fixes column sizes, and creates admin user
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Complete database setup"""
    
    print("🚀 POTPLAG Database Setup")
    print("=" * 50)
    
    # Step 1: Create tables with basic structure first
    print("\n📋 Step 1: Creating database tables...")
    
    # Import without triggering admin user creation
    from app.models import db
    from config import Config
    from flask import Flask
    
    # Create a minimal app just for database operations
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Basic tables created")
            
            # Step 2: Fix the password_hash column size
            print("\n🔧 Step 2: Fixing password_hash column size...")
            
            with db.engine.connect() as conn:
                # MySQL syntax - modify column size
                conn.execute(db.text("ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255)"))
                conn.commit()
            
            print("✅ Password hash column updated to VARCHAR(255)")
            
            # Step 3: Create admin user
            print("\n👤 Step 3: Creating admin user...")
            
            from app.models import User
            
            admin_email = app.config.get('ADMIN_EMAIL', 'admin@potplag.com')
            admin_password = app.config.get('ADMIN_PASSWORD', 'secure_admin_password')
            
            # Check if admin already exists
            admin = User.query.filter_by(email=admin_email).first()
            
            if admin:
                print(f"⚠️  Admin user already exists: {admin_email}")
            else:
                admin = User(
                    username='admin',
                    email=admin_email,
                    is_admin=True,
                    is_active=True
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print(f"✅ Admin user created: {admin_email}")
                print(f"   Password: {admin_password}")
            
            # Step 4: Create test users (run the existing script)
            print("\n👥 Step 4: Creating test users...")
            
            test_users = [
                {'username': 'john_researcher', 'email': 'john.researcher@test.com', 'password': 'test123'},
                {'username': 'sarah_academic', 'email': 'sarah.academic@test.com', 'password': 'test123'},
                {'username': 'mike_professor', 'email': 'mike.professor@test.com', 'password': 'test123'},
                {'username': 'emma_student', 'email': 'emma.student@test.com', 'password': 'test123'},
                {'username': 'david_scholar', 'email': 'david.scholar@test.com', 'password': 'test123'},
                {'username': 'lisa_educator', 'email': 'lisa.educator@test.com', 'password': 'test123'},
                {'username': 'alex_writer', 'email': 'alex.writer@test.com', 'password': 'test123'},
                {'username': 'rachel_analyst', 'email': 'rachel.analyst@test.com', 'password': 'test123'},
                {'username': 'tom_investigator', 'email': 'tom.investigator@test.com', 'password': 'test123'},
                {'username': 'jane_reviewer', 'email': 'jane.reviewer@test.com', 'password': 'test123'}
            ]
            
            created_count = 0
            skipped_count = 0
            
            for user_data in test_users:
                existing_user = User.query.filter(
                    (User.username == user_data['username']) |
                    (User.email == user_data['email'])
                ).first()
                
                if existing_user:
                    skipped_count += 1
                    continue
                
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    is_active=True,
                    is_admin=False
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                created_count += 1
            
            db.session.commit()
            print(f"✅ Created {created_count} test users, skipped {skipped_count}")
            
            print("\n🎉 Database setup completed successfully!")
            
            # Summary
            print("\n📋 Setup Summary:")
            print("=" * 50)
            print(f"📊 Database: potplag")
            print(f"📊 Tables: users, document")
            print(f"👤 Admin user: {admin_email}")
            print(f"👤 Admin password: {admin_password}")
            print(f"👥 Test users: {created_count} created")
            print(f"🔗 Login URL: http://localhost:5000/login")
            
            print("\n🚀 Ready to run the application!")
            
        except Exception as e:
            print(f"❌ Error during setup: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    setup_database()
