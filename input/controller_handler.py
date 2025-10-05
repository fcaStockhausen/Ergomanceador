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
        self.current_element_page = 0  # Current page for element selection
        self.last_dpad_state = (0, 0)  # Track D-pad for page cycling

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
        Returns: 'quit' if should exit, spell_data for casting, None otherwise
        """
        if not self.connected:
            return None

        button = event.button
        print(f"🎮 BUTTON {button} PRESSED")

        # Get current element page
        current_page = ctrl.ELEMENT_PAGES[self.current_element_page]

        # Face buttons X/Y/B queue elements from current page
        if button == ctrl.BUTTON_X:
            element = current_page[ctrl.SLOT_X]
            success = magic_system.queue_element(element)
            if success:
                logging.info(f"Controller X: {element.upper()} queued (Page {self.current_element_page + 1})")
                self._rumble_feedback(100)
            return None

        if button == ctrl.BUTTON_Y:
            element = current_page[ctrl.SLOT_Y]
            success = magic_system.queue_element(element)
            if success:
                logging.info(f"Controller Y: {element.upper()} queued (Page {self.current_element_page + 1})")
                self._rumble_feedback(100)
            return None

        if button == ctrl.BUTTON_B:
            element = current_page[ctrl.SLOT_B]
            success = magic_system.queue_element(element)
            if success:
                logging.info(f"Controller B: {element.upper()} queued (Page {self.current_element_page + 1})")
                self._rumble_feedback(100)
            return None

        if button == ctrl.BUTTON_LB:
            # LB queues 4th element from current page
            element = current_page[ctrl.SLOT_LB]
            success = magic_system.queue_element(element)
            if success:
                logging.info(f"Controller LB: {element.upper()} queued (Page {self.current_element_page + 1})")
                self._rumble_feedback(100)
            return None

        # Actions
        if button == ctrl.ACTION_CAST:
            # Right Bumper - Cast spell
            spell_data = magic_system.cast_spell(player.mana)
            if spell_data:
                logging.info(f"Controller RB CAST: {spell_data['name']}")
                self._rumble_feedback(ctrl.RUMBLE_DURATION)
                return spell_data
            return None

        if button == ctrl.ACTION_CLEAR:
            # Back button - Clear queue
            magic_system.clear_queue()
            logging.info("Controller: Queue cleared")
            return None

        if button == ctrl.ACTION_JUMP:
            # A button - Jump
            player.jump()
            logging.info("Controller A: JUMP")
            return None

        if button == ctrl.BUTTON_START:
            # Start button - Quit
            logging.info("Controller: Quit via START button")
            return 'quit'

        # D-Pad page cycling (D-pad sends button events on macOS)
        if button == ctrl.DPAD_UP:
            old_page = self.current_element_page
            self.current_element_page = (self.current_element_page + 1) % len(ctrl.ELEMENT_PAGES)
            current_page = ctrl.ELEMENT_PAGES[self.current_element_page]
            print(f"🔼 D-PAD UP: PAGE {old_page + 1} ➡️  PAGE {self.current_element_page + 1}/3")
            print(f"   📋 Elements: {current_page}")
            self._rumble_feedback(200)
            return None

        if button == ctrl.DPAD_DOWN:
            old_page = self.current_element_page
            self.current_element_page = (self.current_element_page - 1) % len(ctrl.ELEMENT_PAGES)
            current_page = ctrl.ELEMENT_PAGES[self.current_element_page]
            print(f"🔽 D-PAD DOWN: PAGE {old_page + 1} ➡️  PAGE {self.current_element_page + 1}/3")
            print(f"   📋 Elements: {current_page}")
            self._rumble_feedback(200)
            return None

        return None

    def process_hat_event(self, event, magic_system):
        """Process D-pad (hat) events for page cycling"""
        print(f"🎮 D-PAD EVENT RECEIVED! Value: {event.value}, Connected: {self.connected}")

        if not self.connected:
            print("⚠️  Controller not connected, ignoring D-pad")
            return None

        hat_value = event.value

        # D-pad Up (0, 1) - Next page
        if hat_value == (0, 1):
            old_page = self.current_element_page
            self.current_element_page = (self.current_element_page + 1) % len(ctrl.ELEMENT_PAGES)
            current_page = ctrl.ELEMENT_PAGES[self.current_element_page]
            print(f"🔼 D-PAD UP: PAGE {old_page + 1} ➡️  PAGE {self.current_element_page + 1}/3")
            print(f"   📋 New elements: {current_page}")
            self._rumble_feedback(200)

        # D-pad Down (0, -1) - Previous page
        elif hat_value == (0, -1):
            old_page = self.current_element_page
            self.current_element_page = (self.current_element_page - 1) % len(ctrl.ELEMENT_PAGES)
            current_page = ctrl.ELEMENT_PAGES[self.current_element_page]
            print(f"🔽 D-PAD DOWN: PAGE {old_page + 1} ➡️  PAGE {self.current_element_page + 1}/3")
            print(f"   📋 New elements: {current_page}")
            self._rumble_feedback(200)
        else:
            print(f"↔️  D-PAD OTHER: {hat_value}")

        return None

    def process_analog_movement(self, player, target, dt=0.016):
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
        player.move(player_dx, player_dy, dt)

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
            target.set_aim_direction(right_x, right_y, smooth=False)  # Controller = instant
        elif left_x != 0 or left_y != 0:
            # No right stick but moving - aim follows movement
            target.set_aim_direction(*player.facing_direction, smooth=False)  # Controller = instant
        else:
            pass  # Let keyboard handle targeting

    def check_trigger_casting(self, magic_system, player):
        """
        Check trigger states for spell casting.
        RT = aimed cast, LT = self-cast.
        Returns tuple: (cast_type, spell_data) or None
        """
        if not self.connected or not ctrl.ENABLE_TRIGGER_CASTING:
            return None

        # Right Trigger - Aimed cast
        rt_value = self.controller.get_axis(ctrl.AXIS_RT)
        rt_pressed = rt_value > ctrl.TRIGGER_THRESHOLD

        # Detect rising edge (trigger just pressed)
        if rt_pressed and not self.last_trigger_state['RT']:
            spell_data = magic_system.cast_spell(player.mana)
            if spell_data:
                logging.info(f"Controller RT CAST: {spell_data['name']} (aimed)")
                self._rumble_feedback(ctrl.RUMBLE_DURATION)
                self.last_trigger_state['RT'] = True
                return ('aimed', spell_data)

        if not rt_pressed:
            self.last_trigger_state['RT'] = False

        # Left Trigger - Self-cast
        lt_value = self.controller.get_axis(ctrl.AXIS_LT)
        lt_pressed = lt_value > ctrl.TRIGGER_THRESHOLD

        if lt_pressed and not self.last_trigger_state['LT']:
            spell_data = magic_system.cast_spell(player.mana)
            if spell_data:
                logging.info(f"Controller LT CAST: {spell_data['name']} (self-cast)")
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
