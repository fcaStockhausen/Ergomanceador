"""
Emoji/Unicode font support for pygame.

Pygame's default font doesn't support emoji. This module provides
a fallback system that uses system fonts with emoji support.
"""

import pygame
import sys
import os


def get_emoji_font(size=24):
    """
    Get a font that supports emoji/Unicode characters.

    Tries system fonts in order:
    - macOS: Apple Color Emoji, SF Pro
    - Windows: Segoe UI Emoji
    - Linux: Noto Color Emoji
    - Fallback: pygame default font (will show squares)

    Returns pygame.Font object
    """
    emoji_font_names = []

    # Platform-specific emoji fonts
    if sys.platform == 'darwin':  # macOS
        emoji_font_names = [
            'Apple Color Emoji',
            'AppleColorEmoji',
            '/System/Library/Fonts/Apple Color Emoji.ttc',
            'SF Pro',
            'Helvetica'
        ]
    elif sys.platform == 'win32':  # Windows
        emoji_font_names = [
            'Segoe UI Emoji',
            'seguiemj.ttf',
            'Arial'
        ]
    else:  # Linux
        emoji_font_names = [
            'Noto Color Emoji',
            'Symbola',
            'DejaVu Sans'
        ]

    # Try each font
    for font_name in emoji_font_names:
        try:
            # Check if it's a file path
            if os.path.exists(font_name):
                font = pygame.font.Font(font_name, size)
                return font
            # Try as system font
            font = pygame.font.SysFont(font_name, size)
            if font:
                return font
        except:
            continue

    # Fallback to default font (will show squares for emoji)
    print(f"⚠️  Warning: Could not load emoji font. Icons will appear as squares.")
    print(f"   Platform: {sys.platform}")
    return pygame.font.Font(None, size)


def render_emoji_with_fallback(font, emoji, color, fallback_text=None):
    """
    Render emoji with fallback to text if emoji not supported.

    Args:
        font: pygame.Font object (preferably from get_emoji_font)
        emoji: Unicode emoji string (e.g., "🔥")
        color: RGB tuple
        fallback_text: Text to show if emoji fails (e.g., "Fi" for Fire)

    Returns:
        pygame.Surface with rendered text
    """
    try:
        # Try rendering emoji
        surface = font.render(emoji, True, color)

        # Check if emoji rendered properly (not just a square)
        # If surface is very small or all same color, emoji probably failed
        if surface.get_width() > 5:  # Reasonable size
            return surface
    except:
        pass

    # Fallback to text
    if fallback_text:
        return font.render(fallback_text, True, color)

    # Last resort: just render the emoji anyway (will be square)
    return font.render(emoji, True, color)


# Emoji to fallback text mapping
ELEMENT_FALLBACK_TEXT = {
    '🔥': 'Fi',   # Fire
    '⚡': 'Li',   # Lightning
    '💧': 'Wa',   # Water
    '❄️': 'Ic',   # Ice
    '🌍': 'Ea',   # Earth
    '🌿': 'Na',   # Nature
    '🔮': 'Ar',   # Arcane
    '✨': 'Lig',  # Light
    '🌑': 'Sh'    # Shadow
}


def get_element_fallback(emoji):
    """Get fallback text for an element emoji"""
    return ELEMENT_FALLBACK_TEXT.get(emoji, '??')
