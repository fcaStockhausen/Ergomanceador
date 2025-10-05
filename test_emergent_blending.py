"""
Test emergent stat blending from multi-label classification.

This demonstrates the TRUE emergent approach:
- Properties → Distances → Weights → Blended Stats
- NO hardcoding of "what explosive projectile does"
- The behavior emerges naturally from the weighted blend!
"""

import numpy as np
from magic.element_loader import load_elements_from_json
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
from magic.behavior_composer import BehaviorComposer
from magic.spell_formulas import SpellFormulas


def test_emergent_blending():
    """Show how stats emerge from weighted blending"""

    elements = load_elements_from_json()
    manifold = BehaviorManifold()
    composer = BehaviorComposer(manifold)
    formulas = SpellFormulas()

    print("=" * 80)
    print("EMERGENT STAT BLENDING (Multi-Label)")
    print("=" * 80)
    print()
    print("This shows how spell stats emerge from GEOMETRY, not hardcoding!")
    print()

    # Test case: Fire Fire Fire (should be projectile-ish with AOE influence)
    element_names = ['fire', 'fire', 'fire']
    print(f"🧪 Test Spell: {' + '.join(element_names).title()}")
    print()

    # Get elements and compute property vector
    elems = [elements[name] for name in element_names]
    vector = PropertyVectorComputer.compute(elems)

    print("📊 Property Vector (12D):")
    print(f"   Thermal Flux: {vector.thermal_flux:.3f}")
    print(f"   Temperature: {vector.avg_temperature:.1f}K")
    print(f"   Volatility: {vector.volatility_index:.3f}")
    print(f"   Energy: {vector.total_energy:.1f}")
    print(f"   Polarity: {vector.polarity_tension:.3f}")
    print()

    # Multi-label classification
    activations = composer.classify_multi(vector)
    weights = composer.get_behavior_weights(activations)

    print("🎯 Activated Behaviors (distance-based):")
    for act in activations[:5]:  # Show top 5
        marker = "★" if act == activations[0] else "○"
        print(f"   {marker} {act.behavior:15s} strength={act.strength:.2f} (distance={act.distance:.3f})")
    print()

    print("⚖️  Behavior Weights (normalized, for blending):")
    for behavior, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True)[:5]:
        bar_length = int(weight * 40)
        bar = "█" * bar_length
        print(f"   {behavior:15s}: {weight:5.1%} {bar}")
    print()

    # Compute stats for EACH behavior individually (using formulas)
    print("🔧 Individual Behavior Stats (from formulas):")
    behavior_stats = {}
    for behavior in weights:
        stats = {
            'damage': formulas.compute_damage(vector, behavior),
            'area': formulas.compute_area(vector, behavior),
            'speed': formulas.compute_speed(vector, behavior),
            'duration': formulas.compute_duration(vector, behavior),
        }
        behavior_stats[behavior] = stats

        if weights[behavior] > 0.05:  # Only show significant contributors
            print(f"   {behavior:15s}: damage={stats['damage']:.1f}, area={stats['area']:.1f}, "
                  f"speed={stats['speed']:.1f}, duration={stats['duration']:.2f}s")
    print()

    # EMERGENT BLENDING: Weighted average of all stats
    print("✨ EMERGENT BLENDED STATS (weighted average):")
    print("   Formula: stat = Σ (weight_i × stat_i)")
    print()

    blended_damage = sum(weights[b] * behavior_stats[b]['damage'] for b in weights)
    blended_area = sum(weights[b] * behavior_stats[b]['area'] for b in weights)
    blended_speed = sum(weights[b] * behavior_stats[b]['speed'] for b in weights)
    blended_duration = sum(weights[b] * behavior_stats[b]['duration'] for b in weights)

    print(f"   💥 Damage:   {blended_damage:.1f}")
    print(f"   📏 Area:     {blended_area:.1f}")
    print(f"   🚀 Speed:    {blended_speed:.1f}")
    print(f"   ⏱️  Duration: {blended_duration:.2f}s")
    print()

    # Show how it differs from single-label
    single_label_behavior = manifold.classify(vector)
    single_damage = formulas.compute_damage(vector, single_label_behavior)
    single_area = formulas.compute_area(vector, single_label_behavior)
    single_speed = formulas.compute_speed(vector, single_label_behavior)

    print("📊 Comparison: Multi-Label vs Single-Label")
    print(f"   Single-Label: {single_label_behavior} (nearest only)")
    print(f"      Damage: {single_damage:.1f}, Area: {single_area:.1f}, Speed: {single_speed:.1f}")
    print()
    print(f"   Multi-Label: Weighted blend of {len([w for w in weights.values() if w > 0.05])} behaviors")
    print(f"      Damage: {blended_damage:.1f} ({blended_damage - single_damage:+.1f})")
    print(f"      Area: {blended_area:.1f} ({blended_area - single_area:+.1f})")
    print(f"      Speed: {blended_speed:.1f} ({blended_speed - single_speed:+.1f})")
    print()

    # Name is just descriptive
    name = composer.compose_behavior_name(activations)
    print(f"🏷️  Spell Name (cosmetic): {name}")
    print("    ↑ This is just a LABEL. The stats above are what matter!")
    print()

    print("=" * 80)
    print("KEY INSIGHT:")
    print("The spell's behavior EMERGES from weighted geometry.")
    print("NO hardcoding of 'what projectile_aoe does' - just math!")
    print("=" * 80)


if __name__ == "__main__":
    test_emergent_blending()
