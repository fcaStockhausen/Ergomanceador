"""Color constants"""

# Basic colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
DARK_GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)

# Element colors (for magic system - matches data/elements.json)
ELEMENT_COLORS = {
    'fire': (255, 69, 0),        # Orange-red
    'lightning': (255, 255, 100),  # Bright yellow
    'water': (0, 105, 255),       # Deep blue
    'ice': (150, 200, 255),       # Light blue
    'earth': (139, 69, 19),       # Brown
    'nature': (34, 139, 34),      # Forest green
    'arcane': (138, 43, 226),     # Blue-violet
    'light': (255, 255, 200),     # Pale yellow
    'shadow': (50, 20, 70),       # Dark purple
    'air': CYAN  # Legacy - for backward compatibility
}
