"""Xbox controller configuration and button mappings"""

# Xbox Controller Button Indices (SDL2 standard mapping)
# These map to pygame.JOYBUTTONDOWN/UP events

# Face Buttons (right side)
BUTTON_A = 0  # Bottom (Green)
BUTTON_B = 1  # Right (Red)
BUTTON_X = 2  # Left (Blue)
BUTTON_Y = 3  # Top (Yellow)

# Bumpers
BUTTON_LB = 4  # Left Bumper
BUTTON_RB = 5  # Right Bumper

# Special Buttons
BUTTON_BACK = 6   # Back/View
BUTTON_START = 7  # Start/Menu
BUTTON_GUIDE = 8  # Xbox button (center)

# Stick Clicks
BUTTON_L3 = 9   # Left stick click
BUTTON_R3 = 10  # Right stick click

# D-Pad (treated as hat in pygame)
HAT_CENTERED = (0, 0)
HAT_UP = (0, 1)
HAT_DOWN = (0, -1)
HAT_LEFT = (-1, 0)
HAT_RIGHT = (1, 0)
HAT_UP_LEFT = (-1, 1)
HAT_UP_RIGHT = (1, 1)
HAT_DOWN_LEFT = (-1, -1)
HAT_DOWN_RIGHT = (1, -1)

# Analog Axes
AXIS_LEFT_X = 0   # Left stick horizontal (-1 = left, +1 = right)
AXIS_LEFT_Y = 1   # Left stick vertical (-1 = up, +1 = down)
AXIS_RIGHT_X = 2  # Right stick horizontal
AXIS_RIGHT_Y = 3  # Right stick vertical
AXIS_LT = 4       # Left trigger (0 to 1)
AXIS_RT = 5       # Right trigger (0 to 1)

# Dead zone for analog sticks (ignore small movements)
STICK_DEADZONE = 0.15

# Trigger threshold (when to consider trigger "pressed")
TRIGGER_THRESHOLD = 0.5

# NEW ELEMENT SYSTEM:
# - Face buttons X/Y/B are SLOTS that queue elements
# - A button is JUMP
# - D-pad CYCLES which element set is assigned to X/Y/B slots
# - LB selects the 4th element in current set
#
# D-Pad Up/Down cycles between element pages:
#   Page 1: Fire, Water, Earth, Nature
#   Page 2: Lightning, Ice, Arcane, Light
#   Page 3: Shadow, Fire, Water, Earth (wraps)
#
# Example: D-Up switches to Page 2
#   X = Lightning, Y = Ice, B = Arcane, LB = Light
#

# D-Pad buttons (on macOS, D-pad sends button events, not hat events)
DPAD_UP = 11      # D-pad Up
DPAD_DOWN = 12    # D-pad Down
DPAD_LEFT = 13    # D-pad Left
DPAD_RIGHT = 14   # D-pad Right

# Element pages (4 elements per page for X/Y/B/LB)
ELEMENT_PAGES = [
    ['fire', 'water', 'earth', 'nature'],       # Page 0 (default)
    ['lightning', 'ice', 'arcane', 'light'],    # Page 1
    ['shadow', 'nature', 'fire', 'water'],      # Page 2
]

# Face button slot indices (map to element page indices)
SLOT_X = 0      # X button = slot 0
SLOT_Y = 1      # Y button = slot 1
SLOT_B = 2      # B button = slot 2
SLOT_LB = 3     # LB button = slot 3

# Legacy mappings (kept for compatibility, but overridden by page system)
ELEMENT_MAPPINGS = {}

# Action mappings
ACTION_CAST = BUTTON_RB        # Right Bumper - Cast spell (aimed)
ACTION_CLEAR = BUTTON_BACK     # Back button - Clear queue
ACTION_JUMP = BUTTON_A         # A button - Jump

# Trigger casting modes
ACTION_CAST_TRIGGER = AXIS_RT  # Right Trigger - Aimed cast
ACTION_SELFCAST_TRIGGER = AXIS_LT  # Left Trigger - Self-cast

# Settings
ENABLE_TRIGGER_CASTING = True  # Allow RT to cast spells
ENABLE_RUMBLE = True           # Haptic feedback on spell cast
RUMBLE_DURATION = 200          # Milliseconds

# Targeting Mode Settings (Forward-Facing Quick Cast)
TARGET_MODE = 'forward_facing'  # 'forward_facing' or 'free_aim'
TARGET_FOLLOW_DISTANCE = 3.0    # Tiles ahead of player in forward-facing mode
TARGET_FOLLOW_ENABLED = True    # Auto-follow player's facing direction
RIGHT_STICK_AIM_MODE = True     # True = right stick sets aim direction, False = moves cursor absolutely
AIM_SNAP_THRESHOLD = 0.3        # Minimum right stick input to change aim direction
