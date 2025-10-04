"""Unit tests for Target cursor with smooth aiming"""

import pytest
import math


class TestTargetAiming:
    """Test target aiming direction"""

    def test_initial_state(self, target):
        """Target should start centered on player"""
        assert target.aim_direction == (0, 0), "Should start with no direction"
        assert target.aim_distance == 0.0, "Should start centered"

    def test_set_aim_direction_keyboard(self, target):
        """Keyboard aiming should set target direction for interpolation"""
        target.set_aim_direction(1, 0, smooth=True)

        assert target.target_direction == (1.0, 0.0), "Target direction should be set"
        assert target.aim_direction != (1.0, 0.0), "Current direction should not snap (smooth mode)"

    def test_set_aim_direction_controller(self, target):
        """Controller aiming should set direction instantly"""
        target.set_aim_direction(1, 0, smooth=False)

        assert target.aim_direction == (1.0, 0.0), "Should set instantly (controller)"
        assert target.aim_distance == target.max_distance, "Should move to max distance"

    def test_aim_direction_normalizes(self, target):
        """Aim direction should be normalized to unit vector"""
        target.set_aim_direction(3, 4, smooth=False)  # 3-4-5 triangle

        # Should be normalized (length = 1)
        magnitude = math.sqrt(target.aim_direction[0]**2 + target.aim_direction[1]**2)
        assert abs(magnitude - 1.0) < 0.001, "Direction should be normalized"
        assert abs(target.aim_direction[0] - 0.6) < 0.001, "X component should be 0.6"
        assert abs(target.aim_direction[1] - 0.8) < 0.001, "Y component should be 0.8"

    def test_zero_input_returns_to_center(self, target):
        """Zero input should return cursor to center"""
        target.set_aim_direction(1, 0, smooth=False)
        assert target.aim_distance > 0, "Should be away from center"

        target.set_aim_direction(0, 0, smooth=False)

        assert target.aim_direction == (0, 0), "Direction should be zero"
        assert target.aim_distance == 0.0, "Should return to center"


class TestSmoothInterpolation:
    """Test keyboard smooth aim interpolation"""

    def test_interpolation_moves_toward_target(self, target):
        """Aim should interpolate toward target direction"""
        target.set_aim_direction(1, 0, smooth=True)  # Aim right
        initial_x = target.aim_direction[0]

        target.update(0.1)  # Update 100ms

        assert target.aim_direction[0] > initial_x, "Should move toward target"

    def test_interpolation_reaches_target(self, target):
        """Aim should eventually reach target direction"""
        target.set_aim_direction(1, 0, smooth=True)  # Aim right

        # Update for long enough to reach target
        for _ in range(20):  # 20 frames @ 50ms = 1 second
            target.update(0.05)

        # Should be very close to target
        assert abs(target.aim_direction[0] - 1.0) < 0.01, "Should reach target X"
        assert abs(target.aim_direction[1] - 0.0) < 0.01, "Should reach target Y"

    def test_interpolation_speed_configurable(self, target):
        """Lerp speed should affect interpolation rate"""
        target.keyboard_lerp_speed = 100.0  # Very fast

        target.set_aim_direction(1, 0, smooth=True)
        target.update(0.01)  # Short time so fast doesn't complete

        fast_progress = target.aim_direction[0]

        # Reset and test slow speed
        target.aim_direction = (0, 0)
        target.target_direction = (0, 0)
        target.keyboard_lerp_speed = 1.0  # Very slow

        target.set_aim_direction(1, 0, smooth=True)
        target.update(0.01)

        slow_progress = target.aim_direction[0]

        assert fast_progress > slow_progress, f"Fast lerp ({fast_progress}) should progress more than slow ({slow_progress})"

    def test_interpolation_diagonal(self, target):
        """Should interpolate correctly in diagonal directions"""
        target.set_aim_direction(1, 1, smooth=True)  # Northeast

        target.update(0.1)

        # Should move in both X and Y
        assert target.aim_direction[0] > 0, "X should increase"
        assert target.aim_direction[1] > 0, "Y should increase"


class TestTargetFollowPlayer:
    """Test Diablo 3 style target positioning"""

    def test_follow_player_centered(self, target, player):
        """Target should be on player when aim_distance is 0"""
        target.aim_distance = 0.0
        target.follow_player(player)

        assert target.cart_x == player.cart_x, "Should be on player X"
        assert target.cart_y == player.cart_y, "Should be on player Y"

    def test_follow_player_offset(self, target, player):
        """Target should be offset from player based on aim direction"""
        target.aim_direction = (1.0, 0.0)  # Right
        target.aim_distance = 3.0
        target.follow_player(player)

        assert target.cart_x == player.cart_x + 3.0, "Should be 3 units right of player"
        assert target.cart_y == player.cart_y, "Should have same Y as player"

    def test_follow_player_diagonal(self, target, player):
        """Target should offset diagonally correctly"""
        # Normalized diagonal (1,1) -> (0.707, 0.707)
        target.aim_direction = (1/math.sqrt(2), 1/math.sqrt(2))
        target.aim_distance = 2.0
        target.follow_player(player)

        expected_offset = 2.0 / math.sqrt(2)  # ~1.414
        assert abs(target.cart_x - (player.cart_x + expected_offset)) < 0.01
        assert abs(target.cart_y - (player.cart_y + expected_offset)) < 0.01

    def test_follow_player_stays_in_bounds(self, target, player):
        """Target should clamp to map boundaries"""
        player.cart_x = 19.0  # Near right edge
        target.aim_direction = (1.0, 0.0)  # Aim right
        target.aim_distance = 5.0  # Would go to 24, but max is 20

        target.follow_player(player)

        assert target.cart_x <= 20.0, "Should not exceed right boundary"
        assert target.cart_x >= 0.0, "Should not go below left boundary"
