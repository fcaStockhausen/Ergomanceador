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

# Log-scale normalization constants for temperature-derived dimensions.
# Using log10 because temperature in Kelvin is a ratio scale and the
# element range spans 3 orders of magnitude (100K – 30000K).
_LOG_MAX_TEMP = math.log10(30000.0)    # ~4.477
_LOG_MAX_STE = math.log10(20000.0)     # state_transition_energy upper bound


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
        Convert PropertyVector to normalized numpy array.

n        All dimensions are normalized to [0, 1] (polarity stays [-1, 1]).
        Temperature-derived dims use LOG SCALE because element temps span
        3 orders of magnitude (shadow 100K → lightning 30000K).
        """
        return np.array([
            min(vector.thermal_flux / 2.0, 1.0),                                    # 0: thermal flux (0-2)
            math.log10(max(vector.avg_temperature, 1.0)) / _LOG_MAX_TEMP,            # 1: log temp
            math.log10(max(vector.temp_differential, 1.0)) / _LOG_MAX_TEMP,          # 2: log temp diff
            math.log10(max(vector.state_transition_energy, 1.0)) / _LOG_MAX_STE,     # 3: log state trans
            min(vector.phase_diversity, 1.0),                                        # 4: already 0-1
            min(vector.density_gradient, 1.0),                                       # 5: already 0-1
            min(vector.avg_density, 1.0),                                            # 6: already 0-1
            min(vector.volatility_index, 1.0),                                       # 7: already 0-1
            min(vector.chaos_factor, 1.0),                                           # 8: already 0-1
            min(vector.total_energy / 600.0, 1.0),                                   # 9: energy (max ~6×150)
            min(vector.energy_density / 150.0, 1.0),                                 # 10: energy/elem
            max(-1.0, min(vector.polarity_tension, 1.0)),                           # 11: polarity [-1,1]
        ])

    def _create_behavior_regions(self) -> List[BehaviorRegion]:
        """
        Define prototype points for each behavior in property space.

        These are the "ideal" property vectors for each behavior.
        Real spells are classified by proximity to these prototypes.
        """
        # Data-driven prototypes: positions computed from canonical element
        # combinations (see tools/chord_lab.py), then manually adjusted to
        # resolve collisions.  Metric tensors use per-dimension weights so
        # each behavior's "defining" axes dominate the distance calculation.
        #
        # Dim order:
        #  0 flux  1 log_temp  2 log_tdiff  3 log_ste  4 phase_div
        #  5 dgrad 6 avg_dens  7 volat      8 chaos    9 tot_eng
        # 10 e_dens 11 polarity

        regions = []

        # --- helpers -----------------------------------------------------
        def _proto(vals):
            return np.array(vals, dtype=float)

        def _metric(w):
            """Diagonal metric tensor from per-dimension weights."""
            return np.diag(np.array(w, dtype=float))
        # -----------------------------------------------------------------

        # PROJECTILE — single-element attack (fire, arcane)
        # Defined by: moderate energy density, neutral polarity
        regions.append(BehaviorRegion(
            name=self.PROJECTILE,
            prototype=_proto([
                0.15, 0.67, 0.15, 0.55, 0.25, 0.05, 0.30, 0.60, 0.05, 0.20, 0.72, -0.25
            ]),
            metric_tensor=_metric([
                1, 1, 1, 1, 1, 1, 1.5, 1.5, 1, 1.5, 2.0, 1.0
            ]),
            threshold=1.0
        ))

        # BEAM — focused energy line (arcane + shadow)
        # Defined by: HIGH energy density, LOW volatility, moderate flux
        # Separated from CHAIN by lower flux and higher energy concentration
        regions.append(BehaviorRegion(
            name=self.BEAM,
            prototype=_proto([
                0.50, 0.62, 0.50, 0.50, 0.25, 0.25, 0.35, 0.35, 0.10, 0.45, 0.85, -0.20
            ]),
            metric_tensor=_metric([
                1.5, 1, 1, 1, 0.5, 1, 1.5, 2.0, 1.5, 1, 3.0, 1
            ]),
            threshold=1.0
        ))

        # AOE — explosive burst (triple fire, triple-stacked elements)
        # Defined by: HIGH total energy, HIGH volatility, stacked same element
        regions.append(BehaviorRegion(
            name=self.AOE,
            prototype=_proto([
                0.10, 0.75, 0.10, 0.62, 0.25, 0.05, 0.25, 0.85, 0.10, 0.68, 0.70, -0.50
            ]),
            metric_tensor=_metric([
                0.5, 1, 0.5, 1, 1, 0.5, 1, 3.0, 1.5, 3.5, 1, 0.5
            ]),
            threshold=1.0
        ))

        # AREA_DENIAL — persistent zone (earth, ice+earth)
        # Defined by: high density, low volatility, moderate persistence
        # Separated from SHIELD by LOWER density and HIGHER volatility tolerance
        regions.append(BehaviorRegion(
            name=self.AREA_DENIAL,
            prototype=_proto([
                0.02, 0.54, 0.10, 0.52, 0.25, 0.02, 0.72, 0.15, 0.01, 0.15, 0.37, 0.00
            ]),
            metric_tensor=_metric([
                1, 1, 1, 2.0, 0.5, 0.5, 3.0, 4.0, 2.0, 1, 1, 1
            ]),
            threshold=1.0
        ))

        # BUFF — enhancement aura (earth+nature, water+nature, light+nature)
        # Defined by: positive polarity, low chaos, moderate density
        regions.append(BehaviorRegion(
            name=self.BUFF,
            prototype=_proto([
                0.01, 0.55, 0.19, 0.47, 0.38, 0.20, 0.55, 0.28, 0.07, 0.19, 0.38, 0.50
            ]),
            metric_tensor=_metric([
                1, 1, 1, 1, 1, 1, 1, 2.0, 2.0, 1, 1, 3.0
            ]),
            threshold=1.0
        ))

        # HEAL — restoration (nature, nature+nature)
        # Defined by: VERY HIGH positive polarity, low thermal activity
        regions.append(BehaviorRegion(
            name=self.HEAL,
            prototype=_proto([
                0.00, 0.55, 0.00, 0.44, 0.25, 0.00, 0.40, 0.40, 0.00, 0.17, 0.47, 1.00
            ]),
            metric_tensor=_metric([
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5.0
            ]),
            threshold=1.0
        ))

        # SHIELD — solid barrier (earth+earth, ice+earth+earth)
        # Defined by: VERY HIGH density, very low volatility, high persistence
        # Separated from AREA_DENIAL by HIGHER density + persistence weights
        regions.append(BehaviorRegion(
            name=self.SHIELD,
            prototype=_proto([
                0.02, 0.55, 0.05, 0.60, 0.25, 0.00, 0.97, 0.05, 0.00, 0.25, 0.35, 0.00
            ]),
            metric_tensor=_metric([
                0.5, 0.5, 0.5, 3.0, 0.5, 0.5, 5.0, 3.0, 2.0, 1, 1, 1
            ]),
            threshold=1.0
        ))

        # HOMING — seeking projectile (arcane+arcane, triple arcane)
        # Defined by: LOW density, high energy concentration, MODERATE volatility
        # Separated from PROJECTILE by lower density and higher energy
        regions.append(BehaviorRegion(
            name=self.HOMING,
            prototype=_proto([
                0.00, 0.67, 0.00, 0.56, 0.25, 0.00, 0.18, 0.50, 0.10, 0.50, 0.80, 0.00
            ]),
            metric_tensor=_metric([
                1, 1, 1, 1, 1, 1, 3.0, 1, 2.5, 2.0, 2.0, 1
            ]),
            threshold=1.0
        ))

        # CHAIN — jumping energy (fire+shadow, arcane+shadow)
        # Defined by: VERY HIGH thermal flux, moderate energy
        # Separated from BEAM by higher flux
        regions.append(BehaviorRegion(
            name=self.CHAIN,
            prototype=_proto([
                0.88, 0.65, 0.72, 0.54, 0.38, 0.28, 0.40, 0.45, 0.30, 0.40, 0.68, -0.40
            ]),
            metric_tensor=_metric([
                4.0, 1, 2.0, 1, 1, 1, 1, 1, 1, 1.5, 1, 1
            ]),
            threshold=1.0
        ))

        # SPLIT — fragmenting chaos (fire+light, arcane+fire+light, lightning)
        # Defined by: HIGH chaos, high temp, high flux, low density
        regions.append(BehaviorRegion(
            name=self.SPLIT,
            prototype=_proto([
                0.82, 0.88, 0.85, 0.72, 0.42, 0.18, 0.14, 0.58, 0.72, 0.50, 0.75, -0.10
            ]),
            metric_tensor=_metric([
                1.5, 2.0, 1, 1, 1.5, 1, 2.0, 1.5, 4.0, 1, 1, 1
            ]),
            threshold=1.0
        ))

        return regions
