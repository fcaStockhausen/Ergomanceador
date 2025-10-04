"""Controller HUD - displays Xbox button layout and status"""

import pygame
from config.colors import WHITE, GRAY
from config import controller_config as ctrl


def draw_controller_status(screen, font, input_manager, x=10, y=550):
    """
    Display controller connection status and button hints.
    Shows at bottom of screen when controller is connected.
    """
    if not input_manager.controller.connected:
        return  # Don't show if no controller

    # Background panel
    panel_width = 600
    panel_height = 80
    panel = pygame.Surface((panel_width, panel_height))
    panel.set_alpha(180)
    panel.fill((20, 20, 20))
    screen.blit(panel, (x, y))

    # Title
    title = font.render("🎮 Xbox Controller", True, WHITE)
    screen.blit(title, (x + 10, y + 5))

    # Button hints (two columns)
    hints = [
        # Column 1 - Movement
        ("Left Stick", "Move Player"),
        ("Right Stick", "Move Cursor"),
        ("R3 (Click)", "Jump"),

        # Column 2 - Elements
        ("A/B/X/Y", "Fire/Water/Earth/Nature"),
        ("D-Pad", "Arcane/Light/Shadow/Lightning"),

        # Column 3 - Actions
        ("RB (Bumper)", "Cast Spell"),
        ("LB (Bumper)", "Remove Element"),
        ("RT (Trigger)", "Aimed Cast"),
        ("LT (Trigger)", "Self Cast"),
    ]

    y_offset = 28
    col1_x = x + 15
    col2_x = x + 210
    col3_x = x + 410

    # Draw column 1 (movement)
    for i in range(3):
        button, action = hints[i]
        text = font.render(f"{button}: {action}", True, GRAY)
        screen.blit(text, (col1_x, y + y_offset + i * 18))

    # Draw column 2 (elements)
    for i in range(2):
        button, action = hints[3 + i]
        text = font.render(f"{button}: {action}", True, GRAY)
        screen.blit(text, (col2_x, y + y_offset + i * 18))

    # Draw column 3 (actions)
    for i in range(4):
        button, action = hints[5 + i]
        text = font.render(f"{button}: {action}", True, GRAY)
        screen.blit(text, (col3_x, y + y_offset + i * 18))


def draw_controller_element_hints(screen, font, magic_system, x=700, y=100):
    """
    Show active controller element mappings.
    Displays face button layout with element icons.
    """
    # Don't draw if no elements available
    if not magic_system.unlocked_elements:
        return

    # Background
    size = 100
    panel = pygame.Surface((size, size))
    panel.set_alpha(150)
    panel.fill((30, 30, 30))
    screen.blit(panel, (x, y))

    # Title
    small_font = pygame.font.Font(None, 18)
    title = small_font.render("Face Buttons", True, WHITE)
    screen.blit(title, (x + 10, y + 5))

    # Button layout (diamond shape like Xbox controller)
    #       Y (top)
    #   X       B (right)
    #       A (bottom)

    center_x = x + size // 2
    center_y = y + size // 2 + 10
    button_radius = 12
    offset = 25

    # Get element names
    button_elements = {
        'A': ctrl.ELEMENT_MAPPINGS.get(ctrl.BUTTON_A, '?'),
        'B': ctrl.ELEMENT_MAPPINGS.get(ctrl.BUTTON_B, '?'),
        'X': ctrl.ELEMENT_MAPPINGS.get(ctrl.BUTTON_X, '?'),
        'Y': ctrl.ELEMENT_MAPPINGS.get(ctrl.BUTTON_Y, '?'),
    }

    # Draw buttons in diamond layout
    buttons = [
        ('Y', center_x, center_y - offset, (255, 200, 0)),  # Yellow - Top
        ('B', center_x + offset, center_y, (255, 50, 50)),  # Red - Right
        ('A', center_x, center_y + offset, (50, 255, 50)),  # Green - Bottom
        ('X', center_x - offset, center_y, (100, 150, 255)),  # Blue - Left
    ]

    for label, bx, by, color in buttons:
        # Draw button circle
        pygame.draw.circle(screen, color, (int(bx), int(by)), button_radius)
        pygame.draw.circle(screen, WHITE, (int(bx), int(by)), button_radius, 2)

        # Draw element name below
        elem = button_elements.get(label, '?')
        elem_text = small_font.render(elem[:3].upper(), True, WHITE)
        text_rect = elem_text.get_rect(center=(int(bx), int(by)))
        screen.blit(elem_text, text_rect)
