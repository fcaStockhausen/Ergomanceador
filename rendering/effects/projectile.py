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

    def __init__(self, start_x, start_y, target_x, target_y, spell_data, owner='player', is_child=False):
        """
        Create projectile.

        Args:
            start_x, start_y: Starting cartesian position (player)
            target_x, target_y: Target cartesian position (cursor)
            spell_data: Dict with spell properties (name, damage, area, behavior, color, etc.)
            owner: 'player' or 'bot' - who cast this spell
            is_child: True if this is a child projectile from a split
        """
        self.cart_x = start_x
        self.cart_y = start_y
        self.origin_x = start_x
        self.origin_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.owner = owner  # 'player' or 'bot'
        self.is_child = is_child  # Child projectiles don't split again

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

        # Split behavior tracking
        self.has_split = False
        self.split_time = 0.5  # Split after 0.5 seconds of travel
        self.child_projectiles = []  # Store child projectiles spawned from split

    def update(self, dt):
        """Update projectile position"""
        if not self.alive:
            return

        self.lifetime += dt

        # Die if too old
        if self.lifetime > self.max_lifetime:
            self.alive = False
            return

        # Move projectile (frame-rate independent)
        if self.behavior == 'projectile' or self.behavior == 'homing' or self.behavior == 'split':
            self.cart_x += self.vel_x * dt
            self.cart_y += self.vel_y * dt

            # Check if reached target (within 0.5 units)
            dx = self.target_x - self.cart_x
            dy = self.target_y - self.cart_y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < 0.5:
                self.alive = False

            # SPLIT behavior: spawn child projectiles after split_time
            if self.behavior == 'split' and not self.is_child and not self.has_split:
                if self.lifetime >= self.split_time:
                    self._perform_split()

        # Beams are instant - die immediately
        elif self.behavior == 'beam':
            self.alive = False

    def _perform_split(self):
        """
        Split the projectile into N child projectiles (emergent from properties).
        Number of children and spread angle determined by spell properties.
        """
        import random

        self.has_split = True

        # EMERGENT: Calculate number of children from property vector
        # Access property vector if available
        property_vector = self.spell_data.get('property_vector', None)

        if property_vector:
            # Number of splits based on chaos, volatility, phase_diversity, energy_density
            # Formula: 1-5 children based on these properties
            chaos = property_vector.chaos_factor  # 0-1
            volatility = property_vector.volatility_index  # 0-1
            phase_div = property_vector.phase_diversity  # 0-1
            energy_dens = property_vector.energy_density / 150.0  # Normalize to 0-1

            # Combine factors: more chaotic/volatile = more splits
            split_factor = (chaos * 0.4 + volatility * 0.3 + phase_div * 0.2 + energy_dens * 0.1)

            # Map to 1-5 children (floor so low chaos = 1-2, high chaos = 4-5)
            num_children = int(1 + split_factor * 4)
            num_children = max(1, min(5, num_children))  # Clamp to 1-5

            # Spread angle also emergent: more chaos = wider spread
            spread_angle = 20 + (chaos * 60)  # 20-80 degrees
        else:
            # Fallback if no property vector
            num_children = 3
            spread_angle = 40

        for i in range(num_children):
            # Calculate spread angle for this child
            if num_children == 1:
                angle_offset = 0  # Single child goes straight
            else:
                # Spread evenly across the angle
                angle_offset = (i / (num_children - 1)) * spread_angle - (spread_angle / 2)

            angle_rad = math.radians(angle_offset)

            # Rotate velocity vector by angle_offset
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            new_vel_x = self.vel_x * cos_a - self.vel_y * sin_a
            new_vel_y = self.vel_x * sin_a + self.vel_y * cos_a

            # Calculate new target point (extend from current position)
            extend_distance = 20.0  # How far child projectiles travel
            new_target_x = self.cart_x + new_vel_x * extend_distance / self.speed
            new_target_y = self.cart_y + new_vel_y * extend_distance / self.speed

            # Create child projectile with reduced damage (60% of original)
            child_spell_data = self.spell_data.copy()
            child_spell_data['damage'] = child_spell_data.get('damage', 10) * 0.6
            child_spell_data['behavior'] = 'projectile'  # Children are simple projectiles

            # Create child (marked as is_child=True so it doesn't split again)
            child = Projectile(
                self.cart_x, self.cart_y,
                new_target_x, new_target_y,
                child_spell_data,
                owner=self.owner,
                is_child=True
            )

            self.child_projectiles.append(child)

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw projectile"""
        if not self.alive:
            return

        if self.behavior == 'beam':
            self._draw_beam(screen, camera_offset_x, camera_offset_y)
        elif self.behavior == 'projectile' or self.behavior == 'homing' or self.behavior == 'split':
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
