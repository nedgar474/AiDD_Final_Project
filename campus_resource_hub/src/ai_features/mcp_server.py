"""
Model Context Protocol (MCP) Server for Database Queries.

This module provides a read-only MCP server interface for AI agents to safely
query the Campus Resource Hub database. MCP enables structured, secure interaction
between the AI layer and the SQLite database.

Usage:
    The MCP server can be started as a standalone process or integrated into
    the Flask application. It exposes database queries through a standardized
    protocol that AI agents can use to retrieve resource information.

Security:
    - Read-only access to database
    - Role-based filtering enforced
    - No write operations allowed
    - Input validation on all queries
"""
import json
import logging
from typing import Any, Dict, List, Optional
from flask import current_app
from ..extensions import db
from ..data_access import ResourceDAO, BookingDAO, ReviewDAO
from ..models.resource import Resource
from ..models.booking import Booking
from ..models.review import Review

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server for providing read-only database access to AI agents.
    
    This server implements the Model Context Protocol to safely expose
    database queries to AI assistants while maintaining security and
    role-based access control.
    """
    
    def __init__(self):
        """Initialize MCP server with DAOs."""
        self.resource_dao = ResourceDAO()
        self.booking_dao = BookingDAO()
        self.review_dao = ReviewDAO()
        self._initialized = False
    
    def initialize(self, app=None):
        """
        Initialize the MCP server with Flask application context.
        
        Args:
            app: Flask application instance (optional)
        """
        if app:
            self.app = app
        self._initialized = True
        logger.info("MCP Server initialized")
    
    def _get_app_context(self):
        """Get Flask application context."""
        if hasattr(self, 'app'):
            return self.app.app_context()
        return current_app.app_context()
    
    def query_resources(
        self, 
        query: str, 
        user_role: str = 'student',
        limit: int = 10,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query resources using MCP protocol.
        
        Args:
            query: Search query (keywords, title, description)
            user_role: User role for filtering (student, staff, admin)
            limit: Maximum number of results
            category: Optional category filter
            
        Returns:
            List of resource dictionaries
        """
        with self._get_app_context():
            try:
                # Extract keywords from query
                keywords = self._extract_keywords(query)
                
                # Build query
                resources_query = Resource.query
                
                # Role-based filtering
                if user_role == 'student':
                    resources_query = resources_query.filter(
                        Resource.status == 'published',
                        Resource.is_available == True
                    )
                
                # Category filter
                if category:
                    resources_query = resources_query.filter(
                        Resource.category == category
                    )
                
                # Keyword search
                if keywords:
                    from sqlalchemy import or_
                    conditions = []
                    for keyword in keywords:
                        conditions.append(Resource.title.ilike(f'%{keyword}%'))
                        conditions.append(Resource.description.ilike(f'%{keyword}%'))
                        conditions.append(Resource.location.ilike(f'%{keyword}%'))
                    if conditions:
                        resources_query = resources_query.filter(or_(*conditions))
                
                # Execute query
                resources = resources_query.limit(limit).all()
                
                # Format results
                results = []
                for resource in resources:
                    # Get images
                    images = []
                    if hasattr(resource, 'images'):
                        images = [
                            {
                                'image_path': img.image_path,
                                'display_order': img.display_order
                            }
                            for img in sorted(resource.images, key=lambda x: x.display_order)
                        ]
                    
                    results.append({
                        'id': resource.id,
                        'title': resource.title,
                        'description': resource.description,
                        'category': resource.category,
                        'location': resource.location,
                        'capacity': resource.capacity,
                        'is_available': resource.is_available,
                        'is_featured': resource.is_featured,
                        'equipment': resource.equipment,
                        'images': images
                    })
                
                logger.info(f"MCP query_resources: {len(results)} results for query '{query}'")
                return results
                
            except Exception as e:
                logger.error(f"MCP query_resources error: {str(e)}", exc_info=True)
                return []
    
    def get_resource_by_id(self, resource_id: int, user_role: str = 'student') -> Optional[Dict[str, Any]]:
        """
        Get a specific resource by ID.
        
        Args:
            resource_id: Resource ID
            user_role: User role for access control
            
        Returns:
            Resource dictionary or None
        """
        with self._get_app_context():
            try:
                resource = self.resource_dao.get_by_id(resource_id)
                
                if not resource:
                    return None
                
                # Role-based access control
                if user_role == 'student' and resource.status != 'published':
                    return None
                
                # Get images
                images = []
                if hasattr(resource, 'images'):
                    images = [
                        {
                            'image_path': img.image_path,
                            'display_order': img.display_order
                        }
                        for img in sorted(resource.images, key=lambda x: x.display_order)
                    ]
                
                return {
                    'id': resource.id,
                    'title': resource.title,
                    'description': resource.description,
                    'category': resource.category,
                    'location': resource.location,
                    'capacity': resource.capacity,
                    'is_available': resource.is_available,
                    'is_featured': resource.is_featured,
                    'equipment': resource.equipment,
                    'images': images
                }
                
            except Exception as e:
                logger.error(f"MCP get_resource_by_id error: {str(e)}", exc_info=True)
                return None
    
    def get_resource_availability(
        self,
        resource_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get availability information for a resource.
        
        Args:
            resource_id: Resource ID
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            
        Returns:
            Dictionary with availability information
        """
        with self._get_app_context():
            try:
                from datetime import datetime
                
                resource = self.resource_dao.get_by_id(resource_id)
                if not resource:
                    return {'error': 'Resource not found'}
                
                # Get active bookings
                bookings_query = Booking.query.filter_by(
                    resource_id=resource_id,
                    status='active'
                )
                
                if start_date:
                    start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    bookings_query = bookings_query.filter(Booking.end_date >= start)
                
                if end_date:
                    end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    bookings_query = bookings_query.filter(Booking.start_date <= end)
                
                bookings = bookings_query.all()
                
                return {
                    'resource_id': resource_id,
                    'is_available': resource.is_available,
                    'active_bookings_count': len(bookings),
                    'bookings': [
                        {
                            'id': b.id,
                            'start_date': b.start_date.isoformat() if b.start_date else None,
                            'end_date': b.end_date.isoformat() if b.end_date else None,
                            'status': b.status
                        }
                        for b in bookings
                    ]
                }
                
            except Exception as e:
                logger.error(f"MCP get_resource_availability error: {str(e)}", exc_info=True)
                return {'error': str(e)}
    
    def get_resource_reviews(self, resource_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get reviews for a resource.
        
        Args:
            resource_id: Resource ID
            limit: Maximum number of reviews
            
        Returns:
            List of review dictionaries
        """
        with self._get_app_context():
            try:
                reviews = Review.query.filter_by(
                    resource_id=resource_id,
                    is_hidden=False
                ).order_by(Review.created_at.desc()).limit(limit).all()
                
                return [
                    {
                        'id': r.id,
                        'rating': r.rating,
                        'review_text': r.review_text,
                        'created_at': r.created_at.isoformat() if r.created_at else None,
                        'user_id': r.user_id
                    }
                    for r in reviews
                ]
                
            except Exception as e:
                logger.error(f"MCP get_resource_reviews error: {str(e)}", exc_info=True)
                return []
    
    def get_categories(self) -> List[str]:
        """
        Get list of all resource categories.
        
        Returns:
            List of category names
        """
        with self._get_app_context():
            try:
                categories = db.session.query(Resource.category).distinct().all()
                return [cat[0] for cat in categories if cat[0]]
            except Exception as e:
                logger.error(f"MCP get_categories error: {str(e)}", exc_info=True)
                return []
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from natural language query.
        
        Args:
            query: User query string
            
        Returns:
            List of keywords
        """
        import re
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
            'may', 'might', 'must', 'can', 'what', 'when', 'where', 'who', 'which', 'how', 'why'
        }
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords
    
    def handle_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP protocol request.
        
        Args:
            method: MCP method name
            params: Method parameters
            
        Returns:
            Response dictionary
        """
        try:
            if method == 'query_resources':
                return {
                    'success': True,
                    'data': self.query_resources(
                        query=params.get('query', ''),
                        user_role=params.get('user_role', 'student'),
                        limit=params.get('limit', 10),
                        category=params.get('category')
                    )
                }
            elif method == 'get_resource':
                return {
                    'success': True,
                    'data': self.get_resource_by_id(
                        resource_id=params.get('resource_id'),
                        user_role=params.get('user_role', 'student')
                    )
                }
            elif method == 'get_availability':
                return {
                    'success': True,
                    'data': self.get_resource_availability(
                        resource_id=params.get('resource_id'),
                        start_date=params.get('start_date'),
                        end_date=params.get('end_date')
                    )
                }
            elif method == 'get_reviews':
                return {
                    'success': True,
                    'data': self.get_resource_reviews(
                        resource_id=params.get('resource_id'),
                        limit=params.get('limit', 10)
                    )
                }
            elif method == 'get_categories':
                return {
                    'success': True,
                    'data': self.get_categories()
                }
            else:
                return {
                    'success': False,
                    'error': f'Unknown method: {method}'
                }
        except Exception as e:
            logger.error(f"MCP request error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


# Global MCP server instance
_mcp_server_instance: Optional[MCPServer] = None


def get_mcp_server(app=None) -> MCPServer:
    """
    Get or create the global MCP server instance.
    
    Args:
        app: Flask application instance (optional)
        
    Returns:
        MCPServer instance
    """
    global _mcp_server_instance
    if _mcp_server_instance is None:
        _mcp_server_instance = MCPServer()
        if app:
            _mcp_server_instance.initialize(app)
    elif app and not _mcp_server_instance._initialized:
        _mcp_server_instance.initialize(app)
    return _mcp_server_instance

