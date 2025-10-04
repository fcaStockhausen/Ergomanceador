"""Main game loop"""

import pygame
import logging
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DEBUG_MODE
from config.colors import BLACK
from entities.player import Player
from entities.target_cursor import Target
from entities.enemy import Enemy
from magic.magic_system import MagicSystem
from rendering.grid_renderer import draw_isometric_grid
from rendering.ui.hud import draw_controls
from rendering.ui.spell_preview import draw_spell_preview
from rendering.ui.debug_panel import draw_debug_panel, draw_movement_arrow
from rendering.ui.element_queue_display import draw_element_queue, draw_available_elements
from rendering.ui.controller_hud import draw_controller_status, draw_controller_element_hints
from core.camera import Camera
from input.input_manager import InputManager
from rendering.effects.effect_manager import EffectManager


class Game:
    """Main game class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Karaokeficador - Isometric Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Game entities
        self.player = Player(10, 10)
        self.target = Target()
        self.magic = MagicSystem()

        # Enemies (Phase 5: Combat)
        self.enemies = []
        self._spawn_test_enemy()  # Spawn initial test dummy

        # Camera
        self.camera = Camera()

        # Input system (Phase 3)
        self.input_manager = InputManager()

        # Visual effects system (Phase 4)
        self.effect_manager = EffectManager()
        self.effect_manager.enemies = self.enemies  # Give effects access to enemies
        self.effect_manager.camera = self.camera  # Give effects access to camera for shake

        self.running = True

    def _spawn_test_enemy(self):
        """Spawn a test enemy for combat testing"""
        # Spawn enemy 5 tiles away from player
        enemy = Enemy(15, 15, max_health=100)
        self.enemies.append(enemy)
        logging.info(f"Test enemy spawned at ({enemy.cart_x}, {enemy.cart_y})")

    def handle_events(self):
        """Process input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Keyboard input
                result = self.input_manager.process_keydown(
                    event, self.player, self.target, self.magic, self.effect_manager
                )
                if result == 'quit':
                    self.running = False

            elif event.type == pygame.JOYBUTTONDOWN:
                # Controller button press
                result = self.input_manager.process_controller_button(
                    event, self.player, self.target, self.magic, self.effect_manager
                )
                if result == 'quit':
                    self.running = False

            elif event.type == pygame.JOYHATMOTION:
                # Controller D-pad
                self.input_manager.process_controller_hat(event, self.magic)

    def handle_continuous_input(self):
        """Handle held keys and analog sticks (movement)"""
        keys = pygame.key.get_pressed()
        # Process keyboard + controller analog sticks
        self.input_manager.process_continuous_movement(
            keys, self.player, self.target, self.magic, self.effect_manager
        )

    def update(self):
        """Update game state"""
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        self.camera.follow(self.player)
        self.camera.update(dt)  # Update camera shake
        self.target.update(dt)  # Update smooth keyboard aim interpolation
        self.effect_manager.update(dt)

        # Update enemies
        for enemy in self.enemies[:]:
            # Check if just died (play death sound once)
            was_alive = enemy.alive

            enemy.update(dt)

            # Play death sound on death frame
            if was_alive and not enemy.health.is_alive:
                self.effect_manager.sound.play('death', volume=0.5)

            # Remove dead enemies after animation
            if enemy.should_remove():
                self.enemies.remove(enemy)
                logging.info("Enemy removed from game")

    def render(self):
        """Render everything"""
        self.screen.fill(BLACK)

        # Get camera offset
        camera_offset_x, camera_offset_y = self.camera.get_offset()

        # Draw world
        draw_isometric_grid(self.screen, camera_offset_x, camera_offset_y)
        self.player.draw(self.screen, camera_offset_x, camera_offset_y)

        # Draw enemies (Phase 5)
        for enemy in self.enemies:
            enemy.draw(self.screen, camera_offset_x, camera_offset_y)

        self.target.draw(self.screen, camera_offset_x, camera_offset_y)

        # Draw spell effects (Phase 4)
        self.effect_manager.draw(self.screen, camera_offset_x, camera_offset_y)

        # Draw UI (Phase 3 - new queue display)
        draw_controls(self.screen, self.font)
        draw_element_queue(self.screen, self.font, self.magic)  # New visual queue
        draw_available_elements(self.screen, self.font, self.magic)  # Available elements grid
        draw_spell_preview(self.screen, self.font, self.magic)

        # Draw controller HUD (if connected)
        draw_controller_status(self.screen, self.font, self.input_manager)
        draw_controller_element_hints(self.screen, self.font, self.magic)

        # Draw debug info
        if DEBUG_MODE:
            draw_debug_panel(self.screen, self.font, self.player)
            draw_movement_arrow(self.screen, self.player)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.handle_continuous_input()
            self.update()
            self.render()
            self.clock.tick(FPS)
