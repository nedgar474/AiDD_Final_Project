"""
Context Retriever - Loads and searches markdown files from docs/context/ folder.
"""
import os
import re
from typing import List, Dict, Tuple
from pathlib import Path


class ContextRetriever:
    """Retrieves relevant context from documentation files."""
    
    def __init__(self, context_folder: str = None):
        """
        Initialize context retriever.
        
        Args:
            context_folder: Path to docs/context folder (default: auto-detect)
        """
        if context_folder is None:
            # Auto-detect context folder relative to project root
            current_dir = Path(__file__).resolve()
            # Navigate from src/ai_features/concierge/ to project root
            project_root = current_dir.parent.parent.parent.parent
            context_folder = project_root / 'docs' / 'context'
        
        self.context_folder = Path(context_folder)
        self.documents_cache = {}
        self._load_documents()
    
    def _load_documents(self):
        """Load all markdown files from context folder."""
        if not self.context_folder.exists():
            return
        
        # Recursively find all .md files in docs/context/
        for md_file in self.context_folder.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Store relative path and content
                rel_path = md_file.relative_to(self.context_folder.parent.parent)
                self.documents_cache[str(rel_path)] = {
                    'content': content,
                    'chunks': self._chunk_document(content)
                }
            except Exception as e:
                print(f"Error loading {md_file}: {e}")
                continue
    
    def _chunk_document(self, content: str) -> List[Dict[str, str]]:
        """
        Chunk document by sections/paragraphs.
        
        Args:
            content: Document content
            
        Returns:
            List of chunks with text and metadata
        """
        chunks = []
        
        # Split by markdown headers (##, ###, etc.) and paragraphs
        # First, split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\n+', content)
        
        current_section = "Introduction"
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if paragraph is a header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', para, re.MULTILINE)
            if header_match:
                current_section = header_match.group(2).strip()
                continue
            
            # Create chunk
            chunks.append({
                'text': para,
                'section': current_section,
                'length': len(para)
            })
        
        return chunks
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, any]]:
        """
        Search documents for relevant context.
        
        Args:
            query: User query
            top_k: Number of top results to return
            
        Returns:
            List of relevant chunks with scores
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Expand query with synonyms and related terms
        query_expansions = {
            'book': ['booking', 'reserve', 'reservation', 'schedule', 'appointment'],
            'booking': ['book', 'reserve', 'reservation', 'schedule', 'appointment'],
            'room': ['space', 'resource', 'facility'],
            'study': ['study', 'workspace', 'learning'],
            'process': ['workflow', 'procedure', 'steps', 'how to'],
            'help': ['assistance', 'guide', 'instructions', 'how'],
            'available': ['availability', 'free', 'open', 'vacant'],
        }
        
        # Add expanded terms to query words
        expanded_query_words = set(query_words)
        for word in query_words:
            if word in query_expansions:
                expanded_query_words.update(query_expansions[word])
        
        # Determine if this is a booking/resource query (not LLM provider query)
        is_booking_query = any(word in query_lower for word in ['book', 'booking', 'reserve', 'room', 'study', 'resource', 'facility', 'space'])
        is_llm_query = any(word in query_lower for word in ['ollama', 'openai', 'gpt', 'gemini', 'llm', 'model', 'api key'])
        
        results = []
        
        for doc_path, doc_data in self.documents_cache.items():
            # Boost score for AI_Concierge_Prompt_Context.md for booking/resource queries
            doc_boost = 1.0
            if is_booking_query and 'AI_Concierge_Prompt_Context.md' in doc_path:
                doc_boost = 3.0  # Strongly prefer the booking context file
            elif is_llm_query and 'development_options.md' in doc_path:
                doc_boost = 2.0  # Prefer development_options for LLM queries
            elif is_booking_query and 'development_options.md' in doc_path:
                # Penalize development_options for booking queries (it's about LLM providers)
                doc_boost = 0.3
            
            for chunk in doc_data['chunks']:
                chunk_text_lower = chunk['text'].lower()
                chunk_words = set(chunk_text_lower.split())
                
                # Filter out LLM provider chunks for booking queries
                if is_booking_query and any(llm_term in chunk_text_lower for llm_term in ['ollama', 'openai', 'gpt-4', 'gemini', 'api key', 'llm provider', 'model selection']):
                    # Skip chunks about LLM providers when user is asking about booking
                    continue
                
                # Calculate match score
                # 1. Exact word matches (higher weight)
                exact_matches = len(query_words.intersection(chunk_words))
                # 2. Expanded term matches (lower weight)
                expanded_matches = len(expanded_query_words.intersection(chunk_words)) - exact_matches
                
                # Total matches with weighting
                total_matches = exact_matches * 2 + expanded_matches
                
                if total_matches > 0:
                    # Improved scoring: consider match ratio, chunk length, and section relevance
                    match_ratio = total_matches / max(len(query_words), 1)
                    # Prefer chunks with higher match density (more matches per word)
                    density_score = total_matches / max(len(chunk_words), 1)
                    # Prefer shorter, more focused chunks (but not too short)
                    length_penalty = 1.0 / max(len(chunk['text']) / 500, 1.0)  # Optimal around 500 chars
                    
                    # Boost score for relevant sections
                    section_boost = 1.0
                    section_lower = chunk.get('section', '').lower()
                    if any(term in section_lower for term in ['booking', 'resource', 'process', 'overview']):
                        section_boost = 1.5
                    # Penalize LLM-related sections for booking queries
                    if is_booking_query and any(term in section_lower for term in ['llm', 'openai', 'ollama', 'gemini', 'model', 'api']):
                        section_boost = 0.2
                    
                    # Final score with document boost
                    score = match_ratio * density_score * length_penalty * section_boost * doc_boost
                    
                    results.append({
                        'text': chunk['text'],
                        'source': doc_path,
                        'section': chunk.get('section', ''),
                        'score': score
                    })
        
        # Sort by score (highest first) and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_all_documents(self) -> List[str]:
        """Get list of all loaded document paths."""
        return list(self.documents_cache.keys())

