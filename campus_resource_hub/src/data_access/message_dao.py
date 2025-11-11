"""
Data Access Object for Message model.
"""
from typing import Optional, List
from .base_dao import BaseDAO
from ..models.message import Message
from ..extensions import db


class MessageDAO(BaseDAO):
    """Data Access Object for Message operations."""
    
    def __init__(self):
        super().__init__(Message)
    
    def get_inbox(self, user_id: int, unread_only: bool = False) -> List[Message]:
        """Get inbox messages for a user."""
        query = self.model_class.query.filter_by(recipient_id=user_id, is_hidden=False)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Message.created_at.desc()).all()
    
    def get_sent(self, user_id: int) -> List[Message]:
        """Get sent messages for a user."""
        return self.model_class.query.filter_by(
            sender_id=user_id,
            is_hidden=False
        ).order_by(Message.created_at.desc()).all()
    
    def get_flagged(self) -> List[Message]:
        """Get all flagged messages."""
        return self.model_class.query.filter_by(
            is_flagged=True,
            is_hidden=False
        ).order_by(Message.created_at.desc()).all()
    
    def mark_as_read(self, message_id: int, user_id: int) -> Optional[Message]:
        """Mark a message as read (only if user is recipient)."""
        message = self.get_by_id(message_id)
        if message and message.recipient_id == user_id:
            message.is_read = True
            db.session.commit()
        return message
    
    def flag_message(self, message_id: int) -> Optional[Message]:
        """Flag a message for admin review."""
        message = self.get_by_id(message_id)
        if message:
            message.is_flagged = True
            db.session.commit()
        return message
    
    def unflag_message(self, message_id: int) -> Optional[Message]:
        """Unflag a message."""
        message = self.get_by_id(message_id)
        if message:
            message.is_flagged = False
            db.session.commit()
        return message

