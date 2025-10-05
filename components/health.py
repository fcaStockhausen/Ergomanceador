"""Health component for entities that can take damage"""

import logging


class Health:
    """
    Health component with damage, healing, and death callbacks.
    Attach to any entity (enemy, player, destructible object).
    """

    def __init__(self, max_health, on_death=None, on_damage=None):
        """
        Create health component.

        Args:
            max_health: Maximum health points
            on_death: Callback function when health reaches 0
            on_damage: Callback function when damaged (receives damage amount)
        """
        self.max_health = max_health
        self.current_health = max_health
        self.is_alive = True
        self.on_death_callback = on_death
        self.on_damage_callback = on_damage

        # Visual feedback state
        self.damage_flash_timer = 0.0  # For red flash effect
        self.last_damage = 0  # Track last damage for number display

    def damage(self, amount):
        """
        Deal damage to entity.

        Args:
            amount: Damage points to inflict

        Returns:
            True if entity died, False otherwise
        """
        if not self.is_alive:
            return False

        self.current_health -= amount
        self.last_damage = amount
        self.damage_flash_timer = 0.15  # Flash for 150ms

        logging.info(f"Health damaged: -{amount} (remaining: {self.current_health}/{self.max_health})")

        # Trigger damage callback
        if self.on_damage_callback:
            self.on_damage_callback(amount)

        # Check death
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
            logging.info("Entity died!")

            # Trigger death callback
            if self.on_death_callback:
                self.on_death_callback()

            return True

        return False

    def heal(self, amount):
        """
        Heal entity.

        Args:
            amount: Health points to restore
        """
        if not self.is_alive:
            return

        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)

        actual_heal = self.current_health - old_health
        if actual_heal > 0:
            logging.info(f"Health healed: +{actual_heal} (current: {self.current_health}/{self.max_health})")

    def get_health_percentage(self):
        """Get health as percentage (0.0 to 1.0)"""
        if self.max_health == 0:
            return 0.0
        return self.current_health / self.max_health

    def update(self, dt):
        """Update component state (call each frame)"""
        # Decrease damage flash timer
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            if self.damage_flash_timer < 0:
                self.damage_flash_timer = 0

    def is_flashing(self):
        """Check if currently in damage flash state (for visual feedback)"""
        return self.damage_flash_timer > 0

    def respawn(self):
        """Respawn entity with full health"""
        self.current_health = self.max_health
        self.is_alive = True
        self.damage_flash_timer = 0.0
        self.last_damage = 0
        logging.info(f"Entity respawned with {self.max_health} health")
