#!/usr/bin/env python
"""
Interactive testing script for manifold systems.

Run this to experiment with the new property-based magic engine
and spatial manifold without starting the full game.
"""

from magic.element import Element
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
from magic.spell_formulas import SpellFormulas
from world.spatial_manifold import SpatialManifold, Topology, ManifoldPoint


def test_magic_system():
    """Test the property-based magic system"""
    print("=" * 60)
    print("TESTING PROPERTY-BASED MAGIC SYSTEM")
    print("=" * 60)

    # Create test elements
    fire = Element('fire', 1200.0, 100, 'plasma', 'rising', 0.2, 0.8, 'neutral',
                   {'hot', 'destructive'}, (255, 0, 0))
    water = Element('water', 293.15, 50, 'liquid', 'flowing', 0.8, 0.2, 'neutral',
                    {'cold', 'defensive'}, (0, 0, 255))
    lightning = Element('lightning', 2000.0, 120, 'plasma', 'instant', 0.1, 0.7, 'negative',
                        {'fast', 'destructive'}, (255, 255, 0))
    nature = Element('nature', 293.15, 60, 'liquid', 'flowing', 0.5, 0.3, 'positive',
                     {'healing', 'gentle'}, (0, 255, 0))

    # Initialize systems
    manifold = BehaviorManifold()
    formulas = SpellFormulas()

    # Test spell combinations
    test_spells = [
        ([fire], "Pure Fire"),
        ([water], "Pure Water"),
        ([fire, water], "Fire + Water (Steam?)"),
        ([fire, fire, fire], "Triple Fire (Explosive?)"),
        ([lightning], "Lightning"),
        ([nature], "Nature (Heal?)"),
    ]

    for elements, name in test_spells:
        print(f"\n📜 {name}")
        print("-" * 60)

        # Compute property vector
        vector = PropertyVectorComputer.compute(elements)

        # Classify behavior
        behavior = manifold.classify(vector)

        # Get probabilities
        probs = manifold.get_behavior_probabilities(vector)
        top_3_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]

        # Compute stats
        damage = formulas.compute_damage(vector, behavior)
        area = formulas.compute_area(vector, behavior)
        speed = formulas.compute_speed(vector, behavior)
        duration = formulas.compute_duration(vector, behavior)
        mana = formulas.compute_mana_cost(vector, behavior)

        print(f"  Behavior: {behavior.upper()}")
        print(f"  Probabilities: {top_3_probs[0][0]} ({top_3_probs[0][1]*100:.1f}%), "
              f"{top_3_probs[1][0]} ({top_3_probs[1][1]*100:.1f}%), "
              f"{top_3_probs[2][0]} ({top_3_probs[2][1]*100:.1f}%)")
        print(f"  Stats: DMG={damage}, Area={area}, Speed={speed}, Duration={duration}s, Mana={mana}")
        print(f"  Properties: Thermal Flux={vector.thermal_flux:.2f}, "
              f"Volatility={vector.volatility_index:.2f}, "
              f"Chaos={vector.chaos_factor:.2f}")


def test_spatial_system():
    """Test the topology-independent spatial system"""
    print("\n\n" + "=" * 60)
    print("TESTING SPATIAL MANIFOLD SYSTEM")
    print("=" * 60)

    # Test different topologies
    topologies = [
        (Topology.FLAT, "Flat (Euclidean)"),
        (Topology.TOROIDAL, "Toroidal (Wrap-around)"),
        (Topology.SPHERICAL, "Spherical (Planet)"),
    ]

    for topology, name in topologies:
        print(f"\n🌍 {name}")
        print("-" * 60)

        world = SpatialManifold(topology=topology, width=20.0, height=20.0)

        # Test points
        p1 = ManifoldPoint(1.0, 1.0)
        p2 = ManifoldPoint(19.0, 1.0)

        # Distance
        dist = world.distance(p1, p2)
        print(f"  Distance from (1,1) to (19,1): {dist:.2f} units")

        # Geodesic
        path = world.geodesic(p1, p2, num_points=5)
        print(f"  Geodesic path (5 points):")
        for i, point in enumerate(path):
            print(f"    {i}: ({point.u:.2f}, {point.v:.2f})")

        # Wrapping test
        p_out = ManifoldPoint(25.0, -5.0)
        p_wrapped = world.wrap_point(p_out)
        print(f"  Wrap (25, -5) → ({p_wrapped.u:.2f}, {p_wrapped.v:.2f})")


def test_integration():
    """Test both systems together"""
    print("\n\n" + "=" * 60)
    print("INTEGRATION TEST: Magic + Spatial")
    print("=" * 60)

    # Create spell
    fire = Element('fire', 1200.0, 100, 'plasma', 'rising', 0.2, 0.8, 'neutral',
                   {'hot', 'destructive'}, (255, 0, 0))
    water = Element('water', 293.15, 50, 'liquid', 'flowing', 0.8, 0.2, 'neutral',
                    {'cold', 'defensive'}, (0, 0, 255))

    vector = PropertyVectorComputer.compute([fire, water])
    manifold = BehaviorManifold()
    formulas = SpellFormulas()

    behavior = manifold.classify(vector)
    speed = formulas.compute_speed(vector, behavior)
    duration = formulas.compute_duration(vector, behavior)

    print(f"\n🔥💧 Fire + Water Spell")
    print(f"  Behavior: {behavior}")
    print(f"  Speed: {speed:.2f} units/second")
    print(f"  Duration: {duration:.2f} seconds")

    # Simulate projectile path on toroidal world
    world = SpatialManifold(topology=Topology.TOROIDAL, width=20.0, height=20.0)

    start = ManifoldPoint(1.0, 10.0)
    end = ManifoldPoint(19.0, 10.0)

    # Geodesic path (spell trajectory)
    num_points = int(duration * 10)  # 10 updates per second
    path = world.geodesic(start, end, num_points=num_points)

    print(f"\n  Projectile trajectory ({len(path)} points):")
    print(f"    Start: ({path[0].u:.2f}, {path[0].v:.2f})")
    print(f"    Mid:   ({path[len(path)//2].u:.2f}, {path[len(path)//2].v:.2f})")
    print(f"    End:   ({path[-1].u:.2f}, {path[-1].v:.2f})")

    travel_distance = world.distance(start, end)
    travel_time = travel_distance / speed
    print(f"  Travel distance: {travel_distance:.2f} units")
    print(f"  Travel time: {travel_time:.2f} seconds")


if __name__ == '__main__':
    print("\n🧪 MANIFOLD SYSTEMS INTERACTIVE TEST\n")

    test_magic_system()
    test_spatial_system()
    test_integration()

    print("\n\n✅ All tests complete!\n")
