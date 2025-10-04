"""Automated test runner for game input sequences"""

import pygame
import json
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.game import Game


class AutomatedTester:
    """Runs automated input sequences for testing"""

    def __init__(self, test_sequence_file="tests/test_sequences.json"):
        self.sequences = self._load_sequences(test_sequence_file)
        self.current_sequence = None
        self.sequence_start_time = None
        self.active_keys = set()

    def _load_sequences(self, filepath):
        """Load test sequences from JSON"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def run_test(self, test_name):
        """Run a specific test sequence"""
        if test_name not in self.sequences:
            print(f"Test '{test_name}' not found!")
            print(f"Available tests: {list(self.sequences.keys())}")
            return

        test = self.sequences[test_name]
        print(f"\n{'='*60}")
        print(f"Running test: {test_name}")
        print(f"Description: {test['description']}")
        print(f"Duration: {test['duration']}s")
        print(f"{'='*60}\n")

        # Initialize pygame and game
        pygame.init()
        game = Game()

        self.current_sequence = test['sequence']
        self.sequence_start_time = time.time()
        duration = test['duration']

        # Run game loop with automated inputs
        running = True
        sequence_index = 0

        while running and (time.time() - self.sequence_start_time) < duration:
            # Check for user interrupt (ESC to quit early)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # Inject automated inputs
            elapsed = time.time() - self.sequence_start_time

            # Process sequence events
            while sequence_index < len(self.current_sequence):
                event_data = self.current_sequence[sequence_index]
                event_time = event_data['time']

                if elapsed >= event_time:
                    self._inject_input(event_data)
                    sequence_index += 1
                else:
                    break

            # Update game with injected inputs
            game.handle_continuous_input()
            game.update()
            game.render()
            game.clock.tick(60)

        pygame.quit()
        print(f"\nTest '{test_name}' completed!")

    def _inject_input(self, event_data):
        """Inject keyboard input into pygame"""
        key_name = event_data['key']
        action = event_data['action']

        # Map key names to pygame constants
        key_map = {
            'w': pygame.K_w,
            'a': pygame.K_a,
            's': pygame.K_s,
            'd': pygame.K_d,
            'i': pygame.K_i,
            'j': pygame.K_j,
            'k': pygame.K_k,
            'l': pygame.K_l,
            'q': pygame.K_q,
            'e': pygame.K_e,
            'u': pygame.K_u,
            'o': pygame.K_o,
            'space': pygame.K_SPACE,
            'alt': pygame.K_LALT,
            'esc': pygame.K_ESCAPE
        }

        if key_name not in key_map:
            print(f"Warning: Unknown key '{key_name}'")
            return

        key_code = key_map[key_name]

        if action == 'press':
            # Create KEYDOWN event
            event = pygame.event.Event(pygame.KEYDOWN, {'key': key_code})
            pygame.event.post(event)
            self.active_keys.add(key_code)
            print(f"[{time.time() - self.sequence_start_time:.2f}s] Press {key_name.upper()}")

        elif action == 'release':
            # Create KEYUP event
            event = pygame.event.Event(pygame.KEYUP, {'key': key_code})
            pygame.event.post(event)
            if key_code in self.active_keys:
                self.active_keys.remove(key_code)
            print(f"[{time.time() - self.sequence_start_time:.2f}s] Release {key_name.upper()}")

    def list_tests(self):
        """List all available tests"""
        print("\nAvailable Tests:")
        print("=" * 60)
        for name, test in self.sequences.items():
            print(f"  {name:20} - {test['description']}")
            print(f"  {'':20}   Duration: {test['duration']}s")
            print()


def main():
    """Main entry point for test runner"""
    tester = AutomatedTester()

    if len(sys.argv) < 2:
        print("Usage: python tests/test_runner.py <test_name>")
        print("       python tests/test_runner.py list")
        tester.list_tests()
        return

    test_name = sys.argv[1]

    if test_name == 'list':
        tester.list_tests()
    else:
        tester.run_test(test_name)


if __name__ == "__main__":
    main()
