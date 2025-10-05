"""
Property Vector Display - Shows the 12D property vector visualization in HUD

Displays the current spell's property vector with visual bars.
"""

import pygame
from config.colors import WHITE, GRAY, CYAN, YELLOW, RED, GREEN, BLUE


def draw_property_vector(screen, spell_data, x=10, y=400):
    """
    Draw property vector visualization for current spell.

    Args:
        screen: Pygame screen
        spell_data: Spell dict with 'property_vector' and 'behavior_probabilities'
        x, y: Top-left position
    """
    if not spell_data or 'property_vector' not in spell_data:
        return

    vector = spell_data['property_vector']
    behavior = spell_data.get('behavior', 'unknown')
    probabilities = spell_data.get('behavior_probabilities', {})

    font_small = pygame.font.Font(None, 18)
    font_title = pygame.font.Font(None, 22)

    # Background panel
    panel_width = 280
    panel_height = 240
    panel = pygame.Surface((panel_width, panel_height))
    panel.set_alpha(200)
    panel.fill((20, 20, 30))
    screen.blit(panel, (x, y))

    # Title
    title = font_title.render("PROPERTY VECTOR", True, CYAN)
    screen.blit(title, (x + 10, y + 5))

    # Behavior classification
    behavior_text = font_small.render(f"Behavior: {behavior.upper()}", True, YELLOW)
    screen.blit(behavior_text, (x + 10, y + 25))

    # Top 3 probabilities
    if probabilities:
        sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
        prob_text = f"{sorted_probs[0][0]} {sorted_probs[0][1]*100:.0f}%"
        if len(sorted_probs) > 1:
            prob_text += f", {sorted_probs[1][0]} {sorted_probs[1][1]*100:.0f}%"
        prob_surface = font_small.render(prob_text, True, GRAY)
        screen.blit(prob_surface, (x + 10, y + 42))

    # Property bars
    properties = [
        ("Thermal Flux", vector.thermal_flux, 2.0, YELLOW),
        ("Temp Diff", vector.temp_differential / 2000.0, 1.0, RED),
        ("Volatility", vector.volatility_index, 1.0, RED),
        ("Density", vector.avg_density, 1.0, BLUE),
        ("Chaos", vector.chaos_factor, 1.0, (255, 100, 255)),
        ("Energy", vector.total_energy / 400.0, 1.0, YELLOW),
        ("Polarity", abs(vector.polarity_tension), 1.0, GREEN if vector.polarity_tension > 0 else (150, 150, 255)),
    ]

    y_offset = y + 65
    bar_width = 180
    bar_height = 16

    for prop_name, value, max_val, color in properties:
        # Property name
        name_surf = font_small.render(prop_name, True, WHITE)
        screen.blit(name_surf, (x + 10, y_offset))

        # Value bar background
        pygame.draw.rect(screen, (40, 40, 50), (x + 100, y_offset + 2, bar_width, bar_height - 4))

        # Value bar foreground
        filled_width = int(min(value / max_val, 1.0) * bar_width)
        if filled_width > 0:
            pygame.draw.rect(screen, color, (x + 100, y_offset + 2, filled_width, bar_height - 4))

        # Value text
        value_text = f"{value:.2f}" if value < 10 else f"{value:.0f}"
        val_surf = font_small.render(value_text, True, GRAY)
        screen.blit(val_surf, (x + 100 + bar_width + 5, y_offset))

        y_offset += bar_height + 2


def draw_behavior_distances(screen, spell_data, x=300, y=400):
    """
    Draw distances to all behavior regions (DEBUG).

    Shows which behaviors are "nearby" in manifold.
    """
    if not spell_data or 'property_vector' not in spell_data:
        return

    from magic.behavior_manifold import BehaviorManifold
    manifold = BehaviorManifold()

    vector = spell_data['property_vector']
    distances = manifold.get_behavior_distances(vector)

    font_small = pygame.font.Font(None, 16)
    font_title = pygame.font.Font(None, 20)

    # Background panel
    panel_width = 200
    panel_height = 200
    panel = pygame.Surface((panel_width, panel_height))
    panel.set_alpha(180)
    panel.fill((20, 20, 30))
    screen.blit(panel, (x, y))

    # Title
    title = font_title.render("MANIFOLD DISTANCES", True, CYAN)
    screen.blit(title, (x + 10, y + 5))

    # Sort by distance
    sorted_distances = sorted(distances.items(), key=lambda item: item[1])

    y_offset = y + 28
    for behavior_name, distance in sorted_distances[:8]:  # Top 8
        # Color based on distance (closer = brighter)
        brightness = int(255 * (1.0 - min(distance / 2.0, 1.0)))
        color = (brightness, brightness, brightness)

        # Behavior name
        name_surf = font_small.render(behavior_name[:10], True, color)
        screen.blit(name_surf, (x + 10, y_offset))

        # Distance bar
        bar_width = 80
        bar_height = 12
        filled_width = int(min(distance / 2.0, 1.0) * bar_width)

        pygame.draw.rect(screen, (40, 40, 50), (x + 100, y_offset, bar_width, bar_height))
        if filled_width > 0:
            pygame.draw.rect(screen, (100, 200, 255), (x + 100, y_offset, filled_width, bar_height))

        # Distance value
        dist_text = f"{distance:.2f}"
        dist_surf = font_small.render(dist_text, True, GRAY)
        screen.blit(dist_surf, (x + 100 + bar_width + 5, y_offset))

        y_offset += 18
