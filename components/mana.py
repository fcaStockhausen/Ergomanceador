"""Mana component for spell casting resource management"""

import logging


class Mana:
    """
    Mana component for managing spell casting resources.
    Regenerates over time, consumed by spells.
    """

    def __init__(self, max_mana=100, regen_rate=10.0):
        """
        Create mana component.

        Args:
            max_mana: Maximum mana capacity
            regen_rate: Mana regenerated per second
        """
        self.max_mana = max_mana
        self.current_mana = max_mana
        self.regen_rate = regen_rate  # Mana per second

        # Bonus from terrain (multiplier)
        self.terrain_bonus = 1.0

    def consume(self, amount):
        """
        Consume mana for spell casting.

        Args:
            amount: Mana cost

        Returns:
            True if mana was consumed, False if insufficient mana
        """
        if self.current_mana >= amount:
            self.current_mana -= amount
            logging.info(f"Mana consumed: -{amount} (remaining: {self.current_mana:.1f}/{self.max_mana})")
            return True
        else:
            logging.info(f"Insufficient mana! Need {amount}, have {self.current_mana:.1f}")
            return False

    def regenerate(self, dt):
        """
        Regenerate mana over time.

        Args:
            dt: Delta time in seconds
        """
        if self.current_mana < self.max_mana:
            regen_amount = self.regen_rate * dt * self.terrain_bonus
            old_mana = self.current_mana
            self.current_mana = min(self.max_mana, self.current_mana + regen_amount)

            # Log only when we gain significant mana (avoid spam)
            if int(self.current_mana) > int(old_mana):
                logging.debug(f"Mana regen: {self.current_mana:.1f}/{self.max_mana}")

    def restore(self, amount):
        """
        Restore mana (healing, potions, etc).

        Args:
            amount: Mana to restore
        """
        old_mana = self.current_mana
        self.current_mana = min(self.max_mana, self.current_mana + amount)
        actual_restore = self.current_mana - old_mana
        if actual_restore > 0:
            logging.info(f"Mana restored: +{actual_restore:.1f} (current: {self.current_mana:.1f}/{self.max_mana})")

    def get_mana_percentage(self):
        """Get mana as percentage (0.0 to 1.0)"""
        if self.max_mana == 0:
            return 0.0
        return self.current_mana / self.max_mana

    def update(self, dt):
        """Update component state (call each frame)"""
        self.regenerate(dt)

    def set_terrain_bonus(self, bonus):
        """Set terrain regen bonus (1.0 = normal, 2.0 = 2x regen, etc)"""
        self.terrain_bonus = bonus
        logging.info(f"Terrain mana bonus: {bonus}x")
