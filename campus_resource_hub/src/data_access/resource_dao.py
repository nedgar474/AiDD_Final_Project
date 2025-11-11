"""
Data Access Object for Resource model.
"""
from typing import Optional, List
from sqlalchemy import or_, func
from .base_dao import BaseDAO
from ..models.resource import Resource
from ..models.resource_image import ResourceImage
from ..extensions import db


class ResourceDAO(BaseDAO):
    """Data Access Object for Resource operations."""
    
    def __init__(self):
        super().__init__(Resource)
    
    def get_published(self) -> List[Resource]:
        """Get all published resources."""
        return self.model_class.query.filter_by(status='published').all()
    
    def get_by_category(self, category: str) -> List[Resource]:
        """Get resources by category."""
        return self.model_class.query.filter_by(
            category=category,
            status='published'
        ).all()
    
    def search(self, query: str = None, category: str = None, location: str = None,
               min_capacity: Optional[int] = None) -> List[Resource]:
        """
        Search resources with filters.
        
        Args:
            query: Keyword search in title/description
            category: Filter by category
            location: Filter by location
            min_capacity: Minimum capacity filter
            
        Returns:
            List of matching resources
        """
        resources = self.model_class.query.filter(Resource.status == 'published')
        
        if query:
            resources = resources.filter(or_(
                Resource.title.ilike(f'%{query}%'),
                Resource.description.ilike(f'%{query}%')
            ))
        
        if category:
            resources = resources.filter(Resource.category == category)
        
        if location:
            resources = resources.filter(Resource.location.ilike(f'%{location}%'))
        
        if min_capacity:
            resources = resources.filter(Resource.capacity >= min_capacity)
        
        return resources.all()
    
    def get_by_owner(self, owner_id: int) -> List[Resource]:
        """Get resources by owner."""
        return self.model_class.query.filter_by(owner_id=owner_id).all()
    
    def get_featured(self) -> List[Resource]:
        """Get featured resources."""
        return self.model_class.query.filter_by(
            is_featured=True,
            status='published'
        ).all()
    
    def get_categories(self) -> List[str]:
        """Get all distinct categories."""
        results = self.model_class.query.filter_by(
            status='published'
        ).with_entities(Resource.category).distinct().all()
        return [cat[0] for cat in results]
    
    def get_locations(self) -> List[str]:
        """Get all distinct locations."""
        results = self.model_class.query.filter(
            Resource.status == 'published',
            Resource.location.isnot(None),
            Resource.location != ''
        ).with_entities(Resource.location).distinct().all()
        return [loc[0] for loc in results]
    
    def get_images(self, resource_id: int) -> List[ResourceImage]:
        """Get all images for a resource."""
        return ResourceImage.query.filter_by(
            resource_id=resource_id
        ).order_by(ResourceImage.display_order).all()

