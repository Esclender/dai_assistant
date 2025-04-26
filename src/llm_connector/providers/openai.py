"""OpenAI provider implementation."""
from typing import Dict, Any, Optional, List
import asyncio
from openai import AsyncOpenAI
from openai.types.error import APIError as OpenAIError

from .base import LLMProvider, ProviderConfig, TokenUsage
from ..exceptions import (
    ConfigurationError, UnsupportedModelError, APIError,
    AuthenticationError, RateLimitError
)

class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""

    # Supported models
    SUPPORTED_MODELS = {
        "gpt-4": "gpt-4",
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-3.5-turbo": "gpt-3.5-turbo"
    }

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            organization=config.organization_id,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.config.api_key:
            raise ConfigurationError("OpenAI API key is required")

    async def send_message(self,
                          message: str,
                          model: str,
                          temperature: float = 0.7,
                          max_tokens: Optional[int] = None,
                          stop_sequences: Optional[List[str]] = None,
                          **kwargs) -> Dict[str, Any]:
        """Send message to OpenAI API."""
        if not self.validate_model(model):
            raise UnsupportedModelError(f"Model {model} is not supported by OpenAI")

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop_sequences,
                **kwargs
            )

            usage = response.usage
            return {
                "message": response.choices[0].message.content,
                "usage": TokenUsage(
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens
                ),
                "finish_reason": response.choices[0].finish_reason
            }

        except OpenAIError as e:
            if "rate limit" in str(e).lower():
                raise RateLimitError(str(e))
            elif "authentication" in str(e).lower():
                raise AuthenticationError(str(e))
            else:
                raise APIError(str(e), getattr(e, "status_code", None))

    async def get_token_count(self, text: str, model: str) -> int:
        """Get token count for text using tiktoken."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except ImportError:
            raise ConfigurationError("tiktoken package is required for token counting")
        except KeyError:
            raise UnsupportedModelError(f"Model {model} not found in tiktoken")

    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models."""
        return list(self.SUPPORTED_MODELS.keys())

    def validate_model(self, model: str) -> bool:
        """Check if model is supported."""
        return model in self.SUPPORTED_MODELS 