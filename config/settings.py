"""Game settings and constants"""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Isometric constants
TILE_WIDTH = 64
TILE_HEIGHT = 32

# Grid settings
GRID_SIZE = 50  # Larger arena for more tactical gameplay

# Entity movement settings (centralized, frame-rate independent)
BASE_MOVEMENT_SPEED = 200.0  # Screen-space speed (goes through screen_to_cart transform)

# Cartesian-space speed for AI/bots that bypass screen_to_cart.
# Player's average cartesian speed ≈ 7 units/sec after isometric transform.
CART_MOVEMENT_SPEED = 6.0  # cartesian units/second

# Debug mode
DEBUG_MODE = True
