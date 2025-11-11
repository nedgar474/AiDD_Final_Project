"""
Role Filter - Filters data and responses based on user roles.
"""
from typing import List, Dict, Any


class RoleFilter:
    """Filters data and responses based on user roles and privacy requirements."""
    
    @staticmethod
    def filter_resources(resources: List[Dict], user_role: str) -> List[Dict]:
        """
        Filter resources based on user role.
        
        Args:
            resources: List of resource dictionaries
            user_role: User role (student, staff, admin)
            
        Returns:
            Filtered list of resources
        """
        if user_role in ['admin', 'staff']:
            # Staff/admin can see all resources (published, draft, archived)
            return resources
        else:
            # Students only see published resources
            return [r for r in resources if r.get('status') == 'published']
    
    @staticmethod
    def filter_response_links(response: str, user_role: str) -> str:
        """
        Filter admin dashboard links from response if user is not admin.
        
        Args:
            response: LLM response text
            user_role: User role
            
        Returns:
            Response with filtered links
        """
        if user_role == 'admin':
            # Admins can see all links
            return response
        
        # Remove admin dashboard links for non-admin users
        # Pattern: [text](/admin/...) or links containing /admin/
        import re
        response = re.sub(r'\[([^\]]+)\]\(/admin/[^\)]+\)', r'\1', response)
        response = re.sub(r'<a[^>]*href=["\']/admin/[^"\']*["\'][^>]*>([^<]+)</a>', r'\1', response)
        
        return response
    
    @staticmethod
    def sanitize_user_data(data: Dict, current_user_id: int) -> Dict:
        """
        Remove other users' personal information from data.
        
        Args:
            data: Data dictionary that may contain user information
            current_user_id: ID of current user
            
        Returns:
            Sanitized data dictionary
        """
        sanitized = data.copy()
        
        # Remove fields that could identify other users
        if 'user' in sanitized:
            user_data = sanitized['user']
            if isinstance(user_data, dict) and user_data.get('id') != current_user_id:
                # Only keep non-identifying information
                sanitized['user'] = {
                    'id': user_data.get('id'),
                    'role': user_data.get('role')  # Role is okay to show
                }
        
        # Remove email, username, first_name, last_name for other users
        if 'email' in sanitized and sanitized.get('user_id') != current_user_id:
            del sanitized['email']
        if 'username' in sanitized and sanitized.get('user_id') != current_user_id:
            del sanitized['username']
        
        return sanitized
    
    @staticmethod
    def can_access_resource(resource: Dict, user_role: str) -> bool:
        """
        Check if user can access a resource based on role.
        
        Args:
            resource: Resource dictionary
            user_role: User role
            
        Returns:
            True if user can access, False otherwise
        """
        if user_role in ['admin', 'staff']:
            return True  # Staff/admin can see all resources
        
        # Students can only see published resources
        return resource.get('status') == 'published'
    
    @staticmethod
    def format_aggregated_stats(stats: Dict) -> str:
        """
        Format aggregated statistics for display (no user-specific data).
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Formatted string
        """
        # Only include aggregated data, never individual user data
        parts = []
        
        if 'booking_count' in stats:
            parts.append(f"{stats['booking_count']} bookings")
        if 'utilization_percent' in stats:
            parts.append(f"{stats['utilization_percent']}% utilization")
        if 'average_rating' in stats:
            parts.append(f"{stats['average_rating']}/5.0 rating")
        
        return ", ".join(parts) if parts else "No statistics available"

