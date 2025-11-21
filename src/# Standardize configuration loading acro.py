# Standardize configuration loading across modules
"""
Configuration Module
Handles application configuration and settings
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

from credential_store import CredentialDecryptionError, CredentialStore, CredentialStoreError

logger = logging.getLogger(__name__)

# Configuration directory
CONFIG_DIR = Path.home() / '.gaming_ai_assistant'
KEYBINDS_FILE = CONFIG_DIR / 'keybinds.json'
MACROS_FILE = CONFIG_DIR / 'macros.json'
THEME_FILE = CONFIG_DIR / 'theme.json'


class Config:
    """Application configuration"""

    def __init__(self, env_file: Optional[str] = None, require_keys: bool = False,
                 config_path: Optional[str] = None, config_dir: Optional[str] = None):
        """
        Initialize configuration

        Args:
            env_file: Path to .env file (optional)
            require_keys: If True, raise error if API keys are missing (default: False)
            config_path: Optional path for persisted config data (kept for compatibility)
            config_dir: Optional configuration directory override (kept for compatibility)
        """
        self.config_path = config_path
        self.config_dir = config_dir
        
        # Load environment variables
        self._load_environment(env_file)
        
        # Secure credential storage
        self.credential_store = CredentialStore()
        credentials = self._load_secure_credentials()

        # AI Configuration
        self.ai_provider = os.getenv('AI_PROVIDER', 'anthropic').lower()
        self.openai_api_key = credentials.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = credentials.get('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.gemini_api_key = credentials.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')

        # Session tokens - load from secure storage instead of .env
        self.session_tokens: Dict[str, dict] = {}
        self._load_session_tokens_from_secure_storage(credentials)

        # Application Settings
        self.overlay_hotkey = os.getenv('OVERLAY_HOTKEY', 'ctrl+shift+g')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '5'))

        # Overlay Window Settings
        self.overlay_x = int(os.getenv('OVERLAY_X', '100'))
        self.overlay_y = int(os.getenv('OVERLAY_Y', '100'))
        self.overlay_width = int(os.getenv('OVERLAY_WIDTH', '900'))
        self.overlay_height = int(os.getenv('OVERLAY_HEIGHT', '700'))
        self.overlay_minimized = os.getenv('OVERLAY_MINIMIZED', 'false').lower() == 'true'
        # Validate opacity is in valid range [0.0, 1.0]
        opacity = float(os.getenv('OVERLAY_OPACITY', '0.95'))
        self.overlay_opacity = max(0.0, min(1.0, opacity))

        # Macro & Keybind Settings
        self.macros_enabled = os.getenv('MACROS_ENABLED', 'false').lower() == 'true'
        self.macro_safety_understood = os.getenv('MACRO_SAFETY_UNDERSTOOD', 'false').lower() == 'true'
        self.max_macro_repeat = int(os.getenv('MAX_MACRO_REPEAT', '10'))
        self.macro_execution_timeout = int(os.getenv('MACRO_EXECUTION_TIMEOUT', '30'))  # seconds

        # Extended Settings (stored in separate JSON files)
        self.keybinds: Dict = {}

    def _load_environment(self, env_file: Optional[str] = None) -> None:
        """Load environment variables from .env file"""
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            return

        # Try multiple locations for .env file
        possible_paths = [
            Path('.env'),  # Current working directory
            Path(__file__).parent.parent / '.env',  # Relative to this file
            Path(sys.executable).parent / '.env',  # Next to executable
        ]

        # For PyInstaller, also check sys._MEIPASS
        if getattr(sys, 'frozen', False):
            bundle_dir = Path(sys.executable).parent
            possible_paths.insert(0, bundle_dir / '.env')

        for env_path in possible_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                logger.info("Loaded .env from: %s", env_path)
                break

    def _load_secure_credentials(self) -> Dict[str, str]:
        """Load credentials from secure storage"""
        try:
            return self.credential_store.load_credentials() or {}
        except (CredentialStoreError, CredentialDecryptionError) as e:
            logger.warning("Failed to load secure credentials: %s", e)
            return {}

    def _load_session_tokens_from_secure_storage(self, credentials: Dict[str, str]) -> None:
        """Load session tokens from secure storage"""
        # Implementation would load from secure storage
        pass

    def save_to_env(self, path: Optional[str] = None) -> bool:
        """Save current configuration to .env file"""
        try:
            env_path = path or '.env'
            env_content = f"""# Gaming AI Assistant Configuration
AI_PROVIDER={self.ai_provider}
OPENAI_API_KEY={self.openai_api_key or ''}
ANTHROPIC_API_KEY={self.anthropic_api_key or ''}
GEMINI_API_KEY={self.gemini_api_key or ''}
OVERLAY_HOTKEY={self.overlay_hotkey}
CHECK_INTERVAL={self.check_interval}
OVERLAY_X={self.overlay_x}
OVERLAY_Y={self.overlay_y}
OVERLAY_WIDTH={self.overlay_width}
OVERLAY_HEIGHT={self.overlay_height}
OVERLAY_OPACITY={self.overlay_opacity}
OVERLAY_MINIMIZED={str(self.overlay_minimized).lower()}
MACROS_ENABLED={str(self.macros_enabled).lower()}
MACRO_SAFETY_UNDERSTOOD={str(self.macro_safety_understood).lower()}
MAX_MACRO_REPEAT={self.max_macro_repeat}
MACRO_EXECUTION_TIMEOUT={self.macro_execution_timeout}
"""
            with open(env_path, 'w') as f:
                f.write(env_content)
            logger.info("Configuration saved to %s", env_path)
            return True
        except Exception as e:
            logger.error("Failed to save configuration: %s", e)
            return False

    def is_configured(self) -> bool:
        """Check if the configuration is complete and valid"""
        if not self.ai_provider:
            return False
        
        if self.ai_provider == 'openai':
            return bool(self.openai_api_key)
        elif self.ai_provider == 'anthropic':
            return bool(self.anthropic_api_key)
        elif self.ai_provider == 'gemini':
            return bool(self.gemini_api_key)
        
        return False

    def validate(self) -> Dict[str, str]:
        """Validate configuration and return any errors"""
        errors = {}
        
        if not self.ai_provider:
            errors['ai_provider'] = 'AI provider is required'
        
        if self.ai_provider == 'openai' and not self.openai_api_key:
            errors['openai_api_key'] = 'OpenAI API key is required'
        elif self.ai_provider == 'anthropic' and not self.anthropic_api_key:
            errors['anthropic_api_key'] = 'Anthropic API key is required'
        elif self.ai_provider == 'gemini' and not self.gemini_api_key:
            errors['gemini_api_key'] = 'Gemini API key is required'
        
        if self.overlay_opacity < 0 or self.overlay_opacity > 1:
            errors['overlay_opacity'] = 'Opacity must be between 0.0 and 1.0'
        
        return errors