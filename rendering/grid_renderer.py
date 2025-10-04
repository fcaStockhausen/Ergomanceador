"""Isometric grid rendering"""

import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE
from config.colors import GRAY
from rendering.isometric import cart_to_iso


def draw_isometric_grid(screen, camera_offset_x=0, camera_offset_y=0):
    """Draw isometric grid as floor"""
    for gx in range(GRID_SIZE + 1):
        for gy in range(GRID_SIZE + 1):
            # Get isometric coordinates for this grid point
            iso_x, iso_y = cart_to_iso(gx, gy)
            screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
            screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y

            # Draw tile edges
            if gx < GRID_SIZE:
                next_iso_x, next_iso_y = cart_to_iso(gx + 1, gy)
                next_screen_x = SCREEN_WIDTH // 2 + next_iso_x + camera_offset_x
                next_screen_y = SCREEN_HEIGHT // 2 + next_iso_y + camera_offset_y
                pygame.draw.line(screen, GRAY, (screen_x, screen_y), (next_screen_x, next_screen_y), 1)

            if gy < GRID_SIZE:
                next_iso_x, next_iso_y = cart_to_iso(gx, gy + 1)
                next_screen_x = SCREEN_WIDTH // 2 + next_iso_x + camera_offset_x
                next_screen_y = SCREEN_HEIGHT // 2 + next_iso_y + camera_offset_y
                pygame.draw.line(screen, GRAY, (screen_x, screen_y), (next_screen_x, next_screen_y), 1)
