"""
Response Generator - Formats LLM responses with links and action buttons.
"""
import re
from typing import Dict, List, Optional, Tuple
from .llm_client import LLMClient
from .context_summarizer import ContextSummarizer
from .role_filter import RoleFilter
from .booking_proposer import BookingProposer


class ResponseGenerator:
    """Generates formatted responses with links and actions."""
    
    def __init__(self):
        """Initialize response generator."""
        self.llm_client = LLMClient()
        self.context_summarizer = ContextSummarizer()
        self.role_filter = RoleFilter()
        self.booking_proposer = BookingProposer()
    
    def generate_response(self, query: str, user_role: str, user_id: int,
                         doc_chunks: List[Dict], db_results: List[Dict]) -> Dict:
        """
        Generate formatted response from LLM.
        
        Args:
            query: User query
            user_role: User role
            user_id: Current user ID
            doc_chunks: Retrieved document chunks
            db_results: Retrieved database results
            
        Returns:
            Response dictionary with text, links, and actions
        """
        # Format context
        doc_context, db_context = self.context_summarizer.format_context(doc_chunks, db_results)
        
        # Build prompt
        prompt = self._build_prompt(query, doc_context, db_context, user_role)
        
        # Log prompt length for debugging
        import logging
        prompt_length = len(prompt)
        logging.info(f"Generated prompt length: {prompt_length} characters")
        if prompt_length > 15000:
            logging.warning(f"Prompt is very long ({prompt_length} chars), may cause issues")
        
        # Generate LLM response
        try:
            llm_response = self.llm_client.generate_response(prompt, max_tokens=1000)
        except ValueError as e:
            # API key, configuration error, or rate limit error
            import logging
            error_msg = str(e)
            logging.error(f"LLM error: {error_msg}", exc_info=True)
            
            # Check if it's a rate limit error
            if "rate limit" in error_msg.lower() or "rate_limit" in error_msg.lower():
                return {
                    'text': 'I\'m currently experiencing high demand. Please wait a moment (about 20-30 seconds) and try again. The OpenAI API has rate limits to ensure fair usage.',
                    'links': [],
                    'booking_proposal': None,
                    'sources': []
                }
            # Check if it's an API key error
            elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                return {
                    'text': f'Configuration error: {error_msg}. Please check that the OpenAI API key is properly configured.',
                    'links': [],
                    'booking_proposal': None,
                    'sources': []
                }
            else:
                return {
                    'text': f'Configuration error: {error_msg}. Please try again later.',
                    'links': [],
                    'booking_proposal': None,
                    'sources': []
                }
        except Exception as e:
            import logging
            logging.error(f"Error generating LLM response: {e}", exc_info=True)
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"Full traceback: {error_details}")
            return {
                'text': f'I encountered an error while processing your request: {str(e)}. Please try again later or contact support if the issue persists.',
                'links': [],
                'booking_proposal': None,
                'sources': []
            }
        
        if not llm_response:
            import logging
            logging.warning("LLM returned None/empty response. This could indicate an API error, rate limit, or network issue.")
            # Try to get more information about why it failed
            # The error should have been logged in llm_client.generate_response
            return {
                'text': 'I apologize, but I\'m having trouble processing your request right now. The OpenAI API may be unavailable, rate-limited, or there was a network error. Please wait a moment and try again.',
                'links': [],
                'booking_proposal': None,
                'sources': []
            }
        
        # Extract links and format response
        response_text, links = self._extract_links(llm_response, db_results)
        
        # Filter admin links
        response_text = self.role_filter.filter_response_links(response_text, user_role)
        
        # Check for booking intent
        booking_proposal = self.booking_proposer.propose_booking(query, user_role, db_results)
        
        # Extract sources
        sources = self._extract_sources(doc_chunks, db_results)
        
        return {
            'text': response_text,
            'links': links,
            'booking_proposal': booking_proposal,
            'sources': sources
        }
    
    def _build_prompt(self, query: str, doc_context: str, db_context: str, 
                     user_role: str) -> str:
        """
        Build prompt for LLM.
        
        Args:
            query: User query
            doc_context: Document context
            db_context: Database context
            user_role: User role
            
        Returns:
            Formatted prompt
        """
        # Build context sections
        context_sections = []
        if doc_context and doc_context.strip():
            context_sections.append(f"Context from documentation:\n{doc_context}")
        if db_context and db_context.strip():
            context_sections.append(f"Context from database:\n{db_context}")
        
        full_context = "\n\n".join(context_sections) if context_sections else "No specific context available."
        
        # Check if we have context
        has_context = full_context and full_context.strip() and full_context != "No specific context available."
        
        if has_context:
            prompt = f"""You are a helpful assistant for the Campus Resource Hub - a system for booking campus resources like study rooms, computer labs, AV equipment, event spaces, and other facilities.

The following context contains detailed information about CAMPUS RESOURCES (study rooms, labs, equipment, spaces) and the BOOKING PROCESS for these resources. USE THIS CONTEXT to answer the user's question.

{full_context}

User Question: {query}

IMPORTANT INSTRUCTIONS:
- The context above is about CAMPUS RESOURCES (study rooms, computer labs, equipment, spaces) and how to BOOK them
- This is NOT about LLM providers, AI models, or API keys - ignore any information about Ollama, OpenAI, Gemini, GPT models, or API keys
- You MUST use the context about campus resources and booking to answer the question
- For booking questions: Explain the booking process for campus resources (study rooms, labs, etc.), requirements, approval workflow, and how to create bookings based on the context
- For resource questions: Describe what campus resources are (study rooms, labs, equipment), their fields, categories, and how to find/book them based on the context
- Be specific and reference details from the context (e.g., "According to the booking process, you need to...")
- Include resource names in your answer when available from the database context
- Format resource links as: [Resource Name](resource_id) where resource_id is the numeric ID
- If the user wants to book something, explain the steps they need to take based on the booking process in the context
- Never make up specific resource names, locations, or capabilities that aren't in the context
- Respect user role: {user_role}
- Be helpful, friendly, and actionable
- Focus ONLY on campus resources and booking - ignore any LLM/AI provider information

Answer:"""
        else:
            prompt = f"""You are a helpful assistant for the Campus Resource Hub. Answer the user's question.

User Question: {query}

Instructions:
- Provide helpful guidance about the Campus Resource Hub system
- If you don't have specific information, provide general guidance
- Be helpful and friendly

Answer:"""
        return prompt
    
    def _extract_links(self, response: str, db_results: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        Extract resource links from response and create link objects.
        
        Args:
            response: LLM response text
            db_results: Database results
            
        Returns:
            Tuple of (formatted_response, links_list)
        """
        links = []
        
        # Find resource names in response and match to database results
        for result in db_results:
            resource_name = result.get('title') or result.get('resource', '')
            if resource_name:
                # Look for resource name in response
                pattern = re.escape(resource_name)
                if re.search(pattern, response, re.IGNORECASE):
                    resource_id = result.get('id') or result.get('resource_id')
                    if resource_id:
                        links.append({
                            'text': resource_name,
                            'url': f'/resources/{resource_id}',
                            'type': 'resource'
                        })
        
        # Replace markdown-style links with HTML links
        def replace_link(match):
            link_text = match.group(1)
            resource_id = match.group(2)
            # Check if this resource exists in results
            for result in db_results:
                if str(result.get('id')) == resource_id or str(result.get('resource_id')) == resource_id:
                    return f'<a href="/resources/{resource_id}" class="concierge-link">{link_text}</a>'
            return link_text  # Return plain text if resource not found
        
        formatted_response = re.sub(r'\[([^\]]+)\]\((\d+)\)', replace_link, response)
        
        return formatted_response, links
    
    def _extract_sources(self, doc_chunks: List[Dict], db_results: List[Dict]) -> List[str]:
        """
        Extract source citations.
        
        Args:
            doc_chunks: Document chunks
            db_results: Database results
            
        Returns:
            List of source strings
        """
        sources = []
        
        # Document sources
        doc_sources = set(chunk.get('source', '') for chunk in doc_chunks)
        sources.extend([f"Document: {src}" for src in doc_sources if src])
        
        # Database sources (resource names)
        resource_sources = set(result.get('title', '') for result in db_results if result.get('title'))
        sources.extend([f"Resource: {src}" for src in resource_sources if src])
        
        return sources

