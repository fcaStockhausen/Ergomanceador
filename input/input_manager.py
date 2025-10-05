"""Input manager for dual-hand keyboard controls and Xbox controller"""

import pygame
import logging
from config import keybinds
from input.controller_handler import ControllerHandler


class InputManager:
    """
    Main input router for dual-hand keyboard system and Xbox controller.
    Routes inputs to appropriate handlers (movement, aiming, elements, actions).
    """

    def __init__(self):
        self.escape_press_count = 0  # Track ESC presses for quit
        self.last_escape_time = 0
        self.controller = ControllerHandler()
        self.controller.initialize()

    def process_keydown(self, event, player, target, magic_system, effect_manager=None):
        """Process KEYDOWN events"""
        key = event.key

        # === QUIT HANDLING ===
        if key == keybinds.QUIT_KEY:
            # ESC key - first press clears queue, second press quits
            current_time = pygame.time.get_ticks()
            if current_time - self.last_escape_time < 500:  # 500ms window
                logging.info("Game quit with ESC (double press)")
                return 'quit'
            else:
                magic_system.clear_queue()
                logging.info("Queue cleared with ESC")
                self.last_escape_time = current_time
                return None

        # Cmd+Q or Ctrl+Q
        mods = pygame.key.get_mods()
        if key == pygame.K_q and (mods & keybinds.QUIT_MODIFIER):
            logging.info("Game quit with Cmd/Ctrl+Q")
            return 'quit'

        # === ELEMENT QUEUEING ===
        if key in keybinds.ELEMENT_KEYS:
            element = keybinds.ELEMENT_KEYS[key]
            success = magic_system.queue_element(element)
            if success:
                logging.info(f"Element {element.upper()} queued: {magic_system.element_queue}")
            else:
                logging.warning(f"Cannot queue {element.upper()} (queue full or locked)")
            return None

        # === QUEUE MANIPULATION ===
        if key == keybinds.REMOVE_ELEMENT:
            if magic_system.element_queue:
                removed = magic_system.element_queue[-1]
                magic_system.remove_last_element()
                logging.info(f"Removed {removed.upper()} from queue: {magic_system.element_queue}")
            return None

        # === ACTIONS ===
        if key == keybinds.JUMP:
            player.jump()
            return None

        if key == keybinds.CAST_AIMED:
            # Check for self-cast modifier
            is_self_cast = mods & pygame.KMOD_SHIFT

            if is_self_cast:
                spell_data = magic_system.cast_spell(player.mana)
                if spell_data:
                    logging.info(f"SELF-CAST: {spell_data['name']} (behavior: {spell_data['behavior']})")
                    # Spawn visual effect at player position (Phase 4)
                    if effect_manager:
                        effect_manager.spawn_spell_effect(
                            player.cart_x, player.cart_y,
                            player.cart_x, player.cart_y,  # Self-target
                            spell_data
                        )
                else:
                    logging.info("SELF-CAST failed: no elements queued")
            else:
                spell_data = magic_system.cast_spell(player.mana)
                if spell_data:
                    target_pos = (target.cart_x, target.cart_y)
                    logging.info(f"AIMED CAST: {spell_data['name']} at {target_pos} (behavior: {spell_data['behavior']})")
                    # Spawn visual effect from player to target (Phase 4)
                    if effect_manager:
                        effect_manager.spawn_spell_effect(
                            player.cart_x, player.cart_y,
                            target.cart_x, target.cart_y,
                            spell_data
                        )
                else:
                    logging.info("AIMED CAST failed: no elements queued")
            return None

        return None

    def process_controller_button(self, event, player, target, magic_system, effect_manager=None):
        """Process controller button events"""
        result = self.controller.process_button_event(event, player, target, magic_system)

        # If button returned spell_data, spawn visual effect
        if result and isinstance(result, dict):
            if effect_manager:
                effect_manager.spawn_spell_effect(
                    player.cart_x, player.cart_y,
                    target.cart_x, target.cart_y,
                    result
                )
            return None
        return result  # 'quit' or None

    def process_controller_hat(self, event, magic_system):
        """Process controller D-pad (hat) events"""
        return self.controller.process_hat_event(event, magic_system)

    def process_continuous_movement(self, keys, player, target, magic_system=None, effect_manager=None, dt=0.016):
        """Process held keys and analog sticks for continuous movement"""
        # === KEYBOARD MOVEMENT (WASD) ===
        dx = dy = 0
        if keys[keybinds.MOVE_UP]:
            dy = -1
        if keys[keybinds.MOVE_DOWN]:
            dy = 1
        if keys[keybinds.MOVE_LEFT]:
            dx = -1
        if keys[keybinds.MOVE_RIGHT]:
            dx = 1
        player.move(dx, dy, dt)
        player.update_jump()

        # === TARGET AIMING (IJKL) - Diablo 3 Style ===
        tdx = tdy = 0
        if keys[keybinds.AIM_UP]:
            tdy = -1
        if keys[keybinds.AIM_DOWN]:
            tdy = 1
        if keys[keybinds.AIM_LEFT]:
            tdx = -1
        if keys[keybinds.AIM_RIGHT]:
            tdx = 1

        # IJKL sets aim direction (overrides movement direction)
        if tdx != 0 or tdy != 0:
            target.set_aim_direction(tdx, tdy)
        elif dx != 0 or dy != 0:
            # No IJKL but moving - aim follows movement
            target.set_aim_direction(*player.facing_direction)
        else:
            # No input at all - cursor returns to player center
            target.set_aim_direction(0, 0)

        # === CONTROLLER ANALOG STICKS ===
        if self.controller.connected:
            self.controller.process_analog_movement(player, target, dt)

            # Check trigger casting
            if magic_system and effect_manager:
                cast_result = self.controller.check_trigger_casting(magic_system, player)
                if cast_result:
                    cast_type, spell_data = cast_result
                    if cast_type == 'aimed':
                        effect_manager.spawn_spell_effect(
                            player.cart_x, player.cart_y,
                            target.cart_x, target.cart_y,
                            spell_data
                        )
                    elif cast_type == 'self':
                        effect_manager.spawn_spell_effect(
                            player.cart_x, player.cart_y,
                            player.cart_x, player.cart_y,
                            spell_data
                        )

        # === UPDATE TARGET POSITION (Forward-Facing Mode) ===
        # Always update target position based on player facing direction
        target.follow_player(player)
