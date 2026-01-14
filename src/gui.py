"""
Omnix GUI Module
================

PyQt6 interface styled with the Omnix QSS theme. Provides the main dashboard,
chat panel, settings panel, and in-game overlay window matching the reference
visual design.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtCore import QEvent, Qt, QThread, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)

from src.config import Config
from src.credential_store import CredentialStore
from src.ui.design_system import OmnixDesignSystem, design_system
from src.keybind_manager import KeybindManager
from src.macro_manager import MacroManager
from src.ui.theme_manager import OmnixThemeManager
from src.settings_dialog import TabbedSettingsDialog

# New HUD primitives
from src.omnix_hud import (
    HudPanel,
    NeonButton,
    ChatPanel,
    GameStatusWidget,
    StatBlock,
    OMNIX_GLOBAL_QSS,
)

logger = logging.getLogger(__name__)


def _load_qss() -> str:
    """Load the legacy Omnix QSS stylesheet.

    DEPRECATED: This function loads hardcoded styles that should be replaced
    with design system tokens. This is kept for backward compatibility only.

    TODO: Migrate all styling to use OmnixDesignSystem tokens instead.
    """
    qss_path = Path(__file__).parent / "ui" / "omnix.qss"
    if not qss_path.exists():
        logger.warning("Legacy QSS stylesheet not found at %s", qss_path)
        return _generate_token_based_styles()

    try:
        legacy_qss = qss_path.read_text(encoding="utf-8")
        logger.warning(
            "Loading legacy QSS stylesheet - consider migrating to design system tokens"
        )
        # For now, return legacy styles but log migration warning
        return legacy_qss
    except Exception as e:
        logger.error("Failed to load legacy QSS stylesheet: %s", e)
        return _generate_token_based_styles()


def _generate_token_based_styles() -> str:
    """Generate QSS styles using design system tokens (future migration target)."""
    try:
        from .ui.design_system import design_system

        # Generate minimal styles using design tokens
        styles = f"""
        /* Omnix Design System Generated Styles */
        QWidget {{
            background-color: {design_system.colors.background.primary};
            color: {design_system.colors.text.primary};
            font-family: {design_system.typography.font_primary};
        }}
        
        QPushButton {{
            background-color: {design_system.colors.primary.default};
            color: {design_system.colors.primary.foreground};
            border: none;
            border-radius: {design_system.radius.md}px;
            padding: {design_system.spacing.sm}px {design_system.spacing.md}px;
        }}
        
        QPushButton:hover {{
            background-color: {design_system.colors.primary.hover};
        }}
        """
        return styles
    except ImportError:
        # Fallback if design system not available
        return "/* Design system not available - using minimal fallback styles */"


class AIWorkerThread(QThread):
    """Background worker that calls the AI assistant without blocking the UI."""

    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, assistant, question: str, game_context: Optional[Dict] = None):
        super().__init__()
        self.assistant = assistant
        self.question = question
        self.game_context = game_context or {}

    def run(self) -> None:
        try:
            if self.assistant is None:
                response = "Omnix is standing by. Configure an AI provider to begin."
            else:
                response = self.assistant.ask_question(
                    self.question, game_context=self.game_context
                )
            self.finished.emit(response or "")
        except Exception as exc:
            logger.exception("AI worker failed")
            self.error.emit(str(exc))


class ChatWidget(QWidget):
    """
    HUD-styled chat surface with threaded AI responses.
    Wraps the primitive ChatPanel (bubbles) with an input field and send logic.
    """

    def __init__(
        self, assistant, title: str = "Chat", parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.assistant = assistant
        self.ai_worker: Optional[AIWorkerThread] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 1. Chat History Panel
        self.chat_panel = ChatPanel()
        layout.addWidget(self.chat_panel, 1)

        # 2. Input Area
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("chat-input")
        self.input_field.setPlaceholderText("Ask Omnix...")
        self.input_field.returnPressed.connect(self._on_submit)
        input_row.addWidget(self.input_field, 1)

        self.send_button = NeonButton("SEND", primary=True)
        self.send_button.setFixedSize(80, 32)
        self.send_button.clicked.connect(self._on_submit)
        input_row.addWidget(self.send_button)

        layout.addLayout(input_row)

        self._seed_intro()

    def _seed_intro(self) -> None:
        self.add_message("SYSTEM", "Omnix Online.", role="system")
        self.add_message("AI", "Systems nominal. How can I assist?", role="ai")

    def add_message(self, sender: str, message: str, role: str = "ai") -> None:
        is_user = role.lower() == "user"
        self.chat_panel.add_message(sender, message, is_user)

    def _on_submit(self) -> None:
        if self.ai_worker is not None:
            return
        text = self.input_field.text().strip()
        if not text:
            return
        self._send_message(text)

    def _send_message(self, text: str) -> None:
        self.add_message("YOU", text, role="user")
        self.input_field.clear()
        self.send_button.setEnabled(False)

        self.ai_worker = AIWorkerThread(self.assistant, text)
        self.ai_worker.finished.connect(self._handle_response)
        self.ai_worker.error.connect(self._handle_error)
        self.ai_worker.start()

    def _handle_response(self, response: str) -> None:
        self.add_message("OMNIX", response, role="ai")
        self.send_button.setEnabled(True)
        self.ai_worker = None

    def _handle_error(self, message: str) -> None:
        self.add_message("ERROR", f"System Failure: {message}", role="system")
        self.send_button.setEnabled(True)
        self.ai_worker = None


class OverlayWindow(QWidget):
    """Frameless always-on-top overlay with translucent chat."""

    def __init__(self, assistant, config: Config, ds: OmnixDesignSystem):
        super().__init__()
        self.assistant = assistant
        self.config = config
        self.design_system = ds
        self.minimized = getattr(config, "overlay_minimized", False)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setGeometry(
            int(getattr(config, "overlay_x", 100)),
            int(getattr(config, "overlay_y", 100)),
            int(getattr(config, "overlay_width", 420)),
            int(getattr(config, "overlay_height", 360)),
        )

        # Enable mouse tracking for drag and resize
        self.setMouseTracking(True)
        self._drag_position = None
        self._resize_mode: Optional[str] = None
        self._resize_margin = 10

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Background panel
        self.background_panel = QFrame()
        self.background_panel.setObjectName("OverlayBackground")
        self.background_panel.setMouseTracking(True)

        # Apply semi-transparent background styling
        opacity = getattr(config, "overlay_opacity", 0.8)
        bg_alpha = format(int(opacity * 255), "02x")
        # We'll allow the QSS to handle borders, but set bg alpha here
        self.background_panel.setStyleSheet(f"""
            QFrame#OverlayBackground {{
                background-color: #050816{bg_alpha};
                border: 1px solid #22d3ee;
                border-radius: 12px;
            }}
        """)

        panel_layout = QVBoxLayout(self.background_panel)
        panel_layout.setContentsMargins(8, 8, 8, 8)
        panel_layout.setSpacing(8)

        # Title bar
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("background: transparent;")
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(4, 0, 4, 0)

        title_label = QLabel("OMNIX OVERLAY")
        title_label.setStyleSheet(
            "font-weight: bold; color: #22d3ee; letter-spacing: 1px;"
        )
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()

        min_btn = QPushButton("−")
        min_btn.setFixedSize(20, 20)
        min_btn.setStyleSheet(
            "background: transparent; color: #22d3ee; font-weight: bold; border: none;"
        )
        min_btn.clicked.connect(self.toggle_minimize)
        title_bar_layout.addWidget(min_btn)

        panel_layout.addWidget(self.title_bar)

        # Chat
        self.chat = ChatWidget(assistant, title="Overlay")
        panel_layout.addWidget(self.chat)

        main_layout.addWidget(self.background_panel)

        # Apply styles
        self.setStyleSheet(OMNIX_GLOBAL_QSS)

        self.background_panel.installEventFilter(self)
        self.title_bar.installEventFilter(self)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_position_and_size)
        self._save_delay_ms = 500

        if self.minimized:
            self.toggle_minimize()

    def eventFilter(self, watched, event):
        if watched in (self.background_panel, self.title_bar):
            if event.type() == QEvent.Type.MouseButtonPress:
                self.mousePressEvent(event)
            elif event.type() == QEvent.Type.MouseMove:
                self.mouseMoveEvent(event)
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self.mouseReleaseEvent(event)
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            rect = self.rect()
            margin = self._resize_margin
            on_left = pos.x() < margin
            on_right = pos.x() > rect.width() - margin
            on_top = pos.y() < margin
            on_bottom = pos.y() > rect.height() - margin

            if on_bottom and on_right:
                self._resize_mode = "bottom_right"
            elif on_bottom and on_left:
                self._resize_mode = "bottom_left"
            elif on_top and on_right:
                self._resize_mode = "top_right"
            elif on_top and on_left:
                self._resize_mode = "top_left"
            elif on_bottom:
                self._resize_mode = "bottom"
            elif on_top:
                self._resize_mode = "top"
            elif on_left:
                self._resize_mode = "left"
            elif on_right:
                self._resize_mode = "right"
            else:
                self._resize_mode = None
                self._drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )

    def mouseMoveEvent(self, event) -> None:
        pos = event.position().toPoint()
        rect = self.rect()
        margin = self._resize_margin

        on_left = pos.x() < margin
        on_right = pos.x() > rect.width() - margin
        on_top = pos.y() < margin
        on_bottom = pos.y() > rect.height() - margin

        if (on_bottom and on_right) or (on_top and on_left):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif (on_bottom and on_left) or (on_top and on_right):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif on_left or on_right:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif on_top or on_bottom:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._resize_mode:
                global_pos = event.globalPosition().toPoint()
                geo = self.geometry()
                if "right" in self._resize_mode:
                    geo.setRight(global_pos.x())
                if "left" in self._resize_mode:
                    geo.setLeft(global_pos.x())
                if "bottom" in self._resize_mode:
                    geo.setBottom(global_pos.y())
                if "top" in self._resize_mode:
                    geo.setTop(global_pos.y())

                if geo.width() < 300:
                    geo.setWidth(300)
                if geo.height() < 200:
                    geo.setHeight(200)
                self.setGeometry(geo)
            elif self._drag_position is not None:
                self.move(event.globalPosition().toPoint() - self._drag_position)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = None
            self._resize_mode = None

    def closeEvent(self, event: QEvent) -> None:
        super().closeEvent(event)
        self._save_overlay_config()

    def _save_overlay_config(self) -> None:
        try:
            Config.save_to_env(
                provider=self.config.ai_provider,
                session_tokens=self.config.session_tokens,
                overlay_hotkey=self.config.overlay_hotkey,
                check_interval=self.config.check_interval,
                overlay_x=self.config.overlay_x,
                overlay_y=self.config.overlay_y,
                overlay_width=self.config.overlay_width,
                overlay_height=self.config.overlay_height,
                overlay_minimized=self.config.overlay_minimized,
                overlay_opacity=self.config.overlay_opacity,
            )
        except Exception as e:
            logger.error(f"Failed to save overlay config: {e}")

    def toggle_minimize(self) -> None:
        self.minimized = not self.minimized
        self.config.overlay_minimized = self.minimized
        if self.minimized:
            self._saved_height = self.height()
            self.chat.setVisible(False)
            self.setFixedHeight(40)
        else:
            self.chat.setVisible(True)
            self.setFixedHeight(getattr(self, "_saved_height", 400))

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self._save_timer.start(self._save_delay_ms)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._save_timer.start(self._save_delay_ms)

    def _save_position_and_size(self) -> None:
        try:
            self.config.overlay_x = self.x()
            self.config.overlay_y = self.y()
            self.config.overlay_width = self.width()
            self.config.overlay_height = self.height()
            self.config.save()
        except Exception as e:
            logger.warning(f"Failed to save overlay position: {e}")


class MainWindow(QMainWindow):
    """Omnix main dashboard window with new HUD layout."""

    def __init__(
        self,
        ai_assistant,
        config: Config,
        credential_store: CredentialStore,
        design_system: OmnixDesignSystem = design_system,
        game_detector=None,
    ):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.config = config
        self.credential_store = credential_store
        self.design_system = design_system or OmnixDesignSystem()
        self.game_detector = game_detector
        self.current_game = None

        self.setWindowTitle("OMNIX // HUD")
        self.resize(1280, 800)

        # Apply Global QSS
        self.setStyleSheet(OMNIX_GLOBAL_QSS)

        self.keybind_manager = KeybindManager()
        self.macro_manager = MacroManager()
        self.theme_manager = OmnixThemeManager()
        self.settings_dialog = None

        self.overlay_window = OverlayWindow(ai_assistant, config, self.design_system)

        # Central Container
        central = QWidget()
        self.setCentralWidget(central)

        # Main Layout (Vertical: Header -> Content -> Footer)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # 1. Header
        main_layout.addLayout(self._build_header())

        # 2. Content (3 Columns)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # -- Left: Chat --
        self.left_panel = HudPanel()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        left_title = QLabel("COMMUNICATIONS")
        left_title.setStyleSheet(
            "font-size: 11px; letter-spacing: 2px; color: #94a3b8; font-weight: bold;"
        )
        left_layout.addWidget(left_title)

        self.chat_widget = ChatWidget(self.ai_assistant)
        left_layout.addWidget(self.chat_widget)

        content_layout.addWidget(self.left_panel, 2)

        # -- Center: Game Status --
        self.center_panel = QWidget()  # Transparent container
        center_layout = QVBoxLayout(self.center_panel)
        center_layout.setSpacing(24)
        center_layout.setContentsMargins(0, 0, 0, 0)

        self.game_status = GameStatusWidget()
        center_layout.addWidget(self.game_status)

        self.stat_block = StatBlock()
        center_layout.addWidget(self.stat_block)

        # Quick Actions (Buttons below stats)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        for label in ["SCAN", "OPTIMIZE", "LOG"]:
            btn = NeonButton(label, primary=False)
            actions_layout.addWidget(btn)
        center_layout.addLayout(actions_layout)

        center_layout.addStretch()

        content_layout.addWidget(self.center_panel, 2)

        # -- Right: Settings & Tools --
        self.right_panel = HudPanel()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(16)

        right_title = QLabel("SYSTEMS")
        right_title.setStyleSheet(
            "font-size: 11px; letter-spacing: 2px; color: #94a3b8; font-weight: bold;"
        )
        right_layout.addWidget(right_title)

        # Menu Buttons
        settings_items = [
            ("AI PROVIDERS", 0),
            ("GAME PROFILES", 1),
            ("KNOWLEDGE PACKS", 2),
            ("MACRO SYSTEM", 4),
        ]

        for name, idx in settings_items:
            btn = NeonButton(name, primary=False)
            btn.clicked.connect(lambda _, x=idx: self._open_settings_at_tab(x))
            right_layout.addWidget(btn)

        right_layout.addStretch()

        # Provider Toggle (Visual only since we are Ollama only)
        provider_frame = QFrame()
        provider_frame.setObjectName("settings-row")
        provider_frame.setProperty("active", "true")
        prov_layout = QVBoxLayout(provider_frame)
        prov_label = QLabel("ACTIVE PROVIDER")
        prov_label.setStyleSheet("font-size: 9px; color: #22d3ee; font-weight: bold;")
        prov_val = QLabel("OLLAMA (LOCAL)")
        prov_val.setStyleSheet("font-size: 14px; font-weight: bold;")
        prov_layout.addWidget(prov_label)
        prov_layout.addWidget(prov_val)
        right_layout.addWidget(provider_frame)

        content_layout.addWidget(self.right_panel, 1)

        main_layout.addLayout(content_layout)

        # 3. Footer
        main_layout.addLayout(self._build_footer())

        # Start services
        if self.game_detector:
            self._start_game_detection()

    def _build_header(self) -> QHBoxLayout:
        # Recreating header to match logic flow
        layout = QHBoxLayout()

        frame = QFrame()
        frame.setObjectName("top-bar")
        frame.setFixedHeight(50)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        h_layout = QHBoxLayout(frame)
        h_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("OMNIX")
        logo.setObjectName("omnix-logo")
        h_layout.addWidget(logo)

        sub = QLabel(" // SYSTEM READY")
        sub.setObjectName("omnix-logo-subtitle")
        sub.setContentsMargins(10, 6, 0, 0)
        h_layout.addWidget(sub)

        h_layout.addStretch()

        user = QLabel("PILOT ID: ADMIN")
        user.setObjectName("top-bar-user")
        h_layout.addWidget(user)

        layout.addWidget(frame)
        return layout

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setSpacing(20)

        # Large Overlay Button
        overlay_btn = NeonButton("TOGGLE OVERLAY", primary=True)
        overlay_btn.setMinimumHeight(48)
        overlay_btn.clicked.connect(self._toggle_overlay)
        footer.addWidget(overlay_btn, 1)

        # Large Settings Button
        settings_btn = NeonButton("SYSTEM SETTINGS", primary=False)
        settings_btn.setMinimumHeight(48)
        settings_btn.clicked.connect(self._open_settings)
        footer.addWidget(settings_btn, 1)

        return footer

    def _toggle_overlay(self) -> None:
        if self.overlay_window.isVisible():
            self.overlay_window.hide()
        else:
            self.overlay_window.show()
            self.overlay_window.raise_()

    def _open_settings(self) -> None:
        self._open_settings_at_tab(0)

    def _open_settings_at_tab(self, tab_index: int) -> None:
        if self.settings_dialog is None:
            self.settings_dialog = TabbedSettingsDialog(
                self,
                self.config,
                self.keybind_manager,
                self.macro_manager,
                self.theme_manager,
            )
            self.settings_dialog.settings_saved.connect(self._on_settings_saved)
        self.settings_dialog.set_current_tab(tab_index)
        self.settings_dialog.exec()

    def _on_settings_saved(self, settings: dict) -> None:
        pass

    def _start_game_detection(self) -> None:
        self.game_check_timer = QTimer()
        self.game_check_timer.timeout.connect(self._check_for_game)
        self.game_check_timer.start(5000)
        self._check_for_game()

    def _check_for_game(self) -> None:
        if not self.game_detector:
            return
        game = self.game_detector.detect_running_game()

        if game and game.get("name") != self.current_game:
            self.current_game = game.get("name")
            self._update_game_status(game)
        elif not game and self.current_game:
            self.current_game = None
            self._update_game_status(None)

    def _update_game_status(self, game: Optional[Dict]) -> None:
        online = bool(game)
        name = game.get("name") if game else None
        pid = str(game.get("pid", "--")) if game else "--"

        # Update Center Widget
        self.game_status.set_game(name, online)

        # Update Stats (Mock stats for now, could come from DB)
        if online:
            self.stat_block.set_stats(kd="1.2", matches="42", wins="54%")
        else:
            self.stat_block.set_stats(kd="--", matches="--", wins="--")

        # Notify AI
        if self.ai_assistant:
            self.ai_assistant.set_current_game(game)

    def cleanup(self) -> None:
        if self.overlay_window:
            self.overlay_window.close()
        if hasattr(self, "game_check_timer"):
            self.game_check_timer.stop()


def run_gui(
    ai_assistant,
    config: Config,
    credential_store: CredentialStore,
    ds: OmnixDesignSystem = design_system,
    game_detector=None,
) -> None:
    """Launch the Omnix GUI."""
    app = QApplication.instance() or QApplication(sys.argv)

    # Set dark palette as fallback
    app.setStyle("Fusion")

    window = MainWindow(ai_assistant, config, credential_store, ds, game_detector)
    window.show()
    sys.exit(app.exec())


__all__ = [
    "AIWorkerThread",
    "ChatWidget",
    "OverlayWindow",
    "MainWindow",
    "run_gui",
]
