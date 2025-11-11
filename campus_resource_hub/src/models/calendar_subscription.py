from datetime import datetime
from ..extensions import db
import secrets

class CalendarSubscription(db.Model):
    """Model for storing iCal subscription tokens."""
    __tablename__ = 'calendar_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_accessed_at = db.Column(db.DateTime, nullable=True)
    access_count = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # Optional expiration
    
    # Filter preferences
    status_filter = db.Column(db.String(20), nullable=True)  # active, pending, etc.
    start_date = db.Column(db.DateTime, nullable=True)  # Optional start date filter
    end_date = db.Column(db.DateTime, nullable=True)  # Optional end date filter
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], lazy='joined')
    
    @staticmethod
    def generate_token():
        """Generate a secure random token."""
        return secrets.token_urlsafe(48)  # 64 characters when base64 encoded
    
    @staticmethod
    def create_for_user(user_id, status_filter=None, start_date=None, end_date=None, expires_at=None):
        """Create a new subscription token for a user."""
        # Deactivate any existing tokens for this user
        CalendarSubscription.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
        db.session.commit()
        
        token = CalendarSubscription.generate_token()
        subscription = CalendarSubscription(
            user_id=user_id,
            token=token,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
            expires_at=expires_at,
            is_active=True
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription
    
    def record_access(self):
        """Record that this subscription was accessed."""
        self.last_accessed_at = datetime.utcnow()
        self.access_count += 1
        db.session.commit()
    
    def is_valid(self):
        """Check if this subscription is still valid."""
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def __repr__(self):
        return f'<CalendarSubscription {self.id} for user {self.user_id}>'

