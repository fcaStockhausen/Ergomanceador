"""
Karaokeficador - Arena-based elemental magic combat game

Entry point for the game.

Usage:
    python main.py                    # Normal game
    python main.py --manifold-hud     # With behavior space visualizer panel
    python main.py -m                 # Short form
    MANIFOLD_HUD=1 python main.py     # Alternative (environment variable)
"""

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame
import sys
from utils.logger import setup_logger
from core.game import Game


def main():
    """Initialize and run the game"""
    # Setup logging
    setup_logger()

    # Check for manifold HUD flag
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

    # Create and run game
    game = Game()
    game.run()

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
