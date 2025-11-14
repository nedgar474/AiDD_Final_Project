"""
Query Processor - Processes natural language queries and routes to appropriate retrievers.
"""
import re
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from .context_retriever import ContextRetriever
from .database_retriever import DatabaseRetriever
from .role_filter import RoleFilter


class QueryProcessor:
    """Processes user queries and retrieves relevant context."""
    
    def __init__(self, app=None):
        """
        Initialize query processor.
        
        Args:
            app: Flask application instance (optional, needed for MCP)
        """
        self.context_retriever = ContextRetriever()
        self.db_retriever = DatabaseRetriever(app=app)
        self.role_filter = RoleFilter()
    
    def process_query(self, query: str, user_role: str, user_id: int = None) -> Dict:
        """
        Process user query and retrieve relevant context.
        
        Args:
            query: User query
            user_role: User role
            user_id: Current user ID (for filtering)
            
        Returns:
            Dictionary with retrieved context
        """
        query_lower = query.lower()
        
        # Determine query type and extract parameters
        query_type = self._classify_query(query_lower)
        
        # Retrieve document context
        doc_chunks = self.context_retriever.search(query, top_k=5)
        
        # Retrieve database context based on query type
        db_results = self._retrieve_database_context(query, query_type, user_role, user_id)
        
        # Filter results based on role
        db_results = self.role_filter.filter_resources(db_results, user_role)
        
        return {
            'query': query,
            'query_type': query_type,
            'doc_chunks': doc_chunks,
            'db_results': db_results
        }
    
    def _classify_query(self, query: str) -> str:
        """
        Classify query type.
        
        Args:
            query: Lowercase query
            
        Returns:
            Query type string
        """
        # Availability queries
        if any(word in query for word in ['available', 'availability', 'when can', 'free', 'open', 'booked']):
            return 'availability'
        
        # Booking queries
        if any(word in query for word in ['book', 'reserve', 'schedule', 'appointment']):
            return 'booking'
        
        # Rating/review queries
        if any(word in query for word in ['rating', 'rated', 'review', 'best', 'top', 'worst', 'lowest']):
            return 'rating'
        
        # Popular/most used queries
        if any(word in query for word in ['popular', 'most used', 'most booked', 'frequently', 'often']):
            return 'popular'
        
        # Comparative queries
        if any(word in query for word in ['compare', 'which', 'better', 'more', 'less', 'difference']):
            return 'comparative'
        
        # Temporal queries
        if any(word in query for word in ['weekend', 'weekday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'morning', 'afternoon', 'evening', 'typically', 'usually']):
            return 'temporal'
        
        # Location queries
        if any(word in query for word in ['location', 'where', 'building', 'room']):
            return 'location'
        
        # Category queries
        if any(word in query for word in ['category', 'type', 'kind', 'equipment', 'projector', 'whiteboard']):
            return 'category'
        
        # Default: general information query
        return 'general'
    
    def _retrieve_database_context(self, query: str, query_type: str, 
                                   user_role: str, user_id: int = None) -> List[Dict]:
        """
        Retrieve database context based on query type.
        
        Args:
            query: User query
            query_type: Classified query type
            user_role: User role
            user_id: Current user ID
            
        Returns:
            List of database results
        """
        results = []
        
        if query_type == 'availability':
            # Extract resource name/ID from query if possible
            resource_results = self.db_retriever.query_resources(query, user_role, limit=5)
            for resource in resource_results:
                availability = self.db_retriever.query_availability(resource['id'])
                availability['resource'] = resource['title']
                availability['resource_id'] = resource['id']
                results.append(availability)
        
        elif query_type == 'rating':
            # Get top-rated resources
            top_rated = self.db_retriever.query_top_rated_resources(limit=5)
            results.extend(top_rated)
            # Also include general resource search
            resource_results = self.db_retriever.query_resources(query, user_role, limit=5)
            results.extend(resource_results)
        
        elif query_type == 'popular':
            # Get popular resources
            popular = self.db_retriever.query_popular_resources(days=30, limit=5)
            results.extend(popular)
        
        elif query_type == 'booking':
            # Get resources that match booking query
            resource_results = self.db_retriever.query_resources(query, user_role, limit=10)
            results.extend(resource_results)
        
        else:
            # General query - search resources
            resource_results = self.db_retriever.query_resources(query, user_role, limit=10)
            results.extend(resource_results)
        
        # Remove duplicates (by ID)
        seen_ids = set()
        unique_results = []
        for result in results:
            result_id = result.get('id') or result.get('resource_id')
            if result_id and result_id not in seen_ids:
                seen_ids.add(result_id)
                unique_results.append(result)
        
        return unique_results[:10]  # Limit to top 10

