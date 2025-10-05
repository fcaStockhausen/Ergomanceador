"""Base particle system for spell effects"""

import pygame
import math
import random


class Particle:
    """Single particle with lifetime, velocity, and alpha fading"""

    def __init__(self, x, y, color, lifetime, velocity=(0, 0), size=4):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.velocity = velocity
        self.size = size
        self.alpha = 255

    def update(self, dt):
        """Update particle position and age. Returns True if still alive."""
        self.age += dt
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        # Fade out near end of life
        if self.lifetime > 0:
            self.alpha = int(255 * max(0, 1 - self.age / self.lifetime))

        return self.age < self.lifetime

    def render(self, screen, camera_offset):
        """Render particle with alpha blending"""
        if self.alpha <= 0:
            return

        # Create surface with alpha
        surf = pygame.Surface((self.size, self.size))
        surf.set_alpha(self.alpha)
        surf.fill(self.color)

        # Calculate screen position with camera offset
        screen_x = int(self.x - camera_offset[0] - self.size // 2)
        screen_y = int(self.y - camera_offset[1] - self.size // 2)

        screen.blit(surf, (screen_x, screen_y))


class ParticleSystem:
    """Manages a collection of particles"""

    def __init__(self):
        self.particles = []

    def add_particle(self, particle):
        """Add a particle to the system"""
        self.particles.append(particle)

    def add_particles(self, particles):
        """Add multiple particles"""
        self.particles.extend(particles)

    def update(self, dt):
        """Update all particles, removing dead ones"""
        self.particles = [p for p in self.particles if p.update(dt)]

    def render(self, screen, camera_offset):
        """Render all particles"""
        for particle in self.particles:
            particle.render(screen, camera_offset)

    def clear(self):
        """Remove all particles"""
        self.particles.clear()

    def count(self):
        """Get number of active particles"""
        return len(self.particles)
