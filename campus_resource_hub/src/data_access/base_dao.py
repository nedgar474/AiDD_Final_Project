"""
Base Data Access Object (DAO) class providing common database operations.
"""
from ..extensions import db
from typing import Optional, List, Any
from sqlalchemy.orm import Query


class BaseDAO:
    """Base class for all DAO implementations."""
    
    def __init__(self, model_class):
        """
        Initialize DAO with a model class.
        
        Args:
            model_class: SQLAlchemy model class
        """
        self.model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """
        Get a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        return self.model_class.query.get(id)
    
    def get_or_404(self, id: int) -> Any:
        """
        Get a record by ID or raise 404.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance
            
        Raises:
            404 if not found
        """
        return self.model_class.query.get_or_404(id)
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Any]:
        """
        Get all records.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        query = self.model_class.query
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def count(self) -> int:
        """
        Get total count of records.
        
        Returns:
            Total count
        """
        return self.model_class.query.count()
    
    def create(self, **kwargs) -> Any:
        """
        Create a new record.
        
        Args:
            **kwargs: Model attributes
            
        Returns:
            Created model instance
        """
        instance = self.model_class(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, instance: Any, **kwargs) -> Any:
        """
        Update an existing record.
        
        Args:
            instance: Model instance to update
            **kwargs: Attributes to update
            
        Returns:
            Updated model instance
        """
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance
    
    def delete(self, instance: Any) -> bool:
        """
        Delete a record.
        
        Args:
            instance: Model instance to delete
            
        Returns:
            True if successful
        """
        db.session.delete(instance)
        db.session.commit()
        return True
    
    def filter_by(self, **kwargs) -> Query:
        """
        Get a filtered query.
        
        Args:
            **kwargs: Filter criteria
            
        Returns:
            SQLAlchemy Query object
        """
        return self.model_class.query.filter_by(**kwargs)
    
    def filter(self, *criterion) -> Query:
        """
        Get a filtered query with custom criteria.
        
        Args:
            *criterion: SQLAlchemy filter criteria
            
        Returns:
            SQLAlchemy Query object
        """
        return self.model_class.query.filter(*criterion)

