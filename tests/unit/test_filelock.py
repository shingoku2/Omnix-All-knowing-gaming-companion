"""
Tests for the FileLock module.
"""

import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from omnix.filelock import FileLock


@pytest.mark.unit
class TestFileLock:
    def test_init(self, tmp_path):
        """Test basic initialization of FileLock."""
        lock_file = tmp_path / "test.lock"
        lock = FileLock(str(lock_file), timeout=5, delay=0.1)

        assert lock.lock_file == lock_file
        assert lock.timeout == 5
        assert lock.delay == 0.1
        assert lock._fd is None

    def test_acquire_and_release_success(self, tmp_path):
        """Test successful acquire and release operations."""
        lock_file = tmp_path / "test.lock"
        lock = FileLock(str(lock_file))

        lock.acquire()
        assert lock._fd is not None
        assert lock_file.exists()

        # Store fd to verify it's closed (via mock or OS check if necessary)
        fd = lock._fd

        lock.release()
        assert lock._fd is None
        assert not lock_file.exists()

        # Verify fd is closed by trying to close it again (should raise OSError)
        with pytest.raises(OSError):
            os.close(fd)

    def test_acquire_creates_parent_directories(self, tmp_path):
        """Test that acquire creates parent directories if they don't exist."""
        lock_file = tmp_path / "nested" / "dir" / "test.lock"
        lock = FileLock(str(lock_file))

        lock.acquire()
        assert lock_file.parent.exists()
        lock.release()

    def test_context_manager(self, tmp_path):
        """Test using FileLock as a context manager."""
        lock_file = tmp_path / "test.lock"

        with FileLock(str(lock_file)) as lock:
            assert lock._fd is not None
            assert lock_file.exists()

        assert lock._fd is None
        assert not lock_file.exists()

    def test_acquire_timeout(self, tmp_path):
        """Test acquire timeout when lock is held by another process."""
        lock_file = tmp_path / "test.lock"
        # Simulate lock held by another process
        lock_file.touch()

        lock = FileLock(str(lock_file), timeout=0.1, delay=0.01)

        start = time.time()
        with pytest.raises(TimeoutError, match=f"Timeout while waiting for lock {lock_file}"):
            lock.acquire()

        # Ensure it waited for approximately the timeout duration
        assert time.time() - start >= 0.1

    def test_acquire_no_timeout_waits_forever(self, tmp_path):
        """Test acquire without timeout blocks indefinitely."""
        lock_file = tmp_path / "test.lock"
        lock_file.touch()

        lock = FileLock(str(lock_file), timeout=None, delay=0.01)

        # We can't actually wait forever, so we mock time.sleep to break the loop
        original_sleep = time.sleep

        def mock_sleep(secs):
            # Remove the lock file so the next iteration succeeds
            lock_file.unlink()
            original_sleep(secs)

        with patch('time.sleep', side_effect=mock_sleep):
            lock.acquire()

        assert lock._fd is not None
        assert lock_file.exists()
        lock.release()

    def test_acquire_retry_success(self, tmp_path):
        """Test acquire retries and eventually succeeds when lock becomes free."""
        lock_file = tmp_path / "test.lock"
        lock_file.touch()

        lock = FileLock(str(lock_file), timeout=1.0, delay=0.05)

        # Simulate lock being released during wait
        original_sleep = time.sleep

        def mock_sleep(secs):
            lock_file.unlink()
            original_sleep(secs)

        with patch('time.sleep', side_effect=mock_sleep):
            lock.acquire()

        assert lock._fd is not None
        assert lock_file.exists()
        lock.release()

    def test_release_without_acquire(self, tmp_path):
        """Test release does not crash if acquire was not called."""
        lock_file = tmp_path / "test.lock"
        lock = FileLock(str(lock_file))

        # Should not raise any errors
        lock.release()
        assert lock._fd is None

    def test_release_file_not_found(self, tmp_path):
        """Test release handles missing lock file gracefully."""
        lock_file = tmp_path / "test.lock"
        lock = FileLock(str(lock_file))

        lock.acquire()
        # Manually remove the file to simulate unexpected deletion
        lock_file.unlink()

        # Should not raise FileNotFoundError
        lock.release()
        assert lock._fd is None

    def test_context_manager_exception_handling(self, tmp_path):
        """Test that the lock is released even if an exception occurs."""
        lock_file = tmp_path / "test.lock"

        try:
            with FileLock(str(lock_file)) as lock:
                assert lock._fd is not None
                assert lock_file.exists()
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert lock._fd is None
        assert not lock_file.exists()
