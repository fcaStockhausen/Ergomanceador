"""Projectile entity for spell effects"""

import pygame
import math
from rendering.isometric import cart_to_iso
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Projectile:
    """
    Projectile entity that travels from origin to target.
    Supports multiple behaviors: projectile, beam, homing.
    """

    def __init__(self, start_x, start_y, target_x, target_y, spell_data, owner='player'):
        """
        Create projectile.

        Args:
            start_x, start_y: Starting cartesian position (player)
            target_x, target_y: Target cartesian position (cursor)
            spell_data: Dict with spell properties (name, damage, area, behavior, color, etc.)
            owner: 'player' or 'bot' - who cast this spell
        """
        self.cart_x = start_x
        self.cart_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.owner = owner  # Track who cast this projectile

        self.spell_data = spell_data
        self.behavior = spell_data['behavior']
        self.color = spell_data.get('color', (255, 255, 255))
        self.area = spell_data.get('area', 1.0)
        self.speed = spell_data.get('speed', 0.2)

        # Calculate velocity vector
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
        else:
            self.vel_x = 0
            self.vel_y = 0

        self.alive = True
        self.lifetime = 0.0
        self.max_lifetime = 5.0  # Projectiles die after 5 seconds

    def update(self, dt):
        """Update projectile position"""
        if not self.alive:
            return

        self.lifetime += dt

        # Die if too old
        if self.lifetime > self.max_lifetime:
            self.alive = False
            return

        # Move projectile
        if self.behavior == 'projectile' or self.behavior == 'homing':
            self.cart_x += self.vel_x
            self.cart_y += self.vel_y

            # Check if reached target (within 0.5 units)
            dx = self.target_x - self.cart_x
            dy = self.target_y - self.cart_y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < 0.5:
                self.alive = False

        # Beams are instant - die immediately
        elif self.behavior == 'beam':
            self.alive = False

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw projectile"""
        if not self.alive:
            return

        if self.behavior == 'beam':
            self._draw_beam(screen, camera_offset_x, camera_offset_y)
        elif self.behavior == 'projectile' or self.behavior == 'homing':
            self._draw_projectile(screen, camera_offset_x, camera_offset_y)

    def _draw_projectile(self, screen, camera_offset_x, camera_offset_y):
        """Draw circular projectile"""
        # Convert to isometric screen position
        iso_x, iso_y = cart_to_iso(self.cart_x, self.cart_y)
        screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
        screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y

        # Draw projectile as circle
        radius = int(5 + self.area * 2)
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), radius)

        # Draw glow effect
        glow_color = tuple(min(255, c + 100) for c in self.color)
        pygame.draw.circle(screen, glow_color, (int(screen_x), int(screen_y)), radius + 2, 2)

    def _draw_beam(self, screen, camera_offset_x, camera_offset_y):
        """Draw instant beam from origin to target"""
        # Start position
        iso_x1, iso_y1 = cart_to_iso(self.cart_x, self.cart_y)
        screen_x1 = SCREEN_WIDTH // 2 + iso_x1 + camera_offset_x
        screen_y1 = SCREEN_HEIGHT // 2 + iso_y1 + camera_offset_y

        # End position
        iso_x2, iso_y2 = cart_to_iso(self.target_x, self.target_y)
        screen_x2 = SCREEN_WIDTH // 2 + iso_x2 + camera_offset_x
        screen_y2 = SCREEN_HEIGHT // 2 + iso_y2 + camera_offset_y

        # Draw beam as thick line
        width = int(3 + self.area)
        pygame.draw.line(screen, self.color,
                        (int(screen_x1), int(screen_y1)),
                        (int(screen_x2), int(screen_y2)),
                        width)

        # Draw glow
        glow_color = tuple(min(255, c + 100) for c in self.color)
        pygame.draw.line(screen, glow_color,
                        (int(screen_x1), int(screen_y1)),
                        (int(screen_x2), int(screen_y2)),
                        width + 4)
