"""Spell preview UI - shows current spell properties"""

import pygame
from config.settings import SCREEN_HEIGHT
from config.colors import ORANGE
from rendering.ui.property_vector_display import draw_property_vector


def draw_spell_preview(screen, font, magic_system):
    """Draw current spell preview with enhanced properties (behavior, speed, etc.)"""
    full_effect = magic_system.get_full_effect()
    if full_effect:
        spell_y = SCREEN_HEIGHT - 140
        spell_font = pygame.font.Font(None, 22)

        # Spell name with behavior type
        behavior_display = full_effect.get('behavior', 'unknown').upper()
        name_text = f"Ready [{behavior_display}]: {full_effect['name']}"
        name_surface = spell_font.render(name_text, True, ORANGE)
        screen.blit(name_surface, (10, spell_y))

        # Spell properties (3 lines now)
        props_text = [
            f"Damage: {full_effect['damage']} | Speed: {full_effect.get('speed', 0):.1f} | Area: {full_effect['area']}",
            f"Duration: {full_effect['duration']:.1f}s | Temp: {full_effect['properties']['temperature']:.0f}K",
            f"Mana: {full_effect.get('mana_cost', 0)} | Knockback: {full_effect.get('knockback', 0):.1f}"
        ]

        for i, text in enumerate(props_text):
            surf = spell_font.render(text, True, (200, 200, 200))
            screen.blit(surf, (10, spell_y + 25 + i * 20))

        # NEW: Draw property vector visualization
        draw_property_vector(screen, full_effect, x=10, y=420)
