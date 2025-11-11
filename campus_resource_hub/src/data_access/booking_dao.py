"""
Data Access Object for Booking model.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import and_, or_
from .base_dao import BaseDAO
from ..models.booking import Booking
from ..extensions import db


class BookingDAO(BaseDAO):
    """Data Access Object for Booking operations."""
    
    def __init__(self):
        super().__init__(Booking)
    
    def get_by_user(self, user_id: int, status: Optional[str] = None) -> List[Booking]:
        """Get bookings for a user, optionally filtered by status."""
        query = self.model_class.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Booking.start_date.desc()).all()
    
    def get_by_resource(self, resource_id: int, status: Optional[str] = None) -> List[Booking]:
        """Get bookings for a resource, optionally filtered by status."""
        query = self.model_class.query.filter_by(resource_id=resource_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Booking.start_date.asc()).all()
    
    def get_active_by_resource(self, resource_id: int) -> List[Booking]:
        """Get active bookings for a resource."""
        return self.model_class.query.filter_by(
            resource_id=resource_id,
            status='active'
        ).all()
    
    def check_conflict(self, resource_id: int, start_date: datetime, 
                      end_date: datetime, exclude_id: Optional[int] = None) -> bool:
        """
        Check if there's a booking conflict for a resource.
        
        Args:
            resource_id: Resource ID
            start_date: Booking start date
            end_date: Booking end date
            exclude_id: Booking ID to exclude from conflict check
            
        Returns:
            True if conflict exists
        """
        query = self.model_class.query.filter_by(resource_id=resource_id).filter(
            Booking.status.in_(['pending', 'active']),
            or_(
                and_(Booking.start_date <= start_date, Booking.end_date > start_date),
                and_(Booking.start_date < end_date, Booking.end_date >= end_date),
                and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
            )
        )
        
        if exclude_id:
            query = query.filter(Booking.id != exclude_id)
        
        return query.first() is not None
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime,
                         user_id: Optional[int] = None) -> List[Booking]:
        """Get bookings within a date range."""
        query = self.model_class.query.filter(
            Booking.start_date >= start_date,
            Booking.start_date <= end_date
        )
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.all()
    
    def get_recurring_children(self, parent_booking_id: int) -> List[Booking]:
        """Get all child bookings for a recurring booking series."""
        return self.model_class.query.filter_by(
            parent_booking_id=parent_booking_id
        ).all()
    
    def update_status(self, booking_id: int, status: str) -> Optional[Booking]:
        """Update booking status."""
        booking = self.get_by_id(booking_id)
        if booking:
            booking.status = status
            db.session.commit()
        return booking

