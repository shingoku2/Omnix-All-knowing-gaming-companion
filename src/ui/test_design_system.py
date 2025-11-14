"""
Omnix UI Design System - Test Suite
====================================

Quick test to verify all components import correctly and basic functionality works.
"""

import sys
import os

# Add ui directory to path to import directly
ui_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ui_dir)


def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")

    # Core modules (import directly from ui package)
    import tokens
    import design_system
    from tokens import COLORS, TYPOGRAPHY, SPACING, RADIUS, SHADOWS, ANIMATION, Z_INDEX
    from design_system import OmnixDesignSystem
    from icons import OmnixIcons, icons

    # Components
    from components import (
        OmnixButton,
        OmnixIconButton,
        OmnixLineEdit,
        OmnixTextEdit,
        OmnixComboBox,
        OmnixCard,
        OmnixPanel,
        OmnixInfoCard,
        OmnixVBox,
        OmnixHBox,
        OmnixGrid,
        OmnixFormLayout,
        OmnixSidebar,
        OmnixSidebarButton,
        OmnixHeaderBar,
        OmnixDialog,
        OmnixConfirmDialog,
        OmnixMessageDialog,
        OmnixInputDialog,
    )

    # Overlay components
    from components.overlay import (
        OmnixOverlayPanel,
        OmnixOverlayChatWidget,
        OmnixOverlayTip,
        OmnixOverlayStatus,
    )

    print("✓ All imports successful (basic UI modules)")


def test_tokens():
    """Test design tokens."""
    print("\nTesting design tokens...")

    from tokens import tokens, COLORS

    # Test color palette
    assert COLORS.bg_primary == "#1A1A2E"
    assert COLORS.accent_primary == "#00BFFF"
    assert COLORS.text_primary == "#FFFFFF"

    # Test token access
    color_scheme = tokens.get_color_scheme()
    assert "bg_primary" in color_scheme
    assert "accent_primary" in color_scheme

    font_sizes = tokens.get_font_sizes()
    assert "base" in font_sizes
    assert font_sizes["base"] == 11

    print("✓ Design tokens working correctly")


def test_stylesheet_generation():
    """Test stylesheet generation."""
    print("\nTesting stylesheet generation...")

    from design_system import design_system

    # Generate complete stylesheet
    stylesheet = design_system.generate_complete_stylesheet()
    assert isinstance(stylesheet, str)
    assert len(stylesheet) > 0
    assert "QWidget" in stylesheet
    assert "#1A1A2E" in stylesheet  # bg_primary
    assert "#00BFFF" in stylesheet  # accent_primary

    # Generate overlay stylesheet
    overlay_style = design_system.generate_overlay_stylesheet(opacity=0.75)
    assert isinstance(overlay_style, str)
    assert "rgba" in overlay_style

    print("✓ Stylesheet generation working correctly")


def test_icons():
    """Test icon system."""
    print("\nTesting icon system...")

    from icons import icons

    # Get available icons
    available = icons.available_icons()
    assert len(available) > 0
    assert "omnix_logo" in available
    assert "chat" in available
    assert "settings" in available

    # Get an icon (this will only fully work in PyQt6 environment)
    try:
        from PyQt6.QtGui import QIcon
        icon = icons.get_icon("chat", size=32)
        assert isinstance(icon, QIcon)
        print("✓ Icon system working correctly (PyQt6 available)")
    except ImportError:
        print("⚠ Icon system imports work (PyQt6 not available for full test)")


def test_theme_bridge():
    """Test theme bridge compatibility."""
    print("\nTesting theme bridge...")

    try:
        # Add parent src directory for theme_manager import
        import sys
        import os
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        from theme_bridge import OmnixThemeBridge, migrate_to_omnix_design_system
        from theme_manager import Theme

        # Create bridge
        bridge = OmnixThemeBridge()
        assert bridge is not None

        # Convert legacy theme
        omnix_theme = bridge.convert_legacy_to_omnix()
        assert isinstance(omnix_theme, Theme)
        assert omnix_theme.primary_color == "#00BFFF"  # Omnix accent_primary

        # Migration helper
        bridge2, theme2 = migrate_to_omnix_design_system()
        assert bridge2 is not None
        assert theme2 is not None

        print("✓ Theme bridge working correctly")
    except ImportError as e:
        print(f"⚠ Theme bridge test skipped (dependencies not available): {e}")


def test_component_creation():
    """Test component instantiation (without PyQt6 display)."""
    print("\nTesting component creation...")

    try:
        from PyQt6.QtWidgets import QApplication
        from components import OmnixButton, OmnixCard, OmnixPanel

        # Create minimal app
        app = QApplication.instance() or QApplication([])

        # Create components
        button = OmnixButton("Test Button")
        assert button is not None
        assert button.text() == "Test Button"

        card = OmnixCard(title="Test Card")
        assert card is not None

        panel = OmnixPanel()
        assert panel is not None

        print("✓ Component creation working correctly")

    except ImportError:
        print("⚠ Component creation test skipped (PyQt6 not available)")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Omnix UI Design System - Test Suite")
    print("=" * 60)

    try:
        test_imports()
        test_tokens()
        test_stylesheet_generation()
        test_icons()
        test_theme_bridge()
        test_component_creation()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
