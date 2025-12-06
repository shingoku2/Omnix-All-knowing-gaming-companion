"""
Configuration Module
Handles application configuration and settings

Simplified for Ollama-only - no API keys required.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

from credential_store import CredentialDecryptionError, CredentialStore, CredentialStoreError
from security import ensure_private_dir, ensure_private_file

logger = logging.getLogger(__name__)

# Configuration directory
CONFIG_DIR = Path.home() / '.gaming_ai_assistant'
KEYBINDS_FILE = CONFIG_DIR / 'keybinds.json'
MACROS_FILE = CONFIG_DIR / 'macros.json'
THEME_FILE = CONFIG_DIR / 'theme.json'


class Config:
    """Application configuration (Ollama-only)"""

    def __init__(self, env_file: Optional[str] = None, require_keys: bool = False,
                 config_path: Optional[str] = None, config_dir: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            env_file: Path to .env file (optional)
            require_keys: Ignored (kept for compatibility)
            config_path: Optional path for persisted config data
            config_dir: Optional configuration directory override
        """
        self.config_path = config_path
        self.config_dir = config_dir
        self._ensure_secure_directories()

        # Load environment variables
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            self._protect_file(Path(env_file))
        else:
            possible_paths = [
                Path('.env'),
                Path(__file__).parent.parent / '.env',
                Path(sys.executable).parent / '.env',
            ]

            if getattr(sys, 'frozen', False):
                bundle_dir = Path(sys.executable).parent
                possible_paths.insert(0, bundle_dir / '.env')

            for env_path in possible_paths:
                if env_path.exists():
                    load_dotenv(env_path, override=True)
                    logger.info("Loaded .env from: %s", env_path)
                    self._protect_file(env_path)
                    break

        # Credential storage (kept for potential secured Ollama endpoints)
        self.credential_store = CredentialStore()

        # AI Configuration - Ollama only
        self.ai_provider = "ollama"  # Hardcoded to ollama
        self.ollama_host = os.getenv('OLLAMA_HOST') or os.getenv('OLLAMA_BASE_URL') or 'http://localhost:11434'
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3')

        # Application Settings
        self.overlay_hotkey = os.getenv('OVERLAY_HOTKEY', 'ctrl+shift+g')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '5'))

        # Overlay Window Settings
        self.overlay_x = int(os.getenv('OVERLAY_X', '100'))
        self.overlay_y = int(os.getenv('OVERLAY_Y', '100'))
        self.overlay_width = int(os.getenv('OVERLAY_WIDTH', '900'))
        self.overlay_height = int(os.getenv('OVERLAY_HEIGHT', '700'))
        self.overlay_minimized = os.getenv('OVERLAY_MINIMIZED', 'false').lower() == 'true'
        opacity = float(os.getenv('OVERLAY_OPACITY', '0.95'))
        self.overlay_opacity = max(0.0, min(1.0, opacity))

        # Macro & Keybind Settings
        self.macros_enabled = os.getenv('MACROS_ENABLED', 'false').lower() == 'true'
        self.macro_safety_understood = os.getenv('MACRO_SAFETY_UNDERSTOOD', 'false').lower() == 'true'
        self.max_macro_repeat = int(os.getenv('MAX_MACRO_REPEAT', '10'))
        self.macro_execution_timeout = int(os.getenv('MACRO_EXECUTION_TIMEOUT', '30'))

        # Extended Settings (stored in separate JSON files)
        self.keybinds: Dict = {}
        self.macros: Dict = {}
        self.theme: Dict = {}

        # Session tokens (kept for compatibility but not used)
        self.session_tokens: Dict[str, dict] = {}

        # Load extended settings
        self._load_keybinds()
        self._load_macros()
        self._load_theme()

        # Load from JSON config file if it exists
        self._load_from_file()

    def _ensure_secure_directories(self) -> None:
        """Create configuration directories with hardened permissions."""
        try:
            ensure_private_dir(CONFIG_DIR)
        except Exception as exc:
            logger.warning("Failed to secure default config dir %s: %s", CONFIG_DIR, exc)

        if self.config_dir:
            try:
                ensure_private_dir(Path(self.config_dir))
            except Exception as exc:
                logger.warning("Failed to secure custom config dir %s: %s", self.config_dir, exc)

    def _protect_file(self, path: Path) -> None:
        """Ensure a configuration file is restricted to the current user."""
        try:
            ensure_private_file(path)
        except Exception as exc:
            logger.warning("Unable to harden permissions for %s: %s", path, exc)

    def _load_keybinds(self):
        """Load keybinds from JSON file"""
        try:
            self._protect_file(KEYBINDS_FILE)
            if KEYBINDS_FILE.exists():
                with open(KEYBINDS_FILE, 'r', encoding='utf-8') as f:
                    self.keybinds = json.load(f)
                    logger.info(f"Loaded {len(self.keybinds)} keybinds from {KEYBINDS_FILE}")
            else:
                logger.info("No keybinds file found, using defaults")
                self.keybinds = {}
        except Exception as e:
            logger.error(f"Failed to load keybinds: {e}")
            self.keybinds = {}

    def _load_macros(self):
        """Load macros from JSON file"""
        try:
            self._protect_file(MACROS_FILE)
            if MACROS_FILE.exists():
                with open(MACROS_FILE, 'r', encoding='utf-8') as f:
                    self.macros = json.load(f)
                    logger.info(f"Loaded {len(self.macros)} macros from {MACROS_FILE}")
            else:
                logger.info("No macros file found, using defaults")
                self.macros = {}
        except Exception as e:
            logger.error(f"Failed to load macros: {e}")
            self.macros = {}

    def _load_theme(self):
        """Load theme from JSON file"""
        try:
            self._protect_file(THEME_FILE)
            if THEME_FILE.exists():
                with open(THEME_FILE, 'r', encoding='utf-8') as f:
                    self.theme = json.load(f)
                    logger.info(f"Loaded theme from {THEME_FILE}")
            else:
                logger.info("No theme file found, using defaults")
                self.theme = {}
        except Exception as e:
            logger.error(f"Failed to load theme: {e}")
            self.theme = {}

    def save_keybinds(self, keybinds: Dict) -> bool:
        """Save keybinds to JSON file"""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(KEYBINDS_FILE, 'w', encoding='utf-8') as f:
                json.dump(keybinds, f, indent=2)
            self.keybinds = keybinds
            self._protect_file(KEYBINDS_FILE)
            logger.info(f"Saved {len(keybinds)} keybinds to {KEYBINDS_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save keybinds: {e}")
            return False

    def save_macros(self, macros: Dict) -> bool:
        """Save macros to JSON file"""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(MACROS_FILE, 'w', encoding='utf-8') as f:
                json.dump(macros, f, indent=2)
            self.macros = macros
            self._protect_file(MACROS_FILE)
            logger.info(f"Saved {len(macros)} macros to {MACROS_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save macros: {e}")
            return False

    def save_theme(self, theme: Dict) -> bool:
        """Save theme to JSON file"""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(THEME_FILE, 'w', encoding='utf-8') as f:
                json.dump(theme, f, indent=2)
            self.theme = theme
            self._protect_file(THEME_FILE)
            logger.info(f"Saved theme to {THEME_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save theme: {e}")
            return False

    def is_configured(self) -> bool:
        """
        Check if Ollama is configured.

        Returns:
            True if Ollama host is set (always true with defaults)
        """
        return bool(self.ollama_host)

    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """
        Get API key - returns None as Ollama doesn't require keys.

        Args:
            provider: Ignored

        Returns:
            None (Ollama doesn't require API keys)
        """
        return None

    def set_api_key(self, provider: str, api_key: Optional[str]) -> None:
        """No-op - Ollama doesn't require API keys."""
        pass

    def clear_api_key(self, provider: str) -> None:
        """No-op - Ollama doesn't require API keys."""
        pass

    def get_effective_provider(self) -> str:
        """Returns 'ollama' always."""
        return "ollama"

    def has_provider_key(self, provider: Optional[str] = None) -> bool:
        """
        Check if Ollama is available.

        Returns:
            True if Ollama host is configured
        """
        return bool(self.ollama_host)

    def get_provider_endpoint(self, provider: str = None) -> Optional[str]:
        """Get the Ollama host URL."""
        return self.ollama_host

    def set(self, key: str, value):
        """Set a configuration attribute dynamically."""
        setattr(self, key, value)

    def get(self, key: str, default=None):
        """Get a configuration value dynamically with optional default"""
        return getattr(self, key, default)

    def update(self, values: Dict):
        """Update multiple configuration values at once"""
        for key, value in values.items():
            setattr(self, key, value)

    def save(self):
        """Save configuration to JSON file if config_path is set"""
        if not self.config_path:
            logger.warning("No config_path set, cannot save configuration")
            return False

        try:
            config_data = {
                'ollama_host': self.ollama_host,
                'ollama_model': self.ollama_model,
                'overlay_hotkey': self.overlay_hotkey,
                'check_interval': self.check_interval,
                'overlay_x': self.overlay_x,
                'overlay_y': self.overlay_y,
                'overlay_width': self.overlay_width,
                'overlay_height': self.overlay_height,
                'overlay_minimized': self.overlay_minimized,
                'overlay_opacity': self.overlay_opacity,
                'macros_enabled': self.macros_enabled,
                'macro_safety_understood': self.macro_safety_understood,
                'max_macro_repeat': self.max_macro_repeat,
                'macro_execution_timeout': self.macro_execution_timeout
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Saved configuration to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def _load_from_file(self):
        """Load configuration from JSON file if it exists"""
        if not self.config_path or not Path(self.config_path).exists():
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            logger.info(f"Loaded configuration from {self.config_path}")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse config file, using defaults: {e}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")

    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.ollama_host = 'http://localhost:11434'
        self.ollama_model = 'llama3'
        self.overlay_hotkey = 'ctrl+shift+g'
        self.check_interval = 5
        self.overlay_x = 100
        self.overlay_y = 100
        self.overlay_width = 900
        self.overlay_height = 700
        self.overlay_minimized = False
        self.overlay_opacity = 0.95
        self.macros_enabled = False
        self.macro_safety_understood = False
        self.max_macro_repeat = 10
        self.macro_execution_timeout = 30

    @staticmethod
    def save_to_env(
        provider: str = "ollama",
        session_tokens: Optional[Dict[str, dict]] = None,
        overlay_hotkey: str = 'ctrl+shift+g',
        check_interval: int = 5,
        overlay_x: int = None,
        overlay_y: int = None,
        overlay_width: int = None,
        overlay_height: int = None,
        overlay_minimized: bool = None,
        overlay_opacity: float = None,
        ollama_host: str = None,
        ollama_model: str = None
    ):
        """
        Save configuration to .env file.

        Args:
            provider: Ignored (always 'ollama')
            session_tokens: Ignored
            overlay_hotkey: Hotkey for overlay
            check_interval: Game check interval in seconds
            overlay_x: Overlay window X position
            overlay_y: Overlay window Y position
            overlay_width: Overlay window width
            overlay_height: Overlay window height
            overlay_minimized: Overlay minimized state
            overlay_opacity: Overlay opacity 0.0-1.0
            ollama_host: Ollama host URL
            ollama_model: Default Ollama model
        """
        # Determine .env file location
        if getattr(sys, 'frozen', False):
            env_path = Path(sys.executable).parent / '.env'
        else:
            env_path = Path(__file__).parent.parent / '.env'

        # Read existing .env file if it exists
        existing_content = {}
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_content[key.strip()] = value.strip()

        # Update with new values
        existing_content['OVERLAY_HOTKEY'] = overlay_hotkey
        existing_content['CHECK_INTERVAL'] = str(check_interval)

        if ollama_host:
            existing_content['OLLAMA_HOST'] = ollama_host
        if ollama_model:
            existing_content['OLLAMA_MODEL'] = ollama_model

        # Update overlay settings if provided
        if overlay_x is not None:
            existing_content['OVERLAY_X'] = str(overlay_x)
        if overlay_y is not None:
            existing_content['OVERLAY_Y'] = str(overlay_y)
        if overlay_width is not None:
            existing_content['OVERLAY_WIDTH'] = str(overlay_width)
        if overlay_height is not None:
            existing_content['OVERLAY_HEIGHT'] = str(overlay_height)
        if overlay_minimized is not None:
            existing_content['OVERLAY_MINIMIZED'] = str(overlay_minimized).lower()
        if overlay_opacity is not None:
            existing_content['OVERLAY_OPACITY'] = str(overlay_opacity)

        # Write to .env file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Gaming AI Assistant Configuration (Ollama)\n")
            f.write("# This file was generated by the Settings dialog\n\n")

            f.write("# Ollama Configuration\n")
            f.write(f"OLLAMA_HOST={existing_content.get('OLLAMA_HOST', 'http://localhost:11434')}\n")
            f.write(f"OLLAMA_MODEL={existing_content.get('OLLAMA_MODEL', 'llama3')}\n\n")

            f.write("# Application Settings\n")
            f.write(f"OVERLAY_HOTKEY={existing_content['OVERLAY_HOTKEY']}\n")
            f.write(f"CHECK_INTERVAL={existing_content['CHECK_INTERVAL']}\n\n")

            # Write overlay settings if they exist
            if 'OVERLAY_X' in existing_content:
                f.write("# Overlay Window Settings\n")
                f.write(f"OVERLAY_X={existing_content.get('OVERLAY_X', '100')}\n")
                f.write(f"OVERLAY_Y={existing_content.get('OVERLAY_Y', '100')}\n")
                f.write(f"OVERLAY_WIDTH={existing_content.get('OVERLAY_WIDTH', '900')}\n")
                f.write(f"OVERLAY_HEIGHT={existing_content.get('OVERLAY_HEIGHT', '700')}\n")
                f.write(f"OVERLAY_MINIMIZED={existing_content.get('OVERLAY_MINIMIZED', 'false')}\n")
                f.write(f"OVERLAY_OPACITY={existing_content.get('OVERLAY_OPACITY', '0.95')}\n")

        ensure_private_file(env_path)

        return env_path

    def __repr__(self):
        """String representation"""
        return f"Config(ollama_host={self.ollama_host}, model={self.ollama_model})"


if __name__ == "__main__":
    # Test configuration
    try:
        config = Config()
        print("Configuration loaded successfully:")
        print(config)
        print(f"Ollama Host: {config.ollama_host}")
        print(f"Ollama Model: {config.ollama_model}")
    except Exception as e:
        print(f"Configuration error: {e}")
