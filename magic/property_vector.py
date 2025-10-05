"""
Property Vector System for Emergent Magic Interactions

This module computes property vectors from element combinations.
Vectors represent the fundamental physical state of a spell,
from which all behaviors and effects emerge mathematically.
"""

import math
from dataclasses import dataclass
from typing import List
from magic.element import Element


@dataclass
class PropertyVector:
    """
    Represents the physical property state of a spell combination.
    All spell behaviors and effects emerge from this vector.
    """

    # Thermal properties
    thermal_flux: float         # Rate of temperature change (K/s), drives phase transitions
    avg_temperature: float      # Mean temperature (K), affects base damage
    temp_differential: float    # Temperature range (K), creates instability

    # State/phase properties
    state_transition_energy: float  # Energy required for phase change, affects duration
    phase_diversity: float          # How many different states (0-1), affects area

    # Density/mass properties
    density_gradient: float     # Density variation (0-1), affects projectile behavior
    avg_density: float          # Mean density (0-1), affects speed

    # Volatility/chaos properties
    volatility_index: float     # Tendency to expand/explode (0-1), affects AoE
    chaos_factor: float         # Property variance, affects unpredictability

    # Energy properties
    total_energy: float         # Sum of all energies, drives damage
    energy_density: float       # Energy per element, affects intensity

    # Polarity properties
    polarity_tension: float     # Magnitude of polarity imbalance (-1 to 1)

    # Complexity
    element_count: int          # Number of elements in combination


class PropertyVectorComputer:
    """
    Computes property vectors from element combinations.
    Pure mathematical functions - no hard-coded behavior logic.
    """

    @staticmethod
    def compute(elements: List[Element]) -> PropertyVector:
        """
        Compute property vector from list of elements.
        This is the ONLY place where element properties are read.
        All downstream logic uses the vector, not raw elements.
        """
        if not elements:
            return PropertyVectorComputer._empty_vector()

        n = len(elements)

        # Extract raw properties
        temps = [e.temperature for e in elements]
        energies = [e.energy for e in elements]
        densities = [e.density for e in elements]
        volatilities = [e.volatility for e in elements]
        states = [e.state for e in elements]
        polarities = [e.polarity for e in elements]

        # Thermal properties
        avg_temp = sum(temps) / n
        min_temp = min(temps)
        max_temp = max(temps)
        temp_diff = max_temp - min_temp

        # Thermal flux = rate of temperature equilibration
        # Higher when mixing hot + cold
        thermal_flux = temp_diff / max(avg_temp, 1.0)  # Normalized by avg temp

        # State/phase properties
        unique_states = len(set(states))
        phase_diversity = unique_states / 4.0  # 4 possible states (solid/liquid/gas/plasma)

        # State transition energy (simplified heat capacity model)
        # High when mixing different states (requires energy to homogenize)
        state_transition_energy = phase_diversity * avg_temp

        # Density properties
        avg_density = sum(densities) / n
        density_variance = PropertyVectorComputer._variance(densities)
        density_gradient = math.sqrt(density_variance)  # Std dev

        # Volatility properties
        avg_volatility = sum(volatilities) / n
        volatility_variance = PropertyVectorComputer._variance(volatilities)
        volatility_index = avg_volatility  # Mean volatility

        # Chaos factor = overall property variance
        # High chaos = unpredictable interactions
        temp_var = PropertyVectorComputer._variance([t / 1000.0 for t in temps])  # Normalize temps
        energy_var = PropertyVectorComputer._variance([e / 100.0 for e in energies])  # Normalize energies
        chaos_factor = math.sqrt(temp_var + energy_var + density_variance + volatility_variance) / 4.0

        # Energy properties
        total_energy = sum(energies)
        energy_density = total_energy / n

        # Polarity properties
        polarity_values = {
            'positive': 1.0,
            'negative': -1.0,
            'neutral': 0.0
        }
        polarity_sum = sum(polarity_values.get(p, 0.0) for p in polarities)
        polarity_tension = polarity_sum / n  # Range: -1 (all negative) to +1 (all positive)

        return PropertyVector(
            thermal_flux=thermal_flux,
            avg_temperature=avg_temp,
            temp_differential=temp_diff,
            state_transition_energy=state_transition_energy,
            phase_diversity=phase_diversity,
            density_gradient=density_gradient,
            avg_density=avg_density,
            volatility_index=volatility_index,
            chaos_factor=chaos_factor,
            total_energy=total_energy,
            energy_density=energy_density,
            polarity_tension=polarity_tension,
            element_count=n
        )

    @staticmethod
    def _variance(values: List[float]) -> float:
        """Compute variance of a list of values"""
        if len(values) <= 1:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

    @staticmethod
    def _empty_vector() -> PropertyVector:
        """Return zero vector for empty element list"""
        return PropertyVector(
            thermal_flux=0.0,
            avg_temperature=293.15,  # Room temp
            temp_differential=0.0,
            state_transition_energy=0.0,
            phase_diversity=0.0,
            density_gradient=0.0,
            avg_density=0.5,
            volatility_index=0.0,
            chaos_factor=0.0,
            total_energy=0.0,
            energy_density=0.0,
            polarity_tension=0.0,
            element_count=0
        )
