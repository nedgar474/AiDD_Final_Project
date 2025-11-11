"""
Data Access Object for Review model.
"""
from typing import Optional, List
from .base_dao import BaseDAO
from ..models.review import Review
from ..extensions import db


class ReviewDAO(BaseDAO):
    """Data Access Object for Review operations."""
    
    def __init__(self):
        super().__init__(Review)
    
    def get_by_resource(self, resource_id: int, include_hidden: bool = False) -> List[Review]:
        """Get reviews for a resource."""
        query = self.model_class.query.filter_by(resource_id=resource_id)
        if not include_hidden:
            query = query.filter_by(is_hidden=False)
        return query.order_by(Review.created_at.desc()).all()
    
    def get_by_user(self, user_id: int) -> List[Review]:
        """Get reviews by a user."""
        return self.model_class.query.filter_by(
            user_id=user_id,
            is_hidden=False
        ).order_by(Review.created_at.desc()).all()
    
    def get_by_user_and_resource(self, user_id: int, resource_id: int) -> Optional[Review]:
        """Get a user's review for a specific resource."""
        return self.model_class.query.filter_by(
            user_id=user_id,
            resource_id=resource_id
        ).first()
    
    def get_paginated(self, resource_id: int, page: int = 1, per_page: int = 10,
                     include_hidden: bool = False):
        """Get paginated reviews for a resource."""
        query = self.model_class.query.filter_by(resource_id=resource_id)
        if not include_hidden:
            query = query.filter_by(is_hidden=False)
        return query.order_by(Review.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    def hide_review(self, review_id: int) -> Optional[Review]:
        """Hide a review."""
        review = self.get_by_id(review_id)
        if review:
            review.is_hidden = True
            db.session.commit()
        return review
    
    def unhide_review(self, review_id: int) -> Optional[Review]:
        """Unhide a review."""
        review = self.get_by_id(review_id)
        if review:
            review.is_hidden = False
            db.session.commit()
        return review

