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
