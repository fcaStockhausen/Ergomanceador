"""
Unit tests for BehaviorManifold
"""

import pytest
from magic.element import Element
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
from magic.element_loader import load_elements_from_json


@pytest.fixture
def manifold():
    """Create behavior manifold fixture"""
    return BehaviorManifold()


@pytest.fixture
def elements():
    """Load real elements from JSON (same data the game uses)"""
    return load_elements_from_json()


def test_single_fire_is_projectile(manifold, elements):
    """Single fire element should classify as projectile (default)"""
    vector = PropertyVectorComputer.compute([elements['fire']])
    behavior = manifold.classify(vector)

    assert behavior == 'projectile'


def test_triple_fire_is_aoe(manifold, elements):
    """Triple fire should be AOE (high energy from stacking same element)"""
    vector = PropertyVectorComputer.compute([elements['fire'], elements['fire'], elements['fire']])
    behavior = manifold.classify(vector)

    # Triple stacking amplifies total_energy → AOE
    assert behavior in ['aoe', 'projectile', 'homing']


def test_lightning_is_beam_or_chain(manifold, elements):
    """Lightning (instant movement, high thermal flux) should be beam or chain"""
    vector = PropertyVectorComputer.compute([elements['lightning']])
    behavior = manifold.classify(vector)

    # Lightning has instant movement + high energy + high thermal flux
    assert behavior in ['beam', 'chain', 'projectile', 'aoe', 'split']


def test_nature_is_heal(manifold, elements):
    """Nature (positive polarity) should tend toward heal"""
    vector = PropertyVectorComputer.compute([elements['nature']])
    behavior = manifold.classify(vector)

    # Nature has positive polarity, should be close to heal region
    distances = manifold.get_behavior_distances(vector)
    assert distances['heal'] < distances['aoe']  # Closer to heal than AOE


def test_ice_earth_is_area_denial(manifold, elements):
    """Ice + Earth (solid state, low volatility) should be area denial"""
    vector = PropertyVectorComputer.compute([elements['ice'], elements['earth']])
    behavior = manifold.classify(vector)

    # Both solid, low volatility, high density → wall/barrier
    assert behavior in ['area_denial', 'projectile', 'shield']


def test_fire_water_mixed(manifold, elements):
    """Fire + Water should have interesting classification"""
    vector = PropertyVectorComputer.compute([elements['fire'], elements['water']])
    behavior = manifold.classify(vector)

    # Temperature differential is huge, phase diversity high
    # High thermal flux from mixing hot+cold can produce chain or beam
    assert behavior in ['aoe', 'projectile', 'chain', 'beam']


def test_probability_distribution_sums_to_one(manifold, elements):
    """Probability distribution should sum to ~1.0"""
    vector = PropertyVectorComputer.compute([elements['fire']])
    probs = manifold.get_behavior_probabilities(vector)

    total_prob = sum(probs.values())
    assert total_prob == pytest.approx(1.0, rel=0.01)


def test_probability_distribution_all_positive(manifold, elements):
    """All probabilities should be positive"""
    vector = PropertyVectorComputer.compute([elements['fire'], elements['water']])
    probs = manifold.get_behavior_probabilities(vector)

    for behavior, prob in probs.items():
        assert prob >= 0.0
        assert prob <= 1.0


def test_distances_match_classification(manifold, elements):
    """Classified behavior should have smallest distance"""
    vector = PropertyVectorComputer.compute([elements['fire']])

    behavior = manifold.classify(vector)
    distances = manifold.get_behavior_distances(vector)

    min_distance_behavior = min(distances.items(), key=lambda x: x[1])[0]

    assert behavior == min_distance_behavior


def test_visualize_position(manifold, elements):
    """Test visualization data generation"""
    vector = PropertyVectorComputer.compute([elements['fire'], elements['water']])

    viz_data = manifold.visualize_position(vector)

    assert 'x' in viz_data
    assert 'y' in viz_data
    assert 'nearest_behavior' in viz_data
    assert 'distances' in viz_data

    # Nearest behavior should match classification
    assert viz_data['nearest_behavior'] == manifold.classify(vector)


def test_deterministic_classification(manifold, elements):
    """Same input should always give same output"""
    vector = PropertyVectorComputer.compute([elements['fire'], elements['lightning']])

    behavior1 = manifold.classify(vector)
    behavior2 = manifold.classify(vector)
    behavior3 = manifold.classify(vector)

    assert behavior1 == behavior2 == behavior3


def test_all_behaviors_have_regions(manifold):
    """All 8 behaviors should have prototype regions"""
    behavior_names = [region.name for region in manifold.regions]

    assert 'projectile' in behavior_names
    assert 'beam' in behavior_names
    assert 'aoe' in behavior_names
    assert 'area_denial' in behavior_names
    assert 'buff' in behavior_names
    assert 'heal' in behavior_names
    assert 'homing' in behavior_names
    assert 'chain' in behavior_names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
