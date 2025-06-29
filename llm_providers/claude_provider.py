"""
Anthropic Claude Provider Implementation
"""

import os
from typing import List
from langchain_anthropic import ChatAnthropic
from .base_provider import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """
    Anthropic Claude LLM provider implementation.
    """
    
    def _validate_config(self) -> bool:
        """Validate Claude configuration."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        return True
    
    def _initialize_llm(self):
        """Initialize Claude ChatAnthropic instance."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        return ChatAnthropic(
            model=self.model,
            anthropic_api_key=api_key,
            **self.config
        )
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get supported Claude models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]
    
    @classmethod
    def get_provider_name(cls) -> str:
        """Get provider name."""
        return "claude" 