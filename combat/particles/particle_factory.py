"""Particle factory for generating behavior-specific particle effects"""

import math
import random
import numpy as np
from combat.particles.particle import Particle


class ParticleFactory:
    """Generates particles based on spell behavior and properties"""

    @staticmethod
    def create_projectile_trail(x, y, velocity, color, density=5):
        """Trailing particles for projectile spells"""
        particles = []

        for i in range(density):
            # Random offset around projectile
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-3, 3)

            # Trail velocity (opposite to projectile direction, slower)
            trail_velocity = (
                -velocity[0] * 0.3 + random.uniform(-10, 10),
                -velocity[1] * 0.3 + random.uniform(-10, 10)
            )

            particles.append(Particle(
                x + offset_x,
                y + offset_y,
                color,
                lifetime=0.4,
                velocity=trail_velocity,
                size=random.randint(3, 6)
            ))

        return particles

    @staticmethod
    def create_aoe_burst(x, y, radius, color, density=30):
        """Radial burst for AOE/explosion spells"""
        particles = []

        for i in range(density):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(radius * 0.5, radius * 1.5)

            particles.append(Particle(
                x,
                y,
                color,
                lifetime=0.6,
                velocity=(math.cos(angle) * speed, math.sin(angle) * speed),
                size=random.randint(4, 8)
            ))

        return particles

    @staticmethod
    def create_chain_arc(start, end, color, segments=15):
        """Branching arc for chain lightning"""
        particles = []

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        # Create control point for Bezier curve (offset perpendicular to line)
        mid_x = start[0] + dx * 0.5
        mid_y = start[1] + dy * 0.5

        # Perpendicular offset
        perp_angle = math.atan2(dy, dx) + math.pi / 2
        offset = random.uniform(10, 30)
        ctrl_x = mid_x + math.cos(perp_angle) * offset
        ctrl_y = mid_y + math.sin(perp_angle) * offset

        # Generate particles along Bezier curve
        for i in range(segments):
            t = i / (segments - 1)

            # Quadratic Bezier formula
            x = (1-t)**2 * start[0] + 2*(1-t)*t * ctrl_x + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * ctrl_y + t**2 * end[1]

            # Add jitter for electric effect
            x += random.uniform(-3, 3)
            y += random.uniform(-3, 3)

            particles.append(Particle(
                x, y,
                color,
                lifetime=0.2,
                velocity=(0, 0),
                size=random.randint(2, 5)
            ))

        return particles

    @staticmethod
    def create_beam_particles(start, end, color, density=20):
        """Particles for beam spells (instant line damage)"""
        particles = []

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            return particles

        # Particles along beam line
        for i in range(density):
            t = random.random()
            x = start[0] + dx * t
            y = start[1] + dy * t

            # Perpendicular spread
            perp_angle = math.atan2(dy, dx) + math.pi / 2
            spread = random.uniform(-5, 5)

            particles.append(Particle(
                x + math.cos(perp_angle) * spread,
                y + math.sin(perp_angle) * spread,
                color,
                lifetime=0.3,
                velocity=(0, 0),
                size=random.randint(3, 6)
            ))

        return particles

    @staticmethod
    def create_heal_sparkles(x, y, color, density=15):
        """Rising sparkle particles for heal spells"""
        particles = []

        for i in range(density):
            # Random position around heal center
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, 20)

            # Upward drift with slight randomness
            particles.append(Particle(
                x + math.cos(angle) * radius,
                y + math.sin(angle) * radius,
                color,
                lifetime=0.8,
                velocity=(random.uniform(-10, 10), -30),  # Drift upward
                size=random.randint(2, 4)
            ))

        return particles

    @staticmethod
    def create_buff_orbit(x, y, color, density=10):
        """Orbiting particles for buff spells"""
        particles = []

        for i in range(density):
            angle = (i / density) * 2 * math.pi
            radius = 25

            # Circular motion (velocity tangent to circle)
            orbit_speed = 50
            vx = -math.sin(angle) * orbit_speed
            vy = math.cos(angle) * orbit_speed

            particles.append(Particle(
                x + math.cos(angle) * radius,
                y + math.sin(angle) * radius,
                color,
                lifetime=1.0,
                velocity=(vx, vy),
                size=3
            ))

        return particles

    @staticmethod
    def create_area_denial_cloud(x, y, radius, color, density=25):
        """Lingering cloud for area denial spells"""
        particles = []

        for i in range(density):
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, radius)

            # Slow drift
            particles.append(Particle(
                x + math.cos(angle) * r,
                y + math.sin(angle) * r,
                color,
                lifetime=2.0,  # Long lifetime
                velocity=(random.uniform(-5, 5), random.uniform(-5, 5)),
                size=random.randint(5, 10)
            ))

        return particles

    @staticmethod
    def create_homing_trail(x, y, velocity, color, density=8):
        """Curved trail for homing projectiles"""
        particles = []

        for i in range(density):
            # Similar to projectile but with more spread
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)

            # Velocity perpendicular to movement (spiral effect)
            perp_angle = math.atan2(velocity[1], velocity[0]) + math.pi / 2
            spread_vel = random.uniform(-20, 20)

            trail_vel = (
                -velocity[0] * 0.2 + math.cos(perp_angle) * spread_vel,
                -velocity[1] * 0.2 + math.sin(perp_angle) * spread_vel
            )

            particles.append(Particle(
                x + offset_x,
                y + offset_y,
                color,
                lifetime=0.5,
                velocity=trail_vel,
                size=random.randint(2, 5)
            ))

        return particles

    @staticmethod
    def create_from_behavior(behavior, x, y, color, **kwargs):
        """
        Factory method to create particles based on spell behavior.

        Args:
            behavior: Spell behavior type (projectile, beam, aoe, etc.)
            x, y: Position
            color: RGB tuple
            **kwargs: Behavior-specific parameters

        Returns:
            List of Particle objects
        """
        generators = {
            'projectile': lambda: ParticleFactory.create_projectile_trail(
                x, y, kwargs.get('velocity', (0, 0)), color, kwargs.get('density', 5)
            ),
            'beam': lambda: ParticleFactory.create_beam_particles(
                (x, y), kwargs.get('end', (x+100, y)), color, kwargs.get('density', 20)
            ),
            'aoe': lambda: ParticleFactory.create_aoe_burst(
                x, y, kwargs.get('radius', 50), color, kwargs.get('density', 30)
            ),
            'chain': lambda: ParticleFactory.create_chain_arc(
                (x, y), kwargs.get('end', (x+100, y)), color, kwargs.get('segments', 15)
            ),
            'homing': lambda: ParticleFactory.create_homing_trail(
                x, y, kwargs.get('velocity', (0, 0)), color, kwargs.get('density', 8)
            ),
            'area_denial': lambda: ParticleFactory.create_area_denial_cloud(
                x, y, kwargs.get('radius', 40), color, kwargs.get('density', 25)
            ),
            'heal': lambda: ParticleFactory.create_heal_sparkles(
                x, y, color, kwargs.get('density', 15)
            ),
            'buff': lambda: ParticleFactory.create_buff_orbit(
                x, y, color, kwargs.get('density', 10)
            ),
        }

        generator = generators.get(behavior, lambda: [])
        return generator()
