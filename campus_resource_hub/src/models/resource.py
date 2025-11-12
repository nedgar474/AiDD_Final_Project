from datetime import datetime
from ..extensions import db

class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)  # Legacy column for backward compatibility
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=True)  # Legacy column for backward compatibility (migrated to category)
    location = db.Column(db.String(100))
    image_url = db.Column(db.String(255))
    capacity = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    requires_approval = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, published, archived
    equipment = db.Column(db.Text, nullable=True)  # Comma-separated list of equipment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], lazy='joined')
    bookings = db.relationship('Booking', backref='resource', lazy='dynamic')
    reviews = db.relationship('Review', backref='resource_review', lazy='dynamic', cascade='all, delete-orphan')
    
    def average_rating(self):
        """Calculate average rating for this resource (only visible reviews)."""
        from sqlalchemy import func
        # Import Review here to avoid circular imports
        from .review import Review as ReviewModel
        result = db.session.query(func.avg(ReviewModel.rating)).filter_by(resource_id=self.id, is_hidden=False).scalar()
        return round(result, 1) if result else 0.0
    
    def rating_percentage(self):
        """Get rating as percentage (out of 100)."""
        avg = self.average_rating()
        return round((avg / 5.0) * 100, 0) if avg else 0
    
    def review_count(self):
        """Get total number of visible reviews."""
        # Import Review here to avoid circular imports
        from .review import Review as ReviewModel
        return ReviewModel.query.filter_by(resource_id=self.id, is_hidden=False).count()

    def __repr__(self):
        return f'<Resource {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'location': self.location,
            'image_url': self.image_url,
            'capacity': self.capacity,
            'is_available': self.is_available,
            'is_featured': self.is_featured
        }