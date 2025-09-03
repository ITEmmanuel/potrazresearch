"""Test configuration and fixtures."""

import pytest
import tempfile
import os
from app import create_app
from app.models import db, User, Document
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    # Create a temporary file to be used as the database
    db_fd, db_path = tempfile.mkstemp()
    
    # Override the database URI to use the temporary database
    TestingConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test runner."""
    return app.test_cli_runner()


@pytest.fixture
def user_data():
    """Sample user data for testing."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    }


@pytest.fixture
def admin_data():
    """Sample admin user data for testing."""
    return {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'adminpassword123'
    }


@pytest.fixture
def create_user(app, user_data):
    """Create a test user."""
    with app.app_context():
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            is_active=True
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def create_admin(app, admin_data):
    """Create a test admin user."""
    with app.app_context():
        admin = User(
            username=admin_data['username'],
            email=admin_data['email'],
            is_active=True,
            is_admin=True
        )
        admin.set_password(admin_data['password'])
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture
def logged_in_user(client, create_user, user_data):
    """Log in a test user."""
    client.post('/login', data={
        'email': user_data['email'],
        'password': user_data['password']
    })
    return create_user


@pytest.fixture
def logged_in_admin(client, create_admin, admin_data):
    """Log in a test admin."""
    client.post('/login', data={
        'email': admin_data['email'],
        'password': admin_data['password']
    })
    return create_admin


@pytest.fixture
def sample_document(app, create_user):
    """Create a sample document for testing."""
    with app.app_context():
        doc = Document(
            filename='test_document.pdf',
            original_filename='test_document.pdf',
            path='/tmp/test_document.pdf',
            user_id=create_user.id,
            status='completed',
            similarity_score_value=25.5,
            ai_percentage=15.0,
            word_count=1000
        )
        db.session.add(doc)
        db.session.commit()
        return doc
