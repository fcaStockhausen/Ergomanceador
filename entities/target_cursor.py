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

        # Smooth keyboard aiming
        self.target_direction = (0, 0)  # Target direction for smooth interpolation
        self.keyboard_lerp_speed = 15.0  # How fast keyboard aim interpolates (higher = faster)

    def set_aim_direction(self, dx, dy, smooth=True):
        """Set aim direction from input (Diablo 3 style - direction from player)

        Args:
            dx, dy: Direction input
            smooth: If True, interpolate (keyboard). If False, instant (controller)
        """
        import logging

        if dx == 0 and dy == 0:
            # No input - cursor returns to player center
            self.target_direction = (0, 0)
            if not smooth:
                # Controller: instant response
                self.aim_direction = (0, 0)
                self.aim_distance = 0.0
            self.color = ORANGE  # Centered
            return

        # Normalize to unit vector
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            normalized = (dx / magnitude, dy / magnitude)

            if smooth:
                # Keyboard: smooth interpolation (set target, update in update())
                if self.target_direction != normalized:
                    logging.info(f"Keyboard AIM: target direction set to {normalized} (smooth mode)")
                self.target_direction = normalized
            else:
                # Controller: instant response
                if self.aim_direction != normalized:
                    logging.info(f"Controller AIM: direction set to {normalized} (instant)")
                self.aim_direction = normalized
                self.aim_distance = self.max_distance

            self.color = RED  # Aiming

    def update(self, dt):
        """Update smooth keyboard aim interpolation"""
        # Lerp current direction towards target direction
        if self.target_direction != self.aim_direction:
            # Calculate interpolation factor
            lerp_factor = min(1.0, self.keyboard_lerp_speed * dt)

            # Lerp direction
            current_x, current_y = self.aim_direction
            target_x, target_y = self.target_direction

            new_x = current_x + (target_x - current_x) * lerp_factor
            new_y = current_y + (target_y - current_y) * lerp_factor

            # Normalize if not zero
            magnitude = math.sqrt(new_x**2 + new_y**2)
            if magnitude > 0.01:
                self.aim_direction = (new_x / magnitude, new_y / magnitude)
                self.aim_distance = self.max_distance
            else:
                # Close to zero - snap to center
                self.aim_direction = (0, 0)
                self.aim_distance = 0.0

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
