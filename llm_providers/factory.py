"""
LLM Provider Factory - Factory pattern implementation
"""

from typing import Dict, Type
from .base_provider import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .claude_provider import ClaudeProvider
from .local_provider import LocalProvider


class LLMProviderFactory:
    """
    Factory class for creating LLM providers.
    Implements Factory pattern for provider instantiation.
    """
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "local": LocalProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, model: str = None, **kwargs) -> BaseLLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Name of the provider (openai, gemini, claude, local)
            model: Model name (optional, will use default if not provided)
            **kwargs: Additional configuration parameters
            
        Returns:
            LLM provider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            supported = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported provider: {provider_name}. Supported: {supported}")
        
        provider_class = cls._providers[provider_name]
        
        # Use default model if not provided
        if model is None:
            default_models = {
                "openai": "gpt-4",
                "gemini": "gemini-pro", 
                "claude": "claude-3-sonnet-20240229",
                "local": "deepseek-r1"
            }
            model = default_models[provider_name]
        
        return provider_class(model=model, **kwargs)
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of supported provider names."""
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_info(cls) -> Dict[str, Dict]:
        """Get information about all supported providers and their models."""
        info = {}
        for name, provider_class in cls._providers.items():
            info[name] = {
                "name": provider_class.get_provider_name(),
                "models": provider_class.get_supported_models(),
                "default_model": cls._get_default_model(name)
            }
        return info
    
    @classmethod
    def _get_default_model(cls, provider_name: str) -> str:
        """Get default model for provider."""
        defaults = {
            "openai": "gpt-4",
            "gemini": "gemini-pro",
            "claude": "claude-3-sonnet-20240229", 
            "local": "deepseek-r1"
        }
        return defaults.get(provider_name, "")
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]):
        """
        Register a new provider class.
        Allows for extension without modifying existing code (Open/Closed Principle).
        
        Args:
            name: Provider name
            provider_class: Provider class that extends BaseLLMProvider
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError("Provider class must extend BaseLLMProvider")
        cls._providers[name.lower()] = provider_class 