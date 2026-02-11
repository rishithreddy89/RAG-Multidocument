"""
Client for interacting with external LLM API.
"""

import httpx
from typing import Optional
from config import LLM_API_URL


class OllamaClient:
    """Handles communication with external LLM API server."""
    
    def __init__(self, api_url: str = LLM_API_URL):
        """
        Initialize LLM API client.
        
        Args:
            api_url: URL of the external LLM API endpoint
        """
        self.api_url = api_url
    
    async def generate(self, prompt: str, stream: bool = False) -> str:
        """
        Send a prompt to external LLM API and get response.
        
        Args:
            prompt: User message/question
            stream: Whether to stream response (not used in Phase 1)
        
        Returns:
            Generated response from LLM
        
        Raises:
            httpx.HTTPError: If LLM API service is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "prompt": prompt
                }
                
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                # Try different response formats
                return result.get("response", result.get("output", result.get("text", str(result))))
        
        except httpx.ConnectError:
            raise Exception(
                f"Cannot connect to LLM API at {self.api_url}. "
                "Make sure the API endpoint is accessible."
            )
        except httpx.HTTPError as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    async def chat(self, message: str) -> str:
        """
        Simple chat interface for Phase 1.
        
        In Phase 2, this will be enhanced with RAG:
        TODO: Add document retrieval before generating response
        TODO: Include retrieved context in prompt
        TODO: Add citation to sources in response
        
        Args:
            message: User's question
        
        Returns:
            LLM response
        """
        # Phase 1: Direct pass-through to LLM
        return await self.generate(message)


# Global client instance
ollama_client = OllamaClient()
