"""
Local Models Provider Implementation (Ollama-based)
"""

import os
from typing import List
from langchain_community.llms.ollama import Ollama
from .base_provider import BaseLLMProvider


class LocalProvider(BaseLLMProvider):
    """
    Local LLM provider implementation using Ollama.
    Supports popular local models for code review.
    """
    
    def _validate_config(self) -> bool:
        """Validate local configuration."""
        # Check if base URL is provided or use default
        base_url = self.config.get('base_url', os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434'))
        self.config['base_url'] = base_url
        return True
    
    def _initialize_llm(self):
        """Initialize Ollama instance."""
        return Ollama(
            model=self.model,
            base_url=self.config.get('base_url', 'http://127.0.0.1:11434'),
            **{k: v for k, v in self.config.items() if k != 'base_url'}
        )
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get supported popular local models."""
        return [
            "deepseek-r1",      # DeepSeek R1 - excellent for code
            "llama3",           # Meta's Llama 3
            "codellama",        # Code-specific Llama
            "mistral",          # Mistral 7B
            "mixtral",          # Mixtral 8x7B
            "neural-chat",      # Intel's Neural Chat
            "qwen2",            # Alibaba's Qwen2
            "phi3"              # Microsoft's Phi-3
        ]
    
    @classmethod
    def get_provider_name(cls) -> str:
        """Get provider name."""
        return "local" 