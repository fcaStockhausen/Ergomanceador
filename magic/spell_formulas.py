"""
Formula-Based Spell Stat Computation

All spell stats (damage, area, speed, duration, etc.) are computed
from property vectors using mathematical formulas, not hard-coded values.

Formulas are tunable via coefficients that can be loaded from JSON.
"""

import math
from typing import Dict
from magic.property_vector import PropertyVector


class SpellFormulas:
    """
    Computes spell statistics from property vectors using formulas.
    NO MAGIC NUMBERS - all coefficients are explicit and tunable.
    """

    def __init__(self, coefficients: Dict = None):
        """
        Initialize with tunable coefficients.
        Load from JSON for easy game balance tuning without code changes.
        """
        self.coeff = coefficients or self._default_coefficients()

    # ========== Core Stat Formulas ==========

    def compute_damage(self, vector: PropertyVector, behavior: str) -> int:
        """
        Damage formula: f(total_energy, polarity_tension, temp_differential, behavior_modifier)

        Higher energy → higher damage (linear with saturation)
        Polarity tension amplifies or reduces damage
        Temperature differential adds thermal damage
        Behavior modifier scales based on spell type
        """
        c = self.coeff['damage']

        # Base damage from total energy
        energy_damage = c['energy_multiplier'] * vector.total_energy

        # Polarity amplification (positive + negative = amplify)
        polarity_mult = 1.0 + c['polarity_factor'] * abs(vector.polarity_tension)

        # Thermal damage from temperature differential
        thermal_damage = c['thermal_factor'] * math.sqrt(vector.temp_differential)

        # Behavior modifier
        behavior_mult = c['behavior_modifiers'].get(behavior, 1.0)

        # Total damage with saturation (prevents infinite scaling)
        raw_damage = (energy_damage + thermal_damage) * polarity_mult * behavior_mult
        saturated_damage = c['saturation_limit'] * math.tanh(raw_damage / c['saturation_limit'])

        return int(max(1, saturated_damage))

    def compute_area(self, vector: PropertyVector, behavior: str) -> float:
        """
        Area formula: f(volatility, phase_diversity, chaos_factor, density_gradient, behavior_base)

        Volatility → explosive expansion
        Phase diversity → unstable boundaries
        Chaos → unpredictable spread
        Density gradient → diffusion rate
        """
        c = self.coeff['area']

        # Base area from behavior
        base_area = c['behavior_base_area'].get(behavior, 2.0)

        # Volatility expansion (exponential - high volatility = MUCH bigger area)
        volatility_expansion = c['volatility_factor'] * (math.exp(vector.volatility_index * 2) - 1)

        # Phase diversity adds instability
        diversity_expansion = c['diversity_factor'] * vector.phase_diversity

        # Chaos factor spreads randomly
        chaos_expansion = c['chaos_factor'] * vector.chaos_factor

        # Low density = easier to diffuse = larger area
        density_penalty = c['density_penalty'] * vector.avg_density

        total_area = base_area + volatility_expansion + diversity_expansion + chaos_expansion - density_penalty

        return max(0.5, round(total_area, 1))

    def compute_speed(self, vector: PropertyVector, behavior: str) -> float:
        """
        Speed formula: f(density, energy_density, thermal_flux, behavior_base)

        Low density → fast (light projectiles move faster)
        High energy density → fast (high energy accelerates)
        High thermal flux → fast (rapid energy transfer)
        """
        c = self.coeff['speed']

        # Base speed from behavior
        base_speed = c['behavior_base_speed'].get(behavior, 1.0)

        # Density inversely affects speed (heavy = slow)
        density_factor = c['density_multiplier'] * (1.0 - vector.avg_density)

        # Energy density accelerates
        energy_factor = c['energy_factor'] * math.tanh(vector.energy_density / 50.0)

        # Thermal flux adds speed (rapid energy transfer)
        flux_factor = c['flux_factor'] * vector.thermal_flux

        total_speed = base_speed + density_factor + energy_factor + flux_factor

        return max(0.1, round(total_speed, 2))

    def compute_duration(self, vector: PropertyVector, behavior: str) -> float:
        """
        Duration formula: f(state_transition_energy, volatility, chaos_factor, behavior_base)

        High state transition energy → long duration (hard to dissipate)
        Low volatility → long duration (stable, doesn't explode)
        Low chaos → long duration (predictable, controlled)
        """
        c = self.coeff['duration']

        # Base duration from behavior
        base_duration = c['behavior_base_duration'].get(behavior, 1.0)

        # State transition energy increases persistence
        persistence_factor = c['persistence_multiplier'] * math.tanh(vector.state_transition_energy / 500.0)

        # Low volatility = stable = lasts longer
        stability_factor = c['stability_factor'] * (1.0 - vector.volatility_index)

        # Low chaos = controlled = lasts longer
        control_factor = c['control_factor'] * (1.0 - vector.chaos_factor)

        total_duration = base_duration + persistence_factor + stability_factor + control_factor

        return max(0.1, round(total_duration, 1))

    def compute_mana_cost(self, vector: PropertyVector, behavior: str) -> int:
        """
        Mana cost formula: f(total_energy, element_count, polarity_tension, complexity, behavior_cost)

        More elements → higher cost (complexity)
        More energy → higher cost (power)
        Polarity imbalance → higher cost (instability)
        Behavior specific cost multiplier
        """
        c = self.coeff['mana']

        # Base cost per element
        element_cost = c['cost_per_element'] * vector.element_count

        # Energy cost (more powerful = more mana)
        energy_cost = c['energy_factor'] * vector.total_energy

        # Polarity tension cost (imbalanced spells cost more)
        polarity_cost = c['polarity_factor'] * abs(vector.polarity_tension) * 10

        # Complexity cost (chaotic spells harder to cast)
        complexity_cost = c['complexity_factor'] * vector.chaos_factor * 10

        # Behavior specific multiplier
        behavior_mult = c['behavior_multipliers'].get(behavior, 1.0)

        total_cost = (element_cost + energy_cost + polarity_cost + complexity_cost) * behavior_mult

        return int(max(5, total_cost))

    def compute_range(self, vector: PropertyVector, behavior: str) -> float:
        """
        Range formula: f(speed, duration, energy_density, behavior_base)

        Range = speed * duration for projectiles
        Range = energy for beams/instant effects
        """
        c = self.coeff['range']

        base_range = c['behavior_base_range'].get(behavior, 10.0)

        # For projectiles/homing: range = speed * time
        if behavior in ['projectile', 'homing', 'chain']:
            speed = self.compute_speed(vector, behavior)
            duration = self.compute_duration(vector, behavior)
            projectile_range = speed * duration * c['projectile_multiplier']
            return max(base_range, round(projectile_range, 1))

        # For beams/instant: range = energy-based
        elif behavior in ['beam']:
            energy_range = c['beam_multiplier'] * math.tanh(vector.energy_density / 30.0) * 20
            return max(base_range, round(energy_range, 1))

        # For AOE/area denial: range is area
        else:
            return self.compute_area(vector, behavior)

    def compute_knockback(self, vector: PropertyVector) -> float:
        """
        Knockback formula: f(energy_density, thermal_flux, polarity_tension)

        High energy → high knockback
        High thermal flux → explosive knockback
        Polarity tension amplifies knockback
        """
        c = self.coeff['knockback']

        # Energy-based knockback
        energy_kb = c['energy_factor'] * math.tanh(vector.energy_density / 50.0)

        # Thermal flux amplifies (explosive spells knock back more)
        flux_kb = c['flux_factor'] * vector.thermal_flux

        # Polarity amplification
        polarity_mult = 1.0 + c['polarity_factor'] * abs(vector.polarity_tension)

        total_kb = (energy_kb + flux_kb) * polarity_mult

        return max(0.0, round(total_kb, 2))

    def _default_coefficients(self) -> Dict:
        """
        Default formula coefficients.
        Load from JSON in production for easy tuning without code changes.
        """
        return {
            'damage': {
                'energy_multiplier': 1.2,  # Damage per energy point
                'polarity_factor': 0.3,    # Polarity amplification
                'thermal_factor': 0.15,    # Thermal damage contribution
                'saturation_limit': 55,    # Max damage per hit (high TTK)
                'behavior_modifiers': {
                    'projectile': 1.0,
                    'beam': 0.8,           # Beams do less damage but hit instantly
                    'aoe': 0.7,            # AOE spread out, less per-target damage
                    'area_denial': 0.5,    # Damage over time
                    'buff': 0.0,           # Buffs don't damage
                    'heal': 0.0,           # Heals don't damage
                    'homing': 1.1,         # Homing slightly stronger (harder to dodge)
                    'chain': 0.9,          # Chain splits damage
                    'shield': 0.0,         # Shields don't damage
                    'split': 0.6           # Split: low per-fragment damage
                }
            },
            'area': {
                'behavior_base_area': {
                    'projectile': 1.5,
                    'beam': 0.8,
                    'aoe': 5.0,
                    'area_denial': 4.0,
                    'buff': 0.5,
                    'heal': 2.0,
                    'homing': 1.2,
                    'chain': 1.0,
                    'shield': 2.0,        # Shield covers the caster
                    'split': 0.8           # Split fragments are small
                },
                'volatility_factor': 6.0,
                'diversity_factor': 3.0,
                'chaos_factor': 2.0,
                'density_penalty': 1.5
            },
            'speed': {
                'behavior_base_speed': {
                    'projectile': 8.0,     # Slower for better visibility (units/sec)
                    'beam': 99.0,          # Beams are instant
                    'aoe': 0.5,            # AOE expansion speed
                    'area_denial': 0.0,    # Area denial doesn't move
                    'buff': 0.0,
                    'heal': 0.0,
                    'homing': 6.0,         # Slightly slower but tracks
                    'chain': 10.0,         # Fast jumps
                    'shield': 0.0,         # Shield is stationary
                    'split': 8.0           # Same as projectile
                },
                'density_multiplier': 2.0,
                'energy_factor': 0.5,
                'flux_factor': 0.3
            },
            'duration': {
                'behavior_base_duration': {
                    'projectile': 1.0,
                    'beam': 0.1,           # Instant
                    'aoe': 0.5,            # Quick explosion
                    'area_denial': 5.0,    # Long-lasting zone
                    'buff': 3.0,           # Buffs last a while
                    'heal': 0.1,           # Instant
                    'homing': 2.0,         # Tracking duration
                    'chain': 0.8,          # Chain duration per jump
                    'shield': 4.0,         # Shield persists to absorb hits
                    'split': 1.0           # Same as projectile
                },
                'persistence_multiplier': 2.0,
                'stability_factor': 1.5,
                'control_factor': 1.0
            },
            'mana': {
                'cost_per_element': 8,
                'energy_factor': 0.15,
                'polarity_factor': 1.0,
                'complexity_factor': 2.0,
                'behavior_multipliers': {
                    'projectile': 1.0,
                    'beam': 1.2,           # Beams cost more (instant hit)
                    'aoe': 1.3,            # AOE costs more (multi-target)
                    'area_denial': 1.4,    # Area denial expensive (persistent)
                    'buff': 0.8,           # Buffs cheaper
                    'heal': 0.9,           # Healing slightly cheaper
                    'homing': 1.1,         # Homing slightly expensive
                    'chain': 1.2,          # Chain expensive (multi-hit)
                    'shield': 1.0,         # Shield: standard cost
                    'split': 1.1           # Split: slightly expensive (multi-projectile)
                }
            },
            'range': {
                'behavior_base_range': {
                    'projectile': 10.0,
                    'beam': 15.0,
                    'aoe': 5.0,
                    'area_denial': 3.0,
                    'buff': 0.0,
                    'heal': 3.0,
                    'homing': 12.0,
                    'chain': 8.0,
                    'shield': 1.0,        # Self-range only
                    'split': 8.0           # Same as projectile
                },
                'projectile_multiplier': 5.0,
                'beam_multiplier': 1.5
            },
            'knockback': {
                'energy_factor': 3.0,
                'flux_factor': 2.0,
                'polarity_factor': 0.5
            }
        }
