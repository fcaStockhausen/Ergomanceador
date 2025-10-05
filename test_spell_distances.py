"""
Test script to analyze spell distances to all prototypes.

This helps us understand WHY certain spells are classified incorrectly.
"""

import numpy as np
from magic.element_loader import load_elements_from_json
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold

def test_spell_distances():
    """Show distances from test spells to ALL prototypes"""

    elements = load_elements_from_json()
    manifold = BehaviorManifold()

    # Test cases
    test_cases = [
        (['fire'], "Single Fire (should be Projectile)"),
        (['fire', 'fire', 'fire', 'fire'], "4x Fire (user says it's Heal - WRONG!)"),
        (['nature'], "Nature (should be Heal)"),
        (['fire', 'water'], "Fire + Water (steam)"),
        (['ice', 'ice'], "Ice + Ice (area denial?)"),
    ]

    print("=" * 80)
    print("SPELL DISTANCE ANALYSIS")
    print("=" * 80)
    print()

    for element_names, description in test_cases:
        print(f"🧪 {description}")
        print(f"   Elements: {' + '.join(element_names)}")
        print()

        # Get elements
        elems = [elements[name] for name in element_names]

        # Compute property vector
        vector = PropertyVectorComputer.compute(elems)

        # Show key properties
        print(f"   📊 Properties:")
        print(f"      Thermal Flux: {vector.thermal_flux:.3f}")
        print(f"      Temperature: {vector.avg_temperature:.1f}K")
        print(f"      Volatility: {vector.volatility_index:.3f}")
        print(f"      Energy: {vector.total_energy:.1f}")
        print(f"      Polarity: {vector.polarity_tension:.3f}")
        print()

        # Convert to normalized 12D array
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

        # Compute distance to ALL prototypes
        distances = {}
        for region in manifold.regions:
            dist = manifold._riemannian_distance(vector_12d, region.prototype, region.metric_tensor)
            distances[region.name] = dist

        # Sort by distance
        sorted_distances = sorted(distances.items(), key=lambda x: x[1])

        print(f"   📏 Distances to prototypes:")
        for behavior, distance in sorted_distances:
            marker = "✓ NEAREST" if behavior == sorted_distances[0][0] else ""
            bar_length = int((1 - min(distance, 1.0)) * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            print(f"      {behavior:15s}: {distance:.3f} {bar} {marker}")

        # Current classification
        classified_as = manifold.classify(vector)
        print()
        print(f"   ✨ Classified as: {classified_as.upper()}")
        print()
        print("-" * 80)
        print()

if __name__ == "__main__":
    test_spell_distances()
