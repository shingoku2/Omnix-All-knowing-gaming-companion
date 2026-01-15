import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from src.gui import MainWindow
from src.config import Config
from src.credential_store import CredentialStore
import sys
import os

@pytest.fixture
def app():
    return QApplication.instance() or QApplication(sys.argv)

@pytest.fixture
def config():
    return Config()

@pytest.fixture
def credential_store():
    return CredentialStore()

def test_mainwindow_has_webengineview(app, config, credential_store):
    """Test that MainWindow now uses QWebEngineView for its main content."""
    # Headless mode for CI
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    window = MainWindow(None, config, credential_store)
    
    # We expect a QWebEngineView to be present in the window
    web_view = window.findChild(QWebEngineView)
    assert web_view is not None, "MainWindow should contain a QWebEngineView"
    
    window.close()

from src.gui import MainWindow, JSBridge
from unittest.mock import MagicMock

def test_js_bridge_message_received(mocker):
    """Test that messages from JS are correctly routed to the AI assistant."""
    # Mock the main window
    mock_window = MagicMock(spec=MainWindow)
    
    bridge = JSBridge(mock_window)
    
    # Call the bridge method as if from JS
    bridge.sendMessage("Hello from React")
    
    mock_window.send_message_to_ai.assert_called_once_with("Hello from React")
