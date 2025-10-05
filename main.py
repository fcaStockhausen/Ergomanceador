"""
Karaokeficador - Arena-based elemental magic combat game

Entry point for the game.

Usage:
    python main.py                    # Show menu, choose mode
    python main.py --play             # Skip menu, go straight to game
    python main.py --designer         # Skip menu, go straight to designer mode
    python main.py --manifold-hud     # Game with manifold HUD
    python main.py -m                 # Short form for manifold HUD
    MANIFOLD_HUD=1 python main.py     # Alternative (environment variable)
"""

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame
import sys
import logging
from utils.logger import setup_logger
from core.game import Game
from core.menu import MenuManager
from designer.designer_mode import DesignerMode
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def main():
    """Initialize and run the game"""
    # Setup logging
    setup_logger()

    # Check for command-line flags
    skip_menu = '--play' in sys.argv or '--designer' in sys.argv
    start_designer = '--designer' in sys.argv
    show_manifold = (
        '--manifold-hud' in sys.argv or
        '-m' in sys.argv or
        os.environ.get('MANIFOLD_HUD') == '1'
    )

    if show_manifold:
        print("=" * 70)
        print("🎮 KARAOKEFICADOR - Arena Combat with Behavior Manifold HUD")
        print("=" * 70)
        print()
        print("✨ Queue elements and watch the manifold panel (top-right)")
        print("📊 Yellow dot = your current spell in 12D property space!")
        print("🎯 Colored circles = behavior prototypes")
        print()
        print("=" * 70)
        print()
        os.environ['MANIFOLD_HUD'] = '1'  # Set for Game class to read

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Karaokeficador")
    clock = pygame.time.Clock()

    # Game systems
    game = None
    designer_mode = None
    menu_manager = MenuManager()

    # State management
    current_mode = 'menu'  # 'menu', 'game', 'designer'

    # Skip to requested mode if flag provided
    if skip_menu:
        if start_designer:
            current_mode = 'designer'
            designer_mode = DesignerMode(SCREEN_WIDTH, SCREEN_HEIGHT)
            designer_mode.enter_designer_mode()
            logging.info("🎨 Starting in Designer Mode")
        else:
            current_mode = 'game'
            game = Game()
            logging.info("🎮 Starting Game")
        menu_manager.hide_menu()

    # Main loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        # Event handling - different modes handle events differently
        if current_mode == 'menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                action = menu_manager.handle_event(event)
                if action == 'play':
                    # Start game
                    current_mode = 'game'
                    game = Game()
                    menu_manager.hide_menu()
                    logging.info("🎮 Starting Game")
                elif action == 'designer':
                    # Start designer mode
                    current_mode = 'designer'
                    designer_mode = DesignerMode(SCREEN_WIDTH, SCREEN_HEIGHT)
                    designer_mode.enter_designer_mode()
                    menu_manager.hide_menu()
                    logging.info("🎨 Starting Designer Mode")
                elif action == 'settings':
                    logging.info("⚙️ Settings (not implemented yet)")
                elif action == 'quit':
                    running = False

        elif current_mode == 'game':
            # Game mode - check for F1, then let game handle remaining events
            if game:
                events_to_pass = []
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                        current_mode = 'designer'
                        if not designer_mode:
                            designer_mode = DesignerMode(SCREEN_WIDTH, SCREEN_HEIGHT)
                        designer_mode.enter_designer_mode()
                        logging.info("🎨 Switching to Designer Mode")
                    else:
                        # Save event for game to process
                        events_to_pass.append(event)

                # Put events back in queue for game to handle
                if current_mode == 'game':  # Only if we didn't switch modes
                    for event in events_to_pass:
                        pygame.event.post(event)

                    game.handle_events()

                    # Check if game wants to quit
                    if not game.running:
                        running = False

        elif current_mode == 'designer':
            # Designer mode handles its own events
            if designer_mode:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    result = designer_mode.handle_input(event)
                    if result == 'exit' or result == 'toggle':
                        # Return to game or menu
                        if game:
                            current_mode = 'game'
                            logging.info("🎮 Returning to Game")
                        else:
                            current_mode = 'menu'
                            menu_manager.show_main_menu()
                            logging.info("📋 Returning to Menu")

        # Update
        if current_mode == 'menu':
            menu_manager.update()
        elif current_mode == 'game' and game:
            game.update()
        elif current_mode == 'designer' and designer_mode:
            designer_mode.update(dt)

        # Render
        if current_mode == 'menu':
            menu_manager.draw(screen)
        elif current_mode == 'game' and game:
            game.render()
        elif current_mode == 'designer' and designer_mode:
            # Draw game in background (if exists) then designer overlay
            if game:
                game.render()
            designer_mode.render(screen)

        pygame.display.flip()

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
