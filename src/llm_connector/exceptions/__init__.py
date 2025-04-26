"""Exceptions for LLM connector."""

class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass

class InvalidProviderError(LLMProviderError):
    """Raised when provider is not supported."""
    pass

class UnsupportedModelError(LLMProviderError):
    """Raised when model is not supported by provider."""
    pass

class ConfigurationError(LLMProviderError):
    """Raised when provider configuration is invalid."""
    pass

class TokenLimitError(LLMProviderError):
    """Raised when token limit is exceeded."""
    pass

class RateLimitError(LLMProviderError):
    """Raised when rate limit is hit."""
    pass

class APIError(LLMProviderError):
    """Raised when API returns an error."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class AuthenticationError(LLMProviderError):
    """Raised when authentication fails."""
    pass

class NetworkError(LLMProviderError):
    """Raised when network communication fails."""
    pass

class TimeoutError(LLMProviderError):
    """Raised when request times out."""
    pass 