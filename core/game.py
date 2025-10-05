"""Main game loop"""

import pygame
import logging
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DEBUG_MODE
from config.colors import BLACK
from entities.player import Player
from entities.target_cursor import Target
from entities.enemy import Enemy
from magic.magic_system import MagicSystem
from ai.bot_controller import BotController
from rendering.grid_renderer import draw_isometric_grid
from rendering.terrain_renderer import draw_terrain, draw_terrain_overlay
from rendering.ui.hud import draw_controls
from rendering.ui.spell_preview import draw_spell_preview
from rendering.ui.debug_panel import draw_debug_panel, draw_movement_arrow
from rendering.ui.element_queue_display import draw_element_queue, draw_available_elements
from rendering.ui.controller_hud import draw_controller_status, draw_controller_element_hints
from rendering.ui.manifold_panel import ManifoldPanel
from core.camera import Camera
from input.input_manager import InputManager
from rendering.effects.effect_manager import EffectManager
import os


class Game:
    """Main game class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Karaokeficador - Isometric Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Procedural terrain (Phase 6: World)
        from world.terrain import TerrainGenerator
        from config.settings import GRID_SIZE
        self.terrain = TerrainGenerator(GRID_SIZE, GRID_SIZE, seed=42)
        self.terrain.generate()
        logging.info(f"Generated {GRID_SIZE}x{GRID_SIZE} procedural terrain")

        # Find safe spawn position for player
        player_spawn = self._find_safe_spawn()

        # Game entities
        self.player = Player(player_spawn[0], player_spawn[1])
        self.target = Target()
        self.magic = MagicSystem()

        # Camera
        self.camera = Camera()

        # Input system (Phase 3)
        self.input_manager = InputManager()

        # Visual effects system (Phase 4)
        self.effect_manager = EffectManager()
        self.effect_manager.camera = self.camera  # Give effects access to camera for shake
        self.effect_manager.player = self.player  # Give effects access to player for bot collision
        self.effect_manager.terrain = self.terrain  # Give effects access to terrain for damage bonuses

        # Game state
        self.running = True
        self.game_started = False
        self.countdown_timer = 3.0  # 3 second countdown before game starts

        # Deathmatch scoring (initialize BEFORE spawning enemies)
        self.scores = {
            'player': 0,
            'bot_1': 0,
            'bot_2': 0,
            'bot_3': 0
        }
        self.bot_names = ['bot_1', 'bot_2', 'bot_3']  # Track bot IDs

        # Enemies (Phase 5: Combat) - created AFTER effect_manager and scoring
        self.enemies = []
        self.bots = []  # AI-controlled bots
        self._spawn_initial_enemies()  # Spawn enemies and bots
        self.effect_manager.enemies = self.enemies  # Give effects access to enemies

        # Manifold HUD panel (optional - enabled via environment variable or debug mode)
        self.show_manifold = os.environ.get('MANIFOLD_HUD') == '1' or DEBUG_MODE
        self._last_element_queue = []  # Track changes (always init)

        if self.show_manifold:
            # Position in top-right corner
            panel_width = 320
            panel_height = 280
            panel_x = SCREEN_WIDTH - panel_width - 10
            panel_y = 10
            self.manifold_panel = ManifoldPanel(panel_x, panel_y, panel_width, panel_height)
            logging.info("✨ Behavior Manifold HUD enabled!")
        else:
            self.manifold_panel = None

    def _find_safe_spawn(self):
        """Find a safe spawn position (no damaging terrain)"""
        import random
        from config.settings import GRID_SIZE

        # Try up to 100 times to find safe spawn
        for _ in range(100):
            x = random.uniform(5, GRID_SIZE - 5)
            y = random.uniform(5, GRID_SIZE - 5)

            # Check if this position is safe (no element affinity = plains)
            element = self.terrain.get_element_affinity_at(x, y)
            if element is None:  # Plains biome - safe
                return (x, y)

        # Fallback to center if no safe spot found
        return (GRID_SIZE / 2, GRID_SIZE / 2)

    def _spawn_initial_enemies(self):
        """Spawn initial enemies and bots"""
        import random

        # Spawn 1 static test dummy at safe position
        dummy_pos = self._find_safe_spawn()
        dummy = Enemy(dummy_pos[0], dummy_pos[1], max_health=300)
        self.enemies.append(dummy)
        logging.info(f"Test dummy spawned at ({dummy.cart_x:.1f}, {dummy.cart_y:.1f})")

        # Spawn 3 AI bots at random safe positions
        for i in range(3):
            bot_pos = self._find_safe_spawn()

            # Create enemy
            bot_enemy = Enemy(bot_pos[0], bot_pos[1], max_health=300)  # Higher health for longer fights
            bot_enemy.bot_id = self.bot_names[i]  # Assign bot ID for scoring
            self.enemies.append(bot_enemy)

            # Create AI controller for this enemy
            bot_magic = MagicSystem()  # Each bot has its own magic system
            bot_ai = BotController(bot_enemy, bot_magic, self.effect_manager)
            self.bots.append((bot_enemy, bot_ai, bot_magic))

            logging.info(f"Bot {i+1} ({self.bot_names[i]}) spawned at ({bot_pos[0]:.1f}, {bot_pos[1]:.1f})")

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
                logging.info(f"Controller button {event.button} pressed")
                result = self.input_manager.process_controller_button(
                    event, self.player, self.target, self.magic, self.effect_manager
                )
                if result == 'quit':
                    self.running = False

            elif event.type == pygame.JOYHATMOTION:
                # Controller D-pad
                logging.info(f"JOYHATMOTION event detected: {event}")
                self.input_manager.process_controller_hat(event, self.magic)

    def handle_continuous_input(self, dt):
        """Handle held keys and analog sticks (movement)"""
        keys = pygame.key.get_pressed()
        # Process keyboard + controller analog sticks
        self.input_manager.process_continuous_movement(
            keys, self.player, self.target, self.magic, self.effect_manager, dt
        )

    def update(self):
        """Update game state"""
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        # Clamp dt to prevent large jumps
        dt = min(dt, 0.1)  # Max 100ms per frame to prevent stuttering

        # Countdown before game starts
        if not self.game_started:
            self.countdown_timer -= dt
            if self.countdown_timer <= 0:
                self.game_started = True
                logging.info("GAME STARTED!")
            return  # Don't update game logic during countdown

        # Update player
        self.player.update(dt)

        # Check if player died and should respawn
        if not self.player.health.is_alive:
            # Respawn after 3 seconds
            if not hasattr(self.player, 'death_timer'):
                self.player.death_timer = 0.0
                self.effect_manager.sound.play('death', volume=0.5)
                logging.info("Player died!")

                # Spawn red death particles
                from rendering.effects.particle import ParticleEmitter
                from config.colors import RED
                death_particles = ParticleEmitter(
                    self.player.cart_x,
                    self.player.cart_y,
                    'explosion',
                    RED,
                    duration=1.0,
                    area=2.0
                )
                self.effect_manager.emitters.append(death_particles)

            self.player.death_timer += dt
            if self.player.death_timer >= 3.0:
                self.player.respawn()
                self.player.death_timer = 0.0

                # Spawn white respawn particles
                from rendering.effects.particle import ParticleEmitter
                from config.colors import WHITE, CYAN
                respawn_particles = ParticleEmitter(
                    self.player.cart_x,
                    self.player.cart_y,
                    'explosion',
                    CYAN,
                    duration=0.8,
                    area=2.5
                )
                self.effect_manager.emitters.append(respawn_particles)

        # Update terrain bonuses for player
        current_element = self.terrain.get_element_affinity_at(self.player.cart_x, self.player.cart_y)
        if current_element:
            self.player.mana.set_terrain_bonus(2.0)  # 2x mana regen on elemental terrain
        else:
            self.player.mana.set_terrain_bonus(1.0)  # Normal regen

        self.camera.follow(self.player)
        self.camera.update(dt)  # Update camera shake
        self.target.update(dt)  # Update smooth keyboard aim interpolation
        self.effect_manager.update(dt)

        # Update AI bots - pass all enemies AND player so they fight each other
        all_targets = [self.player] + self.enemies
        for bot_enemy, bot_ai, bot_magic in self.bots[:]:
            if bot_enemy.health.is_alive:
                # Update bot AI behavior (this handles spell casting internally)
                bot_ai.update(dt, all_targets)

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

                # Also remove from bots list if it's a bot
                for i, (bot_enemy, bot_ai, bot_magic) in enumerate(self.bots):
                    if bot_enemy == enemy:
                        self.bots.pop(i)
                        break

                logging.info("Enemy removed from game")

        # Update manifold panel if element queue changed
        if self.show_manifold and self.manifold_panel:
            current_queue = list(self.magic.element_queue)
            if current_queue != self._last_element_queue:
                self.manifold_panel.update_current_spell(current_queue)
                self._last_element_queue = current_queue

    def render(self):
        """Render everything"""
        self.screen.fill(BLACK)

        # Get camera offset
        camera_offset_x, camera_offset_y = self.camera.get_offset()

        # Draw world
        draw_terrain(self.screen, self.terrain, camera_offset_x, camera_offset_y)  # Terrain instead of grid
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
        draw_controller_element_hints(self.screen, self.font, self.input_manager)

        # Draw terrain overlay (biome info)
        draw_terrain_overlay(self.screen, self.font, self.terrain, self.player.cart_x, self.player.cart_y)

        # Draw scoreboard
        from rendering.ui.scoreboard import draw_scoreboard, draw_countdown
        if self.game_started:
            draw_scoreboard(self.screen, self.scores, self.font)
        else:
            draw_countdown(self.screen, self.countdown_timer, self.font)

        # Draw debug info
        if DEBUG_MODE:
            draw_debug_panel(self.screen, self.font, self.player)
            draw_movement_arrow(self.screen, self.player)

        # Draw manifold HUD panel (if enabled)
        if self.show_manifold and self.manifold_panel:
            self.manifold_panel.draw(self.screen)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.get_time() / 1000.0  # Delta time in seconds
            self.handle_events()
            self.handle_continuous_input(dt)
            self.update()
            self.render()
            self.clock.tick(FPS)
