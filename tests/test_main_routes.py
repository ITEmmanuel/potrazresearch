"""Tests for main application routes."""

import pytest
import io
from app.models import Document, User, db


@pytest.mark.integration
class TestMainRoutes:
    """Test main application routes."""
    
    def test_index_page(self, client):
        """Test index page loads."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication."""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_dashboard_logged_in(self, client, logged_in_user):
        """Test dashboard with logged in user."""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower()
    
    def test_upload_page_requires_login(self, client):
        """Test upload page requires authentication."""
        response = client.get('/upload', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_upload_page_logged_in(self, client, logged_in_user):
        """Test upload page with logged in user."""
        response = client.get('/upload')
        assert response.status_code == 200
        assert b'upload' in response.data.lower()
    
    def test_file_upload(self, client, logged_in_user, app):
        """Test file upload functionality."""
        data = {
            'document': (io.BytesIO(b'test file content'), 'test.txt'),
            'csrf_token': 'dummy'
        }
        
        response = client.post('/upload', data=data, 
                             content_type='multipart/form-data',
                             follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check document was created
        with app.app_context():
            doc = Document.query.filter(Document.original_filename == 'test.txt').first()
            assert doc is not None
            assert doc.user_id == logged_in_user.id
    
    def test_view_document(self, client, logged_in_user, sample_document):
        """Test viewing a document."""
        response = client.get(f'/document/{sample_document.id}')
        assert response.status_code == 200
    
    def test_view_document_requires_ownership(self, client, app, user_data, admin_data, sample_document):
        """Test viewing document requires ownership."""
        # Create another user
        with app.app_context():
            other_user = User(
                username='otheruser',
                email='other@example.com',
                is_active=True
            )
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()
        
        # Log in as the other user
        client.post('/login', data={
            'email': 'other@example.com',
            'password': 'password123',
            'csrf_token': 'dummy'
        })
        
        # Try to access the document
        response = client.get(f'/document/{sample_document.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'permission' in response.data.lower()
    
    def test_delete_document(self, client, logged_in_user, sample_document, app):
        """Test document deletion."""
        response = client.post(f'/delete/{sample_document.id}', 
                              data={'csrf_token': 'dummy'},
                              follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check document was deleted
        with app.app_context():
            doc = Document.query.get(sample_document.id)
            assert doc is None
