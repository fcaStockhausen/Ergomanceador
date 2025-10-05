"""
Designer Mode: In-game toolkit for discovering and defining spell behaviors.

Provides a testing environment for:
1. Experimenting with element combinations (1-6 elements)
2. Visualizing position in 12D behavior manifold
3. Defining new behavior prototypes
4. Tuning existing prototypes
5. Following the designer workflow from DESIGNER_GUIDE_BEHAVIOR_TUNING.md
"""

import pygame
import logging
from typing import Optional
from magic.magic_system import MagicSystem
from magic.property_vector import PropertyVectorComputer
from magic.element_loader import load_elements_from_json
from designer.prototype_manager import PrototypeManager


class DesignerMode:
    """
    Main coordinator for designer mode.

    State machine:
    - INACTIVE: Normal game mode
    - TESTING: Element experimentation mode
    - EDITING: Prototype editor mode
    - VISUALIZING: Full-screen manifold visualization
    """

    # States
    STATE_INACTIVE = 'inactive'
    STATE_TESTING = 'testing'
    STATE_EDITING = 'editing'
    STATE_VISUALIZING = 'visualizing'

    def __init__(self, screen_width=1280, screen_height=720):
        self.state = self.STATE_INACTIVE
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Systems
        self.magic_system = MagicSystem()  # Dedicated magic system for testing
        self.prototype_manager = PrototypeManager()
        self.elements = load_elements_from_json()

        # UI Panels (will be created when entering designer mode)
        self.testing_panel = None
        self.prototype_editor = None
        self.manifold_visualizer = None

        # State
        self.current_spell_data = None
        self.current_distances = None
        self.selected_prototype = None

        logging.info("Designer Mode initialized (inactive)")

    def toggle_active(self):
        """Toggle designer mode on/off"""
        if self.state == self.STATE_INACTIVE:
            self.enter_designer_mode()
        else:
            self.exit_designer_mode()

    def enter_designer_mode(self):
        """Enter designer mode (pause game, show toolkit)"""
        self.state = self.STATE_TESTING
        self._init_ui_panels()
        logging.info("🎨 Designer Mode ACTIVATED")

    def exit_designer_mode(self):
        """Exit designer mode (return to game)"""
        self.state = self.STATE_INACTIVE
        # Save custom prototypes before exiting
        self.prototype_manager.save_custom_prototypes()
        logging.info("🎨 Designer Mode DEACTIVATED")

    def _init_ui_panels(self):
        """Initialize UI panels (lazy loading)"""
        from rendering.ui.testing_panel import TestingPanel
        from rendering.ui.prototype_editor import PrototypeEditor
        from magic.behavior_space_visualizer import BehaviorSpaceVisualizer

        if not self.testing_panel:
            self.testing_panel = TestingPanel(
                x=10, y=10,
                width=600, height=self.screen_height - 20
            )

        if not self.prototype_editor:
            self.prototype_editor = PrototypeEditor(
                x=620, y=10,
                width=650, height=self.screen_height - 20,
                prototype_manager=self.prototype_manager
            )

        # Note: manifold_visualizer will be standalone window when needed

    def update(self, dt):
        """Update designer mode state"""
        if self.state == self.STATE_INACTIVE:
            return

        # Update current spell data if queue changed
        if self.magic_system.element_queue:
            self._update_current_spell()

    def _update_current_spell(self):
        """Compute current spell properties and distances"""
        queue = self.magic_system.element_queue
        if not queue:
            self.current_spell_data = None
            self.current_distances = None
            return

        # Get elements
        elems = [self.elements[name] for name in queue if name in self.elements]
        if not elems:
            return

        # Compute property vector
        vector = PropertyVectorComputer.compute(elems)

        # Get distances to all prototypes
        distances = self.prototype_manager.manifold.get_behavior_distances(vector)

        # Sort by distance
        sorted_distances = sorted(distances.items(), key=lambda x: x[1])

        self.current_spell_data = {
            'elements': queue,
            'vector': vector,
            'nearest_behavior': sorted_distances[0][0],
            'nearest_distance': sorted_distances[0][1]
        }
        self.current_distances = sorted_distances

    def handle_input(self, event):
        """Handle designer mode input events"""
        if self.state == self.STATE_INACTIVE:
            return None

        # F-key shortcuts
        if event.type == pygame.KEYDOWN:
            # F1: Toggle designer mode
            if event.key == pygame.K_F1:
                self.toggle_active()
                return 'toggle'

            # F2: Tag current spell as new prototype
            if event.key == pygame.K_F2:
                return self._quick_tag_prototype()

            # F3: Open distance analyzer
            if event.key == pygame.K_F3:
                self.state = self.STATE_TESTING
                return None

            # F4: Export prototypes to JSON
            if event.key == pygame.K_F4:
                self.prototype_manager.save_custom_prototypes()
                return None

            # ESC: Exit designer mode
            if event.key == pygame.K_ESCAPE:
                self.exit_designer_mode()
                return 'exit'

            # TAB: Cycle panels
            if event.key == pygame.K_TAB:
                self._cycle_panel()
                return None

            # Element keys (Q/E/R/F/U/O/P/SEMICOLON)
            if event.key in [pygame.K_q, pygame.K_e, pygame.K_r, pygame.K_f,
                           pygame.K_u, pygame.K_o, pygame.K_p, pygame.K_SEMICOLON]:
                self._handle_element_key(event.key)
                return None

            # Backspace: Remove last element
            if event.key == pygame.K_BACKSPACE:
                self.magic_system.remove_last_element()
                self._update_current_spell()
                return None

        # Forward to active panel
        if self.state == self.STATE_TESTING and self.testing_panel:
            self.testing_panel.handle_input(event, self.magic_system, self.current_spell_data)

        if self.state == self.STATE_EDITING and self.prototype_editor:
            self.prototype_editor.handle_input(event)

        return None

    def _handle_element_key(self, key):
        """Handle element queueing in designer mode"""
        element_map = {
            pygame.K_q: 'fire',
            pygame.K_e: 'water',
            pygame.K_r: 'ice',
            pygame.K_f: 'earth',
            pygame.K_u: 'nature',
            pygame.K_o: 'arcane',
            pygame.K_p: 'light',
            pygame.K_SEMICOLON: 'shadow'
        }

        if key in element_map:
            element = element_map[key]
            self.magic_system.queue_element(element)
            self._update_current_spell()

    def _cycle_panel(self):
        """Cycle between testing and editing panels"""
        if self.state == self.STATE_TESTING:
            self.state = self.STATE_EDITING
        elif self.state == self.STATE_EDITING:
            self.state = self.STATE_TESTING

    def _quick_tag_prototype(self):
        """Quick-tag current spell as new prototype (F2 shortcut)"""
        if not self.current_spell_data:
            logging.info("Cannot tag: no spell queued")
            return None

        # Generate default name
        elements = self.current_spell_data['elements']
        default_name = "_".join(elements)

        # For now, just log (UI dialog will be added)
        logging.info(f"🏷️ Tag prototype: {default_name}")
        logging.info(f"   Nearest: {self.current_spell_data['nearest_behavior']} ({self.current_spell_data['nearest_distance']:.3f})")

        # TODO: Show naming dialog
        return 'tag_prototype'

    def render(self, screen):
        """Render designer mode UI"""
        if self.state == self.STATE_INACTIVE:
            return

        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((10, 10, 20))
        screen.blit(overlay, (0, 0))

        # Draw active panel
        if self.state == self.STATE_TESTING and self.testing_panel:
            self.testing_panel.render(screen, self.magic_system, self.current_spell_data, self.current_distances)

        if self.state == self.STATE_EDITING and self.prototype_editor:
            self.prototype_editor.render(screen)

        # Draw mode indicator
        font = pygame.font.Font(None, 24)
        mode_text = f"DESIGNER MODE - {self.state.upper()} (F1: Exit | TAB: Switch Panel)"
        text_surf = font.render(mode_text, True, (255, 200, 50))
        screen.blit(text_surf, (self.screen_width//2 - text_surf.get_width()//2, self.screen_height - 30))

    def is_active(self):
        """Check if designer mode is active"""
        return self.state != self.STATE_INACTIVE
