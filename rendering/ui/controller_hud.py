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


def draw_controller_element_hints(screen, font, input_manager, x=620, y=50):
    """
    Show current element page and button assignments.
    Displays which elements are mapped to X/Y/B/LB buttons.
    """
    # Only show if controller connected
    if not input_manager.controller.connected:
        return

    # Get current page
    current_page_idx = input_manager.controller.current_element_page
    current_page = ctrl.ELEMENT_PAGES[current_page_idx]

    # Background panel
    panel_width = 260
    panel_height = 140
    panel = pygame.Surface((panel_width, panel_height))
    panel.set_alpha(200)
    panel.fill((20, 20, 30))
    screen.blit(panel, (x, y))
    pygame.draw.rect(screen, WHITE, (x, y, panel_width, panel_height), 2)

    # Title with page indicator
    title_font = pygame.font.Font(None, 28)
    title = title_font.render(f"ELEMENT PAGE {current_page_idx + 1}/3", True, WHITE)
    screen.blit(title, (x + 10, y + 8))

    # Page navigation hint
    hint_font = pygame.font.Font(None, 18)
    nav_hint = hint_font.render("D-Pad Up/Down to change", True, GRAY)
    screen.blit(nav_hint, (x + 10, y + 32))

    # Button assignments (diamond layout)
    small_font = pygame.font.Font(None, 20)
    center_x = x + panel_width // 2
    center_y = y + 90
    button_radius = 15
    offset = 35

    # Map buttons to element slots
    button_layout = [
        ('Y', ctrl.SLOT_Y, center_x, center_y - offset, (255, 220, 0)),  # Yellow - Top
        ('B', ctrl.SLOT_B, center_x + offset, center_y, (220, 50, 50)),  # Red - Right
        ('A', ctrl.ACTION_JUMP, center_x, center_y + offset, (50, 220, 50)),  # Green - Bottom (JUMP)
        ('X', ctrl.SLOT_X, center_x - offset, center_y, (80, 150, 255)),  # Blue - Left
        ('LB', ctrl.SLOT_LB, center_x - offset * 2, center_y - offset // 2, (180, 180, 180)),  # Gray - Far Left
    ]

    for label, slot_idx, bx, by, color in button_layout:
        # Draw button circle
        pygame.draw.circle(screen, color, (int(bx), int(by)), button_radius)
        pygame.draw.circle(screen, WHITE, (int(bx), int(by)), button_radius, 1)

        # Get element for this button
        if label == 'A':
            # A button is jump
            elem_text = small_font.render("JUMP", True, (0, 0, 0))
        else:
            element_name = current_page[slot_idx]
            elem_text = small_font.render(element_name[:3].upper(), True, (0, 0, 0))

        text_rect = elem_text.get_rect(center=(int(bx), int(by)))
        screen.blit(elem_text, text_rect)
