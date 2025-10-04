"""Collision detection for projectiles and entities"""

import math


def circle_collision(x1, y1, radius1, x2, y2, radius2):
    """
    Check collision between two circles.

    Args:
        x1, y1: Center of first circle (cartesian coordinates)
        radius1: Radius of first circle
        x2, y2: Center of second circle
        radius2: Radius of second circle

    Returns:
        True if circles overlap, False otherwise
    """
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    return distance < (radius1 + radius2)


def point_in_circle(px, py, cx, cy, radius):
    """
    Check if point is inside circle.

    Args:
        px, py: Point coordinates
        cx, cy: Circle center
        radius: Circle radius

    Returns:
        True if point is inside circle
    """
    dx = px - cx
    dy = py - cy
    distance = math.sqrt(dx**2 + dy**2)
    return distance <= radius


class CollisionChecker:
    """Helper class for checking projectile vs entity collisions"""

    @staticmethod
    def projectile_vs_entity(projectile, entity, entity_radius=0.5):
        """
        Check if projectile hits entity.

        Args:
            projectile: Projectile object with cart_x, cart_y
            entity: Entity object with cart_x, cart_y
            entity_radius: Collision radius in cartesian units

        Returns:
            True if collision detected
        """
        projectile_radius = 0.3  # Small collision radius for projectiles

        return circle_collision(
            projectile.cart_x, projectile.cart_y, projectile_radius,
            entity.cart_x, entity.cart_y, entity_radius
        )

    @staticmethod
    def projectile_vs_entities(projectile, entities, entity_radius=0.5):
        """
        Check projectile against list of entities.

        Args:
            projectile: Projectile object
            entities: List of entity objects
            entity_radius: Collision radius for entities

        Returns:
            First entity hit, or None
        """
        for entity in entities:
            if CollisionChecker.projectile_vs_entity(projectile, entity, entity_radius):
                return entity
        return None

    @staticmethod
    def aoe_vs_entities(center_x, center_y, radius, entities, entity_radius=0.5):
        """
        Check AoE explosion against entities.

        Args:
            center_x, center_y: AoE center (cartesian)
            radius: AoE radius
            entities: List of entities
            entity_radius: Entity collision radius

        Returns:
            List of entities hit
        """
        hit_entities = []
        for entity in entities:
            if circle_collision(center_x, center_y, radius, entity.cart_x, entity.cart_y, entity_radius):
                hit_entities.append(entity)
        return hit_entities
