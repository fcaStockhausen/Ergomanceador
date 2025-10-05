"""
Shield component for damage absorption.

A shield absorbs damage until its HP pool is depleted.
Shield strength and duration are emergent from property vector.
"""

import logging


class Shield:
    """
    Shield component with damage absorption pool.

    Unlike BUFF (which enhances stats), SHIELD creates a temporary HP barrier
    that absorbs incoming damage until broken.
    """

    def __init__(self, shield_hp, duration):
        """
        Initialize shield with HP pool and duration.

        Args:
            shield_hp: Amount of damage the shield can absorb
            duration: How long the shield lasts (seconds)
        """
        self.max_shield_hp = shield_hp
        self.current_shield_hp = shield_hp
        self.duration = duration
        self.time_remaining = duration
        self.active = True

        logging.info(f"Shield created: {shield_hp} HP, {duration:.1f}s duration")

    def absorb_damage(self, damage):
        """
        Absorb incoming damage with the shield.

        Returns:
            absorbed: Amount of damage absorbed by shield
            overflow: Damage that exceeds shield (passes through to health)
        """
        if not self.active:
            return 0, damage  # Shield broken, all damage passes through

        absorbed = min(damage, self.current_shield_hp)
        overflow = damage - absorbed

        self.current_shield_hp -= absorbed

        if self.current_shield_hp <= 0:
            self.current_shield_hp = 0
            self.active = False
            logging.info("Shield broken!")

        return absorbed, overflow

    def update(self, dt):
        """Update shield timer"""
        if not self.active:
            return

        self.time_remaining -= dt

        if self.time_remaining <= 0:
            self.active = False
            logging.info("Shield expired!")

    def get_strength_ratio(self):
        """Get shield strength as ratio (0-1) for visual effects"""
        if not self.active:
            return 0.0
        return self.current_shield_hp / self.max_shield_hp

    def is_active(self):
        """Check if shield is still active"""
        return self.active and self.current_shield_hp > 0
