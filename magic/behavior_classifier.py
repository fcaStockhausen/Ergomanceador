"""
Behavior Classification System for Property-Based Magic

Maps property vectors to spell behaviors using mathematical classification,
not hard-coded if-else logic. Behaviors emerge from property space regions.
"""

import math
from typing import Dict, Tuple
from magic.property_vector import PropertyVector


class BehaviorClassifier:
    """
    Classifies spell behavior from property vectors using
    geometric regions in property space.

    NO IF-ELSE CHAINS - behaviors emerge from mathematical functions.
    """

    # Behavior types
    PROJECTILE = 'projectile'
    BEAM = 'beam'
    AOE = 'aoe'
    AREA_DENIAL = 'area_denial'
    BUFF = 'buff'
    HEAL = 'heal'
    HOMING = 'homing'
    CHAIN = 'chain'

    def __init__(self, coefficients: Dict = None):
        """
        Initialize classifier with tunable coefficients.
        Coefficients can be loaded from JSON for easy balance tuning.
        """
        self.coefficients = coefficients or self._default_coefficients()

    def classify(self, vector: PropertyVector) -> str:
        """
        Classify behavior from property vector.

        Uses weighted scoring functions - each behavior gets a score,
        highest score wins. NO if-else cascades.
        """
        # Compute score for each behavior
        scores = {
            self.PROJECTILE: self._score_projectile(vector),
            self.BEAM: self._score_beam(vector),
            self.AOE: self._score_aoe(vector),
            self.AREA_DENIAL: self._score_area_denial(vector),
            self.BUFF: self._score_buff(vector),
            self.HEAL: self._score_heal(vector),
            self.HOMING: self._score_homing(vector),
            self.CHAIN: self._score_chain(vector),
        }

        # Return behavior with highest score
        return max(scores.items(), key=lambda x: x[1])[0]

    def get_behavior_probabilities(self, vector: PropertyVector) -> Dict[str, float]:
        """
        Get probability distribution over behaviors.
        Useful for UI showing "this spell is 70% projectile, 30% AOE".
        """
        scores = {
            self.PROJECTILE: self._score_projectile(vector),
            self.BEAM: self._score_beam(vector),
            self.AOE: self._score_aoe(vector),
            self.AREA_DENIAL: self._score_area_denial(vector),
            self.BUFF: self._score_buff(vector),
            self.HEAL: self._score_heal(vector),
            self.HOMING: self._score_homing(vector),
            self.CHAIN: self._score_chain(vector),
        }

        # Softmax to convert scores to probabilities
        total = sum(math.exp(s) for s in scores.values())
        return {k: math.exp(v) / total for k, v in scores.items()}

    # ========== Scoring Functions ==========
    # Each function computes a score for one behavior.
    # Higher score = more likely to be that behavior.
    # These are MATHEMATICAL FORMULAS, not if-else logic.

    def _score_projectile(self, v: PropertyVector) -> float:
        """
        Projectile behavior: moderate density, moderate energy, low volatility.
        Classic "throw a spell" behavior - balanced properties.
        """
        c = self.coefficients['projectile']

        # Projectiles prefer medium density (not too fast, not too slow)
        density_score = c['density_weight'] * (1 - abs(v.avg_density - 0.5) * 2)

        # Moderate energy (not weak, not explosive)
        energy_score = c['energy_weight'] * math.tanh(v.energy_density / 50.0)

        # Low volatility (stable, not chaotic)
        volatility_penalty = c['volatility_penalty'] * v.volatility_index

        return density_score + energy_score - volatility_penalty + c['base_score']

    def _score_beam(self, v: PropertyVector) -> float:
        """
        Beam behavior: low density, high thermal flux, high energy density.
        Concentrated energy in a line - think lightning bolt, laser beam.
        """
        c = self.coefficients['beam']

        # Beams are fast = low density
        density_score = c['density_weight'] * (1 - v.avg_density)

        # High thermal flux (rapid energy transfer)
        flux_score = c['flux_weight'] * v.thermal_flux

        # High energy density (concentrated power)
        energy_score = c['energy_weight'] * math.tanh(v.energy_density / 30.0)

        return density_score + flux_score + energy_score + c['base_score']

    def _score_aoe(self, v: PropertyVector) -> float:
        """
        AOE (Area of Effect) behavior: high volatility, high phase diversity.
        Explosive, unstable, affects large area - fireballs, explosions.
        """
        c = self.coefficients['aoe']

        # High volatility = explosive
        volatility_score = c['volatility_weight'] * v.volatility_index

        # High phase diversity = chaotic energy release
        diversity_score = c['diversity_weight'] * v.phase_diversity

        # High chaos factor = unpredictable expansion
        chaos_score = c['chaos_weight'] * v.chaos_factor

        return volatility_score + diversity_score + chaos_score + c['base_score']

    def _score_area_denial(self, v: PropertyVector) -> float:
        """
        Area denial behavior: low volatility, high state transition energy.
        Persistent zones - walls, barriers, lingering effects.
        """
        c = self.coefficients['area_denial']

        # Low volatility = stable, doesn't explode
        stability_score = c['stability_weight'] * (1 - v.volatility_index)

        # High state transition energy = hard to dissipate
        persistence_score = c['persistence_weight'] * math.tanh(v.state_transition_energy / 500.0)

        # High density = solid, physical presence
        density_score = c['density_weight'] * v.avg_density

        return stability_score + persistence_score + density_score + c['base_score']

    def _score_buff(self, v: PropertyVector) -> float:
        """
        Buff behavior: low energy, low chaos, single element preferred.
        Protective, enhancing, stable - shields, armor, speed boosts.
        """
        c = self.coefficients['buff']

        # Low chaos = controlled, predictable
        control_score = c['control_weight'] * (1 - v.chaos_factor)

        # Low energy = non-aggressive
        gentle_score = c['gentle_weight'] * (1 - math.tanh(v.energy_density / 50.0))

        # Single element bonus (pure element buffs are stronger)
        simplicity_score = c['simplicity_weight'] * (1.0 / max(v.element_count, 1))

        # Positive polarity preferred for buffs
        polarity_score = c['polarity_weight'] * max(0, v.polarity_tension)

        return control_score + gentle_score + simplicity_score + polarity_score + c['base_score']

    def _score_heal(self, v: PropertyVector) -> float:
        """
        Heal behavior: positive polarity, low thermal flux, moderate energy.
        Restorative, life-giving - healing spells.
        """
        c = self.coefficients['heal']

        # Strong positive polarity = life energy
        polarity_score = c['polarity_weight'] * max(0, v.polarity_tension) ** 2

        # Low thermal flux = gentle, not aggressive
        gentle_score = c['gentle_weight'] * (1 - v.thermal_flux)

        # Moderate energy (enough to heal, not to harm)
        energy_score = c['energy_weight'] * math.tanh(v.energy_density / 40.0) * (1 - math.tanh(v.energy_density / 100.0))

        return polarity_score + gentle_score + energy_score + c['base_score']

    def _score_homing(self, v: PropertyVector) -> float:
        """
        Homing behavior: low density, high chaos, moderate volatility.
        Seeking, adaptive - missiles that track targets.
        """
        c = self.coefficients['homing']

        # Low density = fast, agile
        speed_score = c['speed_weight'] * (1 - v.avg_density)

        # Moderate chaos = unpredictable path, but not explosive
        chaos_score = c['chaos_weight'] * v.chaos_factor * (1 - v.volatility_index)

        # High energy density = powerful tracking
        energy_score = c['energy_weight'] * math.tanh(v.energy_density / 60.0)

        return speed_score + chaos_score + energy_score + c['base_score']

    def _score_chain(self, v: PropertyVector) -> float:
        """
        Chain behavior: high thermal flux, moderate density, high energy.
        Jumps between targets - chain lightning, spreading effects.
        """
        c = self.coefficients['chain']

        # High thermal flux = rapid energy transfer between targets
        flux_score = c['flux_weight'] * v.thermal_flux

        # High energy = enough power to jump
        energy_score = c['energy_weight'] * math.tanh(v.energy_density / 50.0)

        # Moderate density = not too slow
        density_score = c['density_weight'] * (1 - abs(v.avg_density - 0.4))

        return flux_score + energy_score + density_score + c['base_score']

    def _default_coefficients(self) -> Dict:
        """
        Default tuning coefficients.
        These can be overridden by loading from JSON config file.
        """
        return {
            'projectile': {
                'base_score': 5.0,  # Baseline: projectile is default behavior
                'density_weight': 3.0,
                'energy_weight': 2.0,
                'volatility_penalty': 2.0
            },
            'beam': {
                'base_score': 0.0,
                'density_weight': 4.0,
                'flux_weight': 3.0,
                'energy_weight': 2.0
            },
            'aoe': {
                'base_score': 0.0,
                'volatility_weight': 5.0,
                'diversity_weight': 3.0,
                'chaos_weight': 2.0
            },
            'area_denial': {
                'base_score': 0.0,
                'stability_weight': 4.0,
                'persistence_weight': 3.0,
                'density_weight': 2.0
            },
            'buff': {
                'base_score': 0.0,
                'control_weight': 3.0,
                'gentle_weight': 2.0,
                'simplicity_weight': 4.0,
                'polarity_weight': 2.0
            },
            'heal': {
                'base_score': 0.0,
                'polarity_weight': 6.0,  # Strong polarity requirement for healing
                'gentle_weight': 3.0,
                'energy_weight': 2.0
            },
            'homing': {
                'base_score': 0.0,
                'speed_weight': 3.0,
                'chaos_weight': 3.0,
                'energy_weight': 2.0
            },
            'chain': {
                'base_score': 0.0,
                'flux_weight': 4.0,
                'energy_weight': 3.0,
                'density_weight': 2.0
            }
        }
