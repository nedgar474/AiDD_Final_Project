# AI Contribution: Admin log model for tracking admin actions
from datetime import datetime
from ..extensions import db

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.Text, nullable=False)
    target_table = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    admin = db.relationship('User', foreign_keys=[admin_id], lazy='joined')
    
    def __repr__(self):
        return f'<AdminLog {self.log_id}: {self.action} by Admin {self.admin_id}>'

