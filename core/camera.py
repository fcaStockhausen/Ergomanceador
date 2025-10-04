"""Camera system for following entities"""

import random
from rendering.isometric import cart_to_iso


class Camera:
    """Camera that follows an entity with screen shake support"""

    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0

        # Screen shake
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.shake_timer = 0.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

    def follow(self, entity):
        """Calculate camera offset to center entity on screen"""
        iso_x, iso_y = cart_to_iso(entity.cart_x, entity.cart_y)
        self.offset_x = -iso_x
        self.offset_y = -iso_y

    def shake(self, intensity=10.0, duration=0.2):
        """Trigger screen shake effect

        Args:
            intensity: Shake magnitude in pixels
            duration: How long to shake in seconds
        """
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = 0.0

    def update(self, dt):
        """Update camera shake"""
        if self.shake_timer < self.shake_duration:
            self.shake_timer += dt

            # Calculate decay (shake gets weaker over time)
            progress = self.shake_timer / self.shake_duration
            current_intensity = self.shake_intensity * (1.0 - progress)

            # Random offset
            self.shake_offset_x = random.uniform(-current_intensity, current_intensity)
            self.shake_offset_y = random.uniform(-current_intensity, current_intensity)
        else:
            # Shake finished
            self.shake_offset_x = 0
            self.shake_offset_y = 0

    def get_offset(self):
        """Return current camera offset (including shake)"""
        return (
            self.offset_x + self.shake_offset_x,
            self.offset_y + self.shake_offset_y
        )
