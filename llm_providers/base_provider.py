"""
Base LLM Provider - Abstract base class following Strategy pattern
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers following Strategy pattern.
    Implements Open/Closed Principle - open for extension, closed for modification.
    """
    
    def __init__(self, model: str, **kwargs):
        """
        Initialize the LLM provider.
        
        Args:
            model: Model name to use
            **kwargs: Additional provider-specific configuration
        """
        self.model = model
        self.config = kwargs
        self._llm = None
    
    @abstractmethod
    def _initialize_llm(self) -> Any:
        """
        Initialize the underlying LLM instance.
        Must be implemented by concrete providers.
        
        Returns:
            Initialized LLM instance
        """
        pass
    
    @abstractmethod
    def _validate_config(self) -> bool:
        """
        Validate provider-specific configuration.
        Must be implemented by concrete providers.
        
        Returns:
            True if configuration is valid
        """
        pass
    
    def get_llm(self):
        """
        Get the LLM instance, initializing if necessary.
        Implements Lazy Loading pattern.
        
        Returns:
            LLM instance
        """
        if self._llm is None:
            if not self._validate_config():
                raise ValueError(f"Invalid configuration for {self.__class__.__name__}")
            self._llm = self._initialize_llm()
        return self._llm
    
    def invoke(self, messages: List[Any]) -> str:
        """
        Invoke the LLM with messages.
        
        Args:
            messages: List of messages (SystemMessage, HumanMessage, etc.)
            
        Returns:
            LLM response as string
        """
        llm = self.get_llm()
        response = llm.invoke(messages)
        return response.content
    
    def invoke_simple(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Convenience method for simple prompt invocation.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLM response as string
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        return self.invoke(messages)
    
    @classmethod
    @abstractmethod
    def get_supported_models(cls) -> List[str]:
        """
        Get list of supported models for this provider.
        Must be implemented by concrete providers.
        
        Returns:
            List of supported model names
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_provider_name(cls) -> str:
        """
        Get the provider name.
        Must be implemented by concrete providers.
        
        Returns:
            Provider name
        """
        pass 