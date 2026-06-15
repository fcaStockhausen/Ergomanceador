"""Utility-based AI controller for enemy bots.

Replaces the simple 3-state FSM (wander/attack/flee) with a utility
evaluation engine inspired by vida_misma's agent architecture.

Each tick the bot evaluates all candidate actions, scores them with
per-action utility functions modulated by personality facets, and
selects one via Boltzmann (softmax) selection to produce behavioral
variety.
"""

import math
import random
import logging
from config.settings import GRID_SIZE, BASE_MOVEMENT_SPEED


class BotPersonality:
    """Immutable personality facets that differentiate bot behavior.

    Each facet is in [0, 1]. These modulate utility scores so that
    two bots facing the same situation make different choices.
    """

    def __init__(self, aggression=0.5, caution=0.5, cunning=0.5, mobility=0.5):
        self.aggression = aggression
        self.caution = caution
        self.cunning = cunning
        self.mobility = mobility

    @staticmethod
    def random():
        return BotPersonality(
            aggression=random.uniform(0.2, 0.9),
            caution=random.uniform(0.1, 0.8),
            cunning=random.uniform(0.1, 0.8),
            mobility=random.uniform(0.2, 0.9),
        )

    def __repr__(self):
        return (f"BotPersonality(aggr={self.aggression:.2f}, "
                f"caut={self.caution:.2f}, cunn={self.cunning:.2f}, "
                f"mobi={self.mobility:.2f})")


class BotController:
    """Utility-based AI controller for enemy bots."""

    ACTIONS = ['attack', 'pursue', 'kite', 'dodge', 'flee', 'retreat', 'wander']

    def __init__(self, enemy, magic_system, effect_manager=None, personality=None):
        self.enemy = enemy
        self.magic_system = magic_system
        self.effect_manager = effect_manager
        self.personality = personality or BotPersonality.random()

        self.target = None
        self.target_distance = 0.0
        self.target_dx = 0.0
        self.target_dy = 0.0

        self.cast_cooldown = 3.0
        self.cast_timer = random.uniform(0.5, 2.5)

        self.dodge_timer = 0.0
        self.dodge_cooldown = 2.0
        self.dodge_direction = (0, 0)

        self.flee_destination = None
        self.flee_timer = 0.0
        self.max_flee_duration = 4.0

        self.wander_direction = (0, 0)
        self.wander_timer = 0.0
        self.wander_duration = 0.0

        self.current_action = 'wander'
        self.boltzmann_tau = 0.35
        self.current_dt = 0.016

        self.action_lock = 0.0          # Minimum seconds before re-evaluating
        self.action_lock_duration = 0.4 # Prevents behavior thrashing

        logging.info(f"Bot spawned with {self.personality}")

    def update(self, dt, targets):
        """Main update loop — evaluate utilities and execute best action."""
        self.current_dt = dt
        self.cast_timer = max(0, self.cast_timer - dt)
        self.dodge_timer = max(0, self.dodge_timer - dt)

        if not isinstance(targets, list):
            targets = [targets]

        self._find_nearest_target(targets)

        if not self.target:
            self._execute_wander(dt)
            return

        incoming_threat = self._detect_incoming_projectiles()

        # Re-evaluate action only if action lock expired, unless there's
        # an imminent threat (dodge overrides lock)
        if self.action_lock > 0 and incoming_threat < 0.5:
            action = self.current_action
        else:
            utilities = self._compute_utilities(incoming_threat)
            action = self._boltzmann_select(utilities)
            if action != self.current_action:
                self.action_lock = self.action_lock_duration

        self.action_lock = max(0, self.action_lock - dt)
        self.current_action = action

        if action == 'attack':
            self._execute_attack()
        elif action == 'pursue':
            self._execute_pursue()
        elif action == 'kite':
            self._execute_kite()
        elif action == 'dodge':
            self._execute_dodge()
        elif action == 'flee':
            self._execute_flee(dt)
        elif action == 'retreat':
            self._execute_retreat()
        else:
            self._execute_wander(dt)

    # ================================================================
    # Utility Computation
    # ================================================================

    def _compute_utilities(self, incoming_threat):
        """Score every candidate action. Returns {action: score}."""
        hp_pct = self.enemy.health.current_health / self.enemy.health.max_health
        dist = self.target_distance

        hp_urgency = hp_pct ** 2.0
        threat_urgency = min(1.0, incoming_threat) ** 1.5

        p = self.personality

        cast_ready = 1.0 if self.cast_timer <= 0 else 0.0
        too_far = max(0.0, (dist - 12.0) / 15.0)
        too_close = max(0.0, (6.0 - dist) / 6.0)
        flee_trigger = max(0.0, (0.3 - hp_pct) / 0.3) ** 2
        retreat_trigger = max(0.0, (0.5 - hp_pct) / 0.5)

        return {
            'attack': (
                cast_ready * (0.4 + 0.6 * p.aggression)
                * (1.0 - 0.5 * threat_urgency)
                * (0.3 + 0.7 * hp_urgency)
            ),
            'pursue': (
                too_far * (0.5 + 0.5 * p.aggression) * p.mobility
                * (0.3 + 0.7 * hp_urgency)
            ),
            'kite': (
                (too_close * 0.6 + 0.4 * p.mobility)
                * (0.4 + 0.6 * p.caution)
            ),
            'dodge': (
                threat_urgency * (0.5 + 0.5 * p.mobility)
                * (0.3 + 0.7 * p.caution)
                * (1.0 if self.dodge_timer <= 0 else 0.0)
            ),
            'flee': (
                flee_trigger * (0.5 + 0.5 * p.caution)
                * (0.5 + 0.5 * p.mobility)
            ),
            'retreat': (
                retreat_trigger * p.caution * 0.6
                * (1.0 - p.aggression * 0.5)
            ),
            'wander': 0.05,
        }

    def _boltzmann_select(self, utilities):
        """Softmax selection over utilities for behavioral variety."""
        tau = self.boltzmann_tau
        max_u = max(utilities.values())
        exp_values = {a: math.exp((u - max_u) / tau) for a, u in utilities.items()}
        total = sum(exp_values.values())

        r = random.uniform(0, total)
        cumulative = 0.0
        for action, exp_u in exp_values.items():
            cumulative += exp_u
            if r <= cumulative:
                return action

        return max(utilities.items(), key=lambda x: x[1])[0]

    # ================================================================
    # Action Execution
    # ================================================================

    def _execute_attack(self):
        if self.cast_timer > 0:
            return

        elements = self._choose_spell_elements()
        self.magic_system.element_queue = []
        for elem in elements:
            self.magic_system.queue_element(elem)

        lead = 0.3 + 0.7 * self.personality.cunning
        mag = math.sqrt(self.target_dx ** 2 + self.target_dy ** 2)
        if mag > 0:
            tx = self.enemy.cart_x + (self.target_dx / mag) * (self.target_distance * lead)
            ty = self.enemy.cart_y + (self.target_dy / mag) * (self.target_distance * lead)
        else:
            tx = self.enemy.cart_x
            ty = self.enemy.cart_y

        spell_data = self.magic_system.cast_spell()
        if spell_data and self.effect_manager:
            self.effect_manager.spawn_spell_effect(
                self.enemy.cart_x, self.enemy.cart_y, tx, ty,
                spell_data, owner='bot'
            )

        self.cast_timer = self.cast_cooldown * (0.8 + 0.4 * (1.0 - self.personality.aggression))

    def _execute_pursue(self):
        mag = math.sqrt(self.target_dx ** 2 + self.target_dy ** 2)
        if mag > 0:
            spd = 0.8 + 0.4 * self.personality.mobility
            self._move_enemy(
                (self.target_dx / mag) * BASE_MOVEMENT_SPEED * spd * self.current_dt,
                (self.target_dy / mag) * BASE_MOVEMENT_SPEED * spd * self.current_dt,
            )

    def _execute_kite(self):
        mag = math.sqrt(self.target_dx ** 2 + self.target_dy ** 2)
        if mag > 0:
            back_x = -(self.target_dx / mag)
            back_y = -(self.target_dy / mag)
            strafe_x = -back_y
            strafe_y = back_x
            sign = 1 if random.random() < 0.5 else -1
            self._move_enemy(
                (back_x * 0.3 + strafe_x * 0.7 * sign) * BASE_MOVEMENT_SPEED * 0.9 * self.current_dt,
                (back_y * 0.3 + strafe_y * 0.7 * sign) * BASE_MOVEMENT_SPEED * 0.9 * self.current_dt,
            )

    def _execute_dodge(self):
        if self.dodge_timer > 0:
            return
        dx, dy = self.dodge_direction
        mag = math.sqrt(dx * dx + dy * dy)
        if mag > 0:
            perp_x = -dy / mag
            perp_y = dx / mag
            sign = 1 if random.random() < 0.5 else -1
            self._move_enemy(
                perp_x * sign * BASE_MOVEMENT_SPEED * 2.0 * self.current_dt,
                perp_y * sign * BASE_MOVEMENT_SPEED * 2.0 * self.current_dt,
            )
        self.dodge_timer = self.dodge_cooldown

    def _execute_flee(self, dt):
        self.flee_timer += dt

        if self.flee_destination is None:
            mag = math.sqrt(self.target_dx ** 2 + self.target_dy ** 2)
            if mag > 0:
                self.flee_destination = (
                    max(0, min(GRID_SIZE, self.enemy.cart_x - (self.target_dx / mag) * 20.0)),
                    max(0, min(GRID_SIZE, self.enemy.cart_y - (self.target_dy / mag) * 20.0)),
                )

        if self.flee_destination:
            ddx = self.flee_destination[0] - self.enemy.cart_x
            ddy = self.flee_destination[1] - self.enemy.cart_y
            ddist = math.sqrt(ddx ** 2 + ddy ** 2)

            if ddist < 2.0 or self.flee_timer >= self.max_flee_duration:
                self.flee_destination = None
                self.flee_timer = 0.0
                return

            if ddist > 0:
                self._move_enemy(
                    (ddx / ddist) * BASE_MOVEMENT_SPEED * 1.5 * self.current_dt,
                    (ddy / ddist) * BASE_MOVEMENT_SPEED * 1.5 * self.current_dt,
                )

    def _execute_retreat(self):
        corners = [(2, 2), (2, GRID_SIZE - 2), (GRID_SIZE - 2, 2), (GRID_SIZE - 2, GRID_SIZE - 2)]
        nearest = min(corners, key=lambda c: (c[0] - self.enemy.cart_x) ** 2 + (c[1] - self.enemy.cart_y) ** 2)
        dx = nearest[0] - self.enemy.cart_x
        dy = nearest[1] - self.enemy.cart_y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist > 1.0:
            self._move_enemy(
                (dx / dist) * BASE_MOVEMENT_SPEED * 0.8 * self.current_dt,
                (dy / dist) * BASE_MOVEMENT_SPEED * 0.8 * self.current_dt,
            )

    def _execute_wander(self, dt):
        self.current_action = 'wander'
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            self.wander_direction = (math.cos(angle), math.sin(angle))
            self.wander_timer = random.uniform(1.5, 3.5)
        self._move_enemy(
            self.wander_direction[0] * BASE_MOVEMENT_SPEED * 0.4 * self.current_dt,
            self.wander_direction[1] * BASE_MOVEMENT_SPEED * 0.4 * self.current_dt,
        )

    # ================================================================
    # Spell Selection
    # ================================================================

    def _choose_spell_elements(self):
        """Choose elements strategically based on situation."""
        hp_pct = self.enemy.health.current_health / self.enemy.health.max_health
        dist = self.target_distance
        p = self.personality

        if hp_pct < 0.35 and random.random() < p.caution:
            if random.random() < 0.5:
                return ['nature', 'nature']
            return ['earth', 'earth']

        if dist < 6.0 and random.random() < p.aggression:
            return ['fire', 'fire', 'fire']

        if dist > 10.0 and random.random() < p.cunning:
            return ['arcane', 'arcane']

        if random.random() < p.cunning * 0.4:
            return ['fire', 'light']

        offensive = ['fire', 'shadow', 'arcane']
        num = random.randint(1, min(3, max(1, int(p.aggression * 3) + 1)))
        return [random.choice(offensive) for _ in range(num)]

    # ================================================================
    # Perception
    # ================================================================

    def _find_nearest_target(self, targets):
        closest = None
        min_dist = float('inf')

        for target in targets:
            if target == self.enemy:
                continue
            if hasattr(target, 'health') and not target.health.is_alive:
                continue
            if not hasattr(target, 'cart_x'):
                continue

            dx = target.cart_x - self.enemy.cart_x
            dy = target.cart_y - self.enemy.cart_y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist < min_dist:
                min_dist = dist
                closest = target

        self.target = closest
        if closest:
            self.target_dx = closest.cart_x - self.enemy.cart_x
            self.target_dy = closest.cart_y - self.enemy.cart_y
            self.target_distance = min_dist
        else:
            self.target_distance = float('inf')

    def _detect_incoming_projectiles(self):
        """Scan projectiles for threats approaching this bot.

        Returns threat score [0, 1]. Also sets dodge_direction.
        """
        if not self.effect_manager or not hasattr(self.effect_manager, 'projectiles'):
            return 0.0

        max_threat = 0.0

        for proj in self.effect_manager.projectiles:
            if proj.owner == 'bot':
                continue

            dx = self.enemy.cart_x - proj.cart_x
            dy = self.enemy.cart_y - proj.cart_y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > 8.0:
                continue

            if hasattr(proj, 'vel_x') and hasattr(proj, 'vel_y'):
                proj_speed = math.sqrt(proj.vel_x ** 2 + proj.vel_y ** 2)
                if proj_speed > 0:
                    to_bot_x = dx / dist if dist > 0 else 0
                    to_bot_y = dy / dist if dist > 0 else 0
                    dot = (proj.vel_x / proj_speed) * to_bot_x + \
                          (proj.vel_y / proj_speed) * to_bot_y

                    if dot > 0.3:
                        closeness = 1.0 - min(1.0, dist / 8.0)
                        threat = closeness * dot
                        if threat > max_threat:
                            max_threat = threat
                            self.dodge_direction = (proj.vel_x, proj.vel_y)

        return max_threat

    # ================================================================
    # Helpers
    # ================================================================

    def _move_enemy(self, dx, dy):
        self.enemy.cart_x = max(0, min(GRID_SIZE, self.enemy.cart_x + dx))
        self.enemy.cart_y = max(0, min(GRID_SIZE, self.enemy.cart_y + dy))

        if dx != 0 or dy != 0:
            mag = math.sqrt(dx ** 2 + dy ** 2)
            if mag > 0:
                self.enemy.facing_direction = (dx / mag, dy / mag)
