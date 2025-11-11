"""
Data Access Object for Notification model.
"""
from typing import Optional, List
from .base_dao import BaseDAO
from ..models.notification import Notification
from ..extensions import db


class NotificationDAO(BaseDAO):
    """Data Access Object for Notification operations."""
    
    def __init__(self):
        super().__init__(Notification)
    
    def get_by_user(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user."""
        query = self.model_class.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).all()
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        return self.model_class.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = self.get_by_id(notification_id)
        if notification and notification.user_id == user_id:
            notification.is_read = True
            db.session.commit()
        return notification
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        count = self.model_class.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        return count
    
    def get_paginated(self, user_id: int, page: int = 1, per_page: int = 20,
                     filter_type: str = 'all'):
        """Get paginated notifications for a user."""
        query = self.model_class.query.filter_by(user_id=user_id)
        
        if filter_type == 'unread':
            query = query.filter_by(is_read=False)
        elif filter_type == 'read':
            query = query.filter_by(is_read=True)
        
        return query.order_by(Notification.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

