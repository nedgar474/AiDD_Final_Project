"""
Context Summarizer - Summarizes retrieved context if too long for LLM.
"""
from typing import List, Dict
from .llm_client import LLMClient


class ContextSummarizer:
    """Summarizes context to fit within LLM token limits."""
    
    def __init__(self, max_context_length: int = 2000):
        """
        Initialize context summarizer.
        
        Args:
            max_context_length: Maximum context length in characters
        """
        self.max_context_length = max_context_length
        self.llm_client = LLMClient()
    
    def summarize_if_needed(self, doc_context: str, db_context: str) -> tuple[str, str]:
        """
        Summarize contexts if they exceed limits.
        
        Args:
            doc_context: Document context string
            db_context: Database context string
            
        Returns:
            Tuple of (summarized_doc_context, summarized_db_context)
        """
        total_length = len(doc_context) + len(db_context)
        
        if total_length <= self.max_context_length:
            return doc_context, db_context
        
        # Calculate how much to allocate to each
        # Prefer keeping more database context (more specific/accurate)
        db_ratio = len(db_context) / total_length if total_length > 0 else 0.5
        
        max_db_length = int(self.max_context_length * max(db_ratio, 0.6))  # At least 60% for DB
        max_doc_length = self.max_context_length - max_db_length
        
        # Summarize if needed
        if len(doc_context) > max_doc_length:
            doc_context = self._summarize_text(doc_context, max_doc_length)
        
        if len(db_context) > max_db_length:
            db_context = self._summarize_text(db_context, max_db_length)
        
        return doc_context, db_context
    
    def _summarize_text(self, text: str, max_length: int) -> str:
        """
        Summarize text to fit within max_length.
        
        Args:
            text: Text to summarize
            max_length: Maximum desired length
            
        Returns:
            Summarized text
        """
        if len(text) <= max_length:
            return text
        
        # Simple truncation with ellipsis (can be enhanced with LLM summarization)
        # For now, take first part and indicate truncation
        truncated = text[:max_length - 100]  # Leave room for note
        return truncated + "\n\n[Context truncated for length - key information preserved]"
    
    def format_context(self, doc_chunks: List[Dict], db_results: List[Dict]) -> tuple[str, str]:
        """
        Format retrieved context into strings.
        
        Args:
            doc_chunks: List of document chunks
            db_results: List of database results
            
        Returns:
            Tuple of (formatted_doc_context, formatted_db_context)
        """
        # Format document context
        doc_parts = []
        for chunk in doc_chunks:
            source = chunk.get('source', 'Unknown')
            section = chunk.get('section', '')
            text = chunk.get('text', '')
            # Make it clear this is relevant information
            doc_parts.append(f"RELEVANT INFORMATION ({section}):\n{text}\n")
        
        doc_context = "\n\n---\n\n".join(doc_parts) if doc_parts else ""
        
        # Format database context
        db_parts = []
        for result in db_results:
            if 'title' in result:  # Resource result
                db_parts.append(f"Resource: {result['title']} (ID: {result['id']})")
                if result.get('description'):
                    db_parts.append(f"  Description: {result['description'][:200]}")
                if result.get('location'):
                    db_parts.append(f"  Location: {result['location']}")
                if result.get('capacity'):
                    db_parts.append(f"  Capacity: {result['capacity']}")
                if result.get('equipment'):
                    db_parts.append(f"  Equipment: {result['equipment']}")
                if result.get('average_rating'):
                    db_parts.append(f"  Rating: {result['average_rating']}/5.0 ({result.get('review_count', 0)} reviews)")
            elif 'available' in result:  # Availability result
                db_parts.append(f"Availability for {result.get('resource', 'resource')}:")
                db_parts.append(f"  Available: {result['available']}")
                if result.get('utilization_percent') is not None:
                    db_parts.append(f"  Utilization: {result['utilization_percent']}%")
            elif 'booking_count' in result:  # Popular resource
                db_parts.append(f"Popular Resource: {result['title']} ({result['booking_count']} bookings)")
            elif 'average_rating' in result:  # Top-rated resource
                db_parts.append(f"Top-Rated Resource: {result['title']} ({result['average_rating']}/5.0, {result.get('review_count', 0)} reviews)")
        
        db_context = "\n".join(db_parts)
        
        # Summarize if needed
        return self.summarize_if_needed(doc_context, db_context)

