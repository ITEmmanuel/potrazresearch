#!/usr/bin/env python3
"""
Test script for document processing integration
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Document
from app.document_processor import DocumentProcessor

def test_document_processing():
    """Test the document processing integration"""

    app = create_app()

    with app.app_context():
        print("🧪 Testing Document Processing Integration")
        print("=" * 50)

        # Check if we have test users
        test_user = User.query.filter_by(username='john_researcher').first()
        if not test_user:
            print("❌ No test users found. Please run create_test_accounts.py first.")
            return

        print(f"✅ Found test user: {test_user.username}")

        # Check if user has any documents
        documents = Document.query.filter_by(user_id=test_user.id).all()
        print(f"📄 Found {len(documents)} documents for user")

        if not documents:
            print("ℹ️  No documents found. You can upload a document through the web interface to test processing.")
            return

        # Test document processor initialization
        print("\n🔧 Testing Document Processor...")

        processor = DocumentProcessor()
        print("✅ Document processor initialized")

        # Test login (this will actually connect to academi.cx)
        print("\n🔐 Testing academi.cx login...")
        login_success = processor.login()

        if login_success:
            print("✅ Successfully logged into academi.cx")

            # Test with the first document
            test_doc = documents[0]
            print(f"\n📤 Testing document upload: {test_doc.original_filename}")

            uploaded_name = processor.upload_document(test_doc.path)

            if uploaded_name:
                print(f"✅ Document uploaded as: {uploaded_name}")

                # Wait a bit for processing
                import time
                print("⏳ Waiting for processing...")
                time.sleep(30)

                # Try to extract results
                print("📊 Extracting results...")
                results = processor.extract_results(uploaded_name)

                if results:
                    print("✅ Results extracted successfully!")
                    print(f"   Similarity: {results.get('similarity_percentage', 'N/A')}")
                    print(f"   AI Score: {results.get('ai_percentage', 'N/A')}")
                    print(f"   Word Count: {results.get('word_count', 'N/A')}")
                else:
                    print("⚠️  Could not extract results (may still be processing)")
            else:
                print("❌ Document upload failed")

            # Cleanup
            processor.cleanup()

        else:
            print("❌ Login to academi.cx failed")
            print("   This could be due to:")
            print("   - Invalid credentials")
            print("   - Network issues")
            print("   - academi.cx service being down")
            print("   - Captcha or additional security measures")

        print("\n" + "=" * 50)
        print("🎯 Integration Test Summary:")
        print("   ✅ Flask app running")
        print("   ✅ Database connection working")
        print("   ✅ Document processor initialized")
        print("   ⚠️  academi.cx integration may need credential verification")

if __name__ == '__main__':
    test_document_processing()

