import pytest
from unittest.mock import MagicMock
import json
from src.gui import JSBridge, MainWindow
from src.macro_manager import MacroManager, Macro, MacroStep

def test_js_bridge_get_macros():
    """Test retrieving macros from JS."""
    mock_window = MagicMock(spec=MainWindow)
    mock_macro_manager = MagicMock(spec=MacroManager)
    
    # Mock some macros
    macro1 = Macro(id="m1", name="Test Macro 1", description="Desc 1", steps=[])
    macro2 = Macro(id="m2", name="Test Macro 2", description="Desc 2", steps=[])
    
    mock_macro_manager.get_all_macros.return_value = [macro1, macro2]
    mock_window.macro_manager = mock_macro_manager
    
    bridge = JSBridge(mock_window)
    
    macros_json = bridge.getMacros()
    macros = json.loads(macros_json)
    
    assert len(macros) == 2
    assert macros[0]["id"] == "m1"
    assert macros[0]["name"] == "Test Macro 1"

def test_js_bridge_save_macro():
    """Test saving a macro from JS."""
    mock_window = MagicMock(spec=MainWindow)
    mock_macro_manager = MagicMock(spec=MacroManager)
    # Mock macros dict
    mock_macro_manager.macros = {}
    
    mock_window.macro_manager = mock_macro_manager
    mock_window.config = MagicMock()
    
    bridge = JSBridge(mock_window)
    
    macro_data = {
        "id": "m1",
        "name": "Updated Macro",
        "description": "Updated Desc",
        "steps": [],
        "repeat": 1
    }
    
    result = bridge.saveMacro(json.dumps(macro_data))
    
    assert result is True
    # Verify it was added to the dict
    assert "m1" in mock_macro_manager.macros
    # Verify save call
    mock_window.config.save_macros.assert_called()

def test_js_bridge_recording():
    """Test start/stop recording."""
    mock_window = MagicMock(spec=MainWindow)
    mock_macro_manager = MagicMock(spec=MacroManager)
    mock_window.macro_manager = mock_macro_manager
    mock_window.config = MagicMock() # Add config mock
    
    bridge = JSBridge(mock_window)
    
    bridge.startMacroRecording()
    mock_macro_manager.start_recording.assert_called()
    
    # Mock stop_recording returning a macro so save is called
    mock_macro_manager.stop_recording.return_value = MagicMock()
    
    bridge.stopMacroRecording()
    mock_macro_manager.stop_recording.assert_called()
    mock_window.config.save_macros.assert_called()
