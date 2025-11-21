# Fix providers.py - add missing imports and error handling
"""
AI Provider Abstraction Layer

Defines a consistent interface for interacting with different AI providers
(OpenAI, Anthropic, Gemini) with a clean abstraction that hides provider-specific details.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple
import requests

logger = logging.getLogger(__name__)


@dataclass
class ProviderHealth:
    """Health status of a provider"""
    is_healthy: bool
    message: str
    error_type: Optional[str] = None  # 'auth', 'quota', 'rate_limit', 'connection', etc.
    details: Optional[Dict[str, Any]] = None


class ProviderError(Exception):
    """Base exception for provider-related errors"""
    pass


class ProviderAuthError(ProviderError):
    """Raised when API key is invalid or missing"""
    pass


class ProviderQuotaError(ProviderError):
    """Raised when quota is exceeded"""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when rate limit is exceeded"""
    pass


class ProviderConnectionError(ProviderError):
    """Raised when unable to connect to provider"""
    pass


class AIProvider(Protocol):
    """Protocol defining the interface all AI providers must implement"""

    name: str

    def is_configured(self) -> bool:
        """Check if provider has valid API key/credentials configured"""
        ...

    def test_connection(self) -> ProviderHealth:
        """Test connection to the provider with a lightweight call"""
        ...

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send a chat message to the provider

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model name to override default
            **kwargs: Additional provider-specific parameters

        Returns:
            Response dict with 'content' and provider-specific fields
        """
        ...


class OpenAIProvider:
    """OpenAI GPT provider implementation"""

    name = "openai"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key
            base_url: Optional custom base URL (for OpenAI-compatible APIs)
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client with proper error handling"""
        try:
            import openai
            if not self.api_key:
                raise ProviderAuthError("OpenAI API key is required")
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        except Exception as e:
            raise ProviderError(f"Failed to initialize OpenAI client: {e}")

    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return bool(self.api_key and self.client is not None)

    def test_connection(self) -> ProviderHealth:
        """Test connection to OpenAI API"""
        try:
            if not self.is_configured():
                return ProviderHealth(
                    is_healthy=False,
                    message="OpenAI not configured",
                    error_type="auth"
                )
            
            # Simple test call
            response = self.client.models.list()
            return ProviderHealth(
                is_healthy=True,
                message="OpenAI connection successful",
                details={"models_available": len(response.data)}
            )
        except Exception as e:
            return ProviderHealth(
                is_healthy=False,
                message=f"OpenAI connection failed: {str(e)}",
                error_type="connection"
            )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Send chat message to OpenAI"""
        try:
            if not self.is_configured():
                raise ProviderAuthError("OpenAI not configured")
            
            response = self.client.chat.completions.create(
                model=model or "gpt-4",
                messages=messages,
                **kwargs
            )
            
            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.dict() if response.usage else {},
                "model": response.model
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise ProviderError(f"OpenAI API error: {e}")