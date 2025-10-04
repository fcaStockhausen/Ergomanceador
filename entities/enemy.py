"""Enemy entity - training dummy for combat testing"""

import pygame
import logging
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from config.colors import RED, WHITE, GREEN, GRAY
from rendering.isometric import cart_to_iso
from components.health import Health


class Enemy:
    """
    Basic enemy entity (training dummy).
    Has health, can take damage, dies when health reaches 0.
    """

    def __init__(self, x, y, max_health=100):
        """
        Create enemy at cartesian position.

        Args:
            x, y: Cartesian coordinates
            max_health: Starting health
        """
        self.cart_x = x
        self.cart_y = y
        self.size = 15
        self.color = RED
        self.collision_radius = 0.5  # Cartesian units

        # Health component
        self.health = Health(
            max_health=max_health,
            on_death=self._on_death,
            on_damage=self._on_damage
        )

        # Visual state
        self.alive = True
        self.death_timer = 0.0
        self.death_duration = 0.5  # Fade out over 0.5 seconds
        self.alpha = 255  # For fade-out effect

        # Knockback physics
        self.knockback_velocity_x = 0.0
        self.knockback_velocity_y = 0.0
        self.knockback_friction = 8.0  # Deceleration rate

    def _on_death(self):
        """Called when health reaches 0"""
        logging.info(f"Enemy died at ({self.cart_x:.1f}, {self.cart_y:.1f})")
        self.alive = False
        # Don't remove immediately - play death animation

    def _on_damage(self, amount):
        """Called when damaged"""
        logging.info(f"Enemy took {amount} damage at ({self.cart_x:.1f}, {self.cart_y:.1f})")

    def apply_knockback(self, direction_x, direction_y, force=3.0):
        """Apply knockback force to enemy

        Args:
            direction_x, direction_y: Normalized direction vector
            force: Knockback strength (cartesian units/second)
        """
        self.knockback_velocity_x = direction_x * force
        self.knockback_velocity_y = direction_y * force

    def update(self, dt):
        """Update enemy state"""
        # Update health component (for damage flash)
        self.health.update(dt)

        # Apply knockback physics
        if abs(self.knockback_velocity_x) > 0.01 or abs(self.knockback_velocity_y) > 0.01:
            # Move enemy based on knockback velocity
            self.cart_x += self.knockback_velocity_x * dt
            self.cart_y += self.knockback_velocity_y * dt

            # Apply friction (slow down)
            friction = self.knockback_friction * dt
            if self.knockback_velocity_x > 0:
                self.knockback_velocity_x = max(0, self.knockback_velocity_x - friction)
            else:
                self.knockback_velocity_x = min(0, self.knockback_velocity_x + friction)

            if self.knockback_velocity_y > 0:
                self.knockback_velocity_y = max(0, self.knockback_velocity_y - friction)
            else:
                self.knockback_velocity_y = min(0, self.knockback_velocity_y + friction)

            # Keep in bounds
            self.cart_x = max(0, min(20, self.cart_x))
            self.cart_y = max(0, min(20, self.cart_y))

        # Death animation
        if not self.health.is_alive:
            self.death_timer += dt
            # Fade out
            fade_progress = min(1.0, self.death_timer / self.death_duration)
            self.alpha = int(255 * (1.0 - fade_progress))

    def should_remove(self):
        """Check if enemy should be removed from game (after death animation)"""
        return not self.health.is_alive and self.death_timer >= self.death_duration

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw enemy"""
        # Convert to isometric coordinates
        iso_x, iso_y = cart_to_iso(self.cart_x, self.cart_y)
        screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
        screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y

        # Determine color (red flash when damaged, fade when dying)
        if self.health.is_flashing():
            # Flash white when damaged
            color = WHITE
        else:
            color = self.color

        # Create surface with alpha for fade-out
        if self.alpha < 255:
            # Draw with transparency
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*color, self.alpha), (self.size, self.size), self.size)
            screen.blit(surface, (int(screen_x - self.size), int(screen_y - self.size)))
        else:
            # Normal draw
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), self.size)

        # Draw health bar above enemy
        if self.health.is_alive:
            self._draw_health_bar(screen, screen_x, screen_y - 25)

    def _draw_health_bar(self, screen, x, y):
        """Draw health bar above enemy"""
        bar_width = 40
        bar_height = 5
        health_pct = self.health.get_health_percentage()

        # Background (gray)
        bg_rect = pygame.Rect(int(x - bar_width // 2), int(y), bar_width, bar_height)
        pygame.draw.rect(screen, GRAY, bg_rect)

        # Health (green)
        health_width = int(bar_width * health_pct)
        if health_width > 0:
            health_rect = pygame.Rect(int(x - bar_width // 2), int(y), health_width, bar_height)
            pygame.draw.rect(screen, GREEN, health_rect)

        # Border
        pygame.draw.rect(screen, WHITE, bg_rect, 1)
