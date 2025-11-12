"""
Configuration Module
Handles loading and managing configuration
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Manages application configuration"""

    DEFAULT_CONFIG = {
        "ai_provider": "anthropic",
        "openai_api_key": "",
        "anthropic_api_key": "",
        "gemini_api_key": "",
        "ollama_endpoint": "http://localhost:11434",
        "open_webui_api_key": "",
        "overlay_width": 400,
        "overlay_height": 300,
        "overlay_opacity": 0.9,
        "overlay_font_size": 10,
        "overlay_hotkey": "Ctrl+Shift+O",
        "auto_launch": False,
        "log_level": "INFO"
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_path: Path to config file (optional)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        if os.name == 'nt':  # Windows
            config_dir = os.path.expandvars(r'%APPDATA%\GamingAIAssistant')
        else:  # Unix/Linux
            config_dir = os.path.expanduser('~/.config/gaming-ai-assistant')

        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'config.json')

    def load_config(self) -> bool:
        """
        Load configuration from file

        Returns:
            True if loaded successfully
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle missing keys
                    self.config.update(loaded_config)
                logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                logger.info("No existing config file found, using defaults")
                self.save_config()
                return False

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            self.config = self.DEFAULT_CONFIG.copy()
            return False
        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            self.config = self.DEFAULT_CONFIG.copy()
            return False

    def save_config(self) -> bool:
        """
        Save configuration to file

        Returns:
            True if saved successfully
        """
        try:
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)

            logger.info(f"Configuration saved to {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving config: {e}", exc_info=True)
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration with dictionary

        Args:
            config_dict: Dictionary with configuration updates
        """
        self.config.update(config_dict)

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate that required API keys are set

        Returns:
            Dictionary with validation results
        """
        provider = self.get("ai_provider", "anthropic").lower()

        validation = {
            "provider_set": provider in ["openai", "anthropic", "gemini", "ollama"],
            "openai_key_set": bool(self.get("openai_api_key")),
            "anthropic_key_set": bool(self.get("anthropic_api_key")),
            "gemini_key_set": bool(self.get("gemini_api_key")),
        }

        # Validate based on selected provider
        if provider == "openai":
            validation["provider_valid"] = validation["openai_key_set"]
        elif provider == "anthropic":
            validation["provider_valid"] = validation["anthropic_key_set"]
        elif provider == "gemini":
            validation["provider_valid"] = validation["gemini_key_set"]
        elif provider == "ollama":
            validation["provider_valid"] = True  # Ollama doesn't require API key
        else:
            validation["provider_valid"] = False

        return validation

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        logger.info("Configuration reset to defaults")

    def __repr__(self) -> str:
        """String representation of config"""
        return f"Config(path={self.config_path}, keys={list(self.config.keys())})"


if __name__ == "__main__":
    config = Config()

    print("Current configuration:")
    for key, value in config.get_all().items():
        # Hide API keys for security
        if "key" in key.lower() or "token" in key.lower():
            value = "***hidden***" if value else "not set"
        print(f"  {key}: {value}")

    print("\nValidation:")
    validation = config.validate_api_keys()
    for check, result in validation.items():
        print(f"  {check}: {result}")
