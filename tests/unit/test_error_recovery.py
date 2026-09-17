import pytest
from unittest.mock import MagicMock, patch

from omnix.error_recovery import ErrorRecovery, error_boundary

class TestErrorRecoveryWithFallback:
    def test_with_fallback_success(self):
        primary_mock = MagicMock(return_value="primary_success")
        fallback_mock = MagicMock()

        result = ErrorRecovery.with_fallback(primary_mock, fallback_mock)

        assert result == "primary_success"
        primary_mock.assert_called_once()
        fallback_mock.assert_not_called()

    def test_with_fallback_primary_fails(self):
        primary_mock = MagicMock(side_effect=ValueError("Primary failed"))
        fallback_mock = MagicMock(return_value="fallback_success")

        result = ErrorRecovery.with_fallback(primary_mock, fallback_mock)

        assert result == "fallback_success"
        primary_mock.assert_called_once()
        fallback_mock.assert_called_once()

    def test_with_fallback_both_fail(self):
        primary_exception = ValueError("Primary failed")
        primary_mock = MagicMock(side_effect=primary_exception)
        fallback_mock = MagicMock(side_effect=TypeError("Fallback failed"))

        with pytest.raises(ValueError) as exc_info:
            ErrorRecovery.with_fallback(primary_mock, fallback_mock)

        assert exc_info.value is primary_exception
        primary_mock.assert_called_once()
        fallback_mock.assert_called_once()

class TestErrorRecoveryGracefulDegrade:
    def test_graceful_degrade_success(self):
        primary_mock = MagicMock(return_value="primary_success")
        fallback_mock = MagicMock()

        result = ErrorRecovery.graceful_degrade("test_feature", primary_mock, fallback_mock)

        assert result == "primary_success"
        primary_mock.assert_called_once()
        fallback_mock.assert_not_called()

    def test_graceful_degrade_primary_fails_uses_fallback(self):
        primary_mock = MagicMock(side_effect=RuntimeError("Primary error"))
        fallback_mock = MagicMock(return_value="fallback_success")

        result = ErrorRecovery.graceful_degrade("test_feature", primary_mock, fallback_mock)

        assert result == "fallback_success"
        primary_mock.assert_called_once()
        fallback_mock.assert_called_once()

    def test_graceful_degrade_primary_fails_no_fallback(self):
        primary_exception = RuntimeError("Primary error")
        primary_mock = MagicMock(side_effect=primary_exception)

        with pytest.raises(RuntimeError) as exc_info:
            ErrorRecovery.graceful_degrade("test_feature", primary_mock)

        assert exc_info.value is primary_exception
        primary_mock.assert_called_once()

    def test_graceful_degrade_both_fail(self):
        primary_exception = RuntimeError("Primary error")
        primary_mock = MagicMock(side_effect=primary_exception)
        fallback_mock = MagicMock(side_effect=ValueError("Fallback error"))

        with pytest.raises(RuntimeError) as exc_info:
            ErrorRecovery.graceful_degrade("test_feature", primary_mock, fallback_mock)

        assert exc_info.value is primary_exception
        primary_mock.assert_called_once()
        fallback_mock.assert_called_once()

class TestErrorRecoverySafeApiCall:
    def test_safe_api_call_success_first_try(self):
        api_mock = MagicMock(return_value="api_success")

        result = ErrorRecovery.safe_api_call(api_mock, max_retries=3)

        assert result == "api_success"
        api_mock.assert_called_once()

    @patch('time.sleep')
    def test_safe_api_call_success_after_retries(self, mock_sleep):
        api_mock = MagicMock(side_effect=[Exception("fail"), Exception("fail"), "api_success"])

        result = ErrorRecovery.safe_api_call(api_mock, max_retries=3, retry_delay=0.1)

        assert result == "api_success"
        assert api_mock.call_count == 3
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(0.1)

    @patch('time.sleep')
    def test_safe_api_call_failure_returns_default(self, mock_sleep):
        api_mock = MagicMock(side_effect=Exception("fail"))

        result = ErrorRecovery.safe_api_call(api_mock, max_retries=3, default_response="default")

        assert result == "default"
        assert api_mock.call_count == 3
        assert mock_sleep.call_count == 2

class TestErrorBoundary:
    def test_error_boundary_success(self):
        @error_boundary("test_feature", fallback_return="fallback")
        def success_func():
            return "success"

        assert success_func() == "success"

    @patch('omnix.error_recovery.logger')
    def test_error_boundary_error_with_logging(self, mock_logger):
        @error_boundary("test_feature", fallback_return="fallback", log_errors=True)
        def error_func():
            raise ValueError("Test error")

        assert error_func() == "fallback"
        mock_logger.error.assert_called_once()
        mock_logger.debug.assert_called_once()

    @patch('omnix.error_recovery.logger')
    def test_error_boundary_error_without_logging(self, mock_logger):
        @error_boundary("test_feature", fallback_return="fallback", log_errors=False)
        def error_func():
            raise ValueError("Test error")

        assert error_func() == "fallback"
        mock_logger.error.assert_not_called()
        mock_logger.debug.assert_not_called()
