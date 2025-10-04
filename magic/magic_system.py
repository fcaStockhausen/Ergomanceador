"""Magic system - player-facing API for spell casting"""

import logging
from magic.interaction_engine import InteractionEngine


class MagicSystem:
    """
    Player-facing magic system with element queueing (Magicka-style).
    Elements are queued in order, then cast together for emergent spells.
    """

    def __init__(self):
        self.engine = InteractionEngine()

        # All available elements (9 total)
        self.all_elements = ['fire', 'lightning', 'water', 'ice', 'earth', 'nature', 'arcane', 'light', 'shadow']

        # Unlocked elements (all 9 elements unlocked for testing)
        # TODO Phase 5: Implement progression system to unlock gradually
        self.unlocked_elements = ['fire', 'water', 'ice', 'earth', 'nature', 'arcane', 'light', 'shadow', 'lightning']

        # Element queue (ordered list, max 4 elements like Magicka)
        self.element_queue = []
        self.max_queue_size = 4

    def queue_element(self, element):
        """
        Add element to queue (Magicka-style).
        Returns True if added successfully, False if queue full.
        """
        if element not in self.unlocked_elements:
            return False

        if len(self.element_queue) < self.max_queue_size:
            self.element_queue.append(element)
            logging.info(f"Element {element.upper()} queued: {self.element_queue}")
            return True
        else:
            logging.info(f"Queue full ({self.max_queue_size} elements), cannot add {element.upper()}")
        return False

    def remove_last_element(self):
        """Remove last queued element (backspace functionality)"""
        if self.element_queue:
            removed = self.element_queue.pop()
            logging.info(f"Removed {removed.upper()} from queue: {self.element_queue}")

    def clear_queue(self):
        """Clear all queued elements"""
        self.element_queue = []

    def cast_spell(self):
        """
        Cast queued spell and clear queue.
        Returns spell effect data or None.
        """
        if not self.element_queue:
            logging.info("Cannot cast: queue is empty")
            return None

        effect = self.engine.compute_interaction(self.element_queue)
        logging.info(f"AIMED CAST: {effect['name']}")
        logging.info(f"  Behavior: {effect['behavior']}")
        logging.info(f"  Damage: {effect['damage']}, Area: {effect['area']}, Duration: {effect['duration']}s")

        self.element_queue = []  # Clear queue after casting
        return effect

    def preview_spell(self):
        """
        Real-time spell preview (doesn't clear queue).
        Returns spell effect data or None.
        """
        if not self.element_queue:
            return None
        return self.engine.compute_interaction(self.element_queue)

    # LEGACY METHODS (for backward compatibility with current controls)
    # TODO: Remove these once Phase 3 input system is implemented

    @property
    def active_elements(self):
        """Legacy property - maps to element_queue"""
        return self.element_queue

    @property
    def elements(self):
        """Legacy property - maps to unlocked_elements"""
        return self.unlocked_elements

    def toggle_element(self, element):
        """
        Legacy method - toggle element in queue.
        For backward compatibility with current Q/E/U/O controls.
        """
        if element in self.element_queue:
            self.element_queue.remove(element)
        else:
            self.queue_element(element)

    def get_combined_effect(self):
        """Legacy method - return spell name"""
        effect = self.preview_spell()
        if effect:
            return effect['name']
        return None

    def get_full_effect(self):
        """Legacy method - return complete effect data"""
        return self.preview_spell()
