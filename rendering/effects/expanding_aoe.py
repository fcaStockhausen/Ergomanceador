"""Expanding AOE effect that deals damage as it expands radially"""

import pygame
import math
import logging
from rendering.isometric import cart_to_iso
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class ExpandingAOE:
    """
    AOE effect that expands radially over time, dealing damage as it grows.
    """

    def __init__(self, x, y, max_radius, color, spell_data, owner='player',
                 expansion_speed=8.0, duration=0.8):
        """
        Create expanding AOE effect.

        Args:
            x, y: Center position (cartesian)
            max_radius: Maximum radius to expand to
            color: RGB color tuple
            spell_data: Spell data dict with damage info
            owner: 'player' or 'bot' (for damage routing)
            expansion_speed: Radius units per second
            duration: Total duration of the effect
        """
        self.cart_x = x
        self.cart_y = y
        self.max_radius = max_radius
        self.current_radius = 0.0
        self.color = color
        self.spell_data = spell_data
        self.owner = owner
        self.expansion_speed = expansion_speed
        self.duration = duration
        self.lifetime = 0.0
        self.alive = True

        # Track which entities have been hit (avoid multi-hit)
        self.hit_entities = set()

        # Visual properties
        self.alpha = 255

    def update(self, dt, enemies=None, player=None, terrain=None, damage_numbers=None, sound=None):
        """Update the expanding AOE"""
        self.lifetime += dt

        # Expand radius
        self.current_radius += self.expansion_speed * dt

        # Fade out alpha over time
        progress = self.lifetime / self.duration
        self.alpha = int(255 * (1.0 - progress))

        # Die when duration expires
        if self.lifetime >= self.duration or self.current_radius >= self.max_radius * 1.2:
            self.alive = False
            return

        # Deal damage to entities as wave passes through them
        damage = self.spell_data.get('damage', 10)

        # Check collisions with entities
        if self.owner == 'player' and enemies:
            for enemy in [e for e in enemies if e.health.is_alive]:
                # Skip if already hit
                if id(enemy) in self.hit_entities:
                    continue

                dx = enemy.cart_x - self.cart_x
                dy = enemy.cart_y - self.cart_y
                distance = math.sqrt(dx**2 + dy**2)

                # Hit if within expanding ring (threshold: ±1.0 unit from current radius)
                if abs(distance - self.current_radius) <= 1.5:
                    # Apply terrain bonus if available
                    actual_damage = damage
                    if terrain and 'elements' in self.spell_data:
                        elements = self.spell_data.get('elements', [])
                        bonus = terrain.get_damage_bonus_at(enemy.cart_x, enemy.cart_y, elements)
                        actual_damage = int(damage * bonus)

                    enemy.health.damage(actual_damage)
                    self.hit_entities.add(id(enemy))
                    logging.info(f"Expanding AOE hit enemy! Dealt {actual_damage} damage")

                    if damage_numbers:
                        damage_numbers.spawn(actual_damage, enemy.cart_x, enemy.cart_y)

                    # Apply knockback
                    if distance > 0.01:
                        knockback_force = 3.0 + (actual_damage * 0.05)
                        dir_x = dx / distance
                        dir_y = dy / distance
                        enemy.apply_knockback(dir_x, dir_y, knockback_force)

        elif self.owner == 'bot' and player and player.health.is_alive:
            # Skip if already hit
            if id(player) not in self.hit_entities:
                dx = player.cart_x - self.cart_x
                dy = player.cart_y - self.cart_y
                distance = math.sqrt(dx**2 + dy**2)

                # Hit if within expanding ring
                if abs(distance - self.current_radius) <= 1.5:
                    player.health.damage(damage)
                    self.hit_entities.add(id(player))
                    logging.info(f"Expanding AOE hit player! Dealt {damage} damage")

                    if damage_numbers:
                        damage_numbers.spawn(damage, player.cart_x, player.cart_y)

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw the expanding ring"""
        if not self.alive or self.current_radius <= 0:
            return

        # Convert center to screen position
        iso_x, iso_y = cart_to_iso(self.cart_x, self.cart_y)
        screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
        screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y

        # Draw expanding ring (isometric approximation)
        # Use ellipse for pseudo-isometric effect
        iso_radius_x = int(self.current_radius * 40)  # Scale to screen space
        iso_radius_y = int(self.current_radius * 20)  # Compressed Y for isometric

        if iso_radius_x > 2 and iso_radius_y > 2:
            # Create surface with alpha
            color_with_alpha = (*self.color, self.alpha)

            # Draw outer ring
            pygame.draw.ellipse(screen, self.color,
                              (screen_x - iso_radius_x, screen_y - iso_radius_y,
                               iso_radius_x * 2, iso_radius_y * 2), 3)

            # Draw inner filled ring (thinner)
            inner_radius_x = max(1, iso_radius_x - 5)
            inner_radius_y = max(1, iso_radius_y - 3)

            # Create semi-transparent surface for fill
            surf = pygame.Surface((iso_radius_x * 2, iso_radius_y * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (*self.color, self.alpha // 3),
                              (0, 0, iso_radius_x * 2, iso_radius_y * 2))
            screen.blit(surf, (screen_x - iso_radius_x, screen_y - iso_radius_y))
