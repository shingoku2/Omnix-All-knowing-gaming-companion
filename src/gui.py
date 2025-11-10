"""
GUI Module
Main application interface with overlay capabilities
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSystemTrayIcon,
    QMenu, QFrame, QScrollArea, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QAction, QFont, QPalette, QColor, QKeySequence, QShortcut
from typing import Optional, Dict
import os


class GameDetectionThread(QThread):
    """Background thread for game detection"""
    game_detected = pyqtSignal(dict)
    game_lost = pyqtSignal()

    def __init__(self, game_detector):
        super().__init__()
        self.game_detector = game_detector
        self.running = True

    def run(self):
        """Main thread loop"""
        while self.running:
            try:
                game = self.game_detector.detect_game()
                if game:
                    self.game_detected.emit(game)
                else:
                    self.game_lost.emit()
                self.msleep(5000)  # Check every 5 seconds
            except Exception as e:
                print(f"Error in game detection thread: {e}")
                self.msleep(5000)

    def stop(self):
        """Stop the thread"""
        self.running = False


class ChatWidget(QWidget):
    """Chat interface widget for Q&A interactions with AI assistant"""

    def __init__(self, ai_assistant):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.init_ui()

    def init_ui(self):
        """Initialize the chat widget UI components"""
        layout = QVBoxLayout()

        # Chat history display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 10px;
                font-size: 12pt;
            }
        """)
        layout.addWidget(self.chat_display)

        # User input area
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask a question about the game...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
                font-size: 11pt;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14b8a6;
            }
            QPushButton:pressed {
                background-color: #0a5a5d;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Clear chat history button
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
        """)
        self.clear_button.clicked.connect(self.clear_chat)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def send_message(self):
        """Process and send user message to AI assistant"""
        question = self.input_field.text().strip()

        if not question:
            return

        # Display user's question in chat
        self.add_message("You", question, is_user=True)
        self.input_field.clear()

        # Disable send button while processing
        self.send_button.setEnabled(False)
        self.send_button.setText("Thinking...")

        try:
            response = self.ai_assistant.ask_question(question)
            self.add_message("AI Assistant", response, is_user=False)
        except Exception as e:
            self.add_message("System", f"Error: {str(e)}", is_user=False)

        # Re-enable send button
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")

    def add_message(self, sender: str, message: str, is_user: bool = True):
        """
        Add a formatted message to the chat display
        
        Args:
            sender: Name of the message sender
            message: Message content
            is_user: True if message is from user, False if from AI/system
        """
        color = "#14b8a6" if is_user else "#f59e0b"
        self.chat_display.append(f'<p><span style="color: {color}; font-weight: bold;">{sender}:</span> {message}</p>')
        # Auto-scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def clear_chat(self):
        """Clear chat display and conversation history"""
        self.chat_display.clear()
        self.ai_assistant.clear_history()


class MainWindow(QMainWindow):
    """Main application window with game detection and AI chat interface"""

    def __init__(self, game_detector, ai_assistant, info_scraper):
        super().__init__()
        self.game_detector = game_detector
        self.ai_assistant = ai_assistant
        self.info_scraper = info_scraper

        self.current_game = None
        self.detection_thread = None

        self.init_ui()
        self.start_game_detection()

    def init_ui(self):
        """Initialize the main window UI components and styling"""
        self.setWindowTitle("Gaming AI Assistant")
        self.setGeometry(100, 100, 900, 700)

        # Apply dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        # Setup central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Application header
        header = self.create_header()
        main_layout.addWidget(header)

        # Game detection status panel
        self.game_info_label = QLabel("No game detected")
        self.game_info_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #14b8a6;
                padding: 15px;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)
        self.game_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.game_info_label)

        # Quick action buttons
        actions_layout = QHBoxLayout()

        self.tips_button = QPushButton("Get Tips")
        self.tips_button.clicked.connect(self.get_tips)
        self.tips_button.setEnabled(False)

        self.overview_button = QPushButton("Game Overview")
        self.overview_button.clicked.connect(self.get_overview)
        self.overview_button.setEnabled(False)

        # Apply styling to action buttons
        for button in [self.tips_button, self.overview_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #6366f1;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 11pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #818cf8;
                }
                QPushButton:disabled {
                    background-color: #374151;
                    color: #6b7280;
                }
            """)
            actions_layout.addWidget(button)

        main_layout.addLayout(actions_layout)

        # AI chat interface
        self.chat_widget = ChatWidget(self.ai_assistant)
        main_layout.addWidget(self.chat_widget)

        central_widget.setLayout(main_layout)

        # System tray integration
        self.create_system_tray()

        # Global keyboard shortcuts
        self.create_shortcuts()

    def create_header(self) -> QWidget:
        """Create and style the application header widget"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("🎮 Gaming AI Assistant")
        title.setStyleSheet("""
            QLabel {
                color: #14b8a6;
                font-size: 20pt;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel("Your real-time gaming companion powered by AI")
        subtitle.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 11pt;
            }
        """)
        layout.addWidget(subtitle)

        header.setLayout(layout)
        return header

    def create_system_tray(self):
        """Create system tray icon with context menu"""
        self.tray_icon = QSystemTrayIcon(self)

        # Build tray context menu
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def create_shortcuts(self):
        """Register global keyboard shortcuts"""
        # Ctrl+Shift+G: Toggle window visibility
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+Shift+G"), self)
        toggle_shortcut.activated.connect(self.toggle_visibility)

    def toggle_visibility(self):
        """Toggle main window visibility between shown and hidden states"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    def start_game_detection(self):
        """Initialize and start the game detection background thread"""
        self.detection_thread = GameDetectionThread(self.game_detector)
        self.detection_thread.game_detected.connect(self.on_game_detected)
        self.detection_thread.game_lost.connect(self.on_game_lost)
        self.detection_thread.start()

    def on_game_detected(self, game: Dict):
        """
        Handle game detection event
        
        Args:
            game: Dictionary containing detected game information
        """
        self.current_game = game
        game_name = game.get('name', 'Unknown Game')

        # Update UI to show detected game
        self.game_info_label.setText(f"🎮 Now Playing: {game_name}")
        self.game_info_label.setStyleSheet("""
            QLabel {
                background-color: #14532d;
                color: #22c55e;
                padding: 15px;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)

        # Enable game-specific action buttons
        self.tips_button.setEnabled(True)
        self.overview_button.setEnabled(True)

        # Update AI assistant context with current game
        if hasattr(self.ai_assistant, 'set_current_game'):
            self.ai_assistant.set_current_game(game)

        # Automatically fetch and display game overview
        self.get_overview()

    def on_game_lost(self):
        """Handle game close/lost detection event"""
        self.current_game = None
        
        # Reset UI to default state
        self.game_info_label.setText("No game detected")
        self.game_info_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #14b8a6;
                padding: 15px;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)

        # Disable game-specific action buttons
        self.tips_button.setEnabled(False)
        self.overview_button.setEnabled(False)

    def get_tips(self):
        """Request and display tips for the currently detected game"""
        if not self.current_game:
            return

        game_name = self.current_game.get('name')
        self.chat_widget.add_message("System", "Getting tips...", is_user=False)

        try:
            if hasattr(self.ai_assistant, 'get_tips_and_strategies'):
                tips = self.ai_assistant.get_tips_and_strategies()
                if tips:
                    self.chat_widget.add_message("AI Assistant", tips, is_user=False)
                else:
                    self.chat_widget.add_message("System", "No tips available", is_user=False)
            else:
                self.chat_widget.add_message("System", "Tips functionality not available", is_user=False)
        except Exception as e:
            self.chat_widget.add_message("System", f"Error: {str(e)}", is_user=False)

    def get_overview(self):
        """Request and display overview of the currently detected game"""
        if not self.current_game:
            return

        game_name = self.current_game.get('name')
        self.chat_widget.add_message("System", f"Getting overview of {game_name}...", is_user=False)

        try:
            if hasattr(self.ai_assistant, 'get_game_overview'):
                overview = self.ai_assistant.get_game_overview(game_name)
                if overview:
                    self.chat_widget.add_message("AI Assistant", overview, is_user=False)
                else:
                    self.chat_widget.add_message("System", "No overview available", is_user=False)
            else:
                self.chat_widget.add_message("System", "Overview functionality not available", is_user=False)
        except Exception as e:
            self.chat_widget.add_message("System", f"Error: {str(e)}", is_user=False)

    def closeEvent(self, event):
        """
        Handle window close event by minimizing to system tray instead of quitting
        
        Args:
            event: QCloseEvent to be handled
        """
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Gaming AI Assistant",
            "Application minimized to tray. Press Ctrl+Shift+G to toggle.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )


def run_gui(game_detector, ai_assistant, info_scraper):
    """
    Initialize and run the GUI application
    
    Args:
        game_detector: Game detection service instance
        ai_assistant: AI assistant service instance
        info_scraper: Information scraper service instance
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Gaming AI Assistant")

    window = MainWindow(game_detector, ai_assistant, info_scraper)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # Module should be run from main.py with proper dependencies
    print("GUI module - run from main.py")
