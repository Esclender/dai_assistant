class LLMProviderError(Exception):
    """Base class for LLM provider errors."""
    pass

class UnsupportedModelError(LLMProviderError):
    """Raised when an unsupported model is requested."""
    def __init__(self, provider: str, model: str, supported_models: list[str]):
        self.provider = provider
        self.model = model
        self.supported_models = supported_models
        
        message = f"Model '{model}' is not supported by {provider}.\n"
        message += "Supported models: " + ", ".join(supported_models)
        super().__init__(message)

class InvalidProviderError(LLMProviderError):
    """Raised when an invalid provider is requested."""
    def __init__(self, provider: str, valid_providers: list[str]):
        self.provider = provider
        self.valid_providers = valid_providers
        
        message = f"Provider '{provider}' is not supported.\n"
        message += "Valid providers: " + ", ".join(valid_providers)
        super().__init__(message)