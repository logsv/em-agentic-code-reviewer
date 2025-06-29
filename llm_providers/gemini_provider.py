"""
Google Gemini Provider Implementation
"""

import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from .base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini LLM provider implementation.
    """
    
    def _validate_config(self) -> bool:
        """Validate Gemini configuration."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return True
    
    def _initialize_llm(self):
        """Initialize Gemini ChatGoogleGenerativeAI instance."""
        api_key = os.getenv("GEMINI_API_KEY")
        return ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=api_key,
            **self.config
        )
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get supported Gemini models."""
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
    
    @classmethod
    def get_provider_name(cls) -> str:
        """Get provider name."""
        return "gemini" 