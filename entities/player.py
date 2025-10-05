"""Player entity"""

import pygame
import logging
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, BASE_MOVEMENT_SPEED
from config.colors import WHITE, GREEN, GRAY, BLUE, CYAN
from rendering.isometric import cart_to_iso, screen_to_cart
from components.health import Health
from components.mana import Mana
from entities.components.shield import Shield


class Player:
    def __init__(self, x, y):
        self.cart_x = x  # Cartesian X
        self.cart_y = y  # Cartesian Y
        self.spawn_x = x  # Respawn position
        self.spawn_y = y
        self.z = 0  # Height above ground
        self.size = 20
        self.base_speed = BASE_MOVEMENT_SPEED  # Use centralized base speed
        self.speed_multiplier = 1.0  # For effects that modify speed (buffs/debuffs)
        self.color = WHITE
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -10

        # Health and Mana components
        self.health = Health(max_health=300)  # Higher health for longer fights
        self.mana = Mana(max_mana=200, regen_rate=15.0)  # Doubled for 6-element queue support
        self.collision_radius = 0.5  # For collision with projectiles

        # Shield component (created when shield spell is cast)
        self.shield = None  # Shield instance, None if no shield active

        # Facing direction (for forward-facing targeting)
        self.facing_direction = (1, 0)  # Default facing right

        # Debug info
        self.last_input = (0, 0)
        self.last_cart_delta = (0, 0)
        self.last_logged_input = (0, 0)  # Track last logged input to avoid spam

    def move(self, screen_dx, screen_dy, dt=0.016):
        """Move using screen-space directions (perspective coordinates)"""
        # Store input for debug
        self.last_input = (screen_dx, screen_dy)

        # Convert screen direction to cartesian movement
        cart_dx, cart_dy = screen_to_cart(screen_dx, screen_dy)

        # Calculate effective speed (base * multiplier * dt for frame-rate independence)
        effective_speed = self.base_speed * self.speed_multiplier * dt

        # Store cartesian delta for debug
        self.last_cart_delta = (cart_dx * effective_speed, cart_dy * effective_speed)

        # Log only on input CHANGE (not every frame)
        if (screen_dx, screen_dy) != self.last_logged_input:
            if screen_dx != 0 or screen_dy != 0:
                logging.info(f"Movement START: Input ({screen_dx}, {screen_dy}) -> Cart delta ({cart_dx:.3f}, {cart_dy:.3f})")
            else:
                logging.info(f"Movement STOP at position ({self.cart_x:.2f}, {self.cart_y:.2f})")
            self.last_logged_input = (screen_dx, screen_dy)

        # Move in cartesian space
        self.cart_x += cart_dx * effective_speed
        self.cart_y += cart_dy * effective_speed

        # Update facing direction when moving
        if cart_dx != 0 or cart_dy != 0:
            import math
            magnitude = math.sqrt(cart_dx**2 + cart_dy**2)
            if magnitude > 0:
                self.facing_direction = (cart_dx / magnitude, cart_dy / magnitude)

        # Keep player in bounds
        self.cart_x = max(0, min(GRID_SIZE, self.cart_x))
        self.cart_y = max(0, min(GRID_SIZE, self.cart_y))

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = self.jump_strength
            logging.info(f"JUMP at position ({self.cart_x:.2f}, {self.cart_y:.2f})")

    def update(self, dt):
        """Update player state"""
        self.health.update(dt)
        self.mana.update(dt)  # Regenerate mana

        # Update shield if active
        if self.shield:
            self.shield.update(dt)
            if not self.shield.is_active():
                self.shield = None  # Remove expired/broken shield

    def take_damage(self, damage):
        """
        Take damage, shield absorbs first if active.

        Args:
            damage: Raw damage amount

        Returns:
            final_damage: Damage dealt to health after shield absorption
        """
        if self.shield and self.shield.is_active():
            absorbed, overflow = self.shield.absorb_damage(damage)
            logging.info(f"Shield absorbed {absorbed} damage, {overflow} overflow")

            if overflow > 0:
                self.health.damage(overflow)
            return overflow
        else:
            # No shield, take full damage
            self.health.damage(damage)
            return damage

    def apply_shield(self, shield_hp, duration):
        """Apply a new shield or refresh existing one"""
        if self.shield and self.shield.is_active():
            # Refresh shield: add HP and reset duration
            self.shield.current_shield_hp += shield_hp
            self.shield.max_shield_hp += shield_hp
            self.shield.time_remaining = max(self.shield.time_remaining, duration)
            logging.info(f"Shield refreshed! New HP: {self.shield.current_shield_hp}")
        else:
            # Create new shield
            self.shield = Shield(shield_hp, duration)

    def update_jump(self):
        if self.is_jumping:
            self.z += self.jump_velocity
            self.jump_velocity += self.gravity

            # Land back on ground
            if self.z >= 0:
                self.z = 0
                self.is_jumping = False
                self.jump_velocity = 0

    def respawn(self):
        """Respawn player at spawn point"""
        self.cart_x = self.spawn_x
        self.cart_y = self.spawn_y
        self.z = 0
        self.is_jumping = False
        self.jump_velocity = 0
        self.health.respawn()
        self.mana.current_mana = self.mana.max_mana  # Full mana on respawn
        logging.info(f"Player respawned at ({self.spawn_x}, {self.spawn_y})")

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

        # Draw health and mana bars above player
        if self.health.is_alive:
            self._draw_health_bar(screen, screen_x, top_y - 20)
            self._draw_mana_bar(screen, screen_x, top_y - 12)

    def _draw_health_bar(self, screen, x, y):
        """Draw health bar above player"""
        bar_width = 50
        bar_height = 6
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

    def _draw_mana_bar(self, screen, x, y):
        """Draw mana bar above player"""
        bar_width = 50
        bar_height = 5
        mana_pct = self.mana.get_mana_percentage()

        # Background (gray)
        bg_rect = pygame.Rect(int(x - bar_width // 2), int(y), bar_width, bar_height)
        pygame.draw.rect(screen, GRAY, bg_rect)

        # Mana (blue/cyan)
        mana_width = int(bar_width * mana_pct)
        if mana_width > 0:
            mana_rect = pygame.Rect(int(x - bar_width // 2), int(y), mana_width, bar_height)
            pygame.draw.rect(screen, CYAN, mana_rect)

        # Border
        pygame.draw.rect(screen, WHITE, bg_rect, 1)
