"""Xbox controller input handler"""

import pygame
import logging
from config import controller_config as ctrl


class ControllerHandler:
    """
    Handles Xbox controller input for dual-stick gameplay.
    Left stick = player movement, Right stick = target aiming.
    """

    def __init__(self):
        self.controller = None
        self.connected = False
        self.last_trigger_state = {'LT': False, 'RT': False}

    def initialize(self):
        """Initialize controller support"""
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            logging.info("No controllers detected")
            return False

        # Use first controller
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        self.connected = True

        logging.info(f"Controller connected: {self.controller.get_name()}")
        logging.info(f"  Axes: {self.controller.get_numaxes()}")
        logging.info(f"  Buttons: {self.controller.get_numbuttons()}")
        logging.info(f"  Hats: {self.controller.get_numhats()}")

        return True

    def disconnect(self):
        """Disconnect controller"""
        if self.controller:
            self.controller.quit()
            self.connected = False
            logging.info("Controller disconnected")

    def process_button_event(self, event, player, target, magic_system):
        """
        Process JOYBUTTONDOWN events.
        Returns: 'quit' if should exit, None otherwise
        """
        if not self.connected:
            return None

        button = event.button

        # Element queueing (face buttons + D-pad handled separately)
        if button in ctrl.ELEMENT_MAPPINGS:
            element = ctrl.ELEMENT_MAPPINGS[button]
            success = magic_system.queue_element(element)
            if success:
                logging.info(f"Controller: Element {element.upper()} queued")
                self._rumble_feedback(100)  # Short rumble
            return None

        # Actions
        if button == ctrl.ACTION_CAST:
            # Right Bumper - Cast spell
            spell_data = magic_system.cast_spell()
            if spell_data:
                logging.info(f"Controller CAST: {spell_data['name']}")
                self._rumble_feedback(ctrl.RUMBLE_DURATION)
                return spell_data  # Return for visual effects
            return None

        if button == ctrl.ACTION_REMOVE:
            # Left Bumper - Remove last element
            if magic_system.element_queue:
                removed = magic_system.element_queue[-1]
                magic_system.remove_last_element()
                logging.info(f"Controller: Removed {removed.upper()}")
            return None

        if button == ctrl.ACTION_CLEAR:
            # Back button - Clear queue
            magic_system.clear_queue()
            logging.info("Controller: Queue cleared")
            return None

        if button == ctrl.ACTION_JUMP:
            # Right stick click - Jump
            player.jump()
            return None

        if button == ctrl.BUTTON_START:
            # Start button - Quit
            logging.info("Controller: Quit via START button")
            return 'quit'

        return None

    def process_hat_event(self, event, magic_system):
        """Process D-pad (hat) events for element selection"""
        if not self.connected:
            return None

        hat_value = event.value

        # Check if hat direction maps to an element
        if hat_value in ctrl.ELEMENT_MAPPINGS:
            element = ctrl.ELEMENT_MAPPINGS[hat_value]
            success = magic_system.queue_element(element)
            if success:
                logging.info(f"Controller D-Pad: Element {element.upper()} queued")
                self._rumble_feedback(100)
        return None

    def process_analog_movement(self, player, target):
        """
        Process analog stick input for continuous movement.
        Left stick = player, Right stick = target cursor.
        """
        if not self.connected:
            return

        # Left stick - Player movement
        left_x = self.controller.get_axis(ctrl.AXIS_LEFT_X)
        left_y = self.controller.get_axis(ctrl.AXIS_LEFT_Y)

        # Apply deadzone
        if abs(left_x) < ctrl.STICK_DEADZONE:
            left_x = 0
        if abs(left_y) < ctrl.STICK_DEADZONE:
            left_y = 0

        # Convert to screen-space direction (up = negative Y)
        player_dx = left_x
        player_dy = left_y  # Positive = down in pygame

        # Move player
        player.move(player_dx, player_dy)

        # Right stick - Aim direction OR free aim (depending on mode)
        right_x = self.controller.get_axis(ctrl.AXIS_RIGHT_X)
        right_y = self.controller.get_axis(ctrl.AXIS_RIGHT_Y)

        # Apply deadzone
        if abs(right_x) < ctrl.STICK_DEADZONE:
            right_x = 0
        if abs(right_y) < ctrl.STICK_DEADZONE:
            right_y = 0

        # Right stick - Aim direction (Diablo 3 style)
        if right_x != 0 or right_y != 0:
            # Right stick sets aim direction (overrides movement)
            player.facing_direction = (right_x, right_y)
            target.set_aim_direction(right_x, right_y)
        elif left_x != 0 or left_y != 0:
            # No right stick but moving - aim follows movement
            target.set_aim_direction(*player.facing_direction)
        else:
            pass  # Let keyboard handle targeting

    def check_trigger_casting(self, magic_system):
        """
        Check trigger states for spell casting.
        RT = aimed cast, LT = self-cast.
        Returns spell_data dict if cast, None otherwise.
        """
        if not self.connected or not ctrl.ENABLE_TRIGGER_CASTING:
            return None

        # Right Trigger - Aimed cast
        rt_value = self.controller.get_axis(ctrl.AXIS_RT)
        rt_pressed = rt_value > ctrl.TRIGGER_THRESHOLD

        # Detect rising edge (trigger just pressed)
        if rt_pressed and not self.last_trigger_state['RT']:
            spell_data = magic_system.cast_spell()
            if spell_data:
                logging.info(f"Controller RT CAST: {spell_data['name']}")
                self._rumble_feedback(ctrl.RUMBLE_DURATION)
                self.last_trigger_state['RT'] = True
                return ('aimed', spell_data)

        if not rt_pressed:
            self.last_trigger_state['RT'] = False

        # Left Trigger - Self-cast
        lt_value = self.controller.get_axis(ctrl.AXIS_LT)
        lt_pressed = lt_value > ctrl.TRIGGER_THRESHOLD

        if lt_pressed and not self.last_trigger_state['LT']:
            spell_data = magic_system.cast_spell()
            if spell_data:
                logging.info(f"Controller LT SELF-CAST: {spell_data['name']}")
                self._rumble_feedback(ctrl.RUMBLE_DURATION)
                self.last_trigger_state['LT'] = True
                return ('self', spell_data)

        if not lt_pressed:
            self.last_trigger_state['LT'] = False

        return None

    def _rumble_feedback(self, duration_ms):
        """Provide haptic feedback (rumble)"""
        if not self.connected or not ctrl.ENABLE_RUMBLE:
            return

        # Try to use rumble if supported
        try:
            # rumble(low_freq, high_freq, duration_ms)
            self.controller.rumble(0.3, 0.7, duration_ms)
        except AttributeError:
            # Rumble not supported on this controller
            pass
