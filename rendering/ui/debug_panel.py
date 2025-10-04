"""Debug panel - coordinate display and movement vectors"""

import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from config.colors import YELLOW, WHITE, GREEN


def draw_debug_panel(screen, font, player):
    """Draw debug information panel"""
    debug_y = SCREEN_HEIGHT - 150
    debug_font = pygame.font.Font(None, 20)

    # Player cartesian coordinates
    debug_text = [
        "=== DEBUG INFO ===",
        f"Cart Pos: ({player.cart_x:.2f}, {player.cart_y:.2f})",
        f"Input (WASD): ({player.last_input[0]:.1f}, {player.last_input[1]:.1f})",
        f"Cart Delta: ({player.last_cart_delta[0]:.3f}, {player.last_cart_delta[1]:.3f})",
        f"Jump Z: {player.z:.2f}",
    ]

    # Draw debug panel background
    debug_panel = pygame.Surface((250, 120))
    debug_panel.set_alpha(180)
    debug_panel.fill((20, 20, 20))
    screen.blit(debug_panel, (SCREEN_WIDTH - 260, debug_y - 10))

    # Draw debug text
    for i, text in enumerate(debug_text):
        color = YELLOW if i == 0 else WHITE
        surface = debug_font.render(text, True, color)
        screen.blit(surface, (SCREEN_WIDTH - 250, debug_y + i * 22))


def draw_movement_arrow(screen, player):
    """Draw movement direction arrow on player"""
    if player.last_input != (0, 0):
        # Player is at center of screen due to camera follow
        player_screen_x = SCREEN_WIDTH // 2
        player_screen_y = SCREEN_HEIGHT // 2 + player.z  # Fixed: + instead of -

        # Arrow showing input direction in screen space
        arrow_len = 40
        arrow_end_x = player_screen_x + player.last_input[0] * arrow_len
        arrow_end_y = player_screen_y + player.last_input[1] * arrow_len

        pygame.draw.line(screen, GREEN, (player_screen_x, player_screen_y),
                       (arrow_end_x, arrow_end_y), 3)
        # Arrowhead
        pygame.draw.circle(screen, GREEN, (int(arrow_end_x), int(arrow_end_y)), 5)
