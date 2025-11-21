# Add comprehensive error handling to key modules
"""
Error Handling and Recovery Module
Provides centralized error handling and recovery mechanisms
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling with recovery strategies"""
    
    def __init__(self):
        self.recovery_handlers = {}
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    def register_recovery(self, error_type: type, handler: Callable):
        """Register a recovery handler for specific error types"""
        self.recovery_handlers[error_type] = handler
        
    def handle_error(self, error: Exception, context: str = "") -> bool:
        """
        Handle an error with appropriate recovery
        
        Args:
            error: The exception to handle
            context: Additional context about where the error occurred
            
        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        logger.error(f"Error in {context}: {error}")
        
        # Look for specific recovery handler
        for error_type, handler in self.recovery_handlers.items():
            if isinstance(error, error_type):
                try:
                    return handler(error, context)
                except Exception as recovery_error:
                    logger.error(f"Recovery handler failed: {recovery_error}")
        
        # Default error handling
        logger.error(f"Unhandled error in {context}: {traceback.format_exc()}")
        return False

    def retry_on_error(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic
        
        Args:
            func: The function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            The function result
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    import time
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    break
        
        raise last_exception if last_exception else Exception("Unknown error")


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(default_return=None):
    """
    Decorator for automatic error handling
    
    Args:
        default_return: Value to return if an error occurs and can't be recovered
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = f"{func.__module__}.{func.__name__}"
                if error_handler.handle_error(e, context):
                    return default_return
                else:
                    raise
        return wrapper
    return decorator


# Specific error recovery handlers
def handle_api_error(error: Exception, context: str) -> bool:
    """Handle API-related errors"""
    error_msg = str(error).lower()
    
    if "quota" in error_msg:
        logger.error("API quota exceeded")
        # Could switch to a different provider here
        return False
    elif "rate limit" in error_msg:
        logger.warning("Rate limit hit, waiting before retry")
        import time
        time.sleep(60)  # Wait 1 minute
        return True  # Retry after waiting
    elif "authentication" in error_msg:
        logger.error("API authentication failed")
        # Could prompt for new API key
        return False
    
    return False


def handle_network_error(error: Exception, context: str) -> bool:
    """Handle network-related errors"""
    logger.warning(f"Network error in {context}, retrying...")
    import time
    time.sleep(5)  # Wait 5 seconds before retry
    return True  # Allow retry


def handle_file_error(error: Exception, context: str) -> bool:
    """Handle file-related errors"""
    if "permission" in str(error).lower():
        logger.error("File permission error")
        return False
    elif "not found" in str(error).lower():
        logger.warning("File not found, creating default")
        # Could create default file here
        return True
    return False


# Register recovery handlers
error_handler.register_recovery(Exception, handle_api_error)
error_handler.register_recovery(OSError, handle_network_error)
error_handler.register_recovery(IOError, handle_file_error)


# Usage examples:
@handle_errors(default_return=None)
def safe_api_call(api_function, *args, **kwargs):
    """Make an API call with error handling"""
    return api_function(*args, **kwargs)


@handle_errors(default_return=[])
def safe_file_read(filepath):
    """Read a file with error handling"""
    with open(filepath, 'r') as f:
        return f.readlines()