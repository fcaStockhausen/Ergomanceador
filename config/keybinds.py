"""Keyboard configuration for dual-hand input system"""

import pygame

# Element keys (8 elements - dual hand layout)
# LEFT HAND: Q/E/R/F (Fire, Water, Ice, Earth)
# RIGHT HAND: U/O/P/; (Nature, Arcane, Light, Shadow)
ELEMENT_KEYS = {
    pygame.K_q: 'fire',      # Left hand - top row
    pygame.K_e: 'water',     # Left hand - top row
    pygame.K_r: 'ice',       # Left hand - top row (new!)
    pygame.K_f: 'earth',     # Left hand - home row (new!)

    pygame.K_u: 'nature',    # Right hand - top row (new!)
    pygame.K_o: 'arcane',    # Right hand - top row (new!)
    pygame.K_p: 'light',     # Right hand - top row (new!)
    pygame.K_SEMICOLON: 'shadow'  # Right hand - home row (new!)
}

# Movement keys (WASD)
MOVE_UP = pygame.K_w
MOVE_DOWN = pygame.K_s
MOVE_LEFT = pygame.K_a
MOVE_RIGHT = pygame.K_d

# Aiming keys (IJKL)
AIM_UP = pygame.K_i
AIM_DOWN = pygame.K_k
AIM_LEFT = pygame.K_j
AIM_RIGHT = pygame.K_l

# Action keys
JUMP = pygame.K_g           # G key (left hand, more comfortable)
CAST_AIMED = pygame.K_SPACE # Spacebar (aimed cast at cursor)
REMOVE_ELEMENT = pygame.K_BACKSPACE  # Backspace (remove last element)
CLEAR_QUEUE = pygame.K_ESCAPE  # Escape (clear queue - also quits if pressed twice)

# Modifier keys (future use)
SELF_CAST_MODIFIER = pygame.K_LSHIFT  # Shift + Space = self-cast

# Quit keys
QUIT_KEY = pygame.K_ESCAPE
QUIT_MODIFIER = pygame.KMOD_META | pygame.KMOD_CTRL  # Cmd+Q or Ctrl+Q

# Display names for UI
ELEMENT_KEY_NAMES = {
    'fire': 'Q',
    'water': 'E',
    'ice': 'R',
    'earth': 'F',
    'nature': 'U',
    'arcane': 'O',
    'light': 'P',
    'shadow': ';'
}
