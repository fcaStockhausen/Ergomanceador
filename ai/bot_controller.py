"""Simple AI controller for enemy bots"""

import math
import random
from config.settings import GRID_SIZE, BASE_MOVEMENT_SPEED


class BotController:
    """Controls AI behavior for enemy bots"""

    def __init__(self, enemy, magic_system, effect_manager=None):
        self.enemy = enemy
        self.magic_system = magic_system
        self.effect_manager = effect_manager  # For spawning projectiles

        # AI state
        self.target = None  # Player to target
        self.behavior_timer = 0
        self.current_behavior = 'idle'
        self.previous_behavior = 'idle'

        # AI parameters
        self.aggro_range = 30.0  # Start attacking when target within this range (increased for more action)
        self.flee_health = 50  # Flee when health below this
        self.cast_cooldown = 3.5  # Seconds between spell casts (slower to reduce spam)
        self.cast_timer = random.uniform(0, 2.0)  # Random initial offset to stagger attacks

        # Movement AI
        self.move_timer = 0
        self.move_duration = 0
        self.move_direction = (0, 0)
        self.previous_direction = (0, 0)
        self.current_dt = 0.016  # Store dt for movement calculations

        # Flee behavior improvements
        self.flee_destination = None
        self.flee_timer = 0
        self.max_flee_duration = 5.0

        # Movement smoothing
        self.behavior_change_cooldown = 0.0

        # Debug tracing
        self.trace_timer = 0
        self.trace_interval = 0.5  # Log position every 0.5 seconds

    def update(self, dt, targets):
        """Update AI behavior - targets can be player or list of all entities"""
        self.current_dt = dt  # Store for movement calculations
        self.behavior_timer += dt
        self.cast_timer = max(0, self.cast_timer - dt)
        self.behavior_change_cooldown = max(0, self.behavior_change_cooldown - dt)

        # Debug trace bot position
        self.trace_timer += dt
        if self.trace_timer >= self.trace_interval:
            print(f"🤖 BOT @ ({self.enemy.cart_x:.1f}, {self.enemy.cart_y:.1f}) "
                  f"HP:{self.enemy.health.current_health}/{self.enemy.health.max_health} "
                  f"Behavior:{self.current_behavior}")
            self.trace_timer = 0

        # Find nearest target (player or other bots)
        if not isinstance(targets, list):
            targets = [targets]

        # Find closest target (excluding self)
        closest_target = None
        min_distance = float('inf')

        for target in targets:
            # Skip if target is self or dead
            if hasattr(target, 'cart_x'):
                if target == self.enemy:
                    continue
                if hasattr(target, 'health') and not target.health.is_alive:
                    continue

                dx = target.cart_x - self.enemy.cart_x
                dy = target.cart_y - self.enemy.cart_y
                distance = math.sqrt(dx**2 + dy**2)

                if distance < min_distance:
                    min_distance = distance
                    closest_target = target

        if not closest_target:
            self._wander_behavior(dt)
            return

        self.target = closest_target
        dx = closest_target.cart_x - self.enemy.cart_x
        dy = closest_target.cart_y - self.enemy.cart_y
        distance = min_distance

        # Choose behavior based on state (with cooldown to prevent rapid switching)
        new_behavior = None

        if self.enemy.health.current_health < self.flee_health and self.flee_timer < self.max_flee_duration:
            new_behavior = 'flee'
        elif distance < self.aggro_range:
            new_behavior = 'attack'
            # Reset flee state if we're attacking (health recovered)
            if self.flee_destination is not None:
                self.flee_destination = None
                self.flee_timer = 0
        else:
            new_behavior = 'wander'
            # Reset flee state if wandering
            if self.flee_destination is not None:
                self.flee_destination = None
                self.flee_timer = 0

        # Apply behavior change cooldown
        if new_behavior != self.current_behavior and self.behavior_change_cooldown > 0:
            # Keep current behavior during cooldown
            new_behavior = self.current_behavior

        # Execute behavior
        if new_behavior == 'flee':
            self._flee_behavior(dx, dy, distance, dt)
        elif new_behavior == 'attack':
            self._attack_behavior(dx, dy, distance, dt)
        else:
            self._wander_behavior(dt)

        # Track behavior changes
        if new_behavior != self.current_behavior:
            self.previous_behavior = self.current_behavior
            self.current_behavior = new_behavior
            self.behavior_change_cooldown = 0.5  # 0.5s cooldown between switches
            print(f"   🔄 Behavior change: {self.previous_behavior} -> {self.current_behavior}")

    def _attack_behavior(self, dx, dy, distance, dt):
        """Attack the target"""
        # Move toward target (but keep some distance)
        preferred_distance = 8.0  # Stay at medium range
        dead_zone = 3.0  # Larger dead zone to prevent jitter

        if distance > preferred_distance + dead_zone:
            # Too far - move closer
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                move_x = (dx / magnitude) * BASE_MOVEMENT_SPEED * self.current_dt
                move_y = (dy / magnitude) * BASE_MOVEMENT_SPEED * self.current_dt
                self._move_enemy(move_x, move_y)
        elif distance < preferred_distance - dead_zone:
            # Too close - back away
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                move_x = -(dx / magnitude) * BASE_MOVEMENT_SPEED * self.current_dt
                move_y = -(dy / magnitude) * BASE_MOVEMENT_SPEED * self.current_dt
                self._move_enemy(move_x, move_y)
        # else: in dead zone, don't move (prevents oscillation)

        # Cast spell at target if cooldown ready
        if self.cast_timer <= 0:
            self._cast_spell_at_target(dx, dy)
            self.cast_timer = self.cast_cooldown

    def _flee_behavior(self, dx, dy, distance, dt):
        """Flee from player when low health"""
        self.flee_timer += dt

        # Pick flee destination if we don't have one
        if self.flee_destination is None:
            # Run in opposite direction from threat for a fixed distance
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                flee_distance = 20.0  # Flee 20 units away
                flee_dir_x = -(dx / magnitude)
                flee_dir_y = -(dy / magnitude)

                # Calculate destination (clamped to grid bounds)
                dest_x = self.enemy.cart_x + flee_dir_x * flee_distance
                dest_y = self.enemy.cart_y + flee_dir_y * flee_distance
                dest_x = max(0, min(GRID_SIZE, dest_x))
                dest_y = max(0, min(GRID_SIZE, dest_y))

                self.flee_destination = (dest_x, dest_y)
                print(f"   🏃 FLEE DESTINATION SET: ({dest_x:.1f}, {dest_y:.1f})")

        # Move toward flee destination
        if self.flee_destination:
            dest_dx = self.flee_destination[0] - self.enemy.cart_x
            dest_dy = self.flee_destination[1] - self.enemy.cart_y
            dest_distance = math.sqrt(dest_dx**2 + dest_dy**2)

            # Reached destination or flee timeout - stop fleeing
            if dest_distance < 2.0 or self.flee_timer >= self.max_flee_duration:
                print(f"   ✋ FLEE COMPLETE (distance: {dest_distance:.1f}, timer: {self.flee_timer:.1f}s)")
                self.flee_destination = None
                self.flee_timer = 0
                return

            # Move toward destination
            magnitude = dest_distance
            if magnitude > 0:
                move_x = (dest_dx / magnitude) * BASE_MOVEMENT_SPEED * 1.5 * self.current_dt  # 1.5x speed when fleeing
                move_y = (dest_dy / magnitude) * BASE_MOVEMENT_SPEED * 1.5 * self.current_dt
                self._move_enemy(move_x, move_y)

    def _wander_behavior(self, dt):
        """Wander randomly when no target"""
        self.current_behavior = 'wander'

        # Update wander timer
        self.move_timer -= dt

        if self.move_timer <= 0:
            # Pick new random direction
            if random.random() < 0.1:
                # 10% chance to stop and idle (reduced from 30%)
                self.move_direction = (0, 0)
                self.move_duration = random.uniform(2.0, 3.0)
            else:
                # 90% chance to move in random direction
                angle = random.uniform(0, 2 * math.pi)
                self.move_direction = (math.cos(angle), math.sin(angle))
                self.move_duration = random.uniform(2.0, 4.0)  # Longer duration for smoother movement

            self.move_timer = self.move_duration

        # Move in current direction
        move_x = self.move_direction[0] * BASE_MOVEMENT_SPEED * 0.5 * self.current_dt  # Slower wander
        move_y = self.move_direction[1] * BASE_MOVEMENT_SPEED * 0.5 * self.current_dt
        self._move_enemy(move_x, move_y)

    def _move_enemy(self, dx, dy):
        """Move enemy in cartesian space"""
        self.enemy.cart_x += dx
        self.enemy.cart_y += dy

        # Keep in bounds
        self.enemy.cart_x = max(0, min(GRID_SIZE, self.enemy.cart_x))
        self.enemy.cart_y = max(0, min(GRID_SIZE, self.enemy.cart_y))

        # Update facing direction
        if dx != 0 or dy != 0:
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                self.enemy.facing_direction = (dx / magnitude, dy / magnitude)

    def _cast_spell_at_target(self, dx, dy):
        """Cast a spell toward the target"""
        import logging

        # Simple AI: randomly queue 2-3 elements and cast
        num_elements = random.randint(2, 3)

        # Choose random elements from unlocked list
        elements = ['fire', 'water', 'earth', 'nature']  # Basic elements for bots

        # Clear queue and add random elements
        self.magic_system.element_queue = []
        for _ in range(num_elements):
            element = random.choice(elements)
            self.magic_system.queue_element(element)

        # Calculate target position (lead the player slightly)
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            target_x = self.enemy.cart_x + (dx / magnitude) * 10
            target_y = self.enemy.cart_y + (dy / magnitude) * 10
        else:
            target_x = self.enemy.cart_x
            target_y = self.enemy.cart_y

        # Cast spell (no args - just computes spell data)
        spell_data = self.magic_system.cast_spell()

        # Spawn projectile through effect manager if available
        if spell_data and self.effect_manager:
            self.effect_manager.spawn_spell_effect(
                self.enemy.cart_x,
                self.enemy.cart_y,
                target_x,
                target_y,
                spell_data,
                owner='bot'  # Mark as bot projectile
            )
            logging.info(f"Bot cast {spell_data['name']} at ({target_x:.1f}, {target_y:.1f})")
            return spell_data

        return None
