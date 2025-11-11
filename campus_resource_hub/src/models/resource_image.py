# AI Contribution: Resource image model for multiple images per resource
from datetime import datetime
from ..extensions import db

class ResourceImage(db.Model):
    __tablename__ = 'resource_images'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    resource = db.relationship('Resource', backref='images', lazy='joined')
    
    def __repr__(self):
        return f'<ResourceImage {self.id} for Resource {self.resource_id}>'

