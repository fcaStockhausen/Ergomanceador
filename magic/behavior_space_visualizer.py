"""
Interactive Behavior Space Visualizer

Shows the 12D property manifold projected to 2D using PCA.
Displays behavior prototypes, current spell position, and emergent regions.

Usage:
    python magic/behavior_space_visualizer.py

    OR integrate into game as a separate window.
"""

import pygame
import numpy as np
from sklearn.decomposition import PCA
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from magic.behavior_manifold import BehaviorManifold
from magic.property_vector import PropertyVectorComputer
from magic.element_loader import load_elements_from_json


class BehaviorSpaceVisualizer:
    """Interactive visualization of the 12D behavior manifold projected to 2D"""

    def __init__(self, width=1200, height=900, high_dpi=True):
        pygame.init()

        # High DPI / Retina display support
        if high_dpi:
            # Create larger internal surface for smoother rendering
            self.render_scale = 2
            self.internal_width = width * self.render_scale
            self.internal_height = height * self.render_scale
            self.internal_screen = pygame.Surface((self.internal_width, self.internal_height))
            self.screen = pygame.display.set_mode((width, height), pygame.SCALED)
        else:
            self.render_scale = 1
            self.internal_width = width
            self.internal_height = height
            self.internal_screen = None
            self.screen = pygame.display.set_mode((width, height))

        pygame.display.set_caption("Behavior Space Visualizer - 12D Manifold")

        self.width = width
        self.height = height
        self.manifold = BehaviorManifold()
        self.elements = load_elements_from_json()

        # High quality fonts (scaled for retina)
        font_scale = self.render_scale
        self.font = pygame.font.Font(None, 28 * font_scale)
        self.font_small = pygame.font.Font(None, 22 * font_scale)
        self.font_title = pygame.font.Font(None, 48 * font_scale)
        self.font_huge = pygame.font.Font(None, 64 * font_scale)

        # Colors for behaviors
        self.behavior_colors = {
            'projectile': (100, 200, 255),    # Light blue
            'beam': (255, 200, 100),          # Orange
            'aoe': (255, 100, 100),           # Red
            'chain': (200, 100, 255),         # Purple
            'homing': (100, 255, 200),        # Cyan
            'area_denial': (150, 150, 150),   # Gray
            'heal': (100, 255, 100),          # Green
            'buff': (255, 255, 100),          # Yellow
        }

        # PCA for dimensionality reduction (12D → 2D)
        self.pca = None
        self.prototype_2d = {}
        self._compute_pca_projection()

        # Current spell state
        self.current_element_queue = []
        self.current_spell_2d = None

        # Mouse state
        self.hovered_behavior = None

    def _compute_pca_projection(self):
        """Compute PCA projection of behavior prototypes from 12D to 2D"""
        # Get all prototype vectors
        prototype_vectors = []
        behavior_names = []

        for region in self.manifold.regions:
            prototype_vectors.append(region.prototype)
            behavior_names.append(region.name)

        # Fit PCA
        self.pca = PCA(n_components=2)
        projected = self.pca.fit_transform(np.array(prototype_vectors))

        # Store 2D positions (normalized to screen space, accounting for render scale)
        margin = 120 * self.render_scale
        x_min, x_max = projected[:, 0].min(), projected[:, 0].max()
        y_min, y_max = projected[:, 1].min(), projected[:, 1].max()

        for i, name in enumerate(behavior_names):
            # Normalize to [margin, width-margin] and [margin, height-margin]
            x = margin + (projected[i, 0] - x_min) / (x_max - x_min) * (self.internal_width - 2*margin)
            y = margin + (projected[i, 1] - y_min) / (y_max - y_min) * (self.internal_height - 2*margin)
            self.prototype_2d[name] = (x, y)

    def _vector_to_2d(self, vector_12d):
        """Project a 12D property vector to 2D using PCA"""
        projected = self.pca.transform([vector_12d])[0]

        # Normalize to screen space (same as prototypes)
        margin = 100
        x_min, x_max = -2, 2  # Approximate range from PCA
        y_min, y_max = -2, 2

        # Get actual range from prototypes
        all_x = [p[0] for p in self.prototype_2d.values()]
        all_y = [p[1] for p in self.prototype_2d.values()]
        x_min_real, x_max_real = min(all_x) - margin, max(all_x) + margin
        y_min_real, y_max_real = min(all_y) - margin, max(all_y) + margin

        # Map projected point to screen space
        x = (projected[0] - self.pca.mean_[0]) / self.pca.components_[0].std() * (x_max_real - x_min_real)/2 + (x_min_real + x_max_real)/2
        y = (projected[1] - self.pca.mean_[1]) / self.pca.components_[1].std() * (y_max_real - y_min_real)/2 + (y_min_real + y_max_real)/2

        return (x, y)

    def update_current_spell(self, element_names):
        """Update the current spell visualization based on element queue"""
        if not element_names:
            self.current_spell_2d = None
            self.current_element_queue = []
            return

        # Get elements
        elems = [self.elements[name] for name in element_names if name in self.elements]
        if not elems:
            self.current_spell_2d = None
            return

        # Compute property vector
        vector = PropertyVectorComputer.compute(elems)

        # Convert to 12D array (same as manifold)
        vector_12d = np.array([
            vector.thermal_flux / 2.0,
            vector.avg_temperature / 2000.0,
            vector.temp_differential / 2000.0,
            vector.state_transition_energy / 1000.0,
            vector.phase_diversity,
            vector.density_gradient,
            vector.avg_density,
            vector.volatility_index,
            vector.chaos_factor,
            vector.total_energy / 400.0,
            vector.energy_density / 150.0,
            vector.polarity_tension
        ])

        # Project to 2D
        self.current_spell_2d = self._vector_to_2d(vector_12d)
        self.current_element_queue = element_names

    def _draw_smooth_circle(self, surface, color, pos, radius, border_color=None, border_width=0):
        """Draw anti-aliased circle with optional border"""
        import pygame.gfxdraw
        x, y = int(pos[0]), int(pos[1])
        r = int(radius)

        # Fill circle
        pygame.gfxdraw.filled_circle(surface, x, y, r, color)
        pygame.gfxdraw.aacircle(surface, x, y, r, color)

        # Border
        if border_color and border_width > 0:
            for i in range(border_width):
                pygame.gfxdraw.aacircle(surface, x, y, r - i, border_color)

    def draw(self):
        """Draw the visualization (high DPI)"""
        # Use internal screen for high-DPI rendering
        draw_surface = self.internal_screen if self.internal_screen else self.screen

        # Dark gradient background
        draw_surface.fill((15, 15, 25))

        # Title with glow effect
        title = self.font_title.render("BEHAVIOR MANIFOLD", True, (255, 255, 255))
        subtitle = self.font.render("12D Property Space → 2D Projection (PCA)", True, (150, 150, 200))
        draw_surface.blit(title, (self.internal_width//2 - title.get_width()//2, 30 * self.render_scale))
        draw_surface.blit(subtitle, (self.internal_width//2 - subtitle.get_width()//2, 80 * self.render_scale))

        # Draw Voronoi regions (simplified - connecting lines with transparency)
        for i, (name1, pos1) in enumerate(self.prototype_2d.items()):
            for name2, pos2 in list(self.prototype_2d.items())[i+1:]:
                pygame.draw.aaline(draw_surface, (40, 40, 60), pos1, pos2)

        # Draw behavior prototypes
        mouse_pos = pygame.mouse.get_pos()
        # Scale mouse position for internal rendering
        scaled_mouse = (mouse_pos[0] * self.render_scale, mouse_pos[1] * self.render_scale)
        self.hovered_behavior = None

        for behavior, pos in self.prototype_2d.items():
            color = self.behavior_colors.get(behavior, (200, 200, 200))

            # Check if mouse hovering (use scaled mouse position)
            dist_to_mouse = np.sqrt((scaled_mouse[0] - pos[0])**2 + (scaled_mouse[1] - pos[1])**2)
            hover_radius = 40 * self.render_scale
            is_hovered = dist_to_mouse < hover_radius

            if is_hovered:
                self.hovered_behavior = behavior

            # Draw glow effect when hovered
            if is_hovered:
                glow_color = tuple(min(255, c + 50) for c in color)
                for r in range(50 * self.render_scale, 20 * self.render_scale, -5 * self.render_scale):
                    alpha = int(20 * (r / (50 * self.render_scale)))
                    glow_c = (*glow_color, alpha)
                    self._draw_smooth_circle(draw_surface, glow_c, pos, r)

            # Draw prototype point (smooth anti-aliased)
            radius = 35 * self.render_scale if is_hovered else 22 * self.render_scale
            self._draw_smooth_circle(draw_surface, color, pos, radius, (255, 255, 255), 3 * self.render_scale)

            # Label with shadow
            label = self.font.render(behavior.upper(), True, (255, 255, 255))
            shadow = self.font.render(behavior.upper(), True, (0, 0, 0))
            label_pos = (pos[0] - label.get_width()//2, pos[1] + 45 * self.render_scale)
            draw_surface.blit(shadow, (label_pos[0] + 2, label_pos[1] + 2))
            draw_surface.blit(label, label_pos)

        # Draw current spell position
        if self.current_spell_2d:
            pos = self.current_spell_2d

            # Draw connecting line to nearest prototype (anti-aliased)
            nearest_behavior = min(
                self.prototype_2d.items(),
                key=lambda item: np.sqrt((item[1][0]-pos[0])**2 + (item[1][1]-pos[1])**2)
            )
            # Draw thick anti-aliased line
            pygame.draw.aaline(draw_surface, (120, 120, 255), pos, nearest_behavior[1])
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                p1 = (pos[0] + offset[0], pos[1] + offset[1])
                p2 = (nearest_behavior[1][0] + offset[0], nearest_behavior[1][1] + offset[1])
                pygame.draw.aaline(draw_surface, (100, 100, 230), p1, p2)

            # Pulsing glow effect for current spell
            import math
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2  # 0-1
            glow_size = int(60 * self.render_scale * (0.8 + 0.4 * pulse))
            for r in range(glow_size, 25 * self.render_scale, -5 * self.render_scale):
                alpha = int(40 * (r / glow_size))
                glow_c = (255, 255, 100, alpha)
                self._draw_smooth_circle(draw_surface, glow_c, pos, r)

            # Draw spell point (larger, glowing)
            self._draw_smooth_circle(draw_surface, (255, 255, 0), pos, 28 * self.render_scale,
                                   (255, 255, 255), 4 * self.render_scale)

            # Draw element queue with background
            elements_text = " + ".join([e.title() for e in self.current_element_queue])
            elem_surf = self.font.render(elements_text, True, (255, 220, 50))
            elem_shadow = self.font.render(elements_text, True, (0, 0, 0))
            text_x = pos[0] - elem_surf.get_width()//2
            text_y = pos[1] - 60 * self.render_scale

            # Background panel
            padding = 10 * self.render_scale
            panel_rect = (text_x - padding, text_y - padding,
                         elem_surf.get_width() + 2*padding, elem_surf.get_height() + 2*padding)
            pygame.draw.rect(draw_surface, (30, 30, 50, 200), panel_rect, border_radius=int(8 * self.render_scale))
            pygame.draw.rect(draw_surface, (255, 220, 50), panel_rect, width=2, border_radius=int(8 * self.render_scale))

            draw_surface.blit(elem_shadow, (text_x + 2, text_y + 2))
            draw_surface.blit(elem_surf, (text_x, text_y))

        # Draw hover info
        if self.hovered_behavior:
            # Find region
            region = next(r for r in self.manifold.regions if r.name == self.hovered_behavior)

            # Info panel (high-DPI scaled)
            info_x = 20 * self.render_scale
            info_y = self.internal_height - 280 * self.render_scale
            panel_width = 420 * self.render_scale
            panel_height = 260 * self.render_scale

            # Semi-transparent background with glow border
            pygame.draw.rect(draw_surface, (25, 25, 40), (info_x, info_y, panel_width, panel_height),
                           border_radius=int(12 * self.render_scale))
            pygame.draw.rect(draw_surface, self.behavior_colors[self.hovered_behavior],
                           (info_x, info_y, panel_width, panel_height),
                           width=int(4 * self.render_scale), border_radius=int(12 * self.render_scale))

            # Behavior name (large)
            name_surf = self.font_title.render(f"{self.hovered_behavior.upper()}", True, (255, 255, 255))
            draw_surface.blit(name_surf, (info_x + 15 * self.render_scale, info_y + 15 * self.render_scale))

            # Prototype properties (show key dimensions with bars)
            proto = region.prototype
            y_offset = 70 * self.render_scale
            props = [
                ("Thermal Flux", proto[0], 1.0),
                ("Temp Diff", proto[2], 1.0),
                ("Volatility", proto[7], 1.0),
                ("Chaos", proto[8], 1.0),
                ("Energy", proto[9], 1.0),
                ("Polarity", proto[11], 1.0),
            ]

            for prop_name, prop_val, prop_max in props:
                # Property name and value
                prop_text = f"{prop_name}: {prop_val:.2f}"
                prop_surf = self.font_small.render(prop_text, True, (220, 220, 220))
                draw_surface.blit(prop_surf, (info_x + 15 * self.render_scale, info_y + y_offset))

                # Value bar
                bar_x = info_x + 200 * self.render_scale
                bar_y = info_y + y_offset + 5 * self.render_scale
                bar_width = 200 * self.render_scale
                bar_height = 12 * self.render_scale
                fill_width = int(bar_width * (prop_val / prop_max))

                # Background
                pygame.draw.rect(draw_surface, (40, 40, 60), (bar_x, bar_y, bar_width, bar_height),
                               border_radius=int(6 * self.render_scale))
                # Fill
                if fill_width > 0:
                    pygame.draw.rect(draw_surface, self.behavior_colors[self.hovered_behavior],
                                   (bar_x, bar_y, fill_width, bar_height),
                                   border_radius=int(6 * self.render_scale))

                y_offset += 30 * self.render_scale

        # Instructions (bottom)
        instructions = [
            "🎮 Queue elements in game to see spell move through space",
            "🖱️  Hover over prototypes to see properties",
            "✨ Gaps between prototypes = Emergent Behaviors!"
        ]

        y_pos = self.internal_height - 100 * self.render_scale
        for instruction in instructions:
            surf = self.font_small.render(instruction, True, (120, 120, 150))
            draw_surface.blit(surf, (20 * self.render_scale, y_pos))
            y_pos += 28 * self.render_scale

        # Scale down to display if using high-DPI rendering
        if self.internal_screen:
            scaled = pygame.transform.smoothscale(self.internal_screen, (self.width, self.height))
            self.screen.blit(scaled, (0, 0))

        pygame.display.flip()

    def run_standalone(self):
        """Run as standalone window for testing"""
        clock = pygame.time.Clock()
        running = True

        # Test cases
        test_spells = [
            ['fire'],
            ['fire', 'water'],
            ['nature'],
            ['fire', 'fire', 'fire'],
            ['earth', 'nature'],
        ]
        test_index = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Cycle through test spells
                        self.update_current_spell(test_spells[test_index])
                        test_index = (test_index + 1) % len(test_spells)
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.draw()
            clock.tick(60)

        pygame.quit()


def main():
    """Standalone test mode"""
    print("🎨 Behavior Space Visualizer")
    print("=" * 50)
    print("Controls:")
    print("  SPACE: Cycle through test spells")
    print("  MOUSE: Hover over prototypes for info")
    print("  ESC: Quit")
    print()

    visualizer = BehaviorSpaceVisualizer()
    visualizer.run_standalone()


if __name__ == "__main__":
    main()
