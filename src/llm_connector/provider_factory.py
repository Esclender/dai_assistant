"""Factory for creating LLM providers."""
import os
from typing import Dict, Type, List, Set
from .providers.base import LLMProvider, ProviderConfig
from .providers.openai import OpenAIProvider
from .exceptions import InvalidProviderError, ConfigurationError

class LLMProviderFactory:
    """Factory for creating and managing LLM providers."""

    # Registry of provider implementations
    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        # Add more providers here
    }

    # Provider-specific environment variable mappings
    _env_mappings = {
        "openai": {
            "api_key": "OPENAI_API_KEY",
            "organization_id": "OPENAI_ORG_ID"
        },
        # Add more provider mappings here
    }

    # Supported models for each provider
    _supported_models: Dict[str, Set[str]] = {
        "openai": {
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        }
        # Add more provider models here
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider], models: Set[str]) -> None:
        """Register a new provider implementation.
        
        Args:
            name: Provider identifier
            provider_class: Provider class implementation
            models: Set of supported models
        """
        cls._providers[name] = provider_class
        cls._supported_models[name] = models

    @classmethod
    def create_provider(cls, provider_name: str, model: str) -> LLMProvider:
        """Create a provider instance.
        
        Args:
            provider_name: Name of the provider to create
            model: Model to validate
            
        Returns:
            Provider instance
            
        Raises:
            InvalidProviderError: If provider is not supported
            ConfigurationError: If provider configuration is invalid
        """
        if provider_name not in cls._providers:
            raise InvalidProviderError(f"Provider {provider_name} is not supported")

        if model not in cls._supported_models.get(provider_name, set()):
            raise InvalidProviderError(f"Model {model} is not supported by {provider_name}")

        # Get provider class and environment variables
        provider_class = cls._providers[provider_name]
        env_vars = cls._env_mappings.get(provider_name, {})

        # Create configuration from environment
        config_kwargs = {}
        for config_key, env_var in env_vars.items():
            value = os.getenv(env_var)
            if value:
                config_kwargs[config_key] = value

        if not config_kwargs.get("api_key"):
            raise ConfigurationError(
                f"API key not found in environment variable {env_vars['api_key']}. "
                f"Please set {env_vars['api_key']} in your .env file."
            )

        # Create provider instance
        return provider_class(ProviderConfig(**config_kwargs))

    @classmethod
    def list_models(cls, provider_name: str = None) -> Dict[str, List[str]]:
        """List available models for providers.
        
        Args:
            provider_name: Optional provider name to filter
            
        Returns:
            Dict mapping provider names to their available models
        """
        if provider_name:
            if provider_name not in cls._supported_models:
                return {provider_name: ["Provider not found"]}
            return {provider_name: sorted(cls._supported_models[provider_name])}
        
        return {
            name: sorted(models)
            for name, models in cls._supported_models.items()
        }

    @classmethod
    def validate_model(cls, provider_name: str, model: str) -> bool:
        """Validate if a model is supported by a provider.
        
        Args:
            provider_name: Name of the provider
            model: Model to validate
            
        Returns:
            True if model is supported, False otherwise
        """
        return model in cls._supported_models.get(provider_name, set())