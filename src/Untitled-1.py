"""
AI Assistant Module
Handles AI queries and maintains conversation context

This module uses the provider abstraction layer and AI router for cleaner separation
of concerns. The AIAssistant focuses on conversation state management and game context,
while delegating actual API calls to the provider layer.
"""

import logging
import os
import threading
from typing import Callable, Dict, List, Optional, TYPE_CHECKING

from config import Config
from ai_router import get_router, AIRouter
from providers import ProviderError, ProviderAuthError, ProviderQuotaError, ProviderRateLimitError
# Fixed: Use relative import instead of absolute
from .knowledge_integration import get_knowledge_integration, KnowledgeIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Avoid circular imports
if TYPE_CHECKING:
    from game_profile import GameProfile


class AIAssistant:
    """AI-powered gaming assistant with conversation context management"""

    # Maximum conversation history to keep
    MAX_CONVERSATION_MESSAGES = 20

    def __init__(
        self,
        provider: Optional[str] = None,
        config: Optional[Config] = None,
        session_tokens: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize AI Assistant

        Args:
            provider: Provider name ('openai', 'anthropic', 'gemini').
                     If None, uses the configured default.
            config: Config instance (if None, creates a new one)
            session_tokens: Optional session tokens (currently stored but not used)
        """
        self.config = config or Config()
        self.router = get_router(self.config)
        self.provider = provider or self.config.ai_provider
        self.session_tokens = session_tokens or {}
        self.conversation_history = []
        self.current_game = None
        self.current_profile = None
        self.current_model = None
        self._session_refresh_handler: Optional[
            Callable[[str, str, Dict[str, str]], None]
        ] = None

        # Thread safety for conversation history
        self._history_lock = threading.Lock()

        # Initialize knowledge integration
        self.knowledge_integration = get_knowledge_integration()

        logger.info(f"AIAssistant initialized with provider: {self.provider}")