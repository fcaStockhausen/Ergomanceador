"""
Spatial Manifold: Topology-Independent Game World

The game world is a 2D Riemannian manifold with configurable topology.
Supports flat (Euclidean), toroidal (wrap-around), and spherical geometries.

Mathematical Structure:
- Manifold M (2D surface)
- Metric g: TM → R (defines distances and angles)
- Charts φ: M → R² (coordinate systems)
- Geodesics γ: [0,1] → M (shortest paths)
"""

import math
import numpy as np
from enum import Enum
from typing import Tuple, List, Optional
from dataclasses import dataclass


class Topology(Enum):
    """Supported manifold topologies"""
    FLAT = 'flat'           # R² - standard Euclidean plane
    TOROIDAL = 'toroidal'   # T² - wrap-around edges (Pac-Man style)
    SPHERICAL = 'spherical'  # S² - sphere surface
    HYPERBOLIC = 'hyperbolic'  # H² - negative curvature (advanced)


@dataclass
class ManifoldPoint:
    """
    A point on the manifold with local coordinates.
    """
    u: float  # Local coordinate 1
    v: float  # Local coordinate 2
    chart: str = 'default'  # Which chart (coordinate system) this point uses


@dataclass
class TangentVector:
    """
    A vector in the tangent space at a point.
    Used for velocity, acceleration, forces.
    """
    base_point: ManifoldPoint
    du: float  # Component in u direction
    dv: float  # Component in v direction


class SpatialManifold:
    """
    The game world as a Riemannian manifold.

    Provides topology-independent geometric operations:
    - Distance calculation (respecting topology)
    - Geodesic pathfinding (shortest paths)
    - Parallel transport (moving vectors along paths)
    - Chart transitions (coordinate transformations)
    """

    def __init__(self,
                 topology: Topology = Topology.FLAT,
                 width: float = 20.0,
                 height: float = 20.0,
                 curvature: float = 0.0):
        """
        Initialize spatial manifold.

        Args:
            topology: Geometric topology of the world
            width: Manifold extent in u direction
            height: Manifold extent in v direction
            curvature: Gaussian curvature (for non-flat manifolds)
        """
        self.topology = topology
        self.width = width
        self.height = height
        self.curvature = curvature

        # Metric tensor (defines geometry)
        self.metric = self._compute_metric_tensor()

    # ========== Distance & Metrics ==========

    def distance(self, p1: ManifoldPoint, p2: ManifoldPoint) -> float:
        """
        Compute Riemannian distance between two points.

        For flat: Euclidean distance
        For toroidal: Shortest distance considering wrapping
        For spherical: Great circle distance
        """
        if self.topology == Topology.FLAT:
            return self._flat_distance(p1, p2)
        elif self.topology == Topology.TOROIDAL:
            return self._toroidal_distance(p1, p2)
        elif self.topology == Topology.SPHERICAL:
            return self._spherical_distance(p1, p2)
        else:
            raise NotImplementedError(f"Distance not implemented for {self.topology}")

    def _flat_distance(self, p1: ManifoldPoint, p2: ManifoldPoint) -> float:
        """Euclidean distance (flat manifold)"""
        du = p2.u - p1.u
        dv = p2.v - p1.v
        return math.sqrt(du**2 + dv**2)

    def _toroidal_distance(self, p1: ManifoldPoint, p2: ManifoldPoint) -> float:
        """
        Toroidal distance (shortest path with wrapping).

        On a torus, you can reach a point by going directly OR by wrapping around.
        Choose the shorter path.
        """
        # Compute direct distance
        du_direct = p2.u - p1.u
        dv_direct = p2.v - p1.v

        # Compute wrapped distances
        du_wrapped = du_direct + (self.width if du_direct < 0 else -self.width)
        dv_wrapped = dv_direct + (self.height if dv_direct < 0 else -self.height)

        # Choose shorter path in each dimension
        du = du_direct if abs(du_direct) < abs(du_wrapped) else du_wrapped
        dv = dv_direct if abs(dv_direct) < abs(dv_wrapped) else dv_wrapped

        return math.sqrt(du**2 + dv**2)

    def _spherical_distance(self, p1: ManifoldPoint, p2: ManifoldPoint) -> float:
        """
        Spherical distance (great circle distance).

        Uses spherical law of cosines.
        """
        # Map (u,v) to spherical coordinates (θ, φ)
        theta1 = p1.u * 2 * math.pi / self.width
        phi1 = p1.v * math.pi / self.height

        theta2 = p2.u * 2 * math.pi / self.width
        phi2 = p2.v * math.pi / self.height

        # Great circle distance on unit sphere
        # d = arccos(sin(φ₁)sin(φ₂) + cos(φ₁)cos(φ₂)cos(Δθ))
        cos_dist = (math.sin(phi1) * math.sin(phi2) +
                   math.cos(phi1) * math.cos(phi2) * math.cos(theta2 - theta1))

        # Clamp to avoid numerical errors
        cos_dist = max(-1.0, min(1.0, cos_dist))

        # Scale by average radius
        radius = (self.width + self.height) / (4 * math.pi)
        return radius * math.acos(cos_dist)

    # ========== Geodesics (Shortest Paths) ==========

    def geodesic(self, p1: ManifoldPoint, p2: ManifoldPoint, num_points: int = 50) -> List[ManifoldPoint]:
        """
        Compute geodesic (shortest path) between two points.

        Returns list of points along the geodesic.
        """
        if self.topology == Topology.FLAT:
            return self._flat_geodesic(p1, p2, num_points)
        elif self.topology == Topology.TOROIDAL:
            return self._toroidal_geodesic(p1, p2, num_points)
        elif self.topology == Topology.SPHERICAL:
            return self._spherical_geodesic(p1, p2, num_points)
        else:
            raise NotImplementedError(f"Geodesic not implemented for {self.topology}")

    def _flat_geodesic(self, p1: ManifoldPoint, p2: ManifoldPoint, num_points: int) -> List[ManifoldPoint]:
        """Straight line (flat manifold)"""
        path = []
        for i in range(num_points):
            t = i / (num_points - 1)
            u = p1.u + t * (p2.u - p1.u)
            v = p1.v + t * (p2.v - p1.v)
            path.append(ManifoldPoint(u, v))
        return path

    def _toroidal_geodesic(self, p1: ManifoldPoint, p2: ManifoldPoint, num_points: int) -> List[ManifoldPoint]:
        """
        Shortest path on torus (may wrap around edges).
        """
        # Determine wrapping direction
        du_direct = p2.u - p1.u
        dv_direct = p2.v - p1.v

        du_wrapped = du_direct + (self.width if du_direct < 0 else -self.width)
        dv_wrapped = dv_direct + (self.height if dv_direct < 0 else -self.height)

        du = du_direct if abs(du_direct) < abs(du_wrapped) else du_wrapped
        dv = dv_direct if abs(dv_direct) < abs(dv_wrapped) else dv_wrapped

        # Generate path (with wrapping)
        path = []
        for i in range(num_points):
            t = i / (num_points - 1)
            u = (p1.u + t * du) % self.width
            v = (p1.v + t * dv) % self.height
            path.append(ManifoldPoint(u, v))
        return path

    def _spherical_geodesic(self, p1: ManifoldPoint, p2: ManifoldPoint, num_points: int) -> List[ManifoldPoint]:
        """
        Great circle path on sphere.

        Uses slerp (spherical linear interpolation).
        """
        # Convert to spherical coordinates
        theta1 = p1.u * 2 * math.pi / self.width
        phi1 = p1.v * math.pi / self.height

        theta2 = p2.u * 2 * math.pi / self.width
        phi2 = p2.v * math.pi / self.height

        # Convert to 3D Cartesian
        x1, y1, z1 = self._spherical_to_cartesian(theta1, phi1)
        x2, y2, z2 = self._spherical_to_cartesian(theta2, phi2)

        # Slerp between two points on unit sphere
        path = []
        omega = math.acos(max(-1, min(1, x1*x2 + y1*y2 + z1*z2)))

        for i in range(num_points):
            t = i / (num_points - 1)

            if omega < 0.001:  # Points very close
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                z = z1 + t * (z2 - z1)
            else:
                factor1 = math.sin((1-t) * omega) / math.sin(omega)
                factor2 = math.sin(t * omega) / math.sin(omega)
                x = factor1 * x1 + factor2 * x2
                y = factor1 * y1 + factor2 * y2
                z = factor1 * z1 + factor2 * z2

            # Convert back to spherical then to (u,v)
            theta, phi = self._cartesian_to_spherical(x, y, z)
            u = theta * self.width / (2 * math.pi)
            v = phi * self.height / math.pi

            path.append(ManifoldPoint(u, v))

        return path

    # ========== Parallel Transport ==========

    def parallel_transport(self, vector: TangentVector, along_path: List[ManifoldPoint]) -> TangentVector:
        """
        Parallel transport a tangent vector along a path.

        This preserves the vector's "direction" as it moves along the manifold.
        Important for physics (velocity, acceleration).
        """
        if self.topology == Topology.FLAT:
            # On flat manifold, parallel transport doesn't change the vector
            return TangentVector(along_path[-1], vector.du, vector.dv)

        # For curved manifolds, need to integrate Christoffel symbols
        # (Simplified implementation - exact would use connection coefficients)
        # TODO: Implement full parallel transport for curved manifolds

        return TangentVector(along_path[-1], vector.du, vector.dv)

    # ========== Chart System ==========

    def wrap_point(self, point: ManifoldPoint) -> ManifoldPoint:
        """
        Apply boundary conditions based on topology.

        For toroidal: wrap coordinates
        For flat: clamp to bounds
        For spherical: handle poles
        """
        if self.topology == Topology.TOROIDAL:
            return ManifoldPoint(
                u=point.u % self.width,
                v=point.v % self.height
            )
        elif self.topology == Topology.FLAT:
            return ManifoldPoint(
                u=max(0, min(self.width, point.u)),
                v=max(0, min(self.height, point.v))
            )
        elif self.topology == Topology.SPHERICAL:
            # Handle pole wrapping
            u = point.u % self.width
            v = max(0, min(self.height, point.v))
            return ManifoldPoint(u, v)
        else:
            return point

    # ========== Helper Methods ==========

    def _compute_metric_tensor(self) -> np.ndarray:
        """
        Compute metric tensor for this manifold.

        For flat: [[1, 0], [0, 1]] (Euclidean)
        For toroidal: [[1, 0], [0, 1]] (flat torus)
        For spherical: [[r²sin²(v), 0], [0, r²]] (sphere)
        """
        if self.topology in [Topology.FLAT, Topology.TOROIDAL]:
            return np.array([[1.0, 0.0], [0.0, 1.0]])
        elif self.topology == Topology.SPHERICAL:
            # Spherical metric depends on position (simplified: use average)
            r = (self.width + self.height) / (4 * math.pi)
            return np.array([[r**2, 0.0], [0.0, r**2]])
        else:
            return np.eye(2)

    def _spherical_to_cartesian(self, theta: float, phi: float) -> Tuple[float, float, float]:
        """Convert spherical (θ, φ) to Cartesian (x,y,z) on unit sphere"""
        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)
        return x, y, z

    def _cartesian_to_spherical(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """Convert Cartesian (x,y,z) to spherical (θ, φ)"""
        r = math.sqrt(x**2 + y**2 + z**2)
        theta = math.atan2(y, x)
        if theta < 0:
            theta += 2 * math.pi
        phi = math.acos(z / max(r, 0.001))
        return theta, phi
