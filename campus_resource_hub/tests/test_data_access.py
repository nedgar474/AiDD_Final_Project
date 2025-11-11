"""
Unit tests for Data Access Layer (DAL).

These tests verify that the DAL properly encapsulates database operations
and that controllers can use DAL methods instead of direct ORM queries.
"""
import pytest
from datetime import datetime, timedelta
from src.data_access import (
    UserDAO, ResourceDAO, BookingDAO, MessageDAO,
    WaitlistDAO, ReviewDAO, NotificationDAO, CalendarSubscriptionDAO
)
from src.models.user import User
from src.models.resource import Resource
from src.models.booking import Booking
from src.models.message import Message
from src.models.waitlist import Waitlist
from src.models.review import Review
from src.models.notification import Notification
from src.models.calendar_subscription import CalendarSubscription
from src.extensions import bcrypt


class TestUserDAO:
    """Test UserDAO operations."""
    
    def test_create_user(self, app):
        """Test creating a user via DAL."""
        with app.app_context():
            dao = UserDAO()
            user = dao.create(
                username='newuser',
                email='newuser@example.com',
                password_hash=bcrypt.generate_password_hash('password').decode('utf-8'),
                role='student'
            )
            assert user.id is not None
            assert user.username == 'newuser'
            assert user.email == 'newuser@example.com'
    
    def test_get_by_id(self, app, test_user):
        """Test getting user by ID."""
        with app.app_context():
            dao = UserDAO()
            user = dao.get_by_id(test_user.id)
            assert user is not None
            assert user.id == test_user.id
            assert user.username == test_user.username
    
    def test_get_by_email(self, app, test_user):
        """Test getting user by email."""
        with app.app_context():
            dao = UserDAO()
            user = dao.get_by_email(test_user.email)
            assert user is not None
            assert user.email == test_user.email
    
    def test_get_by_username(self, app, test_user):
        """Test getting user by username."""
        with app.app_context():
            dao = UserDAO()
            user = dao.get_by_username(test_user.username)
            assert user is not None
            assert user.username == test_user.username
    
    def test_get_by_role(self, app, test_admin):
        """Test getting users by role."""
        with app.app_context():
            dao = UserDAO()
            admins = dao.get_by_role('admin')
            assert len(admins) >= 1
            assert all(u.role == 'admin' for u in admins)
    
    def test_suspend_user(self, app, test_user):
        """Test suspending a user."""
        with app.app_context():
            dao = UserDAO()
            user = dao.suspend_user(test_user.id, reason='Test suspension')
            assert user.is_suspended is True
            assert user.suspension_reason == 'Test suspension'
    
    def test_unsuspend_user(self, app, test_user):
        """Test unsuspending a user."""
        with app.app_context():
            dao = UserDAO()
            # First suspend
            dao.suspend_user(test_user.id)
            # Then unsuspend
            user = dao.unsuspend_user(test_user.id)
            assert user.is_suspended is False
            assert user.suspension_reason is None


class TestResourceDAO:
    """Test ResourceDAO operations."""
    
    def test_get_published(self, app, test_resource):
        """Test getting published resources."""
        with app.app_context():
            dao = ResourceDAO()
            resources = dao.get_published()
            assert len(resources) >= 1
            assert all(r.status == 'published' for r in resources)
    
    def test_get_by_category(self, app, test_resource):
        """Test getting resources by category."""
        with app.app_context():
            dao = ResourceDAO()
            resources = dao.get_by_category('Room')
            assert len(resources) >= 1
            assert all(r.category == 'Room' for r in resources)
    
    def test_search(self, app, test_resource):
        """Test searching resources."""
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
            # Search by capacity
            results = dao.search(min_capacity=5)
            assert len(results) >= 1


class TestBookingDAO:
    """Test BookingDAO operations."""
    
    def test_get_by_user(self, app, test_user, test_booking):
        """Test getting bookings by user."""
        with app.app_context():
            dao = BookingDAO()
            bookings = dao.get_by_user(test_user.id)
            assert len(bookings) >= 1
            assert all(b.user_id == test_user.id for b in bookings)
    
    def test_get_by_resource(self, app, test_resource, test_booking):
        """Test getting bookings by resource."""
        with app.app_context():
            dao = BookingDAO()
            bookings = dao.get_by_resource(test_resource.id)
            assert len(bookings) >= 1
            assert all(b.resource_id == test_resource.id for b in bookings)
    
    def test_check_conflict(self, app, test_resource, test_booking):
        """Test checking for booking conflicts."""
        with app.app_context():
            dao = BookingDAO()
            # Check conflict with existing booking
            start = test_booking.start_date
            end = test_booking.end_date
            has_conflict = dao.check_conflict(test_resource.id, start, end)
            assert has_conflict is True
            
            # Check no conflict with future date
            future_start = datetime.utcnow() + timedelta(days=30)
            future_end = future_start + timedelta(hours=2)
            has_conflict = dao.check_conflict(test_resource.id, future_start, future_end)
            assert has_conflict is False
    
    def test_get_by_date_range(self, app, test_user, test_booking):
        """Test getting bookings by date range."""
        with app.app_context():
            dao = BookingDAO()
            start = datetime.utcnow()
            end = datetime.utcnow() + timedelta(days=7)
            bookings = dao.get_by_date_range(start, end, user_id=test_user.id)
            assert len(bookings) >= 1
    
    def test_update_status(self, app, test_booking):
        """Test updating booking status."""
        with app.app_context():
            dao = BookingDAO()
            booking = dao.update_status(test_booking.id, 'completed')
            assert booking.status == 'completed'


class TestMessageDAO:
    """Test MessageDAO operations."""
    
    def test_get_inbox(self, app, test_user, test_admin):
        """Test getting inbox messages."""
        with app.app_context():
            # Create a message
            message = Message(
                sender_id=test_admin.id,
                recipient_id=test_user.id,
                subject='Test Message',
                body='Test body'
            )
            from src.extensions import db
            db.session.add(message)
            db.session.commit()
            
            dao = MessageDAO()
            inbox = dao.get_inbox(test_user.id)
            assert len(inbox) >= 1
            assert all(m.recipient_id == test_user.id for m in inbox)
    
    def test_mark_as_read(self, app, test_user, test_admin):
        """Test marking message as read."""
        with app.app_context():
            from src.extensions import db
            message = Message(
                sender_id=test_admin.id,
                recipient_id=test_user.id,
                subject='Test',
                body='Test'
            )
            db.session.add(message)
            db.session.commit()
            
            dao = MessageDAO()
            message = dao.mark_as_read(message.id, test_user.id)
            assert message.is_read is True


class TestWaitlistDAO:
    """Test WaitlistDAO operations."""
    
    def test_get_by_user(self, app, test_user, test_resource):
        """Test getting waitlist entries by user."""
        with app.app_context():
            from src.extensions import db
            from datetime import datetime, timedelta
            waitlist = Waitlist(
                user_id=test_user.id,
                resource_id=test_resource.id,
                requested_start_date=datetime.utcnow() + timedelta(days=5),
                requested_end_date=datetime.utcnow() + timedelta(days=5, hours=2),
                status='pending'
            )
            db.session.add(waitlist)
            db.session.commit()
            
            dao = WaitlistDAO()
            entries = dao.get_by_user(test_user.id)
            assert len(entries) >= 1
            assert all(e.user_id == test_user.id for e in entries)


class TestReviewDAO:
    """Test ReviewDAO operations."""
    
    def test_get_by_resource(self, app, test_resource, test_user):
        """Test getting reviews by resource."""
        with app.app_context():
            from src.extensions import db
            review = Review(
                user_id=test_user.id,
                resource_id=test_resource.id,
                rating=5,
                comment='Great resource!'
            )
            db.session.add(review)
            db.session.commit()
            
            dao = ReviewDAO()
            reviews = dao.get_by_resource(test_resource.id)
            assert len(reviews) >= 1
            assert all(r.resource_id == test_resource.id for r in reviews)
    
    def test_get_paginated(self, app, test_resource, test_user):
        """Test getting paginated reviews."""
        with app.app_context():
            from src.extensions import db
            review = Review(
                user_id=test_user.id,
                resource_id=test_resource.id,
                rating=4,
                comment='Good'
            )
            db.session.add(review)
            db.session.commit()
            
            dao = ReviewDAO()
            pagination = dao.get_paginated(test_resource.id, page=1, per_page=10)
            assert pagination.total >= 1
            assert len(pagination.items) >= 1


class TestNotificationDAO:
    """Test NotificationDAO operations."""
    
    def test_get_by_user(self, app, test_user):
        """Test getting notifications by user."""
        with app.app_context():
            from src.extensions import db
            notification = Notification(
                user_id=test_user.id,
                notification_type='booking_created',
                title='Test Notification',
                message='Test message'
            )
            db.session.add(notification)
            db.session.commit()
            
            dao = NotificationDAO()
            notifications = dao.get_by_user(test_user.id)
            assert len(notifications) >= 1
            assert all(n.user_id == test_user.id for n in notifications)
    
    def test_get_unread_count(self, app, test_user):
        """Test getting unread notification count."""
        with app.app_context():
            from src.extensions import db
            notification = Notification(
                user_id=test_user.id,
                notification_type='booking_created',
                title='Test',
                message='Test',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            
            dao = NotificationDAO()
            count = dao.get_unread_count(test_user.id)
            assert count >= 1
    
    def test_mark_as_read(self, app, test_user):
        """Test marking notification as read."""
        with app.app_context():
            from src.extensions import db
            notification = Notification(
                user_id=test_user.id,
                notification_type='booking_created',
                title='Test',
                message='Test',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            
            dao = NotificationDAO()
            notification = dao.mark_as_read(notification.id, test_user.id)
            assert notification.is_read is True


class TestCalendarSubscriptionDAO:
    """Test CalendarSubscriptionDAO operations."""
    
    def test_get_by_token(self, app, test_user):
        """Test getting subscription by token."""
        with app.app_context():
            from src.extensions import db
            subscription = CalendarSubscription.create_for_user(test_user.id)
            
            dao = CalendarSubscriptionDAO()
            found = dao.get_by_token(subscription.token)
            assert found is not None
            assert found.token == subscription.token
    
    def test_get_active_by_user(self, app, test_user):
        """Test getting active subscription by user."""
        with app.app_context():
            subscription = CalendarSubscription.create_for_user(test_user.id)
            
            dao = CalendarSubscriptionDAO()
            found = dao.get_active_by_user(test_user.id)
            assert found is not None
            assert found.user_id == test_user.id
            assert found.is_active is True
    
    def test_record_access(self, app, test_user):
        """Test recording subscription access."""
        with app.app_context():
            subscription = CalendarSubscription.create_for_user(test_user.id)
            initial_count = subscription.access_count
            
            dao = CalendarSubscriptionDAO()
            dao.record_access(subscription.id)
            
            # Refresh from database
            from src.extensions import db
            db.session.refresh(subscription)
            assert subscription.access_count == initial_count + 1
            assert subscription.last_accessed_at is not None

