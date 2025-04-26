"""
Error Handling Module

This module provides centralized error handling for the DAI Assistant system,
including detecting and handling issues like token limits, timeouts, invalid outputs,
and user interruptions.
"""

import logging
import sys
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, Union, List
import traceback
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Severity levels for errors in the system."""
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


class DAIError(Exception):
    """Base exception class for all DAI Assistant errors."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR):
        self.message = message
        self.severity = severity
        super().__init__(message)


class LLMError(DAIError):
    """Errors related to LLM interactions."""
    pass


class TokenLimitError(LLMError):
    """Error when LLM token limits are exceeded."""
    pass


class LLMTimeoutError(LLMError):
    """Error when LLM requests time out."""
    pass


class InvalidOutputError(DAIError):
    """Error when agent output doesn't match expected format."""
    pass


class AgentExecutionError(DAIError):
    """Error during agent execution."""
    pass


class UserInterruptError(DAIError):
    """Error when user interrupts the system."""
    def __init__(self, message: str = "Operation interrupted by user"):
        super().__init__(message, ErrorSeverity.INFO)


class ConfigurationError(DAIError):
    """Error in system configuration."""
    pass


class DependencyError(DAIError):
    """Error in dependency management."""
    pass


class ErrorHandler:
    """
    Central error handling system for DAI Assistant.
    Manages error detection, logging, and fallback strategies.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.error_registry: Dict[Type[Exception], Callable] = {}
        self.fallback_registry: Dict[Type[Exception], Callable] = {}
        self._register_default_handlers()
        self.last_error: Optional[Exception] = None

    def _register_default_handlers(self) -> None:
        """Register default error handlers."""
        # Register default handlers for common errors
        self.register_handler(TokenLimitError, self._handle_token_limit)
        self.register_handler(LLMTimeoutError, self._handle_timeout)
        self.register_handler(InvalidOutputError, self._handle_invalid_output)
        self.register_handler(UserInterruptError, self._handle_user_interrupt)
        
        # Register fallbacks
        self.register_fallback(TokenLimitError, self._fallback_token_limit)
        self.register_fallback(LLMTimeoutError, self._fallback_timeout)
        self.register_fallback(InvalidOutputError, self._fallback_invalid_output)

    def register_handler(self, error_type: Type[Exception], handler: Callable) -> None:
        """
        Register a handler function for a specific error type.
        
        Args:
            error_type: The type of exception to handle
            handler: Function to call when this error occurs
        """
        self.error_registry[error_type] = handler

    def register_fallback(self, error_type: Type[Exception], fallback: Callable) -> None:
        """
        Register a fallback strategy for a specific error type.
        
        Args:
            error_type: The type of exception to handle
            fallback: Function to call as fallback when this error occurs
        """
        self.fallback_registry[error_type] = fallback

    def handle(self, error: Exception) -> Any:
        """
        Handle an error based on its type.
        
        Args:
            error: The exception to handle
            
        Returns:
            Result of the error handler, if any
        """
        self.last_error = error
        
        # Find the most specific handler for this error type
        for error_type, handler in self.error_registry.items():
            if isinstance(error, error_type):
                return handler(error)
        
        # If no specific handler, use generic handling
        return self._handle_generic(error)

    def fallback(self, error: Exception) -> Any:
        """
        Execute fallback strategy for an error.
        
        Args:
            error: The exception to find a fallback for
            
        Returns:
            Result of the fallback function, if any
        """
        # Find the most specific fallback for this error type
        for error_type, fallback_fn in self.fallback_registry.items():
            if isinstance(error, error_type):
                return fallback_fn(error)
                
        # If no specific fallback, use generic fallback
        return self._fallback_generic(error)

    def _handle_token_limit(self, error: TokenLimitError) -> None:
        """Handle token limit exceeded errors."""
        logger.warning(f"Token limit exceeded: {error.message}")
        if self.verbose:
            print(f"Token limit exceeded: {error.message}")

    def _handle_timeout(self, error: LLMTimeoutError) -> None:
        """Handle timeout errors."""
        logger.warning(f"LLM request timed out: {error.message}")
        if self.verbose:
            print(f"LLM request timed out. Retrying with adjusted parameters...")

    def _handle_invalid_output(self, error: InvalidOutputError) -> None:
        """Handle invalid output format errors."""
        logger.error(f"Invalid agent output: {error.message}")
        if self.verbose:
            print(f"Agent produced invalid output: {error.message}")

    def _handle_user_interrupt(self, error: UserInterruptError) -> None:
        """Handle user interruption."""
        logger.info(f"User interrupted: {error.message}")
        if self.verbose:
            print(f"\nOperation interrupted by user.")
        sys.exit(0)

    def _handle_generic(self, error: Exception) -> None:
        """Generic error handler for unregistered error types."""
        logger.error(f"Unexpected error: {str(error)}")
        logger.error(traceback.format_exc())
        if self.verbose:
            print(f"Unexpected error: {str(error)}")

    def _fallback_token_limit(self, error: TokenLimitError) -> Any:
        """Fallback strategy for token limit errors."""
        logger.info("Using fallback for token limit error: reducing context")
        return {"status": "retrying", "action": "reduce_context"}

    def _fallback_timeout(self, error: LLMTimeoutError) -> Any:
        """Fallback strategy for timeout errors."""
        logger.info("Using fallback for timeout error: retrying with backoff")
        return {"status": "retrying", "action": "backoff_retry"}

    def _fallback_invalid_output(self, error: InvalidOutputError) -> Any:
        """Fallback strategy for invalid output errors."""
        logger.info("Using fallback for invalid output: requesting simplified response")
        return {"status": "retrying", "action": "simplify_request"}

    def _fallback_generic(self, error: Exception) -> Any:
        """Generic fallback strategy."""
        logger.info("Using generic fallback strategy")
        return {"status": "error", "message": str(error)}


def retry(max_attempts: int = 3, backoff_factor: float = 1.5, 
          exceptions: List[Type[Exception]] = None):
    """
    Decorator for retrying functions that might fail.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        exceptions: List of exceptions to catch and retry
    """
    if exceptions is None:
        exceptions = [LLMTimeoutError, TokenLimitError]
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except tuple(exceptions) as e:
                    last_exception = e
                    if attempt < max_attempts:
                        wait_time = backoff_factor ** (attempt - 1)
                        logger.info(f"Retry attempt {attempt}/{max_attempts} after {wait_time:.2f}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts")
                        raise
            
            if last_exception:
                raise last_exception
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions) as e:
                    last_exception = e
                    if attempt < max_attempts:
                        wait_time = backoff_factor ** (attempt - 1)
                        logger.info(f"Retry attempt {attempt}/{max_attempts} after {wait_time:.2f}s")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts")
                        raise
            
            if last_exception:
                raise last_exception
        
        # Choose the right wrapper based on if the function is async or not
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Import here to avoid circular imports
import asyncio
