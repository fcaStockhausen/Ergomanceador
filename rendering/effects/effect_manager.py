"""Effect manager - tracks all active visual spell effects"""

import logging
from rendering.effects.projectile import Projectile
from rendering.effects.particle import ParticleEmitter
from rendering.ui.damage_numbers import DamageNumberManager
from physics.collision import CollisionChecker
from audio.sound_manager import SoundManager


class EffectManager:
    """
    Manages all active spell visual effects.
    Handles spawning, updating, and rendering projectiles and particles.
    Now with collision detection and damage!
    """

    def __init__(self):
        self.projectiles = []
        self.emitters = []
        self.enemies = []  # Reference to enemy list (set by Game)
        self.damage_numbers = DamageNumberManager()  # Floating damage numbers
        self.camera = None  # Reference to camera (set by Game) for screen shake
        self.sound = SoundManager(enabled=True)  # Sound effects

    def spawn_spell_effect(self, player_x, player_y, target_x, target_y, spell_data):
        """
        Spawn visual effect based on spell behavior.

        Args:
            player_x, player_y: Player cartesian position
            target_x, target_y: Target cartesian position
            spell_data: Dict with spell properties
        """
        behavior = spell_data.get('behavior', 'projectile')
        color = spell_data.get('color', (255, 255, 255))
        area = spell_data.get('area', 1.0)
        duration = spell_data.get('duration', 1.0)

        logging.info(f"Spawning {behavior} effect: {spell_data.get('name', 'Unknown')}")

        if behavior == 'projectile':
            # Create projectile + trail particles
            proj = Projectile(player_x, player_y, target_x, target_y, spell_data)
            self.projectiles.append(proj)

            # Play cast sound
            self.sound.play('cast', volume=0.5)

            # Explosion on impact (deferred until projectile dies)
            # TODO: Add impact detection and explosion spawn

        elif behavior == 'beam':
            # Instant beam visual
            proj = Projectile(player_x, player_y, target_x, target_y, spell_data)
            self.projectiles.append(proj)

            # Beam impact particles at target
            emitter = ParticleEmitter(
                target_x, target_y,
                'explosion',
                color,
                duration=0.5,
                area=area
            )
            self.emitters.append(emitter)

        elif behavior == 'aoe':
            # Expanding explosion at target
            emitter = ParticleEmitter(
                target_x, target_y,
                'aoe',
                color,
                duration=0.8,
                area=area * 2  # Larger visual
            )
            self.emitters.append(emitter)

        elif behavior == 'area_denial':
            # Persistent zone at target
            emitter = ParticleEmitter(
                target_x, target_y,
                'zone',
                color,
                duration=duration,
                area=area
            )
            self.emitters.append(emitter)

        elif behavior == 'buff':
            # Aura around player (not target)
            emitter = ParticleEmitter(
                player_x, player_y,
                'buff',
                color,
                duration=duration,
                area=0.5
            )
            self.emitters.append(emitter)

        elif behavior == 'homing':
            # Homing projectile
            proj = Projectile(player_x, player_y, target_x, target_y, spell_data)
            self.projectiles.append(proj)

    def update(self, dt):
        """Update all effects and check collisions"""
        # Update projectiles and check hits
        for proj in self.projectiles[:]:
            proj.update(dt)

            # Check collision with enemies
            if proj.alive:
                hit_enemy = CollisionChecker.projectile_vs_entities(
                    proj,
                    [e for e in self.enemies if e.health.is_alive],
                    entity_radius=0.5
                )

                if hit_enemy:
                    # Deal damage
                    damage = proj.spell_data.get('damage', 10)
                    hit_enemy.health.damage(damage)
                    logging.info(f"Projectile hit enemy! Dealt {damage} damage")

                    # Spawn floating damage number
                    self.damage_numbers.spawn(damage, hit_enemy.cart_x, hit_enemy.cart_y)

                    # Screen shake on impact
                    if self.camera:
                        # Stronger shake for more damage
                        shake_intensity = min(5.0 + (damage * 0.3), 15.0)
                        self.camera.shake(intensity=shake_intensity, duration=0.15)

                    # Impact sound
                    self.sound.play('impact', volume=0.6)

                    # Apply knockback
                    import math
                    knockback_force = 3.0 + (damage * 0.05)  # Stronger for more damage
                    dx = hit_enemy.cart_x - proj.cart_x
                    dy = hit_enemy.cart_y - proj.cart_y
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance > 0.01:
                        # Normalize direction
                        dir_x = dx / distance
                        dir_y = dy / distance
                        hit_enemy.apply_knockback(dir_x, dir_y, knockback_force)

                    # Kill projectile
                    proj.alive = False

            if not proj.alive:
                # Spawn explosion on impact for projectiles
                if proj.behavior == 'projectile' or proj.behavior == 'homing':
                    explosion = ParticleEmitter(
                        proj.cart_x, proj.cart_y,
                        'explosion',
                        proj.color,
                        duration=0.5,
                        area=proj.area
                    )
                    self.emitters.append(explosion)

                self.projectiles.remove(proj)

        # Update particle emitters
        for emitter in self.emitters[:]:
            emitter.update(dt)
            if not emitter.alive:
                self.emitters.remove(emitter)

        # Update damage numbers
        self.damage_numbers.update(dt)

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw all effects"""
        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(screen, camera_offset_x, camera_offset_y)

        # Draw particles
        for emitter in self.emitters:
            emitter.draw(screen, camera_offset_x, camera_offset_y)

        # Draw damage numbers (on top of everything)
        self.damage_numbers.draw(screen, camera_offset_x, camera_offset_y)

    def clear_all(self):
        """Clear all active effects"""
        self.projectiles.clear()
        self.emitters.clear()
        self.damage_numbers.clear_all()
