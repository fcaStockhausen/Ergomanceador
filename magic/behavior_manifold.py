"""
Behavior Manifold: Geometric Classification of Spell Behaviors

The property vector space R^N is partitioned into behavior regions.
Behaviors emerge from the manifold geometry, not scoring functions.

This is a GEOMETRIC approach:
- Property vectors are points in R^N
- Each behavior corresponds to a region in this space
- Classification = finding which region contains the point
- Boundaries between regions form a decision manifold
"""

import math
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from magic.property_vector import PropertyVector


@dataclass
class BehaviorRegion:
    """
    Defines a region in property space corresponding to a behavior.

    Uses a **distance metric** from an ideal prototype point.
    The region is a generalized ellipsoid in property space.
    """
    name: str
    prototype: np.ndarray      # Ideal property vector for this behavior
    metric_tensor: np.ndarray  # Defines distance in curved property space
    threshold: float           # Maximum distance for classification


class BehaviorManifold:
    """
    The property space as a Riemannian manifold with behavior regions.

    Mathematical structure:
    - Property space M = R^N (12-dimensional)
    - Metric g: TM → R (distance function)
    - Partition: M = ⋃ Ri (union of behavior regions)
    - Decision boundary: ∂Ri ∩ ∂Rj (where regions meet)
    """

    # Behavior types
    PROJECTILE = 'projectile'
    BEAM = 'beam'
    AOE = 'aoe'
    AREA_DENIAL = 'area_denial'
    BUFF = 'buff'
    HEAL = 'heal'
    SHIELD = 'shield'
    HOMING = 'homing'
    CHAIN = 'chain'
    SPLIT = 'split'

    def __init__(self):
        """Initialize the behavior manifold with prototype regions"""
        self.regions = self._create_behavior_regions()
        self.dimension = 12  # Property vector dimension

    def classify(self, vector: PropertyVector) -> str:
        """
        Classify behavior by finding closest region in manifold.

        Uses geodesic distance in property space (Riemannian metric).
        Returns behavior of nearest prototype.
        """
        # Convert PropertyVector to numpy array
        v = self._vector_to_array(vector)

        # Compute distance to each behavior region
        distances = {}
        for region in self.regions:
            dist = self._riemannian_distance(v, region.prototype, region.metric_tensor)
            distances[region.name] = dist

        # Return behavior with minimum distance
        return min(distances.items(), key=lambda x: x[1])[0]

    def get_behavior_distances(self, vector: PropertyVector) -> Dict[str, float]:
        """
        Get distances to all behavior regions.
        Useful for UI: "This spell is between projectile (0.3) and AOE (0.5)"
        """
        v = self._vector_to_array(vector)

        distances = {}
        for region in self.regions:
            dist = self._riemannian_distance(v, region.prototype, region.metric_tensor)
            distances[region.name] = dist

        return distances

    def get_behavior_probabilities(self, vector: PropertyVector) -> Dict[str, float]:
        """
        Convert distances to probabilities using softmax.
        Closer regions = higher probability.
        """
        distances = self.get_behavior_distances(vector)

        # Invert distances (closer = higher value)
        inv_distances = {k: 1.0 / (v + 0.1) for k, v in distances.items()}

        # Softmax
        total = sum(math.exp(v) for v in inv_distances.values())
        return {k: math.exp(v) / total for k, v in inv_distances.items()}

    def visualize_position(self, vector: PropertyVector) -> Dict:
        """
        Get visualization data for where vector sits in manifold.
        Returns coordinates in 2D projection of property space.
        """
        v = self._vector_to_array(vector)

        # Project to 2D using PCA-like transform
        # (Simplified: use first 2 principal components)
        x_coord = v[0] + v[1]  # Thermal properties
        y_coord = v[4] + v[6]  # Volatility + density

        return {
            'x': x_coord,
            'y': y_coord,
            'nearest_behavior': self.classify(vector),
            'distances': self.get_behavior_distances(vector)
        }

    # ========== Private Methods ==========

    def _riemannian_distance(self, v1: np.ndarray, v2: np.ndarray, metric_tensor: np.ndarray) -> float:
        """
        Compute Riemannian distance between two points using metric tensor.

        Distance: d(v1, v2) = sqrt((v1 - v2)^T * G * (v1 - v2))
        where G is the metric tensor (defines curved geometry)
        """
        delta = v1 - v2
        dist_squared = delta.T @ metric_tensor @ delta
        return math.sqrt(max(0, dist_squared))  # Ensure non-negative

    def _vector_to_array(self, vector: PropertyVector) -> np.ndarray:
        """
        Convert PropertyVector to numpy array for linear algebra.

        IMPORTANT: All dimensions are normalized to [0, 1] range for
        homogeneous distance calculations. Without normalization,
        high-magnitude dimensions dominate the metric.
        """
        return np.array([
            vector.thermal_flux / 2.0,        # Normalize: typical range 0-2
            vector.avg_temperature / 2000.0,  # Normalize: 0-2000K → 0-1
            vector.temp_differential / 2000.0, # Normalize: 0-2000K → 0-1
            vector.state_transition_energy / 1000.0,  # Normalize: 0-1000 → 0-1
            vector.phase_diversity,           # Already 0-1
            vector.density_gradient,          # Already 0-1
            vector.avg_density,               # Already 0-1
            vector.volatility_index,          # Already 0-1
            vector.chaos_factor,              # Already 0-1
            vector.total_energy / 400.0,      # Normalize: 0-400 → 0-1
            vector.energy_density / 150.0,    # Normalize: 0-150 → 0-1
            vector.polarity_tension           # Already -1 to 1
        ])

    def _create_behavior_regions(self) -> List[BehaviorRegion]:
        """
        Define prototype points for each behavior in property space.

        These are the "ideal" property vectors for each behavior.
        Real spells are classified by proximity to these prototypes.
        """
        # Identity metric tensor (Euclidean distance) for all behaviors
        # Can be customized per behavior to create curved regions
        identity_metric = np.eye(12)

        # Define prototype property vectors for each behavior
        # Each value represents the ideal position in that dimension

        regions = []

        # PROJECTILE: Balanced, moderate in all properties
        regions.append(BehaviorRegion(
            name=self.PROJECTILE,
            prototype=np.array([
                0.3,   # thermal_flux (moderate)
                0.4,   # avg_temperature (moderate)
                0.3,   # temp_differential (moderate)
                0.3,   # state_transition_energy
                0.5,   # phase_diversity
                0.4,   # density_gradient
                0.5,   # avg_density (medium)
                0.4,   # volatility (moderate)
                0.3,   # chaos_factor
                0.5,   # total_energy
                0.5,   # energy_density
                0.0    # polarity_tension (neutral)
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # BEAM: Low density, high thermal flux, high energy
        regions.append(BehaviorRegion(
            name=self.BEAM,
            prototype=np.array([
                0.8,   # thermal_flux (HIGH - rapid energy transfer)
                0.6,   # avg_temperature (high)
                0.5,   # temp_differential
                0.3,   # state_transition_energy
                0.3,   # phase_diversity
                0.5,   # density_gradient
                0.2,   # avg_density (LOW - fast)
                0.3,   # volatility (controlled)
                0.2,   # chaos_factor (controlled)
                0.7,   # total_energy (HIGH)
                0.8,   # energy_density (HIGH - concentrated)
                0.0    # polarity_tension
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # AOE: High volatility, high phase diversity, chaos
        regions.append(BehaviorRegion(
            name=self.AOE,
            prototype=np.array([
                0.5,   # thermal_flux
                0.7,   # avg_temperature (hot explosion)
                0.6,   # temp_differential
                0.4,   # state_transition_energy
                0.8,   # phase_diversity (HIGH - multi-state chaos)
                0.6,   # density_gradient
                0.4,   # avg_density
                0.9,   # volatility (HIGH - explosive)
                0.7,   # chaos_factor (HIGH - unpredictable expansion)
                0.6,   # total_energy
                0.5,   # energy_density
                0.0    # polarity_tension
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # AREA_DENIAL: Low volatility, high persistence, high density
        regions.append(BehaviorRegion(
            name=self.AREA_DENIAL,
            prototype=np.array([
                0.2,   # thermal_flux (LOW - stable)
                0.4,   # avg_temperature
                0.2,   # temp_differential (stable)
                0.8,   # state_transition_energy (HIGH - persistent)
                0.4,   # phase_diversity
                0.3,   # density_gradient
                0.8,   # avg_density (HIGH - solid, physical)
                0.2,   # volatility (LOW - doesn't explode)
                0.2,   # chaos_factor (LOW - controlled)
                0.4,   # total_energy
                0.3,   # energy_density
                0.0    # polarity_tension
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # BUFF: Low chaos, low energy, positive polarity, HIGH persistence
        regions.append(BehaviorRegion(
            name=self.BUFF,
            prototype=np.array([
                0.1,   # thermal_flux (VERY LOW - stable aura)
                0.2,   # avg_temperature (cool)
                0.1,   # temp_differential (very stable)
                0.7,   # state_transition_energy (HIGH - long-lasting)
                0.1,   # phase_diversity (VERY simple - pure)
                0.1,   # density_gradient (uniform)
                0.6,   # avg_density (somewhat solid - protective)
                0.1,   # volatility (VERY LOW - stable)
                0.05,  # chaos_factor (VERY LOW - controlled)
                0.2,   # total_energy (LOW - defensive, not offensive)
                0.2,   # energy_density
                0.6    # polarity_tension (MODERATE POSITIVE - protective)
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # HEAL: VERY HIGH polarity, low thermal, ACTIVE energy (not passive like buff)
        regions.append(BehaviorRegion(
            name=self.HEAL,
            prototype=np.array([
                0.3,   # thermal_flux (LOW but more than buff - active restoration)
                0.4,   # avg_temperature (warmer - life energy)
                0.2,   # temp_differential
                0.2,   # state_transition_energy (LOW - quick, not persistent)
                0.3,   # phase_diversity (more diverse - flowing life)
                0.3,   # density_gradient
                0.3,   # avg_density (LOW - flowing, not solid like buff)
                0.3,   # volatility (higher than buff - active effect)
                0.2,   # chaos_factor (higher than buff)
                0.5,   # total_energy (HIGHER - actively heals)
                0.5,   # energy_density (HIGHER - concentrated healing)
                0.95   # polarity_tension (VERY HIGH POSITIVE - pure life)
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # SHIELD: VERY HIGH density, VERY HIGH persistence, solid barrier
        # CRITICAL: This fills the high-density + high-persistence gap in manifold
        # DISTINCT from BUFF (buff = enhancement, shield = absorption)
        regions.append(BehaviorRegion(
            name=self.SHIELD,
            prototype=np.array([
                0.15,  # thermal_flux (VERY LOW - energy contained, not radiating)
                0.3,   # avg_temperature (cool, stable)
                0.1,   # temp_differential (VERY stable - no phase changes)
                0.9,   # state_transition_energy (VERY HIGH - extremely persistent)
                0.2,   # phase_diversity (LOW - single solid state)
                0.2,   # density_gradient (LOW - uniform structure)
                0.95,  # avg_density (VERY HIGH - solid crystalline barrier)
                0.1,   # volatility (VERY LOW - doesn't break easily)
                0.1,   # chaos_factor (VERY LOW - ordered crystal structure)
                0.4,   # total_energy (MODERATE - defensive, not offensive)
                0.4,   # energy_density (moderate - distributed in structure)
                0.4    # polarity_tension (MODERATE POSITIVE - protective but not "holy")
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # HOMING: Low density, moderate chaos, high energy
        regions.append(BehaviorRegion(
            name=self.HOMING,
            prototype=np.array([
                0.4,   # thermal_flux
                0.5,   # avg_temperature
                0.4,   # temp_differential
                0.3,   # state_transition_energy
                0.5,   # phase_diversity
                0.5,   # density_gradient
                0.3,   # avg_density (LOW - fast, agile)
                0.5,   # volatility (moderate)
                0.6,   # chaos_factor (MODERATE - adaptive path)
                0.6,   # total_energy (high)
                0.6,   # energy_density
                0.0    # polarity_tension
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # CHAIN: High thermal flux, moderate density, high energy
        regions.append(BehaviorRegion(
            name=self.CHAIN,
            prototype=np.array([
                0.9,   # thermal_flux (VERY HIGH - rapid transfer between targets)
                0.6,   # avg_temperature
                0.7,   # temp_differential
                0.4,   # state_transition_energy
                0.6,   # phase_diversity
                0.5,   # density_gradient
                0.4,   # avg_density (moderate)
                0.5,   # volatility
                0.5,   # chaos_factor
                0.7,   # total_energy (HIGH - needs power to jump)
                0.6,   # energy_density
                0.0    # polarity_tension
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        # SPLIT: High chaos, high temp, LOW density (non-dense gaseous splitting)
        regions.append(BehaviorRegion(
            name=self.SPLIT,
            prototype=np.array([
                0.6,   # thermal_flux (HIGH - energetic splitting)
                0.8,   # avg_temperature (VERY HIGH - hot, chaotic)
                0.7,   # temp_differential (HIGH - unstable)
                0.3,   # state_transition_energy (LOW - easily fragments)
                0.7,   # phase_diversity (HIGH - multi-state chaos)
                0.6,   # density_gradient (HIGH - uneven distribution causes split)
                0.2,   # avg_density (VERY LOW - gaseous, non-dense)
                0.8,   # volatility (HIGH - explosive tendency)
                0.9,   # chaos_factor (VERY HIGH - unpredictable fragmentation)
                0.6,   # total_energy (HIGH - enough to split)
                0.5,   # energy_density (moderate)
                -0.3   # polarity_tension (SLIGHTLY NEGATIVE - unstable)
            ]),
            metric_tensor=identity_metric,
            threshold=1.0
        ))

        return regions
