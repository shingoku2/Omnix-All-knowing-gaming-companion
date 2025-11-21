# Test the fixes and run validation
"""
Test Suite for Gaming AI Assistant
Comprehensive testing of all modules and fixes
"""

import sys
import os
import unittest
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))


class TestImports(unittest.TestCase):
    """Test that all modules can be imported without circular import errors"""
    
    def test_import_ai_assistant(self):
        """Test AI assistant import"""
        try:
            from ai_assistant import AIAssistant
            self.assertTrue(hasattr(AIAssistant, '__init__'))
        except ImportError as e:
            self.fail(f"Failed to import AIAssistant: {e}")
    
    def test_import_config(self):
        """Test config import"""
        try:
            from config import Config
            self.assertTrue(hasattr(Config, '__init__'))
        except ImportError as e:
            self.fail(f"Failed to import Config: {e}")
    
    def test_import_providers(self):
        """Test providers import"""
        try:
            from providers import OpenAIProvider, ProviderError
            self.assertTrue(hasattr(OpenAIProvider, '__init__'))
            self.assertTrue(issubclass(ProviderError, Exception))
        except ImportError as e:
            self.fail(f"Failed to import providers: {e}")


class TestConfiguration(unittest.TestCase):
    """Test configuration loading and validation"""
    
    def test_config_creation(self):
        """Test basic config creation"""
        from config import Config
        config = Config()
        self.assertIsNotNone(config.ai_provider)
        self.assertIn(config.ai_provider, ['openai', 'anthropic', 'gemini'])
    
    def test_config_validation(self):
        """Test config validation"""
        from config import Config
        config = Config()
        errors = config.validate()
        self.assertIsInstance(errors, dict)


class TestErrorHandling(unittest.TestCase):
    """Test error handling mechanisms"""
    
    def test_error_handler_creation(self):
        """Test error handler creation"""
        from error_handling import ErrorHandler
        handler = ErrorHandler()
        self.assertEqual(handler.max_retries, 3)
    
    def test_retry_logic(self):
        """Test retry logic"""
        from error_handling import ErrorHandler
        handler = ErrorHandler()
        
        # Test successful execution
        def success_func():
            return "success"
        
        result = handler.retry_on_error(success_func)
        self.assertEqual(result, "success")
        
        # Test failing function
        call_count = 0
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = handler.retry_on_error(failing_func)
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)


class TestTypeHints(unittest.TestCase):
    """Test type hint definitions"""
    
    def test_game_info_dataclass(self):
        """Test GameInfo dataclass"""
        from type_definitions import GameInfo, GameStatus
        game = GameInfo(
            name="Test Game",
            process_name="test.exe",
            status=GameStatus.RUNNING,
            pid=1234
        )
        self.assertEqual(game.name, "Test Game")
        self.assertEqual(game.status, GameStatus.RUNNING)
    
    def test_result_wrapper(self):
        """Test Result wrapper"""
        from type_definitions import Result
        
        # Test success
        success_result = Result.success("data")
        self.assertTrue(success_result.success)
        self.assertEqual(success_result.data, "data")
        
        # Test failure
        failure_result = Result.failure("error")
        self.assertFalse(failure_result.success)
        self.assertEqual(failure_result.error, "error")
        
        # Test unwrap
        self.assertEqual(success_result.unwrap(), "data")
        
        # Test unwrap_or
        self.assertEqual(failure_result.unwrap_or("default"), "default")


class TestProviderImplementations(unittest.TestCase):
    """Test AI provider implementations"""
    
    def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization"""
        from providers import OpenAIProvider, ProviderAuthError
        
        # Test without API key
        with self.assertRaises(ProviderAuthError):
            OpenAIProvider(api_key=None)
        
        # Test with invalid API key format
        provider = OpenAIProvider(api_key="invalid_key")
        self.assertFalse(provider.is_configured())


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests([
        TestImports('test_import_ai_assistant'),
        TestImports('test_import_config'),
        TestImports('test_import_providers'),
        TestConfiguration('test_config_creation'),
        TestConfiguration('test_config_validation'),
        TestErrorHandling('test_error_handler_creation'),
        TestErrorHandling('test_retry_logic'),
        TestTypeHints('test_game_info_dataclass'),
        TestTypeHints('test_result_wrapper'),
        TestProviderImplementations('test_openai_provider_initialization'),
    ])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Gaming AI Assistant Test Suite")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)