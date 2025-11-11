"""
Data Access Object for User model.
"""
from typing import Optional, List
from .base_dao import BaseDAO
from ..models.user import User
from ..extensions import db


class UserDAO(BaseDAO):
    """Data Access Object for User operations."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.model_class.query.filter_by(email=email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.model_class.query.filter_by(username=username).first()
    
    def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email or username."""
        return self.model_class.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return self.model_class.query.filter_by(is_active=True).all()
    
    def get_suspended_users(self) -> List[User]:
        """Get all suspended users."""
        return self.model_class.query.filter_by(is_suspended=True).all()
    
    def get_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role."""
        return self.model_class.query.filter_by(role=role).all()
    
    def get_by_department(self, department: str) -> List[User]:
        """Get all users in a specific department."""
        return self.model_class.query.filter_by(department=department).all()
    
    def suspend_user(self, user_id: int, reason: Optional[str] = None) -> User:
        """Suspend a user."""
        user = self.get_by_id(user_id)
        if user:
            user.is_suspended = True
            user.suspension_reason = reason
            db.session.commit()
        return user
    
    def unsuspend_user(self, user_id: int) -> User:
        """Unsuspend a user."""
        user = self.get_by_id(user_id)
        if user:
            user.is_suspended = False
            user.suspension_reason = None
            db.session.commit()
        return user

