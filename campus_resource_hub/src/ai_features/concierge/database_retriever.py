"""
Database Retriever - Queries database using DAL or MCP for resource information.

This module supports both direct DAL access and MCP (Model Context Protocol) access.
MCP is preferred when available as it provides a safer, structured interface for
AI agents to query the database.
"""
import re
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ...data_access import ResourceDAO, BookingDAO, ReviewDAO
from ...models.resource import Resource
from ...models.booking import Booking

# Try to import MCP client (optional)
try:
    from .mcp_client import MCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPClient = None


class DatabaseRetriever:
    """
    Retrieves relevant information from database using DAL or MCP.
    
    Uses MCP (Model Context Protocol) when available for safer, structured
    database access. Falls back to direct DAL access if MCP is not available.
    """
    
    def __init__(self, app=None, use_mcp: Optional[bool] = None):
        """
        Initialize database retriever.
        
        Args:
            app: Flask application instance (optional, needed for MCP)
            use_mcp: Force MCP usage (True) or direct DAL (False). 
                    If None, uses MCP if available and enabled.
        """
        self.resource_dao = ResourceDAO()
        self.booking_dao = BookingDAO()
        self.review_dao = ReviewDAO()
        
        # Initialize MCP client if available
        self.mcp_client = None
        self.use_mcp = use_mcp
        
        if MCP_AVAILABLE and MCPClient:
            try:
                # Check if MCP is enabled via environment variable
                if use_mcp is None:
                    use_mcp = os.environ.get('USE_MCP', 'true').lower() == 'true'
                
                if use_mcp:
                    self.mcp_client = MCPClient(app)
                    if self.mcp_client.is_enabled():
                        self.use_mcp = True
                    else:
                        self.use_mcp = False
                        self.mcp_client = None
                else:
                    self.use_mcp = False
            except Exception as e:
                # If MCP initialization fails, fall back to DAL
                import logging
                logging.warning(f"MCP initialization failed, using DAL: {str(e)}")
                self.use_mcp = False
                self.mcp_client = None
        else:
            self.use_mcp = False
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from natural language query.
        
        Args:
            query: User query
            
        Returns:
            List of keywords
        """
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'what', 'when', 'where', 'who', 'which', 'how', 'why'}
        
        # Extract words (alphanumeric only)
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def query_resources(self, query: str, user_role: str, limit: int = 10) -> List[Dict]:
        """
        Query resources based on user query.
        
        Uses MCP if available, otherwise falls back to direct DAL access.
        
        Args:
            query: User query
            user_role: User role (student, staff, admin)
            limit: Maximum number of results
            
        Returns:
            List of resource information dictionaries
        """
        # Try MCP first if available
        if self.use_mcp and self.mcp_client:
            try:
                mcp_results = self.mcp_client.query_resources(
                    query=query,
                    user_role=user_role,
                    limit=limit
                )
                if mcp_results:
                    # Enhance MCP results with additional fields from DAL
                    enhanced_results = []
                    for result in mcp_results:
                        resource = self.resource_dao.get_by_id(result['id'])
                        if resource:
                            result['average_rating'] = resource.average_rating()
                            result['review_count'] = resource.review_count()
                            result['status'] = resource.status
                        enhanced_results.append(result)
                    return enhanced_results
            except Exception as e:
                import logging
                logging.warning(f"MCP query failed, falling back to DAL: {str(e)}")
        
        # Fall back to direct DAL access
        keywords = self.extract_keywords(query)
        keyword_str = ' '.join(keywords) if keywords else ''
        
        # Get resources based on role
        if user_role in ['admin', 'staff']:
            # Staff/admin can see all resources
            resources = self.resource_dao.search(
                query=keyword_str if keyword_str else None,
                category=None,
                location=None,
                min_capacity=None
            )
        else:
            # Students only see published resources
            resources = self.resource_dao.get_published()
            # Filter by keywords if provided
            if keyword_str:
                resources = [r for r in resources if self._matches_keywords(r, keywords)]
        
        # Format results
        results = []
        for resource in resources[:limit]:
            results.append({
                'id': resource.id,
                'title': resource.title,
                'description': resource.description or '',
                'category': resource.category,
                'location': resource.location or '',
                'capacity': resource.capacity,
                'equipment': resource.equipment or '',
                'average_rating': resource.average_rating(),
                'review_count': resource.review_count(),
                'is_available': resource.is_available,
                'status': resource.status
            })
        
        return results
    
    def _matches_keywords(self, resource: Resource, keywords: List[str]) -> bool:
        """Check if resource matches keywords."""
        search_text = f"{resource.title} {resource.description or ''} {resource.category} {resource.location or ''}".lower()
        return any(keyword in search_text for keyword in keywords)
    
    def query_availability(self, resource_id: int, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> Dict:
        """
        Query availability for a resource.
        
        Args:
            resource_id: Resource ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Availability information
        """
        resource = self.resource_dao.get_by_id(resource_id)
        if not resource:
            return {'available': False, 'message': 'Resource not found'}
        
        # Get bookings for this resource
        if start_date and end_date:
            bookings = self.booking_dao.get_by_date_range(start_date, end_date)
            bookings = [b for b in bookings if b.resource_id == resource_id and b.status in ['pending', 'active']]
        else:
            bookings = self.booking_dao.get_active_by_resource(resource_id)
        
        # Check capacity
        if resource.capacity:
            available = len(bookings) < resource.capacity
            utilization = len(bookings) / resource.capacity * 100
        else:
            available = len(bookings) == 0
            utilization = 100 if not available else 0
        
        return {
            'available': available,
            'booked_count': len(bookings),
            'capacity': resource.capacity,
            'utilization_percent': round(utilization, 1),
            'resource': resource.title
        }
    
    def query_popular_resources(self, days: int = 30, limit: int = 5) -> List[Dict]:
        """
        Get most popular resources based on booking count.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of popular resources
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        bookings = self.booking_dao.get_by_date_range(cutoff_date, datetime.utcnow())
        
        # Count bookings per resource
        resource_counts = {}
        for booking in bookings:
            if booking.status in ['active', 'completed']:
                resource_counts[booking.resource_id] = resource_counts.get(booking.resource_id, 0) + 1
        
        # Get resource details
        results = []
        sorted_resources = sorted(resource_counts.items(), key=lambda x: x[1], reverse=True)
        
        for resource_id, count in sorted_resources[:limit]:
            resource = self.resource_dao.get_by_id(resource_id)
            if resource:
                results.append({
                    'id': resource.id,
                    'title': resource.title,
                    'booking_count': count,
                    'category': resource.category,
                    'location': resource.location or ''
                })
        
        return results
    
    def query_top_rated_resources(self, limit: int = 5) -> List[Dict]:
        """
        Get top-rated resources.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of top-rated resources
        """
        # Get all published resources with reviews
        resources = self.resource_dao.get_published()
        resources_with_reviews = [(r, r.average_rating(), r.review_count()) 
                                 for r in resources if r.review_count() > 0]
        
        # Sort by rating
        resources_with_reviews.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for resource, rating, review_count in resources_with_reviews[:limit]:
            results.append({
                'id': resource.id,
                'title': resource.title,
                'average_rating': rating,
                'review_count': review_count,
                'category': resource.category,
                'location': resource.location or ''
            })
        
        return results

