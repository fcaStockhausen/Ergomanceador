"""Floating damage numbers that appear when enemies are hit"""

import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from config.colors import WHITE, YELLOW, ORANGE, RED
from rendering.isometric import cart_to_iso


class DamageNumber:
    """A single floating damage number"""

    def __init__(self, damage, cart_x, cart_y):
        self.damage = int(damage)
        self.cart_x = cart_x
        self.cart_y = cart_y
        self.z_offset = 0.0  # Start at entity height

        # Animation
        self.lifetime = 1.0  # 1 second
        self.age = 0.0
        self.float_speed = 1.5  # Units per second (upward)
        self.alive = True

        # Visual
        self.font = pygame.font.Font(None, 32)  # Larger font for visibility
        self.color = self._get_color()

    def _get_color(self):
        """Color based on damage amount"""
        if self.damage >= 50:
            return RED  # Critical damage
        elif self.damage >= 25:
            return ORANGE  # Heavy damage
        elif self.damage >= 10:
            return YELLOW  # Medium damage
        else:
            return WHITE  # Light damage

    def update(self, dt):
        """Update animation"""
        self.age += dt
        self.z_offset += self.float_speed * dt

        if self.age >= self.lifetime:
            self.alive = False

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw floating number with fade-out"""
        if not self.alive:
            return

        # Calculate fade (1.0 at start, 0.0 at end)
        fade = 1.0 - (self.age / self.lifetime)
        alpha = int(255 * fade)

        # Convert to screen coordinates
        iso_x, iso_y = cart_to_iso(self.cart_x, self.cart_y)
        screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
        screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y

        # Apply Z offset (floats upward)
        screen_y -= int(self.z_offset * 20)  # Convert to pixels

        # Render text with alpha
        text_surface = self.font.render(str(self.damage), True, self.color)
        text_surface.set_alpha(alpha)

        # Center text on position
        text_rect = text_surface.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(text_surface, text_rect)


class DamageNumberManager:
    """Manages all active damage numbers"""

    def __init__(self):
        self.numbers = []

    def spawn(self, damage, cart_x, cart_y):
        """Spawn a new damage number at position"""
        number = DamageNumber(damage, cart_x, cart_y)
        self.numbers.append(number)

    def update(self, dt):
        """Update all numbers"""
        for number in self.numbers[:]:
            number.update(dt)
            if not number.alive:
                self.numbers.remove(number)

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw all numbers"""
        for number in self.numbers:
            number.draw(screen, camera_offset_x, camera_offset_y)

    def clear_all(self):
        """Clear all damage numbers"""
        self.numbers.clear()
