#!/usr/bin/env python3
"""
Script to create 10 test user accounts for POTRAZ Research
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User

def create_test_accounts():
    """Create 10 test user accounts"""

    # Test user data
    test_users = [
        {
            'username': 'john_researcher',
            'email': 'john.researcher@test.com',
            'password': 'test123'
        },
        {
            'username': 'sarah_academic',
            'email': 'sarah.academic@test.com',
            'password': 'test123'
        },
        {
            'username': 'mike_professor',
            'email': 'mike.professor@test.com',
            'password': 'test123'
        },
        {
            'username': 'emma_student',
            'email': 'emma.student@test.com',
            'password': 'test123'
        },
        {
            'username': 'david_scholar',
            'email': 'david.scholar@test.com',
            'password': 'test123'
        },
        {
            'username': 'lisa_educator',
            'email': 'lisa.educator@test.com',
            'password': 'test123'
        },
        {
            'username': 'alex_writer',
            'email': 'alex.writer@test.com',
            'password': 'test123'
        },
        {
            'username': 'rachel_analyst',
            'email': 'rachel.analyst@test.com',
            'password': 'test123'
        },
        {
            'username': 'tom_investigator',
            'email': 'tom.investigator@test.com',
            'password': 'test123'
        },
        {
            'username': 'jane_reviewer',
            'email': 'jane.reviewer@test.com',
            'password': 'test123'
        }
    ]

    # Create Flask app context
    app = create_app()

    with app.app_context():
        print("Creating test accounts...")

        created_count = 0
        skipped_count = 0

        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == user_data['username']) |
                (User.email == user_data['email'])
            ).first()

            if existing_user:
                print(f"⚠️  User {user_data['username']} already exists, skipping...")
                skipped_count += 1
                continue

            # Create new user
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                is_active=True,
                is_admin=False
            )
            user.set_password(user_data['password'])

            # Add to database
            db.session.add(user)
            created_count += 1

            print(f"✅ Created user: {user_data['username']} ({user_data['email']})")

        # Commit all changes
        db.session.commit()

        print(f"\n📊 Summary:")
        print(f"   Created: {created_count} accounts")
        print(f"   Skipped: {skipped_count} accounts")
        print(f"   Total: {created_count + skipped_count} processed")

        if created_count > 0:
            print(f"\n🔐 Test account credentials:")
            print(f"   Password for all accounts: test123")
            print(f"   Login URL: http://localhost:5000/login")

            print(f"\n👥 Test Accounts Created:")
            for i, user_data in enumerate(test_users[:created_count], 1):
                print(f"   {i}. {user_data['username']} - {user_data['email']}")

def main():
    """Main function"""
    try:
        create_test_accounts()
        print("\n🎉 Test accounts creation completed successfully!")
    except Exception as e:
        print(f"\n❌ Error creating test accounts: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

