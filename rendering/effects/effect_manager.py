"""Effect manager - tracks all active visual spell effects"""

import logging
from rendering.effects.projectile import Projectile
from rendering.effects.particle import ParticleEmitter
from rendering.effects.expanding_aoe import ExpandingAOE
from rendering.effects.chain_lightning import ChainLightningEffect
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
        self.expanding_aoes = []  # Radially expanding AOE effects
        self.chain_lightnings = []  # Chain lightning effects
        self.enemies = []  # Reference to enemy list (set by Game)
        self.player = None  # Reference to player (set by Game)
        self.terrain = None  # Reference to terrain (set by Game) for damage bonuses
        self.damage_numbers = DamageNumberManager()  # Floating damage numbers
        self.camera = None  # Reference to camera (set by Game) for screen shake
        self.sound = SoundManager(enabled=True)  # Sound effects

    def spawn_spell_effect(self, player_x, player_y, target_x, target_y, spell_data, owner='player'):
        """
        Spawn visual effect based on spell behavior.

        Supports HYBRID/MULTI-BEHAVIOR compositions from manifold classification.
        Primary behavior determines main effect, modifiers add secondary effects.

        Args:
            player_x, player_y: Caster cartesian position
            target_x, target_y: Target cartesian position
            spell_data: Dict with spell properties (includes 'behavior', 'modifiers', 'weights')
            owner: 'player' or 'bot' - who cast this spell
        """
        behavior = spell_data.get('behavior', 'projectile')
        modifiers = spell_data.get('modifiers', [])  # Secondary behaviors
        weights = spell_data.get('weights', {behavior: 1.0})  # Behavior strengths
        color = spell_data.get('color', (255, 255, 255))
        area = spell_data.get('area', 1.0)
        duration = spell_data.get('duration', 1.0)

        modifier_str = f" + {modifiers}" if modifiers else ""
        logging.info(f"Spawning {behavior}{modifier_str} effect: {spell_data.get('name', 'Unknown')} (owner: {owner})")

        if behavior == 'projectile' or behavior == 'split':
            # Create projectile (split projectiles fragment mid-flight)
            proj = Projectile(player_x, player_y, target_x, target_y, spell_data, owner=owner)
            self.projectiles.append(proj)

            # Play cast sound
            self.sound.play('cast', volume=0.5)

            # Explosion on impact (deferred until projectile dies)
            # TODO: Add impact detection and explosion spawn

        elif behavior == 'beam':
            # Instant beam visual
            proj = Projectile(player_x, player_y, target_x, target_y, spell_data, owner=owner)
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
            # Create expanding AOE effect
            expansion_speed = 15.0  # Radius units per second
            duration = 0.8  # Total expansion duration

            aoe = ExpandingAOE(
                target_x, target_y,
                max_radius=area,
                color=color,
                spell_data=spell_data,
                owner=owner,
                expansion_speed=expansion_speed,
                duration=duration
            )
            self.expanding_aoes.append(aoe)

            # Screen shake and sound for AOE
            if self.camera:
                self.camera.shake(intensity=10.0, duration=0.2)
            self.sound.play('impact', volume=0.8)

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

        elif behavior == 'heal':
            # Healing spell - heal caster
            heal_amount = spell_data.get('damage', 50)  # Use damage stat as heal amount

            if owner == 'player' and self.player:
                self.player.health.heal(heal_amount)
                logging.info(f"Healed player for {heal_amount} HP!")
                if self.damage_numbers:
                    self.damage_numbers.spawn(heal_amount, player_x, player_y, is_heal=True)

            # Healing particles
            emitter = ParticleEmitter(
                player_x, player_y,
                'buff',  # Use buff visual for healing
                color,
                duration=1.0,
                area=1.5
            )
            self.emitters.append(emitter)
            self.sound.play('cast', volume=0.5)

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
            proj = Projectile(player_x, player_y, target_x, target_y, spell_data, owner=owner)
            self.projectiles.append(proj)

        elif behavior == 'chain':
            # Chain lightning - Quake 1 style zigzag instant beam
            import math

            # Find nearest enemy as primary target
            if owner == 'player':
                valid_enemies = [e for e in self.enemies if e.health.is_alive]
            else:
                # Bot targeting (hit player or other bots)
                valid_enemies = []
                if self.player and self.player.health.is_alive:
                    valid_enemies.append(self.player)
                # Add other enemies (bots can hit each other)
                valid_enemies.extend([e for e in self.enemies if e.health.is_alive])

            if not valid_enemies:
                logging.info("Chain lightning: No valid targets")
                return

            # Find nearest enemy to aim point
            nearest = None
            nearest_dist = float('inf')
            for enemy in valid_enemies:
                dx = enemy.cart_x - target_x
                dy = enemy.cart_y - target_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = enemy

            if nearest:
                # Create chain lightning effect
                chain = ChainLightningEffect(
                    player_x, player_y,
                    nearest,
                    valid_enemies,
                    spell_data,
                    owner=owner,
                    max_chains=3  # Can chain to up to 3 additional targets
                )
                self.chain_lightnings.append(chain)

                # Spawn damage numbers for all hit enemies
                for enemy in chain.hit_enemies:
                    # Calculate damage for this enemy
                    damage = spell_data.get('damage', 50)
                    # Damage already applied in chain lightning, just show numbers
                    if enemy in valid_enemies:  # Still alive to show number
                        self.damage_numbers.spawn(damage, enemy.cart_x, enemy.cart_y)

                # Lightning sound and shake
                self.sound.play('impact', volume=0.7)
                if self.camera:
                    self.camera.shake(intensity=8.0, duration=0.2)

        # ===== HYBRID/MULTI-BEHAVIOR COMPOSITION =====
        # Apply secondary behaviors from modifiers
        self._apply_modifiers(behavior, modifiers, weights, player_x, player_y, target_x, target_y, spell_data, owner, color, area, duration)

    def _apply_modifiers(self, primary, modifiers, weights, player_x, player_y, target_x, target_y, spell_data, owner, color, area, duration):
        """
        Apply secondary behavior effects from multi-label classification.

        This enables COMPOSED BEHAVIORS like:
        - Chain + Heal = Chain Heal (chain lightning that heals allies)
        - Projectile + AOE = Exploding Projectile
        - Beam + Heal = Healing Beam
        - etc.
        """
        if not modifiers:
            return  # No secondary behaviors

        import math

        for modifier in modifiers:
            modifier_weight = weights.get(modifier, 0.0)

            if modifier_weight < 0.2:
                # Skip weak modifiers (less than 20% activation)
                continue

            logging.info(f"  Applying modifier: {modifier} (weight: {modifier_weight:.2f})")

            # ===== CHAIN MODIFIER =====
            if modifier == 'chain' and primary != 'chain':
                # Add chaining to primary effect
                # Example: HEAL + CHAIN = Chain Heal
                if primary == 'heal':
                    self._spawn_chain_heal(player_x, player_y, spell_data, owner)

            # ===== HEAL MODIFIER =====
            elif modifier == 'heal' and primary != 'heal':
                # Add healing to primary effect
                # Example: CHAIN + HEAL = Chain Heal, PROJECTILE + HEAL = Healing Projectile
                heal_amount = spell_data.get('damage', 50) * modifier_weight
                if owner == 'player' and self.player:
                    self.player.health.heal(int(heal_amount))
                    logging.info(f"  Hybrid: Healed {int(heal_amount)} HP from {modifier}")
                    if self.damage_numbers:
                        self.damage_numbers.spawn(int(heal_amount), player_x, player_y, is_heal=True)

            # ===== AOE MODIFIER =====
            elif modifier == 'aoe' and primary not in ['aoe', 'area_denial']:
                # Add AOE explosion to non-AOE effects
                # Example: PROJECTILE + AOE = Exploding Projectile (handled on impact)
                # For now, just add particle burst
                emitter = ParticleEmitter(
                    target_x, target_y,
                    'explosion',
                    color,
                    duration=0.3,
                    area=area * modifier_weight
                )
                self.emitters.append(emitter)

            # ===== SHIELD MODIFIER =====
            elif modifier == 'shield' and primary != 'shield':
                # Add shield to any spell
                # Example: PROJECTILE + SHIELD = projectile grants shield on cast
                shield_hp = spell_data.get('damage', 50) * modifier_weight
                if owner == 'player' and self.player:
                    self.player.apply_shield(int(shield_hp), duration * modifier_weight)
                    logging.info(f"  Hybrid: Applied {int(shield_hp)} HP shield")

    def _spawn_chain_heal(self, player_x, player_y, spell_data, owner):
        """
        Spawn chain heal effect: heals caster + nearby allies.
        Like chain lightning but for healing.
        """
        heal_amount = spell_data.get('damage', 50)

        # Heal primary target (caster)
        if owner == 'player' and self.player:
            self.player.health.heal(heal_amount)
            logging.info(f"Chain Heal: Healed player for {heal_amount} HP")
            if self.damage_numbers:
                self.damage_numbers.spawn(heal_amount, player_x, player_y, is_heal=True)

            # TODO: Chain to nearby allies (would need ally system)
            # For now, just heal caster with nice visual

            # Healing particles
            emitter = ParticleEmitter(
                player_x, player_y,
                'buff',
                (100, 255, 100),  # Green healing color
                duration=1.0,
                area=2.0
            )
            self.emitters.append(emitter)

    def update(self, dt):
        """Update all effects and check collisions"""
        import math

        # Update projectiles and check hits
        for proj in self.projectiles[:]:
            proj.update(dt)

            if proj.alive:
                # Player projectiles hit enemies
                if proj.owner == 'player':
                    hit_enemy = CollisionChecker.projectile_vs_entities(
                        proj,
                        [e for e in self.enemies if e.health.is_alive],
                        entity_radius=0.5
                    )

                    if hit_enemy:
                        # Deal damage with terrain bonus
                        base_damage = proj.spell_data.get('damage', 10)
                        damage = base_damage

                        # Apply terrain damage bonus if available
                        if self.terrain and 'elements' in proj.spell_data:
                            elements = proj.spell_data.get('elements', [])
                            bonus = self.terrain.get_damage_bonus_at(hit_enemy.cart_x, hit_enemy.cart_y, elements)
                            damage = int(base_damage * bonus)
                            if bonus > 1.0:
                                logging.info(f"Terrain bonus: {bonus}x damage!")

                        hit_enemy.health.damage(damage)
                        logging.info(f"Projectile hit enemy! Dealt {damage} damage")

                        # Spawn floating damage number
                        self.damage_numbers.spawn(damage, hit_enemy.cart_x, hit_enemy.cart_y)

                        # Screen shake on impact
                        if self.camera:
                            shake_intensity = min(5.0 + (damage * 0.3), 15.0)
                            self.camera.shake(intensity=shake_intensity, duration=0.15)

                        # Impact sound
                        self.sound.play('impact', volume=0.6)

                        # Apply knockback
                        knockback_force = 3.0 + (damage * 0.05)
                        dx = hit_enemy.cart_x - proj.cart_x
                        dy = hit_enemy.cart_y - proj.cart_y
                        distance = math.sqrt(dx**2 + dy**2)
                        if distance > 0.01:
                            dir_x = dx / distance
                            dir_y = dy / distance
                            hit_enemy.apply_knockback(dir_x, dir_y, knockback_force)

                        # Kill projectile
                        proj.alive = False

                # Bot projectiles hit player and other enemies (except caster)
                elif proj.owner == 'bot':
                    hit_entity = None

                    # Check player
                    if self.player and self.player.health.is_alive:
                        dx = self.player.cart_x - proj.cart_x
                        dy = self.player.cart_y - proj.cart_y
                        distance = math.sqrt(dx**2 + dy**2)
                        if distance <= getattr(self.player, 'collision_radius', 0.5):
                            hit_entity = self.player

                    # Check other enemies (exclude caster via origin proximity)
                    if not hit_entity:
                        for enemy in self.enemies:
                            if not enemy.health.is_alive:
                                continue
                            # Skip if enemy is at projectile origin (the caster)
                            origin_dx = enemy.cart_x - proj.origin_x
                            origin_dy = enemy.cart_y - proj.origin_y
                            if math.sqrt(origin_dx**2 + origin_dy**2) < 1.5:
                                continue
                            dx = enemy.cart_x - proj.cart_x
                            dy = enemy.cart_y - proj.cart_y
                            distance = math.sqrt(dx**2 + dy**2)
                            if distance <= getattr(enemy, 'collision_radius', 0.5):
                                hit_entity = enemy
                                break

                    if hit_entity:
                        damage = proj.spell_data.get('damage', 10)
                        hit_entity.health.damage(damage)

                        target_name = 'player' if hit_entity == self.player else 'enemy'
                        logging.info(f"Bot projectile hit {target_name}! Dealt {damage} damage")

                        self.damage_numbers.spawn(damage, hit_entity.cart_x, hit_entity.cart_y)

                        if self.camera:
                            shake_intensity = min(5.0 + (damage * 0.3), 15.0)
                            self.camera.shake(intensity=shake_intensity, duration=0.15)

                        self.sound.play('impact', volume=0.6)

                        if hasattr(hit_entity, 'apply_knockback'):
                            knockback_force = 3.0 + (damage * 0.05)
                            dx = hit_entity.cart_x - proj.cart_x
                            dy = hit_entity.cart_y - proj.cart_y
                            distance = math.sqrt(dx**2 + dy**2)
                            if distance > 0.01:
                                hit_entity.apply_knockback(
                                    dx / distance, dy / distance, knockback_force
                                )

                        proj.alive = False

            # Check if projectile split and spawn children
            if proj.behavior == 'split' and proj.has_split and len(proj.child_projectiles) > 0:
                # Add child projectiles to the list
                for child in proj.child_projectiles:
                    self.projectiles.append(child)
                    logging.info(f"Split projectile spawned child at ({child.cart_x:.1f}, {child.cart_y:.1f})")

                # Spawn split particle effect
                split_effect = ParticleEmitter(
                    proj.cart_x, proj.cart_y,
                    'explosion',
                    proj.color,
                    duration=0.3,
                    area=proj.area * 0.5  # Smaller split effect
                )
                self.emitters.append(split_effect)

                # Clear children list after spawning
                proj.child_projectiles.clear()

            if not proj.alive:
                # Spawn explosion on impact for projectiles
                if proj.behavior == 'projectile' or proj.behavior == 'homing' or proj.behavior == 'split':
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

        # Update expanding AOEs
        for aoe in self.expanding_aoes[:]:
            aoe.update(dt, self.enemies, self.player, self.terrain, self.damage_numbers, self.sound)
            if not aoe.alive:
                self.expanding_aoes.remove(aoe)

        # Update chain lightning effects
        for chain in self.chain_lightnings[:]:
            chain.update(dt)
            if not chain.alive:
                self.chain_lightnings.remove(chain)

        # Update damage numbers
        self.damage_numbers.update(dt)

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw all effects"""
        # Draw chain lightning (render first, under everything)
        for chain in self.chain_lightnings:
            chain.draw(screen, self.camera)

        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(screen, camera_offset_x, camera_offset_y)

        # Draw expanding AOEs
        for aoe in self.expanding_aoes:
            aoe.draw(screen, camera_offset_x, camera_offset_y)

        # Draw particles
        for emitter in self.emitters:
            emitter.draw(screen, camera_offset_x, camera_offset_y)

        # Draw damage numbers (on top of everything)
        self.damage_numbers.draw(screen, camera_offset_x, camera_offset_y)

    def clear_all(self):
        """Clear all active effects"""
        self.projectiles.clear()
        self.emitters.clear()
        self.expanding_aoes.clear()
        self.damage_numbers.clear_all()
