import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, pyqtSignal
from src.gui import JSBridge, MainWindow

def test_js_bridge_signals():
    """Test JSBridge has required signals."""
    bridge = JSBridge(None)
    assert hasattr(bridge, 'systemStatsUpdated')

@patch('psutil.cpu_percent')
@patch('psutil.virtual_memory')
def test_update_system_stats(mock_mem, mock_cpu):
    """Test the stats update logic."""
    mock_cpu.return_value = 15.5
    mock_mem.return_value.percent = 42.0
    
    # Create a mock MainWindow with the method to test attached or subclassed
    # Since we can't easily modify the class in test, we assume we will add 
    # _update_system_stats to MainWindow.
    
    # Let's verify the logic we WILL add.
    
    # Mock bridge
    mock_bridge = MagicMock()
    
    # Simulate the logic
    cpu = 15.5
    ram = 42.0
    
    # We expect bridge.systemStatsUpdated.emit to be called with json
    import json
    expected_payload = json.dumps({"cpu": 15.5, "ram": 42.0})
    
    # This test is a bit meta because we haven't written the code yet.
    # But checking for the signal existence on JSBridge is a valid Red test.
    
    bridge = JSBridge(None)
    # This should fail if signal doesn't exist (AttributeError)
    # or if we try to access it
    
    # If I run this now, it will fail because systemStatsUpdated is not defined on JSBridge
    assert hasattr(bridge, 'systemStatsUpdated')