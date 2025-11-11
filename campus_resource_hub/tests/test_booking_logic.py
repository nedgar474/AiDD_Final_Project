"""
Unit tests for booking business logic.

Tests conflict detection, status transitions, and booking validation.
"""
import pytest
from datetime import datetime, timedelta
from src.data_access import BookingDAO
from src.models.booking import Booking
from src.models.resource import Resource
from src.models.user import User
from src.extensions import db, bcrypt


class TestBookingConflictDetection:
    """Test booking conflict detection logic."""
    
    def test_no_conflict_when_resource_available(self, app, test_resource, test_user):
        """Test no conflict when resource is available."""
        with app.app_context():
            dao = BookingDAO()
            start = datetime.utcnow() + timedelta(days=10)
            end = start + timedelta(hours=2)
            
            has_conflict = dao.check_conflict(test_resource.id, start, end)
            assert has_conflict is False
    
    def test_conflict_when_time_overlaps(self, app, test_resource, test_user, test_booking):
        """Test conflict detection when booking times overlap."""
        with app.app_context():
            dao = BookingDAO()
            
            # Overlapping start time
            overlap_start = test_booking.start_date - timedelta(minutes=30)
            overlap_end = test_booking.start_date + timedelta(hours=1)
            has_conflict = dao.check_conflict(test_resource.id, overlap_start, overlap_end)
            assert has_conflict is True
            
            # Overlapping end time
            overlap_start = test_booking.end_date - timedelta(hours=1)
            overlap_end = test_booking.end_date + timedelta(minutes=30)
            has_conflict = dao.check_conflict(test_resource.id, overlap_start, overlap_end)
            assert has_conflict is True
            
            # Completely within existing booking
            within_start = test_booking.start_date + timedelta(minutes=15)
            within_end = test_booking.end_date - timedelta(minutes=15)
            has_conflict = dao.check_conflict(test_resource.id, within_start, within_end)
            assert has_conflict is True
    
    def test_no_conflict_when_excluding_self(self, app, test_resource, test_booking):
        """Test no conflict when excluding the booking being updated."""
        with app.app_context():
            dao = BookingDAO()
            # Same time as existing booking, but excluding it
            has_conflict = dao.check_conflict(
                test_resource.id,
                test_booking.start_date,
                test_booking.end_date,
                exclude_id=test_booking.id
            )
            assert has_conflict is False
    
    def test_no_conflict_with_cancelled_bookings(self, app, test_resource, test_user):
        """Test that cancelled bookings don't cause conflicts."""
        with app.app_context():
            # Create a cancelled booking
            start = datetime.utcnow() + timedelta(days=5)
            end = start + timedelta(hours=2)
            cancelled_booking = Booking(
                user_id=test_user.id,
                resource_id=test_resource.id,
                start_date=start,
                end_date=end,
                status='cancelled'
            )
            db.session.add(cancelled_booking)
            db.session.commit()
            
            dao = BookingDAO()
            # Should not conflict with cancelled booking
            has_conflict = dao.check_conflict(test_resource.id, start, end)
            assert has_conflict is False


class TestBookingStatusTransitions:
    """Test booking status transitions."""
    
    def test_update_status_to_completed(self, app, test_booking):
        """Test updating booking status to completed."""
        with app.app_context():
            dao = BookingDAO()
            booking = dao.update_status(test_booking.id, 'completed')
            assert booking.status == 'completed'
    
    def test_update_status_to_cancelled(self, app, test_booking):
        """Test updating booking status to cancelled."""
        with app.app_context():
            dao = BookingDAO()
            booking = dao.update_status(test_booking.id, 'cancelled')
            assert booking.status == 'cancelled'
    
    def test_update_status_to_active(self, app, test_user, test_resource):
        """Test updating booking status to active."""
        with app.app_context():
            start = datetime.utcnow() + timedelta(days=1)
            booking = Booking(
                user_id=test_user.id,
                resource_id=test_resource.id,
                start_date=start,
                end_date=start + timedelta(hours=2),
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            dao = BookingDAO()
            booking = dao.update_status(booking.id, 'active')
            assert booking.status == 'active'


class TestBookingQueries:
    """Test booking query methods."""
    
    def test_get_by_user_filters_by_status(self, app, test_user, test_resource):
        """Test getting bookings by user with status filter."""
        with app.app_context():
            # Create bookings with different statuses
            start = datetime.utcnow() + timedelta(days=1)
            active_booking = Booking(
                user_id=test_user.id,
                resource_id=test_resource.id,
                start_date=start,
                end_date=start + timedelta(hours=2),
                status='active'
            )
            pending_booking = Booking(
                user_id=test_user.id,
                resource_id=test_resource.id,
                start_date=start + timedelta(days=1),
                end_date=start + timedelta(days=1, hours=2),
                status='pending'
            )
            db.session.add_all([active_booking, pending_booking])
            db.session.commit()
            
            dao = BookingDAO()
            active_bookings = dao.get_by_user(test_user.id, status='active')
            assert len(active_bookings) >= 1
            assert all(b.status == 'active' for b in active_bookings)
            
            pending_bookings = dao.get_by_user(test_user.id, status='pending')
            assert len(pending_bookings) >= 1
            assert all(b.status == 'pending' for b in pending_bookings)
    
    def test_get_by_date_range(self, app, test_user, test_resource):
        """Test getting bookings within a date range."""
        with app.app_context():
            # Create bookings at different times
            base_date = datetime.utcnow()
            in_range = Booking(
                user_id=test_user.id,
                resource_id=test_resource.id,
                start_date=base_date + timedelta(days=5),
                end_date=base_date + timedelta(days=5, hours=2),
                status='active'
            )
            out_of_range = Booking(
                user_id=test_user.id,
                resource_id=test_resource.id,
                start_date=base_date + timedelta(days=20),
                end_date=base_date + timedelta(days=20, hours=2),
                status='active'
            )
            db.session.add_all([in_range, out_of_range])
            db.session.commit()
            
            dao = BookingDAO()
            start_range = base_date + timedelta(days=1)
            end_range = base_date + timedelta(days=10)
            bookings = dao.get_by_date_range(start_range, end_range, user_id=test_user.id)
            
            # Should include in_range but not out_of_range
            booking_ids = [b.id for b in bookings]
            assert in_range.id in booking_ids
            assert out_of_range.id not in booking_ids

