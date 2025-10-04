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

# Element mappings to buttons
# Philosophy: Quick access to all 9 elements
#
# FACE BUTTONS (Primary):        D-PAD (Advanced):
#        Y (Nature 🌿)                D-Up (Arcane 🔮)
#        |                                |
# X (Earth 🌍) - B (Water 💧)    D-Left (Light ✨) - D-Right (Lightning ⚡)
#        |                                |
#     A (Fire 🔥)                    D-Down (Shadow 🌑)
#
# LB = Ice ❄️
#
ELEMENT_MAPPINGS = {
    # Face buttons (primary elements - easy thumb access)
    BUTTON_A: 'fire',      # A (bottom) - Fire 🔥
    BUTTON_B: 'water',     # B (right) - Water 💧
    BUTTON_X: 'earth',     # X (left) - Earth 🌍
    BUTTON_Y: 'nature',    # Y (top) - Nature 🌿

    # D-Pad (advanced elements - requires thumb movement)
    HAT_UP: 'arcane',      # D-Up - Arcane 🔮
    HAT_RIGHT: 'lightning', # D-Right - Lightning ⚡
    HAT_DOWN: 'shadow',    # D-Down - Shadow 🌑
    HAT_LEFT: 'light',     # D-Left - Light ✨

    # Bumpers
    BUTTON_LB: 'ice',      # Left Bumper - Ice ❄️
}

# Action mappings
ACTION_CAST = BUTTON_RB        # Right Bumper - Cast spell
ACTION_REMOVE = BUTTON_L3      # Left stick click - Remove last element
ACTION_CLEAR = BUTTON_BACK     # Back button - Clear queue
ACTION_JUMP = BUTTON_R3        # Right stick click - Jump

# Alternative: Triggers for casting
ACTION_CAST_TRIGGER = AXIS_RT  # Right Trigger can also cast
ACTION_SELFCAST_TRIGGER = AXIS_LT  # Left Trigger for self-cast

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
