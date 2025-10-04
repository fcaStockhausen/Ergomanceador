"""
Karaokeficador - Arena-based elemental magic combat game

Entry point for the game.
"""

import pygame
import sys
from utils.logger import setup_logger
from core.game import Game


def main():
    """Initialize and run the game"""
    # Setup logging
    setup_logger()

    # Initialize Pygame
    pygame.init()

    # Create and run game
    game = Game()
    game.run()

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
