"""Player entity"""

import pygame
import logging
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from config.colors import WHITE
from rendering.isometric import cart_to_iso, screen_to_cart


class Player:
    def __init__(self, x, y):
        self.cart_x = x  # Cartesian X
        self.cart_y = y  # Cartesian Y
        self.z = 0  # Height above ground
        self.size = 20
        self.speed = 1
        self.color = WHITE
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -10

        # Facing direction (for forward-facing targeting)
        self.facing_direction = (1, 0)  # Default facing right

        # Debug info
        self.last_input = (0, 0)
        self.last_cart_delta = (0, 0)
        self.last_logged_input = (0, 0)  # Track last logged input to avoid spam

    def move(self, screen_dx, screen_dy):
        """Move using screen-space directions (perspective coordinates)"""
        # Store input for debug
        self.last_input = (screen_dx, screen_dy)

        # Convert screen direction to cartesian movement
        cart_dx, cart_dy = screen_to_cart(screen_dx, screen_dy)

        # Store cartesian delta for debug
        self.last_cart_delta = (cart_dx * self.speed, cart_dy * self.speed)

        # Log only on input CHANGE (not every frame)
        if (screen_dx, screen_dy) != self.last_logged_input:
            if screen_dx != 0 or screen_dy != 0:
                logging.info(f"Movement START: Input ({screen_dx}, {screen_dy}) -> Cart delta ({cart_dx:.3f}, {cart_dy:.3f})")
            else:
                logging.info(f"Movement STOP at position ({self.cart_x:.2f}, {self.cart_y:.2f})")
            self.last_logged_input = (screen_dx, screen_dy)

        # Move in cartesian space
        self.cart_x += cart_dx * self.speed
        self.cart_y += cart_dy * self.speed

        # Update facing direction when moving
        if cart_dx != 0 or cart_dy != 0:
            import math
            magnitude = math.sqrt(cart_dx**2 + cart_dy**2)
            if magnitude > 0:
                self.facing_direction = (cart_dx / magnitude, cart_dy / magnitude)

        # Keep player in bounds
        self.cart_x = max(0, min(20, self.cart_x))
        self.cart_y = max(0, min(20, self.cart_y))

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = self.jump_strength
            logging.info(f"JUMP at position ({self.cart_x:.2f}, {self.cart_y:.2f})")

    def update_jump(self):
        if self.is_jumping:
            self.z += self.jump_velocity
            self.jump_velocity += self.gravity

            # Land back on ground
            if self.z >= 0:
                self.z = 0
                self.is_jumping = False
                self.jump_velocity = 0

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        # Convert to isometric coordinates
        iso_x, iso_y = cart_to_iso(self.cart_x, self.cart_y)
        # Apply camera offset
        screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
        screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y + self.z  # Fixed: + instead of -

        # Draw shadow (ellipse on ground)
        shadow_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y
        pygame.draw.ellipse(screen, (50, 50, 50), (screen_x - 15, shadow_y - 7, 30, 14))

        # Draw cylinder (player)
        cylinder_height = 40
        cylinder_width = 30

        # Top ellipse of cylinder
        top_y = screen_y - cylinder_height
        pygame.draw.ellipse(screen, self.color, (screen_x - cylinder_width//2, top_y - 7, cylinder_width, 14))

        # Cylinder sides (rectangle)
        pygame.draw.rect(screen, self.color, (screen_x - cylinder_width//2, top_y, cylinder_width, cylinder_height))

        # Bottom ellipse of cylinder (darker for depth)
        bottom_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.ellipse(screen, bottom_color, (screen_x - cylinder_width//2, screen_y - 7, cylinder_width, 14))
