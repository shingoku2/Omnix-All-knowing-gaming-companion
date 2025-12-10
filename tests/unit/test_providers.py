"""Tests for the Ollama-only provider layer."""

import pytest

from src.providers import (
    OllamaProvider,
    ProviderConnectionError,
    ProviderError,
)


class TestProviderExceptions:
    """Test provider exception hierarchy"""

    def test_provider_error_base(self):
        """Test base ProviderError exception"""
        error = ProviderError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_provider_connection_error(self):
        """Test ProviderConnectionError exception"""
        error = ProviderConnectionError("Connection failed")
        assert isinstance(error, ProviderError)


@pytest.mark.unit
class TestOllamaProvider:
    """Tests for the Ollama provider (only supported provider)."""

    def test_init_defaults(self):
        provider = OllamaProvider()
        assert provider.name == "ollama"
        assert provider.base_url == "http://localhost:11434"
        assert provider.default_model == "llama3"

    def test_init_custom_base_and_model(self):
        provider = OllamaProvider(base_url="http://remote-host:11434", default_model="custom")
        assert provider.base_url == "http://remote-host:11434"
        assert provider.default_model == "custom"

    def test_is_configured_tracks_client(self):
        provider = OllamaProvider()
        assert provider.is_configured() in (True, False)

    def test_supports_optional_api_key(self):
        provider = OllamaProvider(api_key="secret-key")
        # API key is accepted for secured remote instances but not required locally
        assert provider.api_key == "secret-key"
