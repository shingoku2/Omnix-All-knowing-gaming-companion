#!/usr/bin/env python3
"""
Test for debounced overlay position saving feature.

This test verifies that the overlay window properly debounces position/size
saves to reduce I/O operations during drag/resize.
"""

import sys
import os
import unittest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class TestDebouncedPositionSaving(unittest.TestCase):
    """Test debounced position saving in OverlayWindow."""

    def test_debounce_timer_initialization(self):
        """Test that the debounce timer is properly initialized."""
        # Mock dependencies to avoid requiring full Qt environment
        with patch('src.gui.QTimer') as mock_timer_class, \
             patch('src.gui.ChatWidget'), \
             patch('src.gui._load_qss', return_value=""):

            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer

            from src.gui import OverlayWindow

            # Mock config and design system
            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = False
            mock_config.overlay_opacity = 0.8

            mock_ds = Mock()
            mock_ds.generate_overlay_stylesheet.return_value = ""

            # Create overlay window instance
            overlay = OverlayWindow(None, mock_config, mock_ds)

            # Verify timer was created and configured
            mock_timer_class.assert_called_once()
            mock_timer.setSingleShot.assert_called_once_with(True)
            mock_timer.timeout.connect.assert_called_once()

    def test_save_delay_is_configured(self):
        """Test that the save delay is properly configured."""
        with patch('src.gui.QTimer'), \
             patch('src.gui.ChatWidget'), \
             patch('src.gui._load_qss', return_value=""):

            from src.gui import OverlayWindow

            # Mock config and design system
            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = False
            mock_config.overlay_opacity = 0.8

            mock_ds = Mock()
            mock_ds.generate_overlay_stylesheet.return_value = ""

            # Create overlay window instance
            overlay = OverlayWindow(None, mock_config, mock_ds)

            # Verify save delay is set to 500ms
            self.assertEqual(overlay._save_delay_ms, 500)

    def test_code_structure(self):
        """Test that the required methods exist in OverlayWindow."""
        from src.gui import OverlayWindow

        # Verify the methods exist
        self.assertTrue(hasattr(OverlayWindow, 'moveEvent'))
        self.assertTrue(hasattr(OverlayWindow, 'resizeEvent'))
        self.assertTrue(hasattr(OverlayWindow, '_save_position_and_size'))

        # Verify they are callable
        self.assertTrue(callable(getattr(OverlayWindow, 'moveEvent')))
        self.assertTrue(callable(getattr(OverlayWindow, 'resizeEvent')))
        self.assertTrue(callable(getattr(OverlayWindow, '_save_position_and_size')))


if __name__ == '__main__':
    # Run tests
    print("=" * 70)
    print("Testing Debounced Overlay Position Saving")
    print("=" * 70)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestDebouncedPositionSaving)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)
