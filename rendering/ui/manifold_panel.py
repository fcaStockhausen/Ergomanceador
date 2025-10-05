"""
In-game behavior manifold visualization panel.

Shows the 12D→2D projection of the behavior space as a side panel in the main game.
"""

import pygame
import numpy as np
from sklearn.decomposition import PCA

from magic.behavior_manifold import BehaviorManifold
from magic.property_vector import PropertyVectorComputer
from magic.element_loader import load_elements_from_json


class ManifoldPanel:
    """Embedded manifold visualizer panel for game HUD"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.manifold = BehaviorManifold()
        self.elements = load_elements_from_json()

        # Fonts (smaller for embedded panel)
        self.font = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 14)
        self.font_title = pygame.font.Font(None, 22)

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

        # PCA for dimensionality reduction
        self.pca = None
        self.prototype_2d = {}
        self._compute_pca_projection()

        # Current spell state
        self.current_element_queue = []
        self.current_spell_2d = None

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

        # Store 2D positions (normalized to panel space)
        margin = 40
        x_min, x_max = projected[:, 0].min(), projected[:, 0].max()
        y_min, y_max = projected[:, 1].min(), projected[:, 1].max()

        for i, name in enumerate(behavior_names):
            # Normalize to [margin, width-margin] and [margin, height-margin]
            px = margin + (projected[i, 0] - x_min) / (x_max - x_min) * (self.width - 2*margin)
            py = margin + (projected[i, 1] - y_min) / (y_max - y_min) * (self.height - 2*margin)
            self.prototype_2d[name] = (px, py)

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

        # Convert to 12D array (same normalization as manifold)
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
        projected = self.pca.transform([vector_12d])[0]

        # Get prototype range for normalization
        all_protos = list(self.prototype_2d.values())
        proto_xs = [p[0] for p in all_protos]
        proto_ys = [p[1] for p in all_protos]

        # Get PCA range
        margin = 40
        pca_x_min, pca_x_max = min(proto_xs) - margin, max(proto_xs) + margin
        pca_y_min, pca_y_max = min(proto_ys) - margin, max(proto_ys) + margin

        # Map to panel coordinates
        # Use the PCA mean and std for proper scaling
        proto_vecs = np.array([r.prototype for r in self.manifold.regions])
        proto_proj = self.pca.transform(proto_vecs)
        proj_x_min, proj_x_max = proto_proj[:, 0].min(), proto_proj[:, 0].max()
        proj_y_min, proj_y_max = proto_proj[:, 1].min(), proto_proj[:, 1].max()

        # Normalize projected point
        px = margin + (projected[0] - proj_x_min) / (proj_x_max - proj_x_min) * (self.width - 2*margin)
        py = margin + (projected[1] - proj_y_min) / (proj_y_max - proj_y_min) * (self.height - 2*margin)

        self.current_spell_2d = (px, py)
        self.current_element_queue = element_names

    def draw(self, screen):
        """Draw the manifold panel on the screen"""
        # Background panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (20, 20, 35), panel_rect)
        pygame.draw.rect(screen, (100, 100, 150), panel_rect, 2)

        # Title
        title = self.font_title.render("Behavior Manifold", True, (255, 255, 255))
        screen.blit(title, (self.x + self.width//2 - title.get_width()//2, self.y + 5))

        # Draw connecting lines between prototypes (Voronoi-like)
        for i, (name1, pos1) in enumerate(self.prototype_2d.items()):
            abs_pos1 = (self.x + pos1[0], self.y + pos1[1])
            for name2, pos2 in list(self.prototype_2d.items())[i+1:]:
                abs_pos2 = (self.x + pos2[0], self.y + pos2[1])
                pygame.draw.aaline(screen, (40, 40, 60), abs_pos1, abs_pos2)

        # Draw behavior prototypes
        for behavior, pos in self.prototype_2d.items():
            abs_pos = (self.x + pos[0], self.y + pos[1])
            color = self.behavior_colors.get(behavior, (200, 200, 200))

            # Draw prototype circle
            pygame.draw.circle(screen, color, abs_pos, 8)
            pygame.draw.circle(screen, (255, 255, 255), abs_pos, 8, 1)

            # Label (abbreviated)
            label_text = behavior[:4].upper()
            label = self.font_small.render(label_text, True, (200, 200, 200))
            screen.blit(label, (abs_pos[0] - label.get_width()//2, abs_pos[1] + 12))

        # Draw current spell position
        if self.current_spell_2d:
            abs_pos = (self.x + self.current_spell_2d[0], self.y + self.current_spell_2d[1])

            # Draw connecting line to nearest prototype
            nearest_behavior = min(
                self.prototype_2d.items(),
                key=lambda item: np.sqrt((item[1][0]-self.current_spell_2d[0])**2 +
                                        (item[1][1]-self.current_spell_2d[1])**2)
            )
            nearest_abs = (self.x + nearest_behavior[1][0], self.y + nearest_behavior[1][1])
            pygame.draw.aaline(screen, (150, 150, 255), abs_pos, nearest_abs)

            # Pulsing effect
            import math
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
            glow_radius = int(15 + 5 * pulse)

            # Draw spell point (yellow, pulsing)
            pygame.draw.circle(screen, (255, 255, 0), abs_pos, glow_radius)
            pygame.draw.circle(screen, (255, 255, 255), abs_pos, glow_radius, 2)

            # Show element queue (abbreviated)
            elem_text = "+".join([e[0].upper() for e in self.current_element_queue])
            elem_surf = self.font_small.render(elem_text, True, (255, 220, 50))
            screen.blit(elem_surf, (abs_pos[0] - elem_surf.get_width()//2, abs_pos[1] - 25))

            # Show classified behavior
            behavior_surf = self.font_small.render(f"→ {nearest_behavior[0].upper()}", True, (150, 255, 150))
            screen.blit(behavior_surf, (self.x + 5, self.y + self.height - 20))

        # Instructions
        hint = self.font_small.render("Queue elements to see spell in 12D space", True, (120, 120, 150))
        screen.blit(hint, (self.x + 5, self.y + self.height - 40))
