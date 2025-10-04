"""
TAS-style test runner with log verification.
Runs automated input sequences and verifies expected behaviors via log analysis.
"""

import pygame
import json
import sys
import time
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.game import Game
from utils.logger import setup_logger


class VerifiedTestRunner:
    """TAS-style test runner with automatic verification"""

    def __init__(self, test_file="tests/test_cases.json"):
        self.test_cases = self._load_test_cases(test_file)
        self.log_file = "game_debug.log"
        self.results = []

    def _load_test_cases(self, filepath):
        """Load test cases from JSON"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def _clear_log(self):
        """Clear debug log before test"""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def _read_log(self):
        """Read debug log after test"""
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, 'r') as f:
            return f.readlines()

    def _verify_logs(self, expected_logs, actual_log_lines):
        """
        Verify that expected log entries appear in actual logs.
        Returns (success: bool, missing: list, found: list)
        """
        missing = []
        found = []

        for expected in expected_logs:
            found_match = False
            for line in actual_log_lines:
                if expected in line:
                    found_match = True
                    found.append(expected)
                    break
            if not found_match:
                missing.append(expected)

        return len(missing) == 0, missing, found

    def run_test(self, test_name, verbose=True):
        """Run a single test case with verification"""
        if test_name not in self.test_cases:
            print(f"❌ Test '{test_name}' not found!")
            return False

        test = self.test_cases[test_name]

        if verbose:
            print(f"\n{'='*70}")
            print(f"🎮 Running: {test_name}")
            print(f"📝 {test['description']}")
            print(f"⏱️  Duration: {test['duration']}s")
            print(f"{'='*70}\n")

        # Clear log before test
        self._clear_log()

        # Initialize logger (force reconfiguration for each test)
        # Remove all handlers to allow basicConfig to work again
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        setup_logger()

        # Initialize pygame and game
        pygame.init()
        game = Game()

        sequence = test['sequence']
        duration = test['duration']
        start_time = time.time()
        sequence_index = 0

        # Run game loop with automated inputs
        running = True
        while running and (time.time() - start_time) < duration:
            # Inject automated inputs BEFORE processing events
            elapsed = time.time() - start_time

            while sequence_index < len(sequence):
                event_data = sequence[sequence_index]
                event_time = event_data['time']

                if elapsed >= event_time:
                    self._inject_input(event_data, start_time)
                    sequence_index += 1
                else:
                    break

            # Process events (including injected keypresses)
            game.handle_events()
            if not game.running:
                running = False

            # Update game
            game.handle_continuous_input()
            game.update()
            game.render()
            game.clock.tick(60)

        pygame.quit()

        # Verify results
        actual_logs = self._read_log()
        expected_logs = test.get('expected_logs', [])

        if expected_logs:
            success, missing, found = self._verify_logs(expected_logs, actual_logs)

            if verbose:
                print(f"\n{'='*70}")
                print(f"📊 VERIFICATION RESULTS")
                print(f"{'='*70}")

                if success:
                    print(f"✅ TEST PASSED: All expected behaviors verified!")
                else:
                    print(f"❌ TEST FAILED: Missing expected behaviors")

                print(f"\n✓ Found ({len(found)}/{len(expected_logs)}):")
                for item in found:
                    print(f"  ✓ {item}")

                if missing:
                    print(f"\n✗ Missing ({len(missing)}/{len(expected_logs)}):")
                    for item in missing:
                        print(f"  ✗ {item}")

                print(f"{'='*70}\n")

            result = {
                'test': test_name,
                'passed': success,
                'found': found,
                'missing': missing
            }
            self.results.append(result)
            return success
        else:
            # No verification needed
            if verbose:
                print(f"⚠️  No verification - test completed without errors\n")
            result = {
                'test': test_name,
                'passed': True,
                'found': [],
                'missing': []
            }
            self.results.append(result)
            return True

    def _inject_input(self, event_data, start_time):
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
            'r': pygame.K_r,
            'f': pygame.K_f,
            'u': pygame.K_u,
            'o': pygame.K_o,
            'p': pygame.K_p,
            'semicolon': pygame.K_SEMICOLON,
            'space': pygame.K_SPACE,
            'g': pygame.K_g,
            'backspace': pygame.K_BACKSPACE,
            'esc': pygame.K_ESCAPE
        }

        if key_name not in key_map:
            print(f"⚠️  Unknown key '{key_name}'")
            return

        key_code = key_map[key_name]
        elapsed = time.time() - start_time

        if action == 'press':
            event = pygame.event.Event(pygame.KEYDOWN, {'key': key_code})
            pygame.event.post(event)
            print(f"[{elapsed:.2f}s] ⌨️  Press {key_name.upper()}")
        elif action == 'release':
            event = pygame.event.Event(pygame.KEYUP, {'key': key_code})
            pygame.event.post(event)

    def run_all_tests(self):
        """Run all test cases and report results"""
        print(f"\n{'#'*70}")
        print(f"# TAS TEST SUITE - Running {len(self.test_cases)} tests")
        print(f"{'#'*70}\n")

        passed = 0
        failed = 0

        for test_name in self.test_cases.keys():
            success = self.run_test(test_name, verbose=True)
            if success:
                passed += 1
            else:
                failed += 1
            time.sleep(0.5)  # Brief pause between tests

        # Final report
        print(f"\n{'#'*70}")
        print(f"# FINAL RESULTS")
        print(f"{'#'*70}")
        print(f"✅ Passed: {passed}/{len(self.test_cases)}")
        print(f"❌ Failed: {failed}/{len(self.test_cases)}")
        print(f"{'#'*70}\n")

        return failed == 0

    def list_tests(self):
        """List all available tests"""
        print(f"\n{'='*70}")
        print(f"AVAILABLE TEST CASES")
        print(f"{'='*70}\n")

        for name, test in self.test_cases.items():
            print(f"📋 {name:25} - {test['description']}")
            print(f"   {'':25}   Duration: {test['duration']}s")
            print(f"   {'':25}   Verifications: {len(test.get('expected_logs', []))}")
            print()

        print(f"{'='*70}\n")


def main():
    """Main entry point"""
    runner = VerifiedTestRunner()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tests/verified_test_runner.py <test_name>")
        print("  python tests/verified_test_runner.py all")
        print("  python tests/verified_test_runner.py list")
        runner.list_tests()
        return

    command = sys.argv[1]

    if command == 'list':
        runner.list_tests()
    elif command == 'all':
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    else:
        success = runner.run_test(command, verbose=True)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
