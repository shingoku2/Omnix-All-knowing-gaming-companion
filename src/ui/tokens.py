"""
Omnix UI Design Tokens
======================

Design tokens define the visual foundation of the Omnix UI design system.
Based on a high-tech, AI-focused aesthetic with dark themes and vibrant accents.
"""

from dataclasses import dataclass
from typing import Dict, Literal


@dataclass
class ColorPalette:
    """Color palette for Omnix UI."""

    # Primary Backgrounds - Deep charcoal, near-black
    bg_primary: str = "#1A1A2E"
    bg_primary_alt: str = "#0F0F1A"

    # Secondary Backgrounds/Panels - Dark muted blues/greys
    bg_secondary: str = "#2C2C4A"
    bg_secondary_alt: str = "#3A3A5A"

    # Accent Colors - Vibrant & Digital
    accent_primary: str = "#00BFFF"  # Electric Blue
    accent_primary_bright: str = "#00FFFF"  # Cyan
    accent_primary_dark: str = "#1E90FF"  # Dodger Blue

    accent_secondary: str = "#39FF14"  # Neon Green (warnings, specific data)
    accent_tertiary: str = "#8A2BE2"  # Purple (alternative states)

    # Text Colors - Light grey/white for readability
    text_primary: str = "#FFFFFF"
    text_secondary: str = "#E0E0E0"
    text_muted: str = "#B0B0B0"
    text_disabled: str = "#707070"

    # Status Colors
    success: str = "#39FF14"  # Neon Green
    warning: str = "#FFB800"  # Amber
    error: str = "#FF3B3B"  # Red
    info: str = "#00BFFF"  # Electric Blue

    # Border Colors
    border_subtle: str = "#3A3A5A"
    border_default: str = "#4A4A6A"
    border_accent: str = "#00BFFF"

    # Overlay Colors (with alpha channel)
    overlay_dark: str = "rgba(15, 15, 26, 0.75)"  # 75% opacity
    overlay_medium: str = "rgba(15, 15, 26, 0.85)"  # 85% opacity
    overlay_light: str = "rgba(15, 15, 26, 0.95)"  # 95% opacity

    # Interactive States
    hover_overlay: str = "rgba(0, 191, 255, 0.1)"  # Blue tint
    active_overlay: str = "rgba(0, 191, 255, 0.2)"  # Stronger blue tint
    focus_outline: str = "#00BFFF"  # Electric Blue

    # Gradients (subtle, for depth)
    gradient_dark: str = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A1A2E, stop:1 #0F0F1A)"
    gradient_panel: str = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2C2C4A, stop:1 #1A1A2E)"


@dataclass
class Typography:
    """Typography system for Omnix UI."""

    # Font Families
    font_primary: str = "Roboto, 'Open Sans', Montserrat, sans-serif"
    font_monospace: str = "'Fira Code', 'Source Code Pro', 'Courier New', monospace"

    # Font Sizes (in pt)
    size_xs: int = 9
    size_sm: int = 10
    size_base: int = 11
    size_md: int = 12
    size_lg: int = 14
    size_xl: int = 16
    size_2xl: int = 20
    size_3xl: int = 24
    size_4xl: int = 32

    # Font Weights
    weight_normal: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700

    # Line Heights (relative to font size)
    line_height_tight: float = 1.2
    line_height_normal: float = 1.5
    line_height_relaxed: float = 1.75

    # Letter Spacing (in em)
    letter_spacing_tight: str = "-0.02em"
    letter_spacing_normal: str = "0em"
    letter_spacing_wide: str = "0.05em"


@dataclass
class Spacing:
    """Spacing system for consistent layouts."""

    # Base spacing unit (in px)
    unit: int = 4

    # Spacing scale (multiples of base unit)
    xs: int = 4   # 1 unit
    sm: int = 8   # 2 units
    md: int = 12  # 3 units
    base: int = 16  # 4 units
    lg: int = 24  # 6 units
    xl: int = 32  # 8 units
    xl2: int = 48  # 12 units
    xl3: int = 64  # 16 units

    # Common padding values
    padding_button: str = "8px 16px"
    padding_input: str = "10px 12px"
    padding_card: str = "16px"
    padding_panel: str = "24px"

    # Common margin values
    margin_sm: str = "8px"
    margin_md: str = "12px"
    margin_lg: str = "24px"


@dataclass
class BorderRadius:
    """Border radius values for components."""

    none: int = 0
    sm: int = 3
    base: int = 5
    md: int = 8
    lg: int = 12
    xl: int = 16
    full: int = 9999  # Pill shape


@dataclass
class Shadows:
    """Shadow effects for depth and elevation."""

    # Subtle shadows for panels
    sm: str = "0 1px 2px rgba(0, 0, 0, 0.3)"
    base: str = "0 2px 4px rgba(0, 0, 0, 0.4)"
    md: str = "0 4px 8px rgba(0, 0, 0, 0.5)"
    lg: str = "0 8px 16px rgba(0, 0, 0, 0.6)"
    xl: str = "0 12px 24px rgba(0, 0, 0, 0.7)"

    # Glow effects (using accent colors)
    glow_blue_sm: str = "0 0 4px rgba(0, 191, 255, 0.5)"
    glow_blue_md: str = "0 0 8px rgba(0, 191, 255, 0.6)"
    glow_blue_lg: str = "0 0 12px rgba(0, 191, 255, 0.7)"

    glow_green_sm: str = "0 0 4px rgba(57, 255, 20, 0.5)"
    glow_green_md: str = "0 0 8px rgba(57, 255, 20, 0.6)"

    # Inner shadow for depth
    inner: str = "inset 0 2px 4px rgba(0, 0, 0, 0.3)"


@dataclass
class Animation:
    """Animation timing and easing functions."""

    # Duration (in ms)
    duration_fast: int = 150
    duration_base: int = 250
    duration_slow: int = 350
    duration_slower: int = 500

    # Easing functions (CSS-style)
    ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    ease_out: str = "cubic-bezier(0, 0, 0.2, 1)"
    ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    ease_linear: str = "linear"
    ease_smooth: str = "cubic-bezier(0.25, 0.1, 0.25, 1)"


@dataclass
class ZIndex:
    """Z-index layering system."""

    base: int = 0
    dropdown: int = 100
    sticky: int = 200
    overlay: int = 300
    modal: int = 400
    popover: int = 500
    tooltip: int = 600
    notification: int = 700


class OmnixDesignTokens:
    """
    Central design tokens for the Omnix UI design system.

    This class provides access to all design tokens including colors,
    typography, spacing, shadows, and animations.

    Usage:
        tokens = OmnixDesignTokens()
        primary_bg = tokens.colors.bg_primary
        accent = tokens.colors.accent_primary
    """

    def __init__(self):
        self.colors = ColorPalette()
        self.typography = Typography()
        self.spacing = Spacing()
        self.radius = BorderRadius()
        self.shadows = Shadows()
        self.animation = Animation()
        self.z_index = ZIndex()

    def get_color_scheme(self) -> Dict[str, str]:
        """
        Get the complete color scheme as a dictionary.
        Useful for theming and bulk operations.
        """
        return {
            'bg_primary': self.colors.bg_primary,
            'bg_primary_alt': self.colors.bg_primary_alt,
            'bg_secondary': self.colors.bg_secondary,
            'bg_secondary_alt': self.colors.bg_secondary_alt,
            'accent_primary': self.colors.accent_primary,
            'accent_primary_bright': self.colors.accent_primary_bright,
            'accent_primary_dark': self.colors.accent_primary_dark,
            'accent_secondary': self.colors.accent_secondary,
            'accent_tertiary': self.colors.accent_tertiary,
            'text_primary': self.colors.text_primary,
            'text_secondary': self.colors.text_secondary,
            'text_muted': self.colors.text_muted,
            'success': self.colors.success,
            'warning': self.colors.warning,
            'error': self.colors.error,
            'info': self.colors.info,
        }

    def get_spacing_scale(self) -> Dict[str, int]:
        """Get the spacing scale as a dictionary."""
        return {
            'xs': self.spacing.xs,
            'sm': self.spacing.sm,
            'md': self.spacing.md,
            'base': self.spacing.base,
            'lg': self.spacing.lg,
            'xl': self.spacing.xl,
            'xl2': self.spacing.xl2,
            'xl3': self.spacing.xl3,
        }

    def get_font_sizes(self) -> Dict[str, int]:
        """Get the font size scale as a dictionary."""
        return {
            'xs': self.typography.size_xs,
            'sm': self.typography.size_sm,
            'base': self.typography.size_base,
            'md': self.typography.size_md,
            'lg': self.typography.size_lg,
            'xl': self.typography.size_xl,
            '2xl': self.typography.size_2xl,
            '3xl': self.typography.size_3xl,
            '4xl': self.typography.size_4xl,
        }


# Singleton instance for easy access
tokens = OmnixDesignTokens()


# Export commonly used values for convenience
COLORS = tokens.colors
TYPOGRAPHY = tokens.typography
SPACING = tokens.spacing
RADIUS = tokens.radius
SHADOWS = tokens.shadows
ANIMATION = tokens.animation
Z_INDEX = tokens.z_index
