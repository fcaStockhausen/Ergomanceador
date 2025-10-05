"""Terrain rendering for isometric view"""

import pygame
from rendering.isometric import cart_to_iso
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_terrain(screen, terrain_generator, camera_offset_x=0, camera_offset_y=0):
    """
    Draw terrain tiles in isometric view.

    Args:
        screen: Pygame surface
        terrain_generator: TerrainGenerator instance
        camera_offset_x, camera_offset_y: Camera offset for scrolling
    """
    # Tile size in isometric projection
    tile_width = 40
    tile_height = 20

    # Draw tiles from back to front for proper isometric layering
    for y in range(terrain_generator.height):
        for x in range(terrain_generator.width):
            tile = terrain_generator.get_tile(x, y)
            if not tile:
                continue

            # Convert to isometric screen coordinates
            iso_x, iso_y = cart_to_iso(x, y)
            screen_x = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
            screen_y = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y

            # Draw isometric diamond (rhombus) tile
            color = tile.color

            # Diamond points
            points = [
                (screen_x, screen_y - tile_height // 2),          # Top
                (screen_x + tile_width // 2, screen_y),           # Right
                (screen_x, screen_y + tile_height // 2),          # Bottom
                (screen_x - tile_width // 2, screen_y),           # Left
            ]

            # Fill tile
            pygame.draw.polygon(screen, color, points)

            # Optional: Draw element affinity indicator
            if tile.element_affinity:
                _draw_element_indicator(screen, screen_x, screen_y, tile.element_affinity)

            # Border (darker shade)
            border_color = tuple(max(0, c - 40) for c in color)
            pygame.draw.polygon(screen, border_color, points, 1)


def _draw_element_indicator(screen, x, y, element):
    """Draw small indicator showing element affinity"""
    from config.colors import ELEMENT_COLORS

    # Small circle in center of tile
    color = ELEMENT_COLORS.get(element, (255, 255, 255))

    # Pulsing effect (optional - could animate)
    radius = 3
    pygame.draw.circle(screen, color, (int(x), int(y)), radius)


def draw_terrain_overlay(screen, font, terrain_generator, player_x, player_y):
    """
    Draw terrain info overlay (current biome, bonuses).

    Args:
        screen: Pygame surface
        font: Pygame font
        terrain_generator: TerrainGenerator instance
        player_x, player_y: Player position
    """
    tile = terrain_generator.get_tile(int(player_x), int(player_y))
    if not tile:
        return

    # Draw biome info in bottom-left
    y_offset = SCREEN_HEIGHT - 120

    # Biome name
    biome_text = font.render(f"Biome: {tile.biome_type.capitalize()}", True, (255, 255, 255))
    screen.blit(biome_text, (10, y_offset))

    # Element affinity
    if tile.element_affinity:
        affinity_text = font.render(f"Element: {tile.element_affinity.capitalize()} ({tile.mana_bonus}x mana)", True, (150, 255, 150))
        screen.blit(affinity_text, (10, y_offset + 25))

        damage_text = font.render(f"Damage Bonus: {tile.damage_bonus}x", True, (255, 150, 150))
        screen.blit(damage_text, (10, y_offset + 50))
    else:
        affinity_text = font.render("Element: None", True, (150, 150, 150))
        screen.blit(affinity_text, (10, y_offset + 25))
