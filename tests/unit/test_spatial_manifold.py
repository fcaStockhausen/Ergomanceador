"""
Unit tests for SpatialManifold
"""

import pytest
import math
from world.spatial_manifold import SpatialManifold, Topology, ManifoldPoint, TangentVector


@pytest.fixture
def flat_manifold():
    """Create flat (Euclidean) manifold"""
    return SpatialManifold(topology=Topology.FLAT, width=20.0, height=20.0)


@pytest.fixture
def toroidal_manifold():
    """Create toroidal (wrap-around) manifold"""
    return SpatialManifold(topology=Topology.TOROIDAL, width=20.0, height=20.0)


@pytest.fixture
def spherical_manifold():
    """Create spherical manifold"""
    return SpatialManifold(topology=Topology.SPHERICAL, width=20.0, height=20.0)


# ========== Flat Manifold Tests ==========

def test_flat_distance_horizontal(flat_manifold):
    """Test horizontal distance on flat manifold"""
    p1 = ManifoldPoint(0.0, 0.0)
    p2 = ManifoldPoint(5.0, 0.0)

    dist = flat_manifold.distance(p1, p2)
    assert dist == pytest.approx(5.0, rel=0.01)


def test_flat_distance_diagonal(flat_manifold):
    """Test diagonal distance on flat manifold"""
    p1 = ManifoldPoint(0.0, 0.0)
    p2 = ManifoldPoint(3.0, 4.0)

    dist = flat_manifold.distance(p1, p2)
    assert dist == pytest.approx(5.0, rel=0.01)  # 3-4-5 triangle


def test_flat_geodesic_straight_line(flat_manifold):
    """Geodesic on flat manifold should be straight line"""
    p1 = ManifoldPoint(0.0, 0.0)
    p2 = ManifoldPoint(10.0, 10.0)

    path = flat_manifold.geodesic(p1, p2, num_points=11)

    assert len(path) == 11
    assert path[0].u == pytest.approx(0.0, abs=0.01)
    assert path[0].v == pytest.approx(0.0, abs=0.01)
    assert path[5].u == pytest.approx(5.0, abs=0.01)  # Midpoint
    assert path[5].v == pytest.approx(5.0, abs=0.01)
    assert path[10].u == pytest.approx(10.0, abs=0.01)
    assert path[10].v == pytest.approx(10.0, abs=0.01)


def test_flat_wrap_clamps_to_bounds(flat_manifold):
    """Flat manifold should clamp points to bounds"""
    p_out_of_bounds = ManifoldPoint(25.0, -5.0)
    p_wrapped = flat_manifold.wrap_point(p_out_of_bounds)

    assert p_wrapped.u == 20.0  # Clamped to max
    assert p_wrapped.v == 0.0   # Clamped to min


# ========== Toroidal Manifold Tests ==========

def test_toroidal_distance_wrapping(toroidal_manifold):
    """Test distance with wrapping on toroidal manifold"""
    p1 = ManifoldPoint(1.0, 1.0)
    p2 = ManifoldPoint(19.0, 1.0)

    # Direct distance: 18 units
    # Wrapped distance: 2 units (wrapping left)
    # Should choose wrapped distance

    dist = toroidal_manifold.distance(p1, p2)
    assert dist < 5.0  # Should be close to 2.0, not 18.0


def test_toroidal_geodesic_wraps_around(toroidal_manifold):
    """Geodesic on torus should wrap around edges when shorter"""
    p1 = ManifoldPoint(1.0, 10.0)
    p2 = ManifoldPoint(19.0, 10.0)

    path = toroidal_manifold.geodesic(p1, p2, num_points=10)

    # Path should wrap around (go through 0 or 20, not through 10)
    # Check if any point has u close to 0 or 20
    wrapped = any(p.u < 2.0 or p.u > 18.0 for p in path[1:-1])
    assert wrapped


def test_toroidal_wrap_modulo(toroidal_manifold):
    """Toroidal wrap should use modulo"""
    p_over = ManifoldPoint(25.0, 15.0)
    p_wrapped = toroidal_manifold.wrap_point(p_over)

    assert p_wrapped.u == pytest.approx(5.0, abs=0.01)  # 25 % 20 = 5
    assert p_wrapped.v == pytest.approx(15.0, abs=0.01)

    p_under = ManifoldPoint(-3.0, 10.0)
    p_wrapped2 = toroidal_manifold.wrap_point(p_under)

    assert p_wrapped2.u == pytest.approx(17.0, abs=0.01)  # -3 % 20 = 17
    assert p_wrapped2.v == pytest.approx(10.0, abs=0.01)


# ========== Spherical Manifold Tests ==========

def test_spherical_distance_equator(spherical_manifold):
    """Test distance along equator on sphere"""
    p1 = ManifoldPoint(0.0, 10.0)  # Equator
    p2 = ManifoldPoint(5.0, 10.0)  # Equator, 90° away

    dist = spherical_manifold.distance(p1, p2)

    # Should be > 0 (great circle distance)
    assert dist > 0.0


def test_spherical_distance_poles(spherical_manifold):
    """Test distance between poles on sphere"""
    # North pole
    p_north = ManifoldPoint(10.0, 0.0)

    # South pole
    p_south = ManifoldPoint(10.0, 20.0)

    dist = spherical_manifold.distance(p_north, p_south)

    # Distance between poles should be π * radius (half circumference)
    # radius ≈ (20 + 20) / (4π) ≈ 3.18
    expected_dist = math.pi * ((20.0 + 20.0) / (4 * math.pi))

    assert dist == pytest.approx(expected_dist, rel=0.1)


def test_spherical_geodesic_great_circle(spherical_manifold):
    """Geodesic on sphere should follow great circle"""
    p1 = ManifoldPoint(0.0, 10.0)
    p2 = ManifoldPoint(10.0, 10.0)

    path = spherical_manifold.geodesic(p1, p2, num_points=50)

    assert len(path) == 50

    # Path should be smooth (no jumps)
    for i in range(len(path) - 1):
        du = abs(path[i+1].u - path[i].u)
        dv = abs(path[i+1].v - path[i].v)
        # Each step should be small
        assert du < 1.0
        assert dv < 1.0


# ========== Distance Properties Tests ==========

def test_distance_is_symmetric(flat_manifold):
    """Distance should be symmetric: d(a,b) = d(b,a)"""
    p1 = ManifoldPoint(3.0, 5.0)
    p2 = ManifoldPoint(8.0, 12.0)

    dist1 = flat_manifold.distance(p1, p2)
    dist2 = flat_manifold.distance(p2, p1)

    assert dist1 == pytest.approx(dist2, rel=0.01)


def test_distance_triangle_inequality(flat_manifold):
    """Triangle inequality: d(a,c) <= d(a,b) + d(b,c)"""
    p1 = ManifoldPoint(0.0, 0.0)
    p2 = ManifoldPoint(5.0, 0.0)
    p3 = ManifoldPoint(5.0, 5.0)

    d12 = flat_manifold.distance(p1, p2)
    d23 = flat_manifold.distance(p2, p3)
    d13 = flat_manifold.distance(p1, p3)

    assert d13 <= d12 + d23 + 0.001  # Small epsilon for float errors


def test_distance_to_self_is_zero(flat_manifold):
    """Distance from point to itself should be zero"""
    p = ManifoldPoint(5.0, 8.0)

    dist = flat_manifold.distance(p, p)

    assert dist == pytest.approx(0.0, abs=0.001)


# ========== Geodesic Properties Tests ==========

def test_geodesic_starts_and_ends_correctly(flat_manifold):
    """Geodesic should start at p1 and end at p2"""
    p1 = ManifoldPoint(2.0, 3.0)
    p2 = ManifoldPoint(8.0, 9.0)

    path = flat_manifold.geodesic(p1, p2, num_points=20)

    assert path[0].u == pytest.approx(p1.u, abs=0.01)
    assert path[0].v == pytest.approx(p1.v, abs=0.01)
    assert path[-1].u == pytest.approx(p2.u, abs=0.01)
    assert path[-1].v == pytest.approx(p2.v, abs=0.01)


def test_geodesic_length_matches_distance(flat_manifold):
    """Sum of geodesic segment lengths should equal distance"""
    p1 = ManifoldPoint(0.0, 0.0)
    p2 = ManifoldPoint(6.0, 8.0)

    path = flat_manifold.geodesic(p1, p2, num_points=100)

    # Sum path lengths
    total_length = 0.0
    for i in range(len(path) - 1):
        segment_len = flat_manifold.distance(path[i], path[i+1])
        total_length += segment_len

    expected_dist = flat_manifold.distance(p1, p2)

    assert total_length == pytest.approx(expected_dist, rel=0.05)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
