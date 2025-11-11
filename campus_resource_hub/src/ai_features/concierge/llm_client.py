"""
LLM Client - Wrapper for OpenAI API integration.
"""
import os
import openai
from typing import Optional


class LLMClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", timeout: int = 30):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model name (default: gpt-4o-mini)
            timeout: Request timeout in seconds
        """
        api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in your .env file or environment.")
        
        self.client = openai.OpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        self.timeout = timeout
    
    def generate_response(self, prompt: str, temperature: float = 0.7, 
                         max_tokens: int = 500) -> Optional[str]:
        """
        Generate response from LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response or None if error
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except openai.AuthenticationError as e:
            print(f"OpenAI Authentication Error: Invalid API key. {e}")
            return None
        except openai.RateLimitError as e:
            print(f"OpenAI Rate Limit Error: {e}")
            return None
        except openai.APIError as e:
            print(f"OpenAI API Error: {e}")
            return None
        except Exception as e:
            print(f"LLM Error: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if LLM is available.
        
        Returns:
            True if LLM is available, False otherwise
        """
        try:
            # Test with a simple prompt
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False
    
    def summarize_context(self, context: str, max_length: int = 1000) -> str:
        """
        Summarize context if it's too long.
        
        Args:
            context: Context text to summarize
            max_length: Maximum desired length
            
        Returns:
            Summarized context
        """
        if len(context) <= max_length:
            return context
        
        # Use LLM to summarize
        summary_prompt = f"""Summarize the following context while preserving key information about resources, bookings, and system capabilities. Keep it under {max_length} characters.

Context:
{context}

Summary:"""
        
        summary = self.generate_response(summary_prompt, temperature=0.3, max_tokens=200)
        return summary if summary else context[:max_length] + "..."

