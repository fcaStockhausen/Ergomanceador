"""
Testing Panel: Element experimentation and distance analysis.

Follows the workflow from DESIGNER_GUIDE_BEHAVIOR_TUNING.md:
1. Queue elements (1-6)
2. View property vector
3. Check distances to all prototypes
4. Decision helper (create new / tune existing)
"""

import pygame
import numpy as np
from typing import Optional, Dict, List
from config.colors import WHITE, BLACK


class TestingPanel:
    """Left panel for element testing and distance analysis"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Fonts
        self.font_title = pygame.font.Font(None, 32)
        self.font_section = pygame.font.Font(None, 24)
        self.font_text = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

        # Colors
        self.bg_color = (20, 20, 30)
        self.border_color = (100, 100, 150)
        self.section_color = (30, 30, 50)

        # Scroll state
        self.scroll_offset = 0

    def render(self, screen, magic_system, spell_data: Optional[Dict], distances: Optional[List]):
        """Render the testing panel"""
        # Background panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, panel_rect)
        pygame.draw.rect(screen, self.border_color, panel_rect, 2)

        # Title
        title = self.font_title.render("🧪 Spell Testing Lab", True, (255, 200, 100))
        screen.blit(title, (self.x + 10, self.y + 10))

        y_offset = 60

        # Section 1: Element Queue
        y_offset = self._draw_element_queue(screen, magic_system, y_offset)

        # Section 2: Property Vector (if spell queued)
        if spell_data:
            y_offset = self._draw_property_vector(screen, spell_data, y_offset)

        # Section 3: Distance Analysis (if spell queued)
        if spell_data and distances:
            y_offset = self._draw_distance_analysis(screen, distances, y_offset)

        # Section 4: Decision Helper (if spell queued)
        if spell_data and distances:
            y_offset = self._draw_decision_helper(screen, spell_data, distances, y_offset)

        # Instructions at bottom
        self._draw_instructions(screen)

    def _draw_element_queue(self, screen, magic_system, y_offset):
        """Draw current element queue"""
        # Section header
        section_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, 30)
        pygame.draw.rect(screen, self.section_color, section_rect)
        header = self.font_section.render("Step 1: Queue Elements", True, WHITE)
        screen.blit(header, (self.x + 15, self.y + y_offset + 5))
        y_offset += 40

        # Element queue display
        queue = magic_system.element_queue
        queue_text = " → ".join([e.upper() for e in queue]) if queue else "(empty)"
        queue_surf = self.font_text.render(queue_text, True, (100, 255, 200))
        screen.blit(queue_surf, (self.x + 20, self.y + y_offset))
        y_offset += 30

        # Queue status
        status = f"{len(queue)}/{magic_system.max_queue_size} elements"
        status_surf = self.font_small.render(status, True, (150, 150, 150))
        screen.blit(status_surf, (self.x + 20, self.y + y_offset))
        y_offset += 25

        # Element hints
        hint = "Press Q/E/R/F/U/O/P/; to queue elements"
        hint_surf = self.font_small.render(hint, True, (120, 120, 150))
        screen.blit(hint_surf, (self.x + 20, self.y + y_offset))
        y_offset += 35

        return y_offset

    def _draw_property_vector(self, screen, spell_data, y_offset):
        """Draw 12D property vector"""
        # Section header
        section_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, 30)
        pygame.draw.rect(screen, self.section_color, section_rect)
        header = self.font_section.render("Step 2: Property Vector (12D)", True, WHITE)
        screen.blit(header, (self.x + 15, self.y + y_offset + 5))
        y_offset += 40

        # Get property vector
        vector = spell_data['vector']

        # Property names and values
        properties = [
            ('Thermal Flux', vector.thermal_flux / 2.0),
            ('Avg Temperature', vector.avg_temperature / 2000.0),
            ('Temp Differential', vector.temp_differential / 2000.0),
            ('State Transition', vector.state_transition_energy / 1000.0),
            ('Phase Diversity', vector.phase_diversity),
            ('Density Gradient', vector.density_gradient),
            ('Avg Density', vector.avg_density),
            ('Volatility', vector.volatility_index),
            ('Chaos Factor', vector.chaos_factor),
            ('Total Energy', vector.total_energy / 400.0),
            ('Energy Density', vector.energy_density / 150.0),
            ('Polarity', vector.polarity_tension)
        ]

        for name, value in properties:
            # Property name
            name_surf = self.font_small.render(f"{name}:", True, (180, 180, 180))
            screen.blit(name_surf, (self.x + 20, self.y + y_offset))

            # Value bar
            bar_x = self.x + 180
            bar_y = self.y + y_offset + 2
            bar_width = 200
            bar_height = 12

            # Background
            pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_width, bar_height))

            # Value fill (normalize to 0-1, handle negative polarity)
            if value < 0:
                # Negative value (polarity can be -1 to 1)
                fill_width = int(abs(value) * bar_width / 2)
                fill_x = bar_x + bar_width // 2 - fill_width
                pygame.draw.rect(screen, (255, 100, 100), (fill_x, bar_y, fill_width, bar_height))
            else:
                fill_width = int(value * bar_width)
                if value > 1.0:
                    fill_width = bar_width
                if name == 'Polarity':
                    # Polarity uses center as zero
                    fill_width = int(value * bar_width / 2)
                    fill_x = bar_x + bar_width // 2
                else:
                    fill_x = bar_x
                pygame.draw.rect(screen, (100, 200, 255), (fill_x, bar_y, fill_width, bar_height))

            # Value text
            value_text = f"{value:.3f}"
            value_surf = self.font_small.render(value_text, True, (200, 200, 200))
            screen.blit(value_surf, (bar_x + bar_width + 10, self.y + y_offset))

            y_offset += 18

        y_offset += 10
        return y_offset

    def _draw_distance_analysis(self, screen, distances, y_offset):
        """Draw distances to all prototypes"""
        # Section header
        section_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, 30)
        pygame.draw.rect(screen, self.section_color, section_rect)
        header = self.font_section.render("Step 3: Distances to Prototypes", True, WHITE)
        screen.blit(header, (self.x + 15, self.y + y_offset + 5))
        y_offset += 40

        # Distance list (sorted, showing top 8)
        for i, (behavior, distance) in enumerate(distances[:8]):
            # Color code by distance
            if distance < 0.8:
                color = (100, 255, 100)  # Strong match - green
                label = "STRONG"
            elif distance < 1.2:
                color = (255, 255, 100)  # Medium match - yellow
                label = "MEDIUM"
            elif distance < 1.6:
                color = (255, 150, 100)  # Weak match - orange
                label = "WEAK"
            else:
                color = (150, 150, 150)  # No match - gray
                label = "NONE"

            # Behavior name
            name_surf = self.font_text.render(f"{i+1}. {behavior}:", True, color)
            screen.blit(name_surf, (self.x + 20, self.y + y_offset))

            # Distance value
            dist_text = f"{distance:.3f} ({label})"
            dist_surf = self.font_small.render(dist_text, True, color)
            screen.blit(dist_surf, (self.x + 200, self.y + y_offset + 2))

            y_offset += 25

        y_offset += 15
        return y_offset

    def _draw_decision_helper(self, screen, spell_data, distances, y_offset):
        """Draw decision helper based on distances"""
        # Section header
        section_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, 30)
        pygame.draw.rect(screen, self.section_color, section_rect)
        header = self.font_section.render("Step 4: Decision Helper", True, WHITE)
        screen.blit(header, (self.x + 15, self.y + y_offset + 5))
        y_offset += 40

        nearest_behavior, nearest_distance = distances[0]

        # Decision logic
        if nearest_distance > 1.2:
            # Far from all prototypes - suggest new
            recommendation = "CREATE NEW PROTOTYPE"
            reason = f"Spell is far from all behaviors (nearest: {nearest_behavior} at {nearest_distance:.3f})"
            action_color = (100, 255, 100)
            action_text = "Press F2 to tag as new prototype"
        elif nearest_distance < 0.8:
            # Very close match - good
            recommendation = "WELL CLASSIFIED"
            reason = f"Spell strongly matches '{nearest_behavior}' (distance {nearest_distance:.3f})"
            action_color = (100, 255, 255)
            action_text = "No action needed - classification is good!"
        else:
            # Medium distance - might need tuning
            recommendation = f"CONSIDER TUNING '{nearest_behavior.upper()}'"
            reason = f"Spell moderately close to '{nearest_behavior}' ({nearest_distance:.3f})"
            action_color = (255, 255, 100)
            action_text = "Switch to Editor (TAB) to tune prototype"

        # Recommendation
        rec_surf = self.font_text.render(recommendation, True, action_color)
        screen.blit(rec_surf, (self.x + 20, self.y + y_offset))
        y_offset += 30

        # Reason
        reason_lines = self._wrap_text(reason, 550)
        for line in reason_lines:
            line_surf = self.font_small.render(line, True, (180, 180, 180))
            screen.blit(line_surf, (self.x + 20, self.y + y_offset))
            y_offset += 20

        y_offset += 10

        # Action hint
        action_surf = self.font_small.render(action_text, True, (150, 150, 255))
        screen.blit(action_surf, (self.x + 20, self.y + y_offset))
        y_offset += 30

        return y_offset

    def _draw_instructions(self, screen):
        """Draw instructions at bottom"""
        y = self.y + self.height - 80

        instructions = [
            "F1: Exit Designer Mode | F2: Tag New Prototype",
            "TAB: Switch to Editor | BACKSPACE: Clear Queue",
            "Q/E/R/F/U/O/P/; : Queue Elements"
        ]

        for i, text in enumerate(instructions):
            surf = self.font_small.render(text, True, (120, 120, 150))
            screen.blit(surf, (self.x + 10, y + i * 20))

    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max_width pixels"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = self.font_small.render(test_line, True, WHITE)
            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def handle_input(self, event, magic_system, spell_data):
        """Handle input events specific to testing panel"""
        # Currently no interactive elements
        pass
