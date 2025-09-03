"""Tests for authentication routes."""

import pytest
from app.models import User, db


@pytest.mark.integration
class TestAuthRoutes:
    """Test authentication routes."""
    
    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_register_page(self, client):
        """Test register page loads."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower()
    
    def test_user_registration(self, client, app):
        """Test user registration."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'csrf_token': 'dummy'  # CSRF disabled in testing config
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check user was created
        with app.app_context():
            user = User.query.filter_by(email='new@example.com').first()
            assert user is not None
            assert user.username == 'newuser'
            assert user.is_active is False  # Should be inactive initially
    
    def test_duplicate_user_registration(self, client, create_user, user_data):
        """Test registration with duplicate email."""
        response = client.post('/register', data={
            'username': 'differentuser',
            'email': user_data['email'],  # Same email as existing user
            'password': 'password123',
            'confirm_password': 'password123',
            'csrf_token': 'dummy'
        })
        
        assert response.status_code == 200
        assert b'already registered' in response.data
    
    def test_login_valid_user(self, client, create_user, user_data):
        """Test login with valid credentials."""
        response = client.post('/login', data={
            'email': user_data['email'],
            'password': user_data['password'],
            'csrf_token': 'dummy'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
    
    def test_login_invalid_user(self, client):
        """Test login with invalid credentials."""
        response = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword',
            'csrf_token': 'dummy'
        })
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_login_inactive_user(self, client, app, user_data):
        """Test login with inactive user."""
        with app.app_context():
            user = User(
                username='inactive',
                email='inactive@example.com',
                is_active=False
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'email': 'inactive@example.com',
            'password': 'password123',
            'csrf_token': 'dummy'
        })
        
        assert response.status_code == 200
        assert b'deactivated' in response.data
    
    def test_logout(self, client, logged_in_user):
        """Test user logout."""
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data.lower()
    
    def test_logout_requires_login(self, client):
        """Test logout requires authentication."""
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()
