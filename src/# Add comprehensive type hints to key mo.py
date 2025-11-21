# Add comprehensive type hints to key modules
"""
Type Definitions and Annotations
Provides comprehensive type hints for the codebase
"""

from typing import Any, Dict, List, Optional, Union, Tuple, Callable, TypeVar, Generic
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Type variables for generic functions
T = TypeVar('T')
U = TypeVar('U')

# Game-related types
class GameStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


@dataclass
class GameInfo:
    """Information about a detected game"""
    name: str
    process_name: str
    status: GameStatus
    pid: Optional[int] = None
    window_title: Optional[str] = None
    executable_path: Optional[Path] = None
    detected_at: Optional[float] = None


@dataclass
class AIConfig:
    """AI provider configuration"""
    provider: str
    api_key: Optional[str] = None
    model: str = "default"
    temperature: float = 0.7
    max_tokens: int = 1000
    base_url: Optional[str] = None


@dataclass
class UIConfig:
    """UI configuration"""
    overlay_enabled: bool = True
    overlay_hotkey: str = "ctrl+shift+g"
    overlay_opacity: float = 0.95
    overlay_width: int = 900
    overlay_height: int = 700
    theme: str = "dark"


@dataclass
class MacroConfig:
    """Macro configuration"""
    enabled: bool = False
    safety_understood: bool = False
    max_repeat: int = 10
    execution_timeout: int = 30


@dataclass
class AppConfig:
    """Main application configuration"""
    ai: AIConfig
    ui: UIConfig
    macro: MacroConfig
    check_interval: int = 5
    version: str = "1.0.0"


# Function type aliases
MessageHandler = Callable[[Dict[str, Any]], None]
ErrorHandler = Callable[[Exception, str], bool]
ProgressCallback = Callable[[float, str], None]

# API response types
class APIResponse(Dict[str, Any]):
    """Base class for API responses"""
    @property
    def success(self) -> bool:
        return self.get('success', False)
    
    @property
    def data(self) -> Any:
        return self.get('data')
    
    @property
    def error(self) -> Optional[str]:
        return self.get('error')


class ChatResponse(APIResponse):
    """Chat API response"""
    @property
    def message(self) -> str:
        return self.get('message', '')
    
    @property
    def usage(self) -> Dict[str, int]:
        return self.get('usage', {})


class GameDetectionResponse(APIResponse):
    """Game detection response"""
    @property
    def games(self) -> List[GameInfo]:
        return self.get('games', [])


# Generic result wrapper
@dataclass
class Result(Generic[T]):
    """Generic result wrapper for operations that can fail"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def success(cls, data: T) -> 'Result[T]':
        return cls(success=True, data=data)
    
    @classmethod
    def failure(cls, error: str) -> 'Result[T]':
        return cls(success=False, error=error)
    
    def unwrap(self) -> T:
        """Get the data or raise an error"""
        if self.success:
            return self.data
        raise ValueError(self.error or "Unknown error")
    
    def unwrap_or(self, default: T) -> T:
        """Get the data or return a default value"""
        return self.data if self.success else default


# Async types for modern Python
from typing import AsyncIterator, Awaitable

AsyncTask = Awaitable[T]
AsyncStream = AsyncIterator[T]


# Configuration validation types
class ValidationError(Exception):
    """Configuration validation error"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[ValidationError] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def add_error(self, field: str, message: str) -> None:
        """Add a validation error"""
        self.errors.append(ValidationError(field, message))
        self.is_valid = False
    
    def throw_if_invalid(self) -> None:
        """Throw an exception if validation failed"""
        if not self.is_valid:
            error_messages = [str(error) for error in self.errors]
            raise ValidationError("Configuration", "\n".join(error_messages))


# Event types for the event system
class Event:
    """Base event class"""
    def __init__(self, name: str, data: Dict[str, Any] = None):
        self.name = name
        self.data = data or {}
        self.timestamp = time.time()
    
    def __repr__(self) -> str:
        return f"Event(name={self.name}, data={self.data})"


class GameEvent(Event):
    """Game-related events"""
    def __init__(self, game: GameInfo, event_type: str, **kwargs):
        super().__init__(f"game_{event_type}", {"game": game, **kwargs})


class AIEvent(Event):
    """AI-related events"""
    def __init__(self, event_type: str, **kwargs):
        super().__init__(f"ai_{event_type}", kwargs)


# Import time for Event base class
import time