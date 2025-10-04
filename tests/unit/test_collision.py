"""Unit tests for collision detection"""

import pytest
from physics.collision import circle_collision, CollisionChecker


class TestCircleCollision:
    """Test circle-circle collision math"""

    def test_collision_touching_circles(self):
        """Circles touching at edge should collide"""
        # Two circles radius 1, distance 2 apart (touching)
        result = circle_collision(0, 0, 1.0, 2, 0, 1.0)
        assert result is True, "Touching circles should collide"

    def test_collision_overlapping_circles(self):
        """Overlapping circles should collide"""
        # Two circles radius 1, distance 1 apart (overlapping)
        result = circle_collision(0, 0, 1.0, 1, 0, 1.0)
        assert result is True, "Overlapping circles should collide"

    def test_no_collision_distant_circles(self):
        """Distant circles should not collide"""
        # Two circles radius 1, distance 5 apart
        result = circle_collision(0, 0, 1.0, 5, 0, 1.0)
        assert result is False, "Distant circles should not collide"

    def test_collision_same_position(self):
        """Circles at same position should collide"""
        result = circle_collision(0, 0, 1.0, 0, 0, 1.0)
        assert result is True, "Same position should collide"

    def test_collision_diagonal(self):
        """Collision should work in diagonal direction"""
        # Two circles radius 1, sqrt(2) apart diagonally
        result = circle_collision(0, 0, 1.0, 1, 1, 1.0)
        assert result is True, "Diagonal touching should collide"

    def test_collision_different_radii(self):
        """Should handle different radii correctly"""
        # Small circle (r=0.5) and large circle (r=2.0) distance 2.5 apart
        result = circle_collision(0, 0, 0.5, 2.5, 0, 2.0)
        assert result is True, "Should collide with combined radius = 2.5"

        # Same but distance 3 apart
        result = circle_collision(0, 0, 0.5, 3, 0, 2.0)
        assert result is False, "Should not collide at distance 3"


class TestCollisionChecker:
    """Test CollisionChecker utility class"""

    def test_projectile_vs_entity_hit(self):
        """Projectile should hit entity when close enough"""
        # Create mock projectile
        class MockProjectile:
            cart_x = 10.0
            cart_y = 10.0

        # Create mock entity
        class MockEntity:
            cart_x = 10.5  # 0.5 units away
            cart_y = 10.0

        projectile = MockProjectile()
        entity = MockEntity()

        result = CollisionChecker.projectile_vs_entity(projectile, entity, entity_radius=0.5)
        assert result is True, "Projectile should hit entity"

    def test_projectile_vs_entity_miss(self):
        """Projectile should miss entity when far enough"""
        class MockProjectile:
            cart_x = 0.0
            cart_y = 0.0

        class MockEntity:
            cart_x = 10.0
            cart_y = 10.0

        projectile = MockProjectile()
        entity = MockEntity()

        result = CollisionChecker.projectile_vs_entity(projectile, entity, entity_radius=0.5)
        assert result is False, "Projectile should miss distant entity"

    def test_projectile_vs_entities_finds_hit(self):
        """Should find hit among multiple entities"""
        class MockProjectile:
            cart_x = 5.0
            cart_y = 5.0

        class MockEntity:
            def __init__(self, x, y):
                self.cart_x = x
                self.cart_y = y

        projectile = MockProjectile()
        entities = [
            MockEntity(0, 0),    # Far
            MockEntity(10, 10),  # Far
            MockEntity(5.3, 5.0),  # Close! (0.3 units away)
            MockEntity(15, 15),  # Far
        ]

        hit_entity = CollisionChecker.projectile_vs_entities(projectile, entities, entity_radius=0.5)

        assert hit_entity is not None, "Should find a hit"
        assert hit_entity.cart_x == 5.3, "Should return the close entity"

    def test_projectile_vs_entities_no_hit(self):
        """Should return None when no entities hit"""
        class MockProjectile:
            cart_x = 0.0
            cart_y = 0.0

        class MockEntity:
            def __init__(self, x, y):
                self.cart_x = x
                self.cart_y = y

        projectile = MockProjectile()
        entities = [
            MockEntity(10, 10),
            MockEntity(20, 20),
            MockEntity(30, 30),
        ]

        hit_entity = CollisionChecker.projectile_vs_entities(projectile, entities, entity_radius=0.5)

        assert hit_entity is None, "Should return None with no hits"
