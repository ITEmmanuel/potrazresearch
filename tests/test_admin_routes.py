"""Tests for admin routes."""

import pytest
from app.models import User, db


@pytest.mark.integration
class TestAdminRoutes:
    """Test admin routes."""
    
    def test_admin_dashboard_requires_login(self, client):
        """Test admin dashboard requires authentication."""
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_admin_dashboard_requires_admin(self, client, logged_in_user):
        """Test admin dashboard requires admin privileges."""
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'permission' in response.data.lower() or b'access' in response.data.lower()
    
    def test_admin_dashboard_success(self, client, logged_in_admin):
        """Test admin dashboard with admin user."""
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'admin' in response.data.lower()
    
    def test_toggle_user_activation(self, client, logged_in_admin, create_user, app):
        """Test toggling user activation status."""
        with app.app_context():
            initial_status = create_user.is_active
            
        response = client.get(f'/admin/user/toggle/{create_user.id}', 
                             follow_redirects=True)
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.get(create_user.id)
            assert user.is_active != initial_status
    
    def test_make_user_admin(self, client, logged_in_admin, create_user, app):
        """Test making a user admin."""
        response = client.get(f'/admin/user/make_admin/{create_user.id}', 
                             follow_redirects=True)
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.get(create_user.id)
            assert user.is_admin is True
    
    def test_remove_admin_privileges(self, client, logged_in_admin, app):
        """Test removing admin privileges from a user."""
        # Create an admin user first
        with app.app_context():
            admin_user = User(
                username='testadmin',
                email='testadmin@example.com',
                is_admin=True,
                is_active=True
            )
            admin_user.set_password('password123')
            db.session.add(admin_user)
            db.session.commit()
            admin_user_id = admin_user.id
        
        response = client.get(f'/admin/user/remove_admin/{admin_user_id}', 
                             follow_redirects=True)
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.get(admin_user_id)
            assert user.is_admin is False
    
    def test_delete_user(self, client, logged_in_admin, create_user, app):
        """Test deleting a user."""
        user_id = create_user.id
        
        response = client.post(f'/admin/user/delete/{user_id}', 
                              follow_redirects=True)
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.get(user_id)
            assert user is None
    
    def test_admin_cannot_modify_self(self, client, logged_in_admin):
        """Test admin cannot modify their own status."""
        response = client.get(f'/admin/user/toggle/{logged_in_admin.id}', 
                             follow_redirects=True)
        assert response.status_code == 200
        assert b'cannot modify your own' in response.data.lower()
