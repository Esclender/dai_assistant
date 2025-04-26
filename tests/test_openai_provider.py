"""Tests for OpenAI provider implementation."""
import pytest
import os
from llm_connector.provider_factory import LLMProviderFactory
from llm_connector.providers.base import ProviderConfig
from llm_connector.exceptions import (
    InvalidProviderError, ConfigurationError,
    AuthenticationError, RateLimitError
)
from dotenv import load_dotenv

load_dotenv()

# Test configuration
TEST_API_KEY = os.getenv("OPENAI_API_KEY", "test-key")
TEST_MODEL = "gpt-3.5-turbo"

@pytest.mark.asyncio
async def test_basic_api_communication():
    """Test basic message sending and response handling."""
    provider = LLMProviderFactory.create_provider("openai", TEST_MODEL)
    
    # Test simple message
    response = await provider.send_message(
        message="Hello, how are you?",
        model=TEST_MODEL
    )
    assert "message" in response
    assert "usage" in response
    assert response["usage"].total_tokens > 0
    
    # Test message with parameters
    response = await provider.send_message(
        message="Write a short story",
        model=TEST_MODEL,
        temperature=0.8,
        max_tokens=100
    )
    assert len(response["message"]) > 0

@pytest.mark.asyncio
async def test_error_handling():
    """Test various error scenarios."""
    provider = LLMProviderFactory.create_provider("openai", TEST_MODEL)
    
    # Test invalid model
    with pytest.raises(InvalidProviderError):
        await provider.send_message(
            message="Hello",
            model="invalid-model"
        )
    
    # Test invalid API key
    invalid_provider = provider.__class__(ProviderConfig(api_key="invalid-key"))
    with pytest.raises(AuthenticationError):
        await invalid_provider.send_message(
            message="Hello",
            model=TEST_MODEL
        )

@pytest.mark.asyncio
async def test_token_counting():
    """Test token counting functionality."""
    provider = LLMProviderFactory.create_provider("openai", TEST_MODEL)
    
    # Test basic text
    text = "Hello, world!"
    count = await provider.get_token_count(text, TEST_MODEL)
    assert count > 0
    
    # Test longer text
    long_text = "This is a longer text that should have more tokens. " * 10
    count = await provider.get_token_count(long_text, TEST_MODEL)
    assert count > 0

def test_model_validation():
    """Test model validation functionality."""
    # Test valid models
    assert LLMProviderFactory.validate_model("openai", "gpt-3.5-turbo")
    assert LLMProviderFactory.validate_model("openai", "gpt-4")
    
    # Test invalid models
    assert not LLMProviderFactory.validate_model("openai", "invalid-model")
    assert not LLMProviderFactory.validate_model("invalid-provider", "gpt-3.5-turbo")

def test_provider_factory():
    """Test provider factory functionality."""
    # Test list all models
    models = LLMProviderFactory.list_models()
    assert "openai" in models
    assert "gpt-3.5-turbo" in models["openai"]
    
    # Test list specific provider models
    openai_models = LLMProviderFactory.list_models("openai")
    assert "gpt-3.5-turbo" in openai_models["openai"]
    
    # Test invalid provider
    invalid_models = LLMProviderFactory.list_models("invalid-provider")
    assert invalid_models["invalid-provider"] == ["Provider not found"]

def test_configuration():
    """Test configuration handling."""
    # Test valid configuration
    config = ProviderConfig(api_key=TEST_API_KEY)
    provider = LLMProviderFactory.create_provider("openai", TEST_MODEL)
    assert provider.config.api_key == TEST_API_KEY
    
    # Test missing API key
    with pytest.raises(ConfigurationError):
        LLMProviderFactory.create_provider("openai", TEST_MODEL, api_key="") 