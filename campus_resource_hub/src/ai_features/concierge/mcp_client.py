"""
MCP Client for Database Queries.

This module provides a client interface to the MCP server for the AI concierge.
It allows the concierge to use MCP for database queries instead of direct DAL access.
"""
import logging
from typing import List, Dict, Optional, Any
from ...ai_features.mcp_server import get_mcp_server

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client for querying database through Model Context Protocol.
    
    This client provides a clean interface for the AI concierge to access
    database information through MCP, ensuring secure, read-only access.
    """
    
    def __init__(self, app=None):
        """
        Initialize MCP client.
        
        Args:
            app: Flask application instance (optional)
        """
        self.server = get_mcp_server(app)
        self._enabled = True
    
    def is_enabled(self) -> bool:
        """Check if MCP is enabled and available."""
        return self._enabled and self.server is not None
    
    def query_resources(
        self,
        query: str,
        user_role: str = 'student',
        limit: int = 10,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query resources using MCP.
        
        Args:
            query: Search query
            user_role: User role for filtering
            limit: Maximum results
            category: Optional category filter
            
        Returns:
            List of resource dictionaries
        """
        if not self.is_enabled():
            logger.warning("MCP client not enabled, falling back to direct DAL")
            return []
        
        try:
            response = self.server.handle_mcp_request('query_resources', {
                'query': query,
                'user_role': user_role,
                'limit': limit,
                'category': category
            })
            
            if response.get('success'):
                return response.get('data', [])
            else:
                logger.error(f"MCP query_resources failed: {response.get('error')}")
                return []
        except Exception as e:
            logger.error(f"MCP query_resources error: {str(e)}", exc_info=True)
            return []
    
    def get_resource_by_id(
        self,
        resource_id: int,
        user_role: str = 'student'
    ) -> Optional[Dict[str, Any]]:
        """
        Get resource by ID using MCP.
        
        Args:
            resource_id: Resource ID
            user_role: User role for access control
            
        Returns:
            Resource dictionary or None
        """
        if not self.is_enabled():
            return None
        
        try:
            response = self.server.handle_mcp_request('get_resource', {
                'resource_id': resource_id,
                'user_role': user_role
            })
            
            if response.get('success'):
                return response.get('data')
            else:
                logger.error(f"MCP get_resource failed: {response.get('error')}")
                return None
        except Exception as e:
            logger.error(f"MCP get_resource error: {str(e)}", exc_info=True)
            return None
    
    def get_resource_availability(
        self,
        resource_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get resource availability using MCP.
        
        Args:
            resource_id: Resource ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Availability information dictionary
        """
        if not self.is_enabled():
            return {}
        
        try:
            response = self.server.handle_mcp_request('get_availability', {
                'resource_id': resource_id,
                'start_date': start_date,
                'end_date': end_date
            })
            
            if response.get('success'):
                return response.get('data', {})
            else:
                logger.error(f"MCP get_availability failed: {response.get('error')}")
                return {}
        except Exception as e:
            logger.error(f"MCP get_availability error: {str(e)}", exc_info=True)
            return {}
    
    def get_resource_reviews(
        self,
        resource_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get resource reviews using MCP.
        
        Args:
            resource_id: Resource ID
            limit: Maximum number of reviews
            
        Returns:
            List of review dictionaries
        """
        if not self.is_enabled():
            return []
        
        try:
            response = self.server.handle_mcp_request('get_reviews', {
                'resource_id': resource_id,
                'limit': limit
            })
            
            if response.get('success'):
                return response.get('data', [])
            else:
                logger.error(f"MCP get_reviews failed: {response.get('error')}")
                return []
        except Exception as e:
            logger.error(f"MCP get_reviews error: {str(e)}", exc_info=True)
            return []
    
    def get_categories(self) -> List[str]:
        """
        Get resource categories using MCP.
        
        Returns:
            List of category names
        """
        if not self.is_enabled():
            return []
        
        try:
            response = self.server.handle_mcp_request('get_categories', {})
            
            if response.get('success'):
                return response.get('data', [])
            else:
                logger.error(f"MCP get_categories failed: {response.get('error')}")
                return []
        except Exception as e:
            logger.error(f"MCP get_categories error: {str(e)}", exc_info=True)
            return []

