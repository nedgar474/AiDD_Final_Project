from datetime import datetime
from ..extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # booking_created, booking_approved, booking_rejected, booking_cancelled, booking_modified, recurring_series, waitlist_available, owner_notified
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    related_booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)
    related_resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications', lazy='joined')
    related_booking = db.relationship('Booking', foreign_keys=[related_booking_id], lazy='joined')
    related_resource = db.relationship('Resource', foreign_keys=[related_resource_id], lazy='joined')

    def __repr__(self):
        return f'<Notification {self.id} - {self.type} for User {self.user_id}>'
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        db.session.commit()
    
    @property
    def notification_icon(self):
        """Return appropriate icon class based on notification type."""
        icon_map = {
            'booking_created': 'fa-calendar-check',
            'booking_approved': 'fa-check-circle',
            'booking_rejected': 'fa-times-circle',
            'booking_cancelled': 'fa-calendar-times',
            'booking_modified': 'fa-edit',
            'recurring_series': 'fa-redo',
            'waitlist_available': 'fa-bell',
            'owner_notified': 'fa-user-tie'
        }
        return icon_map.get(self.type, 'fa-bell')
    
    @property
    def notification_color(self):
        """Return appropriate color class based on notification type."""
        color_map = {
            'booking_created': 'info',
            'booking_approved': 'success',
            'booking_rejected': 'danger',
            'booking_cancelled': 'warning',
            'booking_modified': 'primary',
            'recurring_series': 'info',
            'waitlist_available': 'success',
            'owner_notified': 'primary'
        }
        return color_map.get(self.type, 'secondary')

