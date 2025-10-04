"""Target cursor entity with Diablo 3 style relative positioning"""

import pygame
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from config.colors import YELLOW, ORANGE, RED
from rendering.isometric import cart_to_iso
from config import controller_config as ctrl


class Target:
    def __init__(self):
        self.cart_x = 10
        self.cart_y = 10
        self.size = 10
        self.speed = 0.3  # Not used in new system
        self.color = ORANGE
        self.visible = True

        # Aim direction (relative to player)
        self.aim_direction = (0, 0)  # Default: on player (no offset)
        self.aim_distance = 0.0  # Distance from player (0 = centered on player)
        self.max_distance = ctrl.TARGET_FOLLOW_DISTANCE

    def set_aim_direction(self, dx, dy):
        """Set aim direction from input (Diablo 3 style - direction from player)"""
        if dx == 0 and dy == 0:
            # No input - cursor returns to player center
            self.aim_direction = (0, 0)
            self.aim_distance = 0.0
            self.color = ORANGE  # Centered
            return

        # Normalize to unit vector
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            self.aim_direction = (dx / magnitude, dy / magnitude)
            self.aim_distance = self.max_distance
            self.color = RED  # Aiming

    def follow_player(self, player):
        """Position target relative to player (ALWAYS - Diablo 3 style)"""
        # Target is ALWAYS positioned relative to player
        # If aim_distance is 0, cursor is ON player
        # If aim_distance > 0, cursor is ahead in aim direction
        self.cart_x = player.cart_x + self.aim_direction[0] * self.aim_distance
        self.cart_y = player.cart_y + self.aim_direction[1] * self.aim_distance

        # Keep in bounds
        self.cart_x = max(0, min(20, self.cart_x))
        self.cart_y = max(0, min(20, self.cart_y))

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        if self.visible:
            # Convert to isometric coordinates
            iso_x, iso_y = cart_to_iso(self.cart_x, self.cart_y)
            screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
            screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y

            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.size)
            # Draw crosshair
            pygame.draw.line(screen, self.color, (screen_x - 15, screen_y), (screen_x + 15, screen_y), 2)
            pygame.draw.line(screen, self.color, (screen_x, screen_y - 15), (screen_x, screen_y + 15), 2)
