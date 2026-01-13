import pytest
from src.providers import MockProvider, LLMProvider

def test_mock_provider_implementation():
    """Verify MockProvider implements LLMProvider correctly."""
    provider = MockProvider()
    assert isinstance(provider, LLMProvider)
    
    # Test default response
    assert provider.generate_response("sys", "user") == "Mock response"
    assert provider.health_check() is True

def test_mock_provider_custom_response():
    """Verify MockProvider can return custom responses."""
    provider = MockProvider(response_text="Custom")
    assert provider.generate_response("sys", "user") == "Custom"
