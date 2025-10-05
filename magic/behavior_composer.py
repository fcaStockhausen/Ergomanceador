"""
Multi-label behavior classification system.

Instead of "nearest prototype wins", allows spells to have MULTIPLE behaviors
based on distance thresholds. This enables composable spell behaviors:
- Projectile + AOE = Explosive fireball
- Projectile + Homing = Seeking missile
- Heal + AOE = Area heal

This is MORE aligned with manifold theory than Voronoi partitioning!
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class BehaviorActivation:
    """A behavior that's activated with a certain strength"""
    behavior: str
    distance: float  # Distance to prototype (lower = stronger)
    strength: float  # Activation strength 0-1 (1 = perfect match)


class BehaviorComposer:
    """
    Multi-label classifier for spell behaviors.

    Uses distance thresholds instead of "nearest wins" to allow
    multiple behaviors to activate simultaneously.
    """

    # Distance thresholds for behavior activation
    # Behaviors closer than this distance are considered "active"
    THRESHOLD_STRONG = 0.8   # Strong activation (dominant behavior)
    THRESHOLD_MEDIUM = 1.2   # Medium activation (modifier behavior)
    THRESHOLD_WEAK = 1.6     # Weak activation (hint/flavor)

    # Minimum activation strength (below this, behavior is ignored)
    MIN_STRENGTH = 0.1

    def __init__(self, manifold):
        """
        Args:
            manifold: BehaviorManifold instance with prototypes
        """
        self.manifold = manifold

    def classify_multi(self, property_vector) -> List[BehaviorActivation]:
        """
        Classify spell with multiple possible behaviors.

        Returns list of activated behaviors sorted by strength (strongest first).
        """
        # Convert property vector to 12D array
        vector_12d = np.array([
            property_vector.thermal_flux / 2.0,
            property_vector.avg_temperature / 2000.0,
            property_vector.temp_differential / 2000.0,
            property_vector.state_transition_energy / 1000.0,
            property_vector.phase_diversity,
            property_vector.density_gradient,
            property_vector.avg_density,
            property_vector.volatility_index,
            property_vector.chaos_factor,
            property_vector.total_energy / 400.0,
            property_vector.energy_density / 150.0,
            property_vector.polarity_tension
        ])

        # Compute distances to all prototypes
        activations = []

        for region in self.manifold.regions:
            dist = self.manifold._riemannian_distance(
                vector_12d,
                region.prototype,
                region.metric_tensor
            )

            # Compute activation strength (inverse of distance, normalized)
            # Using exponential decay: strength = exp(-dist/threshold)
            strength = np.exp(-dist / self.THRESHOLD_MEDIUM)

            # Only include behaviors above minimum strength
            if strength >= self.MIN_STRENGTH:
                activations.append(BehaviorActivation(
                    behavior=region.name,
                    distance=dist,
                    strength=strength
                ))

        # Sort by strength (strongest first)
        activations.sort(key=lambda x: x.strength, reverse=True)

        return activations

    def get_primary_behavior(self, activations: List[BehaviorActivation]) -> str:
        """Get the dominant (strongest) behavior"""
        return activations[0].behavior if activations else 'projectile'

    def get_modifiers(self, activations: List[BehaviorActivation]) -> List[str]:
        """Get secondary behaviors that modify the primary"""
        if len(activations) <= 1:
            return []

        # Return all except the strongest, but only if they're reasonably strong
        modifiers = []
        primary_strength = activations[0].strength

        for activation in activations[1:]:
            # Modifier must be at least 30% as strong as primary
            if activation.strength >= primary_strength * 0.3:
                modifiers.append(activation.behavior)

        return modifiers

    def compose_behavior_name(self, activations: List[BehaviorActivation]) -> str:
        """
        Generate a DESCRIPTIVE name from multiple behaviors.

        IMPORTANT: This is COSMETIC ONLY! The actual behavior emerges from
        weighted property blending, not from this name.

        This name just helps players/designers understand what activated.

        Examples:
            - [projectile(0.9), aoe(0.6)] → "projectile_aoe"
            - [heal(0.95), aoe(0.5)] → "heal_aoe"
            - [beam(0.8), chain(0.7)] → "beam_chain"
        """
        if not activations:
            return "projectile"

        primary = activations[0].behavior
        modifiers = self.get_modifiers(activations)

        if not modifiers:
            return primary

        # EMERGENT: Just list the activated behaviors
        # The actual spell behavior emerges from weighted stats,
        # NOT from this name!
        return f"{primary}_{'_'.join(modifiers[:2])}"  # Max 3 behaviors in name

    def get_behavior_weights(self, activations: List[BehaviorActivation]) -> Dict[str, float]:
        """
        Get normalized weights for blending behavior stats.

        This allows you to compute spell stats as weighted average:
            damage = Σ (weight_i * damage_i)
        """
        if not activations:
            return {'projectile': 1.0}

        # Normalize strengths to sum to 1
        total_strength = sum(a.strength for a in activations)

        weights = {}
        for activation in activations:
            weights[activation.behavior] = activation.strength / total_strength

        return weights

    def format_activations(self, activations: List[BehaviorActivation]) -> str:
        """Pretty-print activations for debugging"""
        lines = []
        for i, act in enumerate(activations):
            marker = "★" if i == 0 else "○"
            bar_length = int(act.strength * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            lines.append(
                f"{marker} {act.behavior:15s} {act.strength:.2f} {bar} (dist: {act.distance:.3f})"
            )
        return "\n".join(lines)


def test_composer():
    """Test the composer with various spell combinations"""
    from magic.element_loader import load_elements_from_json
    from magic.property_vector import PropertyVectorComputer
    from magic.behavior_manifold import BehaviorManifold

    elements = load_elements_from_json()
    manifold = BehaviorManifold()
    composer = BehaviorComposer(manifold)

    test_cases = [
        (['fire'], "Single Fire"),
        (['fire', 'fire', 'fire'], "Triple Fire (should be projectile + AOE?)"),
        (['nature'], "Nature (pure heal)"),
        (['nature', 'nature'], "Double Nature (area heal?)"),
        (['fire', 'water'], "Fire + Water"),
        (['arcane', 'arcane'], "Double Arcane (homing?)"),
    ]

    print("=" * 80)
    print("MULTI-LABEL BEHAVIOR CLASSIFICATION")
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

        # Multi-label classification
        activations = composer.classify_multi(vector)

        print("   📊 Activated Behaviors:")
        print("   " + "\n   ".join(composer.format_activations(activations).split("\n")))
        print()

        # Composed behavior
        composed = composer.compose_behavior_name(activations)
        print(f"   ✨ Composed Behavior: {composed.upper()}")
        print()

        # Behavior weights (for stat blending)
        weights = composer.get_behavior_weights(activations)
        print(f"   ⚖️  Stat Weights:")
        for behavior, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            if weight > 0.05:  # Only show significant weights
                print(f"      {behavior:15s}: {weight:.1%}")
        print()
        print("-" * 80)
        print()


if __name__ == "__main__":
    test_composer()
