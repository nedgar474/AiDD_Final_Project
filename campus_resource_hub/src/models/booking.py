from datetime import datetime
from ..extensions import db

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    # Legacy columns for backward compatibility with existing database schema
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed, cancelled
    notes = db.Column(db.Text)
    # Recurrence fields
    recurrence_type = db.Column(db.String(20), nullable=True)  # 'daily', 'weekly', 'monthly', or None
    recurrence_end_date = db.Column(db.DateTime, nullable=True)  # End date for recurrence series
    parent_booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)  # Link to parent booking in series
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], lazy='joined')
    # resource relationship is provided by backref from Resource.bookings
    parent_booking = db.relationship('Booking', remote_side=[id], backref='child_bookings')

    def __repr__(self):
        return f'<Booking {self.id}>'
    
    @property
    def start_time_display(self):
        """Formatted start time for display (uses start_date)."""
        if self.start_date:
            return self.start_date.strftime('%I:%M %p')
        return ''
    
    @property
    def end_time_display(self):
        """Formatted end time for display (uses end_date)."""
        if self.end_date:
            return self.end_date.strftime('%I:%M %p')
        return ''
    
    @property
    def status_color(self):
        status_colors = {
            'pending': 'warning',
            'active': 'success',
            'completed': 'info',
            'cancelled': 'danger'
        }
        return status_colors.get(self.status, 'secondary')