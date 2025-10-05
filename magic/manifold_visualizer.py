"""
Behavior Manifold Visualization

Visualizes the property space and behavior regions.
Helps understand the geometric structure of spell classification.

RUN FROM PROJECT ROOT:
    cd /path/to/Karaokeficador
    python magic/manifold_visualizer.py
"""

import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import numpy as np
from typing import List
from magic.property_vector import PropertyVector, PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
from magic.element import Element


class ManifoldVisualizer:
    """
    Visualizes the behavior manifold in 2D projections.
    """

    def __init__(self, manifold: BehaviorManifold):
        self.manifold = manifold

    def plot_property_space_2d(self, elements_list: List[List[Element]], labels: List[str] = None):
        """
        Plot property space in 2D using PCA-like projection.

        Shows where different element combinations land in the manifold.
        """
        fig, ax = plt.subplots(figsize=(12, 10))

        # Compute property vectors for all element combinations
        vectors = [PropertyVectorComputer.compute(elems) for elems in elements_list]

        # Get 2D coordinates
        coords = []
        behaviors = []
        for v in vectors:
            pos = self.manifold.visualize_position(v)
            coords.append((pos['x'], pos['y']))
            behaviors.append(pos['nearest_behavior'])

        # Plot behavior regions (approximate)
        self._plot_behavior_regions(ax)

        # Plot spell points
        colors = {
            'projectile': 'blue',
            'beam': 'yellow',
            'aoe': 'red',
            'area_denial': 'green',
            'buff': 'cyan',
            'heal': 'lime',
            'homing': 'magenta',
            'chain': 'orange'
        }

        for i, (coord, behavior) in enumerate(zip(coords, behaviors)):
            label = labels[i] if labels else f"Spell {i+1}"
            ax.scatter(coord[0], coord[1],
                      color=colors.get(behavior, 'gray'),
                      s=100,
                      alpha=0.7,
                      edgecolors='black',
                      linewidths=1.5)
            ax.annotate(label, coord, fontsize=8, ha='right')

        ax.set_xlabel('Thermal Axis (flux + temp)', fontsize=12)
        ax.set_ylabel('Volatility + Density Axis', fontsize=12)
        ax.set_title('Spell Property Space: Behavior Manifold', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=c, label=b) for b, c in colors.items()]
        ax.legend(handles=legend_elements, loc='upper right')

        plt.tight_layout()
        return fig

    def plot_distance_heatmap(self, vector: PropertyVector):
        """
        Plot heatmap showing distances to all behaviors.
        Shows which behaviors are "nearby" in manifold.
        """
        distances = self.manifold.get_behavior_distances(vector)

        behaviors = list(distances.keys())
        dist_values = list(distances.values())

        fig, ax = plt.subplots(figsize=(10, 6))

        # Create bar chart
        colors_map = {
            'projectile': 'blue',
            'beam': 'yellow',
            'aoe': 'red',
            'area_denial': 'green',
            'buff': 'cyan',
            'heal': 'lime',
            'homing': 'magenta',
            'chain': 'orange'
        }
        bar_colors = [colors_map.get(b, 'gray') for b in behaviors]

        bars = ax.barh(behaviors, dist_values, color=bar_colors, alpha=0.7, edgecolor='black')

        # Highlight closest behavior
        min_idx = dist_values.index(min(dist_values))
        bars[min_idx].set_linewidth(3)
        bars[min_idx].set_edgecolor('red')

        ax.set_xlabel('Distance in Property Space', fontsize=12)
        ax.set_title('Behavior Distances (Closest = Classified Behavior)', fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Closest on top
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        return fig

    def plot_probability_pie(self, vector: PropertyVector):
        """
        Plot probability distribution as pie chart.
        Shows how "certain" the classification is.
        """
        probs = self.manifold.get_behavior_probabilities(vector)

        # Filter out very small probabilities for clarity
        probs = {k: v for k, v in probs.items() if v > 0.01}

        behaviors = list(probs.keys())
        prob_values = list(probs.values())

        colors_map = {
            'projectile': 'blue',
            'beam': 'yellow',
            'aoe': 'red',
            'area_denial': 'green',
            'buff': 'cyan',
            'heal': 'lime',
            'homing': 'magenta',
            'chain': 'orange'
        }
        slice_colors = [colors_map.get(b, 'gray') for b in behaviors]

        fig, ax = plt.subplots(figsize=(8, 8))

        ax.pie(prob_values,
               labels=behaviors,
               colors=slice_colors,
               autopct='%1.1f%%',
               startangle=90,
               textprops={'fontsize': 10, 'weight': 'bold'})

        ax.set_title('Behavior Probability Distribution', fontsize=14, fontweight='bold')

        plt.tight_layout()
        return fig

    def _plot_behavior_regions(self, ax):
        """
        Plot approximate behavior regions in 2D projection.
        (Simplified: shows prototype positions + circles)
        """
        for region in self.manifold.regions:
            # Project prototype to 2D
            proto_2d = self._project_to_2d(region.prototype)

            # Draw circle around prototype (radius = threshold)
            circle = plt.Circle(proto_2d, region.threshold * 0.5,
                               alpha=0.15,
                               color=self._behavior_color(region.name),
                               linewidth=2,
                               linestyle='--',
                               fill=True)
            ax.add_patch(circle)

            # Label prototype
            ax.plot(proto_2d[0], proto_2d[1],
                   marker='x',
                   markersize=12,
                   markeredgewidth=3,
                   color='black')
            ax.annotate(region.name.upper(),
                       proto_2d,
                       fontsize=9,
                       fontweight='bold',
                       ha='center',
                       va='bottom')

    def _project_to_2d(self, vector_12d: np.ndarray) -> tuple:
        """
        Project 12D property vector to 2D for visualization.
        Uses same projection as visualize_position.
        """
        x = vector_12d[0] + vector_12d[1]  # Thermal axis
        y = vector_12d[7] + vector_12d[6]  # Volatility + density
        return (x, y)

    def _behavior_color(self, behavior: str) -> str:
        """Get color for behavior"""
        colors = {
            'projectile': 'blue',
            'beam': 'yellow',
            'aoe': 'red',
            'area_denial': 'green',
            'buff': 'cyan',
            'heal': 'lime',
            'homing': 'magenta',
            'chain': 'orange'
        }
        return colors.get(behavior, 'gray')


# ========== Example Usage ==========

if __name__ == '__main__':
    """
    Example: Visualize property space with different element combinations
    """
    from magic.element_loader import load_elements_from_json

    # Load elements
    elements = load_elements_from_json()

    # Create manifold
    manifold = BehaviorManifold()
    visualizer = ManifoldVisualizer(manifold)

    # Define test spell combinations
    test_spells = [
        ([elements['fire']], 'Fire'),
        ([elements['water']], 'Water'),
        ([elements['fire'], elements['water']], 'Fire+Water'),
        ([elements['fire'], elements['fire'], elements['fire']], 'Fire x3'),
        ([elements['lightning']], 'Lightning'),
        ([elements['earth']], 'Earth'),
        ([elements['nature']], 'Nature (Heal)'),
        ([elements['ice'], elements['earth']], 'Ice+Earth (Wall)'),
    ]

    spell_elements = [s[0] for s in test_spells]
    spell_labels = [s[1] for s in test_spells]

    # Plot property space
    fig1 = visualizer.plot_property_space_2d(spell_elements, spell_labels)
    plt.savefig('behavior_manifold_2d.png', dpi=150)
    plt.show()

    # Plot distance heatmap for a specific spell
    fire_water_vector = PropertyVectorComputer.compute([elements['fire'], elements['water']])
    fig2 = visualizer.plot_distance_heatmap(fire_water_vector)
    plt.savefig('spell_distances.png', dpi=150)
    plt.show()

    # Plot probability distribution
    fig3 = visualizer.plot_probability_pie(fire_water_vector)
    plt.savefig('spell_probabilities.png', dpi=150)
    plt.show()

    print("✓ Manifold visualizations saved!")
