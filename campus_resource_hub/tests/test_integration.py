"""
Integration tests for Campus Resource Hub.

Tests complete workflows including authentication, booking creation, and resource management.
"""
import pytest
from datetime import datetime, timedelta
from src.data_access import UserDAO, ResourceDAO, BookingDAO, WaitlistDAO
from src.models.user import User
from src.models.resource import Resource
from src.models.booking import Booking
from src.extensions import db, bcrypt


class TestAuthFlow:
    """Test authentication workflow."""
    
    def test_user_registration_and_login_flow(self, app, client):
        """Test complete registration and login flow."""
        with app.app_context():
            # Register new user
            response = client.post('/auth/register', data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'password_confirm': 'password123',
                'first_name': 'New',
                'last_name': 'User',
                'role': 'student',
                'department': 'Computer Science'
            }, follow_redirects=True)
            
            # Should redirect after registration
            assert response.status_code == 200
            
            # Verify user was created
            dao = UserDAO()
            user = dao.get_by_username('newuser')
            assert user is not None
            assert user.email == 'newuser@example.com'
            
            # Test login
            response = client.post('/auth/login', data={
                'email': 'newuser@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            assert response.status_code == 200


class TestBookingWorkflow:
    """Test complete booking workflow."""
    
    def test_create_booking_workflow(self, app, client, test_user, test_resource):
        """Test creating a booking through the application."""
        with app.app_context():
            # Login as user
            client.post('/auth/login', data={
                'email': test_user.email,
                'password': 'password123'
            })
            
            # Create booking
            start_date = datetime.utcnow() + timedelta(days=2)
            end_date = start_date + timedelta(hours=2)
            
            response = client.post(f'/resources/{test_resource.id}/book', data={
                'start_date': start_date.strftime('%Y-%m-%dT%H:%M'),
                'end_date': end_date.strftime('%Y-%m-%dT%H:%M'),
                'notes': 'Test booking',
                'recurrence_type': '',
                'recurrence_end_date': ''
            }, follow_redirects=True)
            
            # Should create booking
            dao = BookingDAO()
            bookings = dao.get_by_user(test_user.id)
            assert len(bookings) >= 1
    
    def test_booking_conflict_detection(self, app, test_user, test_resource, test_booking):
        """Test that booking conflicts are properly detected."""
        with app.app_context():
            dao = BookingDAO()
            
            # Try to book overlapping time
            overlap_start = test_booking.start_date + timedelta(minutes=30)
            overlap_end = test_booking.end_date
            
            has_conflict = dao.check_conflict(
                test_resource.id,
                overlap_start,
                overlap_end
            )
            
            assert has_conflict is True


class TestResourceManagement:
    """Test resource management workflows."""
    
    def test_resource_search_workflow(self, app, test_resource):
        """Test searching for resources."""
        with app.app_context():
            dao = ResourceDAO()
            
            # Search by keyword
            results = dao.search(query='Test')
            assert len(results) >= 1
            
            # Search by category
            results = dao.search(category='Room')
            assert len(results) >= 1
            
            # Search by location
            results = dao.search(location='Building')
            assert len(results) >= 1
    
    def test_resource_creation_workflow(self, app, client, test_admin):
        """Test creating a resource as admin."""
        with app.app_context():
            # Login as admin
            client.post('/auth/login', data={
                'email': test_admin.email,
                'password': 'admin123'
            })
            
            # Create resource
            response = client.post('/admin/resources/create', data={
                'title': 'New Resource',
                'description': 'A new resource',
                'category': 'Equipment',
                'location': 'Building B',
                'capacity': 5,
                'is_available': True,
                'status': 'published'
            }, follow_redirects=True)
            
            # Verify resource was created
            dao = ResourceDAO()
            resource = dao.filter_by(title='New Resource').first()
            assert resource is not None
            assert resource.category == 'Equipment'


class TestDataAccessLayer:
    """Test that DAL properly encapsulates database operations."""
    
    def test_controllers_use_dal_not_direct_orm(self, app):
        """Verify that DAL methods are used instead of direct ORM queries."""
        with app.app_context():
            # This test verifies the pattern - actual implementation
            # should use DAL methods
            dao = BookingDAO()
            
            # DAL should provide methods, not require direct query access
            assert hasattr(dao, 'get_by_user')
            assert hasattr(dao, 'get_by_resource')
            assert hasattr(dao, 'check_conflict')
            assert hasattr(dao, 'create')
            assert hasattr(dao, 'update')
            assert hasattr(dao, 'delete')
    
    def test_dal_encapsulates_crud_operations(self, app, test_user, test_resource):
        """Test that DAL properly encapsulates CRUD operations."""
        with app.app_context():
            dao = BookingDAO()
            
            # Create via DAL
            start = datetime.utcnow() + timedelta(days=3)
            booking = dao.create(
                user_id=test_user.id,
                resource_id=test_resource.id,
                start_date=start,
                end_date=start + timedelta(hours=2),
                status='pending'
            )
            assert booking.id is not None
            
            # Read via DAL
            found = dao.get_by_id(booking.id)
            assert found is not None
            assert found.id == booking.id
            
            # Update via DAL
            updated = dao.update(booking, status='active')
            assert updated.status == 'active'
            
            # Delete via DAL
            result = dao.delete(booking)
            assert result is True
            
            # Verify deleted
            deleted = dao.get_by_id(booking.id)
            assert deleted is None

