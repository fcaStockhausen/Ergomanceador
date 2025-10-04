"""Isometric coordinate transformation functions"""

from config.settings import TILE_WIDTH, TILE_HEIGHT


def cart_to_iso(x, y):
    """Convert cartesian coordinates to isometric screen coordinates"""
    iso_x = (x - y) * (TILE_WIDTH // 2)
    iso_y = (x + y) * (TILE_HEIGHT // 2)
    return iso_x, iso_y


def iso_to_cart(iso_x, iso_y):
    """Convert isometric screen coordinates to cartesian coordinates"""
    cart_x = (iso_x / (TILE_WIDTH // 2) + iso_y / (TILE_HEIGHT // 2)) / 2
    cart_y = (iso_y / (TILE_HEIGHT // 2) - iso_x / (TILE_WIDTH // 2)) / 2
    return cart_x, cart_y


def screen_to_cart(screen_dx, screen_dy):
    """
    Convert screen-space direction (WASD perspective) to cartesian movement.
    In isometric view:
    - Screen UP (W) should move in direction that appears up on screen
    - Screen DOWN (S) should move down on screen
    - Screen LEFT (A) should move left on screen
    - Screen RIGHT (D) should move right on screen

    Screen up = negative Y in screen = requires moving in iso space
    We need to find cartesian dx, dy that produces the desired iso movement
    """
    # For isometric projection where iso_x = (x-y)*32 and iso_y = (x+y)*16
    # To move up on screen (negative screen_dy), we want negative iso_y
    # To move right on screen (positive screen_dx), we want positive iso_x

    # Inverse transformation to get cartesian deltas from desired iso deltas
    cart_dx = (screen_dx / (TILE_WIDTH // 2) + screen_dy / (TILE_HEIGHT // 2)) / 2
    cart_dy = (screen_dy / (TILE_HEIGHT // 2) - screen_dx / (TILE_WIDTH // 2)) / 2

    return cart_dx, cart_dy
