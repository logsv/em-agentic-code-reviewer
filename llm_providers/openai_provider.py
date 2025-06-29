"""
OpenAI Provider Implementation
"""

import os
from typing import List
from langchain_openai import ChatOpenAI
from .base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider implementation.
    """
    
    def _validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return True
    
    def _initialize_llm(self):
        """Initialize OpenAI ChatOpenAI instance."""
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=self.model,
            api_key=api_key,
            **self.config
        )
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get supported OpenAI models."""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
    
    @classmethod
    def get_provider_name(cls) -> str:
        """Get provider name."""
        return "openai" 