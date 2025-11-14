"""
Booking Proposer - Handles booking suggestion and proposal flow.
"""
import re
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from .database_retriever import DatabaseRetriever
from .role_filter import RoleFilter


class BookingProposer:
    """Proposes bookings based on user queries."""
    
    def __init__(self, app=None):
        """
        Initialize booking proposer.
        
        Args:
            app: Flask application instance (optional, needed for MCP)
        """
        self.db_retriever = DatabaseRetriever(app=app)
        self.role_filter = RoleFilter()
    
    def extract_booking_intent(self, query: str) -> Optional[Dict]:
        """
        Extract booking intent from query.
        
        Args:
            query: User query
            
        Returns:
            Booking intent dictionary or None
        """
        query_lower = query.lower()
        
        # Check for booking keywords
        booking_keywords = ['book', 'reserve', 'schedule', 'appointment', 'rent', 'use']
        if not any(keyword in query_lower for keyword in booking_keywords):
            return None
        
        intent = {
            'resource_name': None,
            'date': None,
            'time': None,
            'duration': None
        }
        
        # Extract resource name (look for quoted text or common patterns)
        # Pattern: "book [resource name]" or "reserve [resource name]"
        resource_match = re.search(r'(?:book|reserve|schedule)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', query)
        if resource_match:
            intent['resource_name'] = resource_match.group(1)
        
        # Extract date patterns
        date_patterns = [
            r'(?:on\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(?:on\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:on\s+)?(today|tomorrow|next\s+week)',
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, query_lower)
            if date_match:
                intent['date'] = date_match.group(1)
                break
        
        # Extract time patterns
        time_patterns = [
            r'at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)',
            r'(\d{1,2}):?(\d{2})?\s*(am|pm)',
            r'(morning|afternoon|evening)',
        ]
        for pattern in time_patterns:
            time_match = re.search(pattern, query_lower)
            if time_match:
                intent['time'] = time_match.group(0)
                break
        
        # Extract duration
        duration_match = re.search(r'(?:for\s+)?(\d+)\s*(?:hour|hr|minute|min)', query_lower)
        if duration_match:
            intent['duration'] = duration_match.group(1)
        
        return intent if any(intent.values()) else None
    
    def propose_booking(self, query: str, user_role: str, 
                       retrieved_resources: List[Dict]) -> Optional[Dict]:
        """
        Propose a booking based on query and retrieved resources.
        
        Args:
            query: User query
            retrieved_resources: List of resources from database retrieval
            user_role: User role
            
        Returns:
            Booking proposal dictionary or None
        """
        intent = self.extract_booking_intent(query)
        if not intent:
            return None
        
        # Find matching resource
        resource = None
        if intent['resource_name']:
            # Try to match by name
            for r in retrieved_resources:
                if intent['resource_name'].lower() in r.get('title', '').lower():
                    resource = r
                    break
        
        # If no match by name, use first resource from results
        if not resource and retrieved_resources:
            resource = retrieved_resources[0]
        
        if not resource:
            return None
        
        # Check if user can access this resource
        if not self.role_filter.can_access_resource(resource, user_role):
            return None
        
        # Check availability
        availability = self.db_retriever.query_availability(resource['id'])
        
        # Propose default time if not specified
        proposed_date = intent.get('date') or 'tomorrow'
        proposed_time = intent.get('time') or '10:00 AM'
        proposed_duration = intent.get('duration') or '2'  # Default 2 hours
        
        proposal = {
            'resource_id': resource['id'],
            'resource_title': resource['title'],
            'resource_location': resource.get('location', ''),
            'resource_capacity': resource.get('capacity'),
            'resource_equipment': resource.get('equipment', ''),
            'proposed_date': proposed_date,
            'proposed_time': proposed_time,
            'proposed_duration': proposed_duration,
            'available': availability.get('available', False),
            'utilization': availability.get('utilization_percent', 0)
        }
        
        return proposal
    
    def format_booking_proposal(self, proposal: Dict) -> str:
        """
        Format booking proposal as natural language.
        
        Args:
            proposal: Booking proposal dictionary
            
        Returns:
            Formatted proposal text
        """
        parts = [
            f"I can help you book **{proposal['resource_title']}**",
        ]
        
        if proposal.get('resource_location'):
            parts.append(f"located at {proposal['resource_location']}")
        
        parts.append(f"on {proposal['proposed_date']} at {proposal['proposed_time']}")
        parts.append(f"for {proposal['proposed_duration']} hour(s)")
        
        if proposal.get('resource_capacity'):
            parts.append(f"(Capacity: {proposal['resource_capacity']} people)")
        
        if proposal.get('resource_equipment'):
            parts.append(f"Equipment: {proposal['resource_equipment']}")
        
        availability_note = "This resource is currently available" if proposal.get('available') else f"This resource is {proposal.get('utilization', 0)}% utilized"
        parts.append(availability_note)
        
        return " ".join(parts)

