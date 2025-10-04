"""Particle system for spell visual effects"""

import pygame
import math
import random
from rendering.isometric import cart_to_iso
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Particle:
    """Single particle with position, velocity, and lifetime"""

    def __init__(self, x, y, vel_x, vel_y, color, lifetime, size=3):
        self.cart_x = x
        self.cart_y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.max_lifetime = lifetime
        self.lifetime = 0.0
        self.size = size
        self.alive = True

    def update(self, dt):
        """Update particle position and lifetime"""
        self.lifetime += dt
        if self.lifetime >= self.max_lifetime:
            self.alive = False
            return

        # Move particle
        self.cart_x += self.vel_x * dt * 10  # Scale for visibility
        self.cart_y += self.vel_y * dt * 10

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw particle with fade-out based on lifetime"""
        if not self.alive:
            return

        # Calculate alpha based on remaining lifetime
        alpha = 1.0 - (self.lifetime / self.max_lifetime)
        color = tuple(int(c * alpha) for c in self.color)

        # Convert to screen position
        iso_x, iso_y = cart_to_iso(self.cart_x, self.cart_y)
        screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
        screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y

        # Draw particle
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), size)


class ParticleEmitter:
    """
    Particle emitter for various spell effects.
    Supports: explosions, trails, zones, buffs, auras.
    """

    def __init__(self, x, y, effect_type, color, duration=1.0, area=1.0):
        """
        Create particle emitter.

        Args:
            x, y: Cartesian position
            effect_type: 'explosion', 'trail', 'zone', 'buff', 'aura'
            color: RGB tuple
            duration: How long effect lasts
            area: Size multiplier
        """
        self.cart_x = x
        self.cart_y = y
        self.effect_type = effect_type
        self.color = color
        self.duration = duration
        self.area = area
        self.lifetime = 0.0
        self.particles = []
        self.alive = True

        # Emit initial burst for explosions
        if effect_type == 'explosion':
            self._emit_explosion()
        elif effect_type == 'aoe':
            self._emit_aoe()

    def _emit_explosion(self):
        """Emit radial burst of particles"""
        particle_count = int(20 * self.area)
        for _ in range(particle_count):
            # Random angle and speed
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.1, 0.3) * self.area
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed

            # Create particle
            p = Particle(
                self.cart_x, self.cart_y,
                vel_x, vel_y,
                self.color,
                lifetime=random.uniform(0.3, 0.6),
                size=random.randint(2, 4)
            )
            self.particles.append(p)

    def _emit_aoe(self):
        """Emit expanding ring of particles"""
        particle_count = int(30 * self.area)
        for i in range(particle_count):
            # Evenly distributed around circle
            angle = (i / particle_count) * 2 * math.pi
            radius = 0.5 * self.area

            # Position on circle
            offset_x = math.cos(angle) * radius
            offset_y = math.sin(angle) * radius

            # Velocity outward
            speed = 0.2
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed

            p = Particle(
                self.cart_x + offset_x,
                self.cart_y + offset_y,
                vel_x, vel_y,
                self.color,
                lifetime=0.8,
                size=3
            )
            self.particles.append(p)

    def _emit_zone_particle(self):
        """Emit single particle for persistent zone (called per frame)"""
        # Random position within zone radius
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, self.area * 0.5)
        x = self.cart_x + math.cos(angle) * radius
        y = self.cart_y + math.sin(angle) * radius

        # Slow upward drift
        vel_x = random.uniform(-0.05, 0.05)
        vel_y = random.uniform(-0.1, -0.05)

        p = Particle(
            x, y, vel_x, vel_y,
            self.color,
            lifetime=random.uniform(0.5, 1.0),
            size=random.randint(2, 3)
        )
        self.particles.append(p)

    def _emit_buff_particle(self):
        """Emit orbiting particle for buff aura"""
        angle = random.uniform(0, 2 * math.pi)
        radius = 0.3
        x = self.cart_x + math.cos(angle) * radius
        y = self.cart_y + math.sin(angle) * radius

        # Tangential velocity (orbit)
        vel_x = -math.sin(angle) * 0.3
        vel_y = math.cos(angle) * 0.3

        p = Particle(
            x, y, vel_x, vel_y,
            self.color,
            lifetime=0.8,
            size=2
        )
        self.particles.append(p)

    def update(self, dt):
        """Update emitter and all particles"""
        self.lifetime += dt

        # Die when duration expires and no particles left
        if self.lifetime > self.duration and len(self.particles) == 0:
            self.alive = False
            return

        # Emit continuous particles for zone/buff effects
        if self.lifetime < self.duration:
            if self.effect_type == 'zone':
                # Emit 2 particles per frame for zone
                for _ in range(2):
                    self._emit_zone_particle()
            elif self.effect_type == 'buff' or self.effect_type == 'aura':
                # Emit 1 particle per frame for buff
                self._emit_buff_particle()

        # Update all particles
        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self.particles.remove(p)

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw all particles"""
        for p in self.particles:
            p.draw(screen, camera_offset_x, camera_offset_y)
