"""Unit tests for models."""

import pytest
from app.models import User, Document


@pytest.mark.unit
class TestUser:
    """Test User model."""
    
    def test_create_user(self, app):
        """Test creating a user."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                is_active=True
            )
            user.set_password('testpassword')
            
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.is_active is True
            assert user.is_admin is False
            assert user.check_password('testpassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_repr(self, app, create_user):
        """Test user string representation."""
        with app.app_context():
            assert create_user.username in str(create_user)
    
    def test_admin_user(self, app):
        """Test creating an admin user."""
        with app.app_context():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True
            )
            admin.set_password('adminpass')
            
            assert admin.is_admin is True
            assert admin.is_active is True


@pytest.mark.unit
class TestDocument:
    """Test Document model."""
    
    def test_create_document(self, app, create_user):
        """Test creating a document."""
        with app.app_context():
            doc = Document(
                filename='test.pdf',
                original_filename='original_test.pdf',
                path='/path/to/test.pdf',
                user_id=create_user.id,
                status='completed',
                similarity_score_value=25.5
            )
            
            assert doc.filename == 'test.pdf'
            assert doc.original_filename == 'original_test.pdf'
            assert doc.path == '/path/to/test.pdf'
            assert doc.status == 'completed'
            assert doc.similarity_score == 25.5
    
    def test_document_file_type(self, app, create_user):
        """Test document file type detection."""
        with app.app_context():
            doc = Document(
                filename='test.pdf',
                original_filename='test.pdf',
                path='/path/to/test.pdf',
                user_id=create_user.id
            )
            
            assert doc.file_type == 'PDF'
    
    def test_document_formatted_size(self, app, create_user):
        """Test document formatted size property."""
        with app.app_context():
            doc = Document(
                filename='test.pdf',
                original_filename='test.pdf',
                path='/nonexistent/path.pdf',
                user_id=create_user.id
            )
            
            # Should return "0 B" for non-existent files
            assert doc.formatted_size == "0 B"
    
    def test_filepath_property(self, app, create_user):
        """Test filepath property alias."""
        with app.app_context():
            doc = Document(
                filename='test.pdf',
                original_filename='test.pdf',
                path='/path/to/test.pdf',
                user_id=create_user.id
            )
            
            assert doc.filepath == '/path/to/test.pdf'
            
            doc.filepath = '/new/path/test.pdf'
            assert doc.path == '/new/path/test.pdf'
