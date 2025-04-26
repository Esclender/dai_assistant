"""Base classes for LLM providers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    """Configuration for LLM providers."""
    api_key: str
    organization_id: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

@dataclass
class TokenUsage:
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider configuration."""
        pass

    @abstractmethod
    async def send_message(self, 
                          message: str, 
                          model: str, 
                          temperature: float = 0.7,
                          max_tokens: Optional[int] = None,
                          stop_sequences: Optional[List[str]] = None,
                          **kwargs) -> Dict[str, Any]:
        """Send a message to the LLM provider.
        
        Args:
            message: The input message/prompt
            model: Model identifier
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            stop_sequences: Sequences that stop generation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict containing response and metadata
        """
        pass

    @abstractmethod
    async def get_token_count(self, text: str, model: str) -> int:
        """Get token count for text.
        
        Args:
            text: Input text
            model: Model to use for counting
            
        Returns:
            Number of tokens
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass

    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Validate if model is available.
        
        Args:
            model: Model identifier to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass

class TokenManager:
    """Manages token usage and limits."""

    def __init__(self):
        self._usage: Dict[str, TokenUsage] = {}

    def add_usage(self, provider: str, model: str, usage: TokenUsage):
        """Add token usage for provider/model."""
        key = f"{provider}:{model}"
        if key not in self._usage:
            self._usage[key] = usage
        else:
            current = self._usage[key]
            self._usage[key] = TokenUsage(
                prompt_tokens=current.prompt_tokens + usage.prompt_tokens,
                completion_tokens=current.completion_tokens + usage.completion_tokens,
                total_tokens=current.total_tokens + usage.total_tokens,
                cost=current.cost + usage.cost
            )

    def get_usage(self, provider: str, model: str) -> Optional[TokenUsage]:
        """Get token usage for provider/model."""
        return self._usage.get(f"{provider}:{model}")

    def get_total_cost(self) -> float:
        """Get total cost across all providers/models."""
        return sum(usage.cost for usage in self._usage.values())

# Global token manager instance
token_manager = TokenManager() 