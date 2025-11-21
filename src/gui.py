"""
GUI Module
Main application interface with overlay capabilities
"""

import logging
import sys
import traceback
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtCore import (
    QObject,
    Qt,
    QTimer,
    QtMsgType,
    pyqtSignal,
    qInstallMessageHandler,
    QUrl,
)
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
    QWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


from config import Config
from credential_store import CredentialStore, CredentialStoreError
from game_profile import get_profile_store
from game_watcher import get_game_watcher
from keybind_manager import DEFAULT_KEYBINDS, KeybindManager
from macro_manager import MacroActionType, MacroManager
from macro_runner import MacroRunner
from session_recap_dialog import SessionRecapDialog
from settings_dialog import TabbedSettingsDialog
from theme_compat import DEFAULT_DARK_THEME, ThemeManager

# from ai_assistant import AIWorkerThread # This will be moved

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def qt_message_handler(msg_type, context, message):
    """
    Custom Qt message handler to catch Qt warnings and errors.
    This helps catch C++ level Qt errors that might not be visible in Python exceptions.
    """
    if msg_type == QtMsgType.QtDebugMsg:
        logger.debug(f"Qt Debug: {message}")
    elif msg_type == QtMsgType.QtInfoMsg:
        logger.info(f"Qt Info: {message}")
    elif msg_type == QtMsgType.QtWarningMsg:
        logger.warning(f"Qt Warning: {message}")
        logger.warning(f"  File: {context.file if context.file else 'unknown'}")
        logger.warning(f"  Line: {context.line if context.line else 'unknown'}")
        logger.warning(f"  Function: {context.function if context.function else 'unknown'}")
    elif msg_type == QtMsgType.QtCriticalMsg:
        logger.critical(f"Qt Critical: {message}")
        logger.critical(f"  File: {context.file if context.file else 'unknown'}")
        logger.critical(f"  Line: {context.line if context.line else 'unknown'}")
        logger.critical(f"  Function: {context.function if context.function else 'unknown'}")
    elif msg_type == QtMsgType.QtFatalMsg:
        logger.critical(f"Qt Fatal: {message}")
        logger.critical(f"  File: {context.file if context.file else 'unknown'}")
        logger.critical(f"  Line: {context.line if context.line else 'unknown'}")
        logger.critical(f"  Function: {context.function if context.function else 'unknown'}")
        logger.critical("=" * 70)
        logger.critical("Qt FATAL ERROR - Application will crash!")
        logger.critical("=" * 70)
