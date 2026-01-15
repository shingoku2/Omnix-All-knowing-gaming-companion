import pytest
from unittest.mock import MagicMock
import json
from src.gui import JSBridge, MainWindow
from src.config import Config

def test_js_bridge_get_config():
    """Test that getConfig returns the current configuration as a JSON string."""
    mock_window = MagicMock(spec=MainWindow)
    # Mock config data
    mock_config = MagicMock(spec=Config)
    # Set attributes directly on the mock
    mock_config.ai_provider = "ollama"
    mock_config.ollama_model = "llama3"
    mock_config.overlay_opacity = 0.9
    mock_config.theme = {"name": "cyberpunk"}
    
    mock_window.config = mock_config
    
    bridge = JSBridge(mock_window)
    
    config_json = bridge.getConfig()
    config_data = json.loads(config_json)
    
    assert config_data["ui"]["theme"]["name"] == "cyberpunk"
    assert config_data["ai"]["model"] == "llama3"

def test_js_bridge_save_settings():
    """Test that saveSettings updates the config and calls save."""
    mock_window = MagicMock(spec=MainWindow)
    mock_config = MagicMock(spec=Config)
    mock_window.config = mock_config
    
    bridge = JSBridge(mock_window)
    
    # React sends structured data
    new_settings = {
        "ui": {"opacity": 0.8},
        "ai": {"model": "gpt-4"}
    }
    
    result = bridge.saveSettings(json.dumps(new_settings))
    
    assert result is True
    
    # Bridge should map these to Config flat structure
    expected_update = {
        "overlay_opacity": 0.8,
        "ollama_model": "gpt-4"
    }
    
    # Verify update was called with mapped settings
    # We use ANY or check subset because bridge might send more
    mock_config.update.assert_called()
    call_args = mock_config.update.call_args[0][0]
    assert call_args["overlay_opacity"] == 0.8
    assert call_args["ollama_model"] == "gpt-4"
    
    # Verify save was called
    mock_config.save.assert_called_once()
