"""
Data Access Object for Waitlist model.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import and_, or_
from .base_dao import BaseDAO
from ..models.waitlist import Waitlist
from ..extensions import db


class WaitlistDAO(BaseDAO):
    """Data Access Object for Waitlist operations."""
    
    def __init__(self):
        super().__init__(Waitlist)
    
    def get_by_user(self, user_id: int, status: Optional[str] = None) -> List[Waitlist]:
        """Get waitlist entries for a user."""
        query = self.model_class.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Waitlist.created_at.desc()).all()
    
    def get_by_resource(self, resource_id: int, status: Optional[str] = None) -> List[Waitlist]:
        """Get waitlist entries for a resource."""
        query = self.model_class.query.filter_by(resource_id=resource_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Waitlist.created_at.asc()).all()
    
    def check_existing(self, user_id: int, resource_id: int, 
                      start_date: datetime, end_date: datetime) -> Optional[Waitlist]:
        """Check if user already has a pending waitlist entry for this time period."""
        return self.model_class.query.filter(
            Waitlist.user_id == user_id,
            Waitlist.resource_id == resource_id,
            Waitlist.status == 'pending',
            or_(
                and_(Waitlist.requested_start_date <= start_date, Waitlist.requested_end_date > start_date),
                and_(Waitlist.requested_start_date < end_date, Waitlist.requested_end_date >= end_date),
                and_(Waitlist.requested_start_date >= start_date, Waitlist.requested_end_date <= end_date)
            )
        ).first()
    
    def update_status(self, waitlist_id: int, status: str) -> Optional[Waitlist]:
        """Update waitlist entry status."""
        entry = self.get_by_id(waitlist_id)
        if entry:
            entry.status = status
            if status == 'notified':
                from datetime import datetime
                entry.notified_at = datetime.utcnow()
            db.session.commit()
        return entry

