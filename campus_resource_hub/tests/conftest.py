"""
Pytest configuration and fixtures for Campus Resource Hub tests.
"""
import pytest
from src.app import create_app
from src.extensions import db
from src.models.user import User
from src.models.resource import Resource
from src.models.booking import Booking
import os
import tempfile


@pytest.fixture
def app():
    """Create application for testing."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('development')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        from src.extensions import bcrypt
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
            first_name='Test',
            last_name='User',
            role='student',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_admin(app):
    """Create a test admin user."""
    with app.app_context():
        from src.extensions import bcrypt
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture
def test_resource(app, test_user):
    """Create a test resource."""
    with app.app_context():
        resource = Resource(
            title='Test Resource',
            description='A test resource',
            category='Room',
            location='Building A',
            capacity=10,
            is_available=True,
            status='published',
            owner_id=test_user.id
        )
        db.session.add(resource)
        db.session.commit()
        return resource


@pytest.fixture
def test_booking(app, test_user, test_resource):
    """Create a test booking."""
    with app.app_context():
        from datetime import datetime, timedelta
        start_date = datetime.utcnow() + timedelta(days=1)
        end_date = start_date + timedelta(hours=2)
        
        booking = Booking(
            user_id=test_user.id,
            resource_id=test_resource.id,
            start_date=start_date,
            end_date=end_date,
            status='active',
            notes='Test booking'
        )
        db.session.add(booking)
        db.session.commit()
        return booking

