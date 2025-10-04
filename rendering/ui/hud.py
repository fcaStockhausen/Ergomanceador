"""HUD rendering - controls display"""

import pygame
from config.colors import WHITE


def draw_controls(screen, font):
    """Draw control instructions (Phase 3: updated for 8 elements)"""
    controls_text = [
        "WASD - Move | G - Jump | IJKL - Aim",
        "Q/E/R/F - Fire/Water/Ice/Earth (Left Hand)",
        "U/O/P/; - Nature/Arcane/Light/Shadow (Right)",
        "SPACE - Cast | BACKSPACE - Remove Element"
    ]
    for i, text in enumerate(controls_text):
        surface = font.render(text, True, WHITE)
        screen.blit(surface, (10, 10 + i * 22))
