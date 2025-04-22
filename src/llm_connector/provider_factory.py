from .base_provider import BaseLLMProvider
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .exceptions import InvalidProviderError, UnsupportedModelError
from typing import Dict, Any, List, Optional
import os

class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider
    }
    
    @staticmethod
    def create_provider(provider_name: str, model_name: str) -> BaseLLMProvider:
        """Create a provider instance based on provider name and model."""
        if provider_name not in LLMProviderFactory.PROVIDERS:
            valid_providers = list(LLMProviderFactory.PROVIDERS.keys())
            raise InvalidProviderError(provider_name, valid_providers)
            
        provider_class = LLMProviderFactory.PROVIDERS[provider_name]
        api_key = os.getenv(f"{provider_name.upper()}_API_KEY")
        
        if not api_key:
            raise ValueError(f"API key not found for provider: {provider_name}")
            
        provider = provider_class(api_key, model_name)
        
        if not provider.validate_model():
            supported_models = list(provider_class.SUPPORTED_MODELS.keys())
            raise UnsupportedModelError(provider_name, model_name, supported_models)
            
        return provider
    
    @staticmethod
    def get_supported_models(provider_name: str) -> Dict[str, str]:
        """Get supported models for a provider."""
        if provider_name not in LLMProviderFactory.PROVIDERS:
            valid_providers = list(LLMProviderFactory.PROVIDERS.keys())
            raise InvalidProviderError(provider_name, valid_providers)
            
        provider_class = LLMProviderFactory.PROVIDERS[provider_name]
        return provider_class.SUPPORTED_MODELS
    
    @staticmethod
    def list_models(provider_name: Optional[str] = None) -> Dict[str, List[str]]:
        """List all available models for all providers or a specific provider."""
        models = {}
        
        if provider_name:
            if provider_name not in LLMProviderFactory.PROVIDERS:
                valid_providers = list(LLMProviderFactory.PROVIDERS.keys())
                raise InvalidProviderError(provider_name, valid_providers)
                
            provider_class = LLMProviderFactory.PROVIDERS[provider_name]
            models[provider_name] = list(provider_class.SUPPORTED_MODELS.keys())
        else:
            for name, provider_class in LLMProviderFactory.PROVIDERS.items():
                models[name] = list(provider_class.SUPPORTED_MODELS.keys())
                
        return models