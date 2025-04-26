from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def __init__(self, api_key: str, model_name: str):
        """Initialize provider with API key and model name."""
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key."""
        pass

    @abstractmethod
    def validate_model(self) -> bool:
        """Validate if the selected model is supported by this provider."""
        pass

    @abstractmethod
    async def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the LLM and get a response."""
        pass