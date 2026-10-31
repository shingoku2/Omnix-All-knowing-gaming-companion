"""
Configuration Module
Handles application configuration and settings

Simplified for Ollama-only - no API keys required.
"""

import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

from omnix.credential_store import CredentialDecryptionError, CredentialStore, CredentialStoreError
from omnix.security import ensure_private_dir, ensure_private_file

logger = logging.getLogger(__name__)


def _atomic_write_text(path: Path, text: str) -> None:
    """Write text via temp file + rename so a crash can't truncate the target."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _atomic_write_json(path: Path, value) -> None:
    _atomic_write_text(path, json.dumps(value, indent=2))


# Configuration directory
CONFIG_DIR = Path(os.getenv("OMNIX_CONFIG_DIR", str(Path.home() / ".gaming_ai_assistant")))
KEYBINDS_FILE = CONFIG_DIR / "keybinds.json"
MACROS_FILE = CONFIG_DIR / "macros.json"
THEME_FILE = CONFIG_DIR / "theme.json"

# AI Provider Constants
DEFAULT_AI_PROVIDER = "ollama"
SUPPORTED_AI_PROVIDERS = [DEFAULT_AI_PROVIDER]  # Currently only Ollama is supported

# Default Configuration Values
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3"
DEFAULT_OVERLAY_HOTKEY = "ctrl+shift+g"
DEFAULT_CHECK_INTERVAL = 5
DEFAULT_OVERLAY_X = 100
DEFAULT_OVERLAY_Y = 100
DEFAULT_OVERLAY_WIDTH = 900
DEFAULT_OVERLAY_HEIGHT = 700
DEFAULT_OVERLAY_MINIMIZED = False
DEFAULT_OVERLAY_OPACITY = 0.95
DEFAULT_MACROS_ENABLED = False
DEFAULT_MACRO_SAFETY_UNDERSTOOD = False
DEFAULT_MAX_MACRO_REPEAT = 10
DEFAULT_MACRO_EXECUTION_TIMEOUT = 30

CONFIG_FILENAME = "config.json"

# Marks a config.json written by Config.save(). Files without it predate 3.0
# (3.0 never wrote one), so their values are stale and must not override .env.
SETTINGS_VERSION_KEY = "settings_version"
SETTINGS_VERSION = 1

# Persisted ints that must be positive to be usable.
_POSITIVE_FIELDS = {
    "check_interval",
    "overlay_width",
    "overlay_height",
    "max_macro_repeat",
    "macro_execution_timeout",
}

# Attributes Config.save() persists, with the JSON types accepted on load.
_PERSISTED_FIELDS = {
    "ai_provider": (str,),
    "ollama_host": (str,),
    "ollama_model": (str,),
    "ai_base_url": (str, type(None)),
    "ai_model": (str, type(None)),
    "overlay_hotkey": (str,),
    "check_interval": (int,),
    "overlay_x": (int,),
    "overlay_y": (int,),
    "overlay_width": (int,),
    "overlay_height": (int,),
    "overlay_minimized": (bool,),
    "overlay_opacity": (int, float),
    "macros_enabled": (bool,),
    "macro_safety_understood": (bool,),
    "max_macro_repeat": (int,),
    "macro_execution_timeout": (int,),
}


def _is_valid_setting(key: str, value, types: tuple) -> bool:
    """Check a value read from config.json before applying it."""
    # bool is an int subclass; only accept it where a bool is meant.
    if not isinstance(value, types) or (isinstance(value, bool) and bool not in types):
        return False
    if key in _POSITIVE_FIELDS:
        return value > 0
    if key == "ai_provider":
        return value in SUPPORTED_AI_PROVIDERS
    return True


class Config:
    """Application configuration (Ollama-only)"""

    def __init__(
        self,
        env_file: Optional[str] = None,
        require_keys: bool = False,
        config_path: Optional[str] = None,
        config_dir: Optional[str] = None,
    ):
        """
        Initialize configuration.

        Args:
            env_file: Path to .env file (optional)
            require_keys: Ignored (kept for compatibility)
            config_path: Optional path for persisted config data; defaults to
                config.json in the configuration directory
            config_dir: Optional configuration directory override
        """
        resolved_config_dir = (
            Path(config_dir)
            if config_dir
            else Path(config_path).parent if config_path else CONFIG_DIR
        )
        self.config_path = str(config_path or resolved_config_dir / CONFIG_FILENAME)
        self.config_dir = str(resolved_config_dir)
        self.keybinds_file = resolved_config_dir / "keybinds.json"
        self.macros_file = resolved_config_dir / "macros.json"
        self.theme_file = resolved_config_dir / "theme.json"
        self._ensure_secure_directories()

        # Load environment variables
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            self._protect_file(Path(env_file))
        else:
            possible_paths = [
                Path(".env"),
                Path(__file__).parent.parent / ".env",
                Path(sys.executable).parent / ".env",
            ]

            if getattr(sys, "frozen", False):
                bundle_dir = Path(sys.executable).parent
                possible_paths.insert(0, bundle_dir / ".env")

            for env_path in possible_paths:
                if env_path.exists():
                    load_dotenv(env_path, override=True)
                    logger.info("Loaded .env from: %s", env_path)
                    self._protect_file(env_path)
                    break

        # Credential storage (kept for potential secured Ollama endpoints).
        # Scoped to this Config's own config_dir so custom-profile/test
        # instances don't read or write into the real user vault.
        self.credential_store = CredentialStore(config_dir=self.config_dir)

        # AI Configuration - Ollama and OpenAI-compatible
        self.ai_provider = os.getenv("AI_PROVIDER", DEFAULT_AI_PROVIDER)
        self.ollama_host = (
            os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_BASE_URL") or DEFAULT_OLLAMA_HOST
        )
        self.ollama_model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)

        # OpenAI-Compatible Configuration
        self.ai_api_key = os.getenv("AI_API_KEY")
        self.ai_base_url = os.getenv("AI_BASE_URL")
        self.ai_model = os.getenv("AI_MODEL")

        # The key value known to be in the vault, so save() can skip rewriting it.
        self._vaulted_api_key: Optional[str] = None
        if self.ai_api_key:
            # A plaintext key found in .env (legacy) is migrated into the
            # encrypted credential store; save_to_env() no longer writes it
            # back to disk in plaintext once this has run.
            try:
                self.credential_store.save_credentials({"AI_API_KEY": self.ai_api_key})
                self._vaulted_api_key = self.ai_api_key
            except CredentialStoreError as exc:
                logger.warning("Could not migrate AI_API_KEY into credential store: %s", exc)
        else:
            try:
                self.ai_api_key = self.credential_store.get("AI_API_KEY")
                self._vaulted_api_key = self.ai_api_key
            except CredentialStoreError as exc:
                logger.warning("Could not read AI_API_KEY from credential store: %s", exc)

        # Application Settings
        self.overlay_hotkey = os.getenv("OVERLAY_HOTKEY", DEFAULT_OVERLAY_HOTKEY)
        self.check_interval = int(os.getenv("CHECK_INTERVAL", DEFAULT_CHECK_INTERVAL))

        # Overlay Window Settings
        self.overlay_x = int(os.getenv("OVERLAY_X", DEFAULT_OVERLAY_X))
        self.overlay_y = int(os.getenv("OVERLAY_Y", DEFAULT_OVERLAY_Y))
        self.overlay_width = int(os.getenv("OVERLAY_WIDTH", DEFAULT_OVERLAY_WIDTH))
        self.overlay_height = int(os.getenv("OVERLAY_HEIGHT", DEFAULT_OVERLAY_HEIGHT))
        self.overlay_minimized = (
            os.getenv("OVERLAY_MINIMIZED", str(DEFAULT_OVERLAY_MINIMIZED)).lower() == "true"
        )
        opacity = float(os.getenv("OVERLAY_OPACITY", DEFAULT_OVERLAY_OPACITY))
        self.overlay_opacity = max(0.0, min(1.0, opacity))

        # Macro & Keybind Settings
        self.macros_enabled = (
            os.getenv("MACROS_ENABLED", str(DEFAULT_MACROS_ENABLED)).lower() == "true"
        )
        self.macro_safety_understood = (
            os.getenv("MACRO_SAFETY_UNDERSTOOD", str(DEFAULT_MACRO_SAFETY_UNDERSTOOD)).lower()
            == "true"
        )
        self.max_macro_repeat = int(os.getenv("MAX_MACRO_REPEAT", DEFAULT_MAX_MACRO_REPEAT))
        self.macro_execution_timeout = int(
            os.getenv("MACRO_EXECUTION_TIMEOUT", DEFAULT_MACRO_EXECUTION_TIMEOUT)
        )

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
            ensure_private_dir(Path(self.config_dir))
        except Exception as exc:
            logger.warning("Failed to secure config dir %s: %s", self.config_dir, exc)

    def _protect_file(self, path: Path) -> None:
        """Ensure a configuration file is restricted to the current user."""
        try:
            ensure_private_file(path)
        except Exception as exc:
            logger.warning("Unable to harden permissions for %s: %s", path, exc)

    def _load_keybinds(self):
        """Load keybinds from JSON file"""
        try:
            self._protect_file(self.keybinds_file)
            if self.keybinds_file.exists():
                with open(self.keybinds_file, "r", encoding="utf-8") as f:
                    self.keybinds = json.load(f)
                    logger.info(f"Loaded {len(self.keybinds)} keybinds from {self.keybinds_file}")
            else:
                logger.info("No keybinds file found, using defaults")
                self.keybinds = {}
        except Exception as e:
            logger.error(f"Failed to load keybinds: {e}")
            self.keybinds = {}

    def _load_macros(self):
        """Load macros from JSON file"""
        try:
            self._protect_file(self.macros_file)
            if self.macros_file.exists():
                with open(self.macros_file, "r", encoding="utf-8") as f:
                    self.macros = json.load(f)
                    logger.info(f"Loaded {len(self.macros)} macros from {self.macros_file}")
            else:
                logger.info("No macros file found, using defaults")
                self.macros = {}
        except Exception as e:
            logger.error(f"Failed to load macros: {e}")
            self.macros = {}

    def _load_theme(self):
        """Load theme from JSON file"""
        try:
            self._protect_file(self.theme_file)
            if self.theme_file.exists():
                with open(self.theme_file, "r", encoding="utf-8") as f:
                    self.theme = json.load(f)
                    logger.info(f"Loaded theme from {self.theme_file}")
            else:
                logger.info("No theme file found, using defaults")
                self.theme = {}
        except Exception as e:
            logger.error(f"Failed to load theme: {e}")
            self.theme = {}

    def save_keybinds(self, keybinds: Dict) -> bool:
        """Save keybinds to JSON file"""
        try:
            Path(self.config_dir).mkdir(parents=True, exist_ok=True)
            _atomic_write_json(self.keybinds_file, keybinds)
            self.keybinds = keybinds
            self._protect_file(self.keybinds_file)
            logger.info(f"Saved {len(keybinds)} keybinds to {self.keybinds_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save keybinds: {e}")
            return False

    def save_macros(self, macros: Dict) -> bool:
        """Save macros to JSON file"""
        try:
            Path(self.config_dir).mkdir(parents=True, exist_ok=True)
            _atomic_write_json(self.macros_file, macros)
            self.macros = macros
            self._protect_file(self.macros_file)
            logger.info(f"Saved {len(macros)} macros to {self.macros_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save macros: {e}")
            return False

    def save_theme(self, theme: Dict) -> bool:
        """Save theme to JSON file"""
        try:
            Path(self.config_dir).mkdir(parents=True, exist_ok=True)
            _atomic_write_json(self.theme_file, theme)
            self.theme = theme
            self._protect_file(self.theme_file)
            logger.info(f"Saved theme to {self.theme_file}")
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

    def get_provider_endpoint(self, provider: Optional[str] = None) -> Optional[str]:
        """Get the Ollama host URL."""
        return self.ollama_host

    def get_ai_config(self) -> Dict:
        """Get AI configuration as a dictionary for the provider factory."""
        return {
            "AI_PROVIDER": self.ai_provider,
            "OLLAMA_BASE_URL": self.ollama_host,
            "OLLAMA_MODEL": self.ollama_model,
            "AI_API_KEY": self.ai_api_key,
            "AI_BASE_URL": self.ai_base_url,
            "AI_MODEL": self.ai_model,
        }

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
        """Save configuration to config.json"""
        path = Path(self.config_path)
        try:
            # The key is kept out of the JSON, so make sure the vault holds it
            # first (a legacy config.json may have been its only copy).
            if self.ai_api_key and self.ai_api_key != self._vaulted_api_key:
                try:
                    self.credential_store.save_credentials({"AI_API_KEY": self.ai_api_key})
                    self._vaulted_api_key = self.ai_api_key
                except CredentialStoreError as exc:
                    logger.error("Not saving configuration: AI_API_KEY vault write failed: %s", exc)
                    return False

            # Keep keys this method doesn't manage (e.g. the migrations'
            # schema_version), but never carry a plaintext key forward.
            config_data = {}
            if path.exists():
                try:
                    existing = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(existing, dict):
                        config_data = existing
                except (OSError, ValueError) as exc:
                    logger.warning("Overwriting unreadable config file %s: %s", path, exc)
            config_data.pop("ai_api_key", None)
            config_data.update({key: getattr(self, key) for key in _PERSISTED_FIELDS})
            config_data[SETTINGS_VERSION_KEY] = SETTINGS_VERSION

            _atomic_write_json(path, config_data)
            self._protect_file(path)

            logger.info(f"Saved configuration to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def _load_from_file(self):
        """Load configuration from config.json if it exists"""
        path = Path(self.config_path)
        if not path.exists():
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("config file must contain a JSON object")

            # A pre-3.0 file may hold the only copy of the API key; keep it
            # in memory so save() moves it into the vault.
            legacy_key = data.get("ai_api_key")
            if isinstance(legacy_key, str) and legacy_key and not self.ai_api_key:
                self.ai_api_key = legacy_key

            stamp = data.get(SETTINGS_VERSION_KEY)
            # True and 1.0 compare equal to 1, so check the exact type too.
            if type(stamp) is not int or stamp != SETTINGS_VERSION:
                logger.info("Ignoring settings in legacy config file %s", path)
                return

            for key, types in _PERSISTED_FIELDS.items():
                if key not in data:
                    continue
                value = data[key]
                if _is_valid_setting(key, value, types):
                    setattr(self, key, value)
                else:
                    logger.warning("Ignoring invalid %s in %s: %r", key, path, value)
            self.overlay_opacity = max(0.0, min(1.0, float(self.overlay_opacity)))

            logger.info(f"Loaded configuration from {self.config_path}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse config file, using defaults: {e}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")

    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.ai_provider = DEFAULT_AI_PROVIDER
        self.ollama_host = DEFAULT_OLLAMA_HOST
        self.ollama_model = DEFAULT_OLLAMA_MODEL
        self.overlay_hotkey = DEFAULT_OVERLAY_HOTKEY
        self.check_interval = DEFAULT_CHECK_INTERVAL
        self.overlay_x = DEFAULT_OVERLAY_X
        self.overlay_y = DEFAULT_OVERLAY_Y
        self.overlay_width = DEFAULT_OVERLAY_WIDTH
        self.overlay_height = DEFAULT_OVERLAY_HEIGHT
        self.overlay_minimized = DEFAULT_OVERLAY_MINIMIZED
        self.overlay_opacity = DEFAULT_OVERLAY_OPACITY
        self.macros_enabled = DEFAULT_MACROS_ENABLED
        self.macro_safety_understood = DEFAULT_MACRO_SAFETY_UNDERSTOOD
        self.max_macro_repeat = DEFAULT_MAX_MACRO_REPEAT
        self.macro_execution_timeout = DEFAULT_MACRO_EXECUTION_TIMEOUT

    @staticmethod
    def save_to_env(
        provider: str = DEFAULT_AI_PROVIDER,
        session_tokens: Optional[Dict[str, dict]] = None,
        overlay_hotkey: str = DEFAULT_OVERLAY_HOTKEY,
        check_interval: int = DEFAULT_CHECK_INTERVAL,
        overlay_x: Optional[int] = None,
        overlay_y: Optional[int] = None,
        overlay_width: Optional[int] = None,
        overlay_height: Optional[int] = None,
        overlay_minimized: Optional[bool] = None,
        overlay_opacity: Optional[float] = None,
        ollama_host: Optional[str] = None,
        ollama_model: Optional[str] = None,
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
        if getattr(sys, "frozen", False):
            env_path = Path(sys.executable).parent / ".env"
        else:
            env_path = Path(__file__).parent.parent / ".env"

        # Read existing .env file if it exists
        existing_content = {}
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        existing_content[key.strip()] = value.strip()

        # Callers always pass the value they want persisted.
        existing_content["OVERLAY_HOTKEY"] = overlay_hotkey
        existing_content["CHECK_INTERVAL"] = str(check_interval)

        if ollama_host:
            existing_content["OLLAMA_HOST"] = ollama_host
        if ollama_model:
            existing_content["OLLAMA_MODEL"] = ollama_model

        # Update overlay settings if provided
        if overlay_x is not None:
            existing_content["OVERLAY_X"] = str(overlay_x)
        if overlay_y is not None:
            existing_content["OVERLAY_Y"] = str(overlay_y)
        if overlay_width is not None:
            existing_content["OVERLAY_WIDTH"] = str(overlay_width)
        if overlay_height is not None:
            existing_content["OVERLAY_HEIGHT"] = str(overlay_height)
        if overlay_minimized is not None:
            existing_content["OVERLAY_MINIMIZED"] = str(overlay_minimized).lower()
        if overlay_opacity is not None:
            existing_content["OVERLAY_OPACITY"] = str(overlay_opacity)

        # AI API key: migrate any plaintext value found in the existing
        # .env into the encrypted credential store instead of writing it
        # back to disk in plaintext on every settings save. Only drop it
        # from .env once the vault write actually succeeds - otherwise
        # (e.g. keyring unavailable and no master password configured)
        # keep writing it in plaintext so the key isn't silently lost.
        # This runs before the file is touched so a vault failure can't
        # leave a half-written .env behind.
        ai_api_key = existing_content.get("AI_API_KEY", "")
        ai_base_url = existing_content.get("AI_BASE_URL", "")
        ai_model = existing_content.get("AI_MODEL", "")
        migrated = False
        if ai_api_key:
            try:
                CredentialStore().save_credentials({"AI_API_KEY": ai_api_key})
                migrated = True
            except CredentialStoreError as exc:
                logger.warning(
                    "Could not migrate AI_API_KEY to credential store, keeping it in .env: %s",
                    exc,
                )

        lines = [
            "# Gaming AI Assistant Configuration (Ollama)",
            "# This file was generated by the Settings dialog",
            "",
            "# Ollama Configuration",
            f"OLLAMA_HOST={existing_content.get('OLLAMA_HOST', 'http://localhost:11434')}",
            f"OLLAMA_MODEL={existing_content.get('OLLAMA_MODEL', 'llama3')}",
            "",
            "# Application Settings",
            f"OVERLAY_HOTKEY={existing_content['OVERLAY_HOTKEY']}",
            f"CHECK_INTERVAL={existing_content['CHECK_INTERVAL']}",
            "",
        ]

        if (ai_api_key and not migrated) or ai_base_url or ai_model:
            lines.append("# AI API Settings")
            if ai_api_key and not migrated:
                lines.append(f"AI_API_KEY={ai_api_key}")
            if ai_base_url:
                lines.append(f"AI_BASE_URL={ai_base_url}")
            if ai_model:
                lines.append(f"AI_MODEL={ai_model}")
            lines.append("")

        if "OVERLAY_X" in existing_content:
            lines += [
                "# Overlay Window Settings",
                f"OVERLAY_X={existing_content.get('OVERLAY_X', '100')}",
                f"OVERLAY_Y={existing_content.get('OVERLAY_Y', '100')}",
                f"OVERLAY_WIDTH={existing_content.get('OVERLAY_WIDTH', '900')}",
                f"OVERLAY_HEIGHT={existing_content.get('OVERLAY_HEIGHT', '700')}",
                f"OVERLAY_MINIMIZED={existing_content.get('OVERLAY_MINIMIZED', 'false')}",
                f"OVERLAY_OPACITY={existing_content.get('OVERLAY_OPACITY', '0.95')}",
                "",
            ]

        # Keep keys this function doesn't manage (SUPABASE_URL, AI_PROVIDER,
        # MACROS_ENABLED, ...) instead of silently dropping them on save.
        managed = {
            "OLLAMA_HOST",
            "OLLAMA_MODEL",
            "OVERLAY_HOTKEY",
            "CHECK_INTERVAL",
            "AI_API_KEY",
            "AI_BASE_URL",
            "AI_MODEL",
            "OVERLAY_X",
            "OVERLAY_Y",
            "OVERLAY_WIDTH",
            "OVERLAY_HEIGHT",
            "OVERLAY_MINIMIZED",
            "OVERLAY_OPACITY",
        }
        other = {k: v for k, v in existing_content.items() if k not in managed}
        if other:
            lines.append("# Other Settings")
            lines += [f"{key}={value}" for key, value in other.items()]
            lines.append("")

        # A value containing a line break would inject extra KEY=VALUE lines
        # that load on the next launch, so refuse it rather than write it.
        for line in lines:
            if "\n" in line or "\r" in line:
                key = line.split("=", 1)[0]
                raise ValueError(f"Refusing to write a line break into .env value for {key}")

        _atomic_write_text(env_path, "\n".join(lines) + "\n")

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
