"""
Data Access Object for CalendarSubscription model.
"""
from typing import Optional
from datetime import datetime
from .base_dao import BaseDAO
from ..models.calendar_subscription import CalendarSubscription
from ..extensions import db


class CalendarSubscriptionDAO(BaseDAO):
    """Data Access Object for CalendarSubscription operations."""
    
    def __init__(self):
        super().__init__(CalendarSubscription)
    
    def get_by_token(self, token: str) -> Optional[CalendarSubscription]:
        """Get subscription by token."""
        return self.model_class.query.filter_by(token=token).first()
    
    def get_active_by_user(self, user_id: int) -> Optional[CalendarSubscription]:
        """Get active subscription for a user."""
        return self.model_class.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
    
    def deactivate_all_for_user(self, user_id: int) -> int:
        """Deactivate all subscriptions for a user."""
        count = self.model_class.query.filter_by(
            user_id=user_id,
            is_active=True
        ).update({'is_active': False})
        db.session.commit()
        return count
    
    def record_access(self, subscription_id: int) -> Optional[CalendarSubscription]:
        """Record that a subscription was accessed."""
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.last_accessed_at = datetime.utcnow()
            subscription.access_count += 1
            db.session.commit()
        return subscription

