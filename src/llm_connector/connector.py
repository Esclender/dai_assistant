"""
LLM Connector Module.
Handles requests to external LLM APIs like OpenAI, Anthropic, etc.
"""
import os
import json
import asyncio
from typing import Dict, Any, Optional, List
import httpx
from rich.console import Console

console = Console()

class LLMConnector:
    """
    Connector for Large Language Model APIs.
    
    Handles API requests to different providers (OpenAI, Anthropic, etc.).
    Manages token limits, usage tracking, and provider-specific behaviors.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM connector with configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.api_keys = {}
        self.usage_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "requests": 0
        }
        self.client = httpx.AsyncClient(timeout=60.0)
        
    def configure_provider(self, provider: str, api_key: str) -> None:
        """
        Configure a specific LLM provider with API key.
        
        Args:
            provider: Provider name (e.g., "openai", "anthropic")
            api_key: API key for the provider
        """
        self.api_keys[provider] = api_key
    
    async def generate(self, prompt: str, model: str = "gpt-4-turbo", 
                      max_tokens: int = 1000, temperature: float = 0.7, 
                      **kwargs) -> str:
        """
        Generate text using an LLM model.
        
        Args:
            prompt: The prompt to send to the LLM
            model: The model name to use
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Generated text from the LLM
        """
        provider = self._get_provider_from_model(model)
        
        if provider == "openai":
            return await self._generate_openai(prompt, model, max_tokens, temperature, **kwargs)
        elif provider == "anthropic":
            return await self._generate_anthropic(prompt, model, max_tokens, temperature, **kwargs)
        else:
            raise ValueError(f"Unsupported provider for model: {model}")
    
    async def _generate_openai(self, prompt: str, model: str, 
                              max_tokens: int, temperature: float, 
                              **kwargs) -> str:
        """
        Generate text using OpenAI API.
        
        Args:
            prompt: The prompt to send
            model: OpenAI model name
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        api_key = self.api_keys.get("openai")
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not configured")
        
        # Prepare request data
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        # TODO: Add proper error handling and retries
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # Update usage statistics
            self.usage_stats["requests"] += 1
            if "usage" in result:
                self.usage_stats["total_tokens"] += result["usage"]["total_tokens"]
                # TODO: Calculate cost based on model and tokens
            
            # Extract and return the generated text
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            console.print(f"[bold red]Error in OpenAI API call:[/bold red] {str(e)}")
            # Implement retry logic here
            raise
    
    async def _generate_anthropic(self, prompt: str, model: str, 
                                 max_tokens: int, temperature: float, 
                                 **kwargs) -> str:
        """
        Generate text using Anthropic API.
        
        Args:
            prompt: The prompt to send
            model: Anthropic model name
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        api_key = self.api_keys.get("anthropic")
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not configured")
        
        # Prepare request data for Anthropic's Claude
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "anthropic-version": "2023-06-01"  # Update as needed
        }
        
        try:
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # Update usage statistics
            self.usage_stats["requests"] += 1
            # TODO: Update token counting for Anthropic
            
            # Extract and return the generated text
            return result["content"][0]["text"]
        
        except Exception as e:
            console.print(f"[bold red]Error in Anthropic API call:[/bold red] {str(e)}")
            # Implement retry logic here
            raise
    
    def _get_provider_from_model(self, model: str) -> str:
        """
        Determine the provider from the model name.
        
        Args:
            model: Model name
            
        Returns:
            Provider name
        """
        if model.startswith(("gpt-", "text-davinci")):
            return "openai"
        elif model.startswith(("claude-")):
            return "anthropic"
        else:
            # Default to OpenAI
            return "openai"
    
    def get_token_usage(self) -> Dict[str, Any]:
        """
        Get token usage statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        return self.usage_stats
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
