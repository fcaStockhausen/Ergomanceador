"""
Chain Lightning Effect - Quake 1 style zigzag lightning that chains between targets.

Visual: Instant zigzag beam that jumps from target to target
Behavior: Hits primary target, then chains to nearby enemies
"""

import pygame
import random
import math
from rendering.isometric import cart_to_iso


class ChainLightningBolt:
    """Single lightning bolt segment with zigzag rendering"""

    def __init__(self, start_x, start_y, end_x, end_y, color, intensity=1.0, duration=0.3):
        """
        Create a lightning bolt from start to end.

        Args:
            start_x, start_y: Start position (cartesian)
            end_x, end_y: End position (cartesian)
            color: RGB tuple
            intensity: Brightness multiplier (0-1, decreases per chain jump)
            duration: How long the bolt lasts (seconds)
        """
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.color = color
        self.intensity = intensity
        self.duration = duration
        self.age = 0.0
        self.alive = True

        # Zigzag parameters (Quake 1 style)
        self.segments = 8  # Number of zigzag points
        self.jitter = 0.3  # How much the lightning zigzags
        self._generate_zigzag()

    def _generate_zigzag(self):
        """Generate zigzag points between start and end"""
        self.points = []

        # Always start at start position
        self.points.append((self.start_x, self.start_y))

        # Generate intermediate zigzag points
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        distance = math.sqrt(dx*dx + dy*dy)

        # Perpendicular vector for jitter
        if distance > 0:
            perp_x = -dy / distance
            perp_y = dx / distance
        else:
            perp_x, perp_y = 0, 0

        # Add zigzag points
        for i in range(1, self.segments):
            t = i / self.segments  # 0 to 1
            # Linear interpolation
            mid_x = self.start_x + dx * t
            mid_y = self.start_y + dy * t

            # Add random jitter perpendicular to direction
            jitter_amount = (random.random() - 0.5) * self.jitter * 2
            mid_x += perp_x * jitter_amount
            mid_y += perp_y * jitter_amount

            self.points.append((mid_x, mid_y))

        # Always end at end position
        self.points.append((self.end_x, self.end_y))

    def update(self, dt):
        """Update bolt lifetime"""
        self.age += dt
        if self.age >= self.duration:
            self.alive = False

        # Regenerate zigzag occasionally for flickering effect
        if random.random() < 0.3:  # 30% chance per frame
            self._generate_zigzag()

    def draw(self, screen, camera):
        """Draw zigzag lightning bolt"""
        if not self.alive:
            return

        # Fade out over time
        fade = 1.0 - (self.age / self.duration)
        alpha = int(255 * fade * self.intensity)
        if alpha <= 0:
            return

        # Adjust color brightness
        r = min(255, int(self.color[0] * self.intensity))
        g = min(255, int(self.color[1] * self.intensity))
        b = min(255, int(self.color[2] * self.intensity))
        color = (r, g, b)

        # Convert all points to screen space
        screen_points = []
        for cart_x, cart_y in self.points:
            iso_x, iso_y = cart_to_iso(cart_x, cart_y)
            screen_x = iso_x - camera.offset_x
            screen_y = iso_y - camera.offset_y
            screen_points.append((screen_x, screen_y))

        # Draw main bolt (thick line)
        if len(screen_points) >= 2:
            pygame.draw.lines(screen, color, False, screen_points, 3)

            # Draw glow (thinner, brighter line on top)
            bright_color = (
                min(255, r + 100),
                min(255, g + 100),
                min(255, b + 100)
            )
            pygame.draw.lines(screen, bright_color, False, screen_points, 1)


class ChainLightningEffect:
    """Manages chain lightning that jumps between multiple targets"""

    def __init__(self, start_x, start_y, primary_target, enemies, spell_data, owner='player', max_chains=3):
        """
        Create chain lightning effect.

        Args:
            start_x, start_y: Caster position
            primary_target: First enemy to hit (or None to hit nearest)
            enemies: List of all enemies to potentially chain to
            spell_data: Spell properties (damage, color, etc.)
            owner: Who cast it
            max_chains: Maximum number of chain jumps
        """
        self.start_x = start_x
        self.start_y = start_y
        self.enemies = enemies
        self.spell_data = spell_data
        self.owner = owner
        self.max_chains = max_chains

        self.color = spell_data.get('color', (255, 255, 100))  # Default yellow
        self.damage = spell_data.get('damage', 50)
        self.chain_range = 5.0  # Units - how far lightning can jump

        self.bolts = []  # List of ChainLightningBolt objects
        self.hit_enemies = set()  # Track hit enemies (don't hit twice)
        self.alive = True

        # Execute chain lightning immediately
        self._execute_chain(start_x, start_y, primary_target)

    def _execute_chain(self, from_x, from_y, primary_target):
        """Execute the chain lightning sequence"""
        current_x, current_y = from_x, from_y
        current_target = primary_target
        chain_count = 0
        intensity = 1.0

        while chain_count < self.max_chains:
            # Find next target
            if current_target is None:
                current_target = self._find_nearest_target(current_x, current_y)

            if current_target is None:
                break  # No more targets

            # Create lightning bolt to this target
            bolt = ChainLightningBolt(
                current_x, current_y,
                current_target.cart_x, current_target.cart_y,
                self.color,
                intensity=intensity,
                duration=0.3 + chain_count * 0.1  # Longer duration for later chains
            )
            self.bolts.append(bolt)

            # Deal damage (reduced per chain)
            damage = int(self.damage * intensity)
            current_target.health.damage(damage)
            self.hit_enemies.add(current_target)

            # Move to this target for next chain
            current_x = current_target.cart_x
            current_y = current_target.cart_y

            # Reduce intensity for next chain
            intensity *= 0.7

            # Find next target (different from current)
            current_target = self._find_nearest_target(current_x, current_y, exclude=current_target)
            chain_count += 1

    def _find_nearest_target(self, from_x, from_y, exclude=None):
        """Find nearest enemy within chain range"""
        nearest = None
        nearest_dist = self.chain_range

        for enemy in self.enemies:
            if enemy in self.hit_enemies:
                continue  # Already hit
            if exclude and enemy == exclude:
                continue  # Exclude specific enemy
            if not enemy.health.is_alive:
                continue  # Dead

            # Calculate distance
            dx = enemy.cart_x - from_x
            dy = enemy.cart_y - from_y
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < nearest_dist:
                nearest_dist = dist
                nearest = enemy

        return nearest

    def update(self, dt):
        """Update all lightning bolts"""
        for bolt in self.bolts:
            bolt.update(dt)

        # Remove dead bolts
        self.bolts = [b for b in self.bolts if b.alive]

        # Die when all bolts are gone
        if not self.bolts:
            self.alive = False

    def draw(self, screen, camera):
        """Draw all lightning bolts"""
        for bolt in self.bolts:
            bolt.draw(screen, camera)
