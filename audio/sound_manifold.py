"""
Sound Manifold - Maps audio samples to spell behavior space.

Philosophy:
- Sounds live in their own natural 8D audio property space
- Mapping function projects sound vectors → spell manifold (12D)
- Enables geometric matching: pick sounds closest to spell in shared space
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class SoundVector:
    """
    8-dimensional sound property vector.

    Natural audio dimensions that sound designers understand.
    Values normalized 0-1.
    """
    # Amplitude envelope
    attack: float = 0.5      # 0=slow fade in, 1=instant/sharp attack
    decay: float = 0.5       # 0=sustained, 1=quick decay

    # Spectral content
    brightness: float = 0.5  # 0=dark/bass, 1=bright/treble
    richness: float = 0.5    # 0=pure tone, 1=complex harmonics

    # Temporal character
    texture: float = 0.5     # 0=smooth, 1=noisy/granular
    density: float = 0.5     # 0=sparse, 1=thick/dense

    # Energy
    intensity: float = 0.5   # 0=quiet, 1=loud
    temperature: float = 0.5 # 0=cold, 1=hot (metaphorical warmth)

    def to_array(self):
        """Convert to numpy array for distance calculations"""
        return np.array([
            self.attack, self.decay, self.brightness, self.richness,
            self.texture, self.density, self.intensity, self.temperature
        ])

    @classmethod
    def from_dict(cls, d):
        """Load from JSON dict"""
        return cls(
            attack=d.get('attack', 0.5),
            decay=d.get('decay', 0.5),
            brightness=d.get('brightness', 0.5),
            richness=d.get('richness', 0.5),
            texture=d.get('texture', 0.5),
            density=d.get('density', 0.5),
            intensity=d.get('intensity', 0.5),
            temperature=d.get('temperature', 0.5)
        )

    def to_dict(self):
        """Save to JSON dict"""
        return {
            'attack': self.attack,
            'decay': self.decay,
            'brightness': self.brightness,
            'richness': self.richness,
            'texture': self.texture,
            'density': self.density,
            'intensity': self.intensity,
            'temperature': self.temperature
        }


class SoundManifold:
    """
    Maps sound vectors (8D audio space) to spell manifold (12D property space).

    Allows geometric matching: sounds near spells in projected space.
    Includes category prototypes (anchors) for semantic matching.
    """

    # Category prototypes - anchor points in 8D sound space
    # These define where each element/category should live
    CATEGORY_PROTOTYPES = {
        'lightning': SoundVector(attack=0.95, decay=0.8, brightness=0.9, richness=0.6,
                                 texture=0.7, density=0.4, intensity=0.9, temperature=0.8),
        'thunder': SoundVector(attack=0.3, decay=0.9, brightness=0.3, richness=0.8,
                              texture=0.9, density=0.9, intensity=1.0, temperature=0.5),
        'fire': SoundVector(attack=0.6, decay=0.5, brightness=0.7, richness=0.7,
                           texture=0.8, density=0.5, intensity=0.7, temperature=0.95),
        'ice': SoundVector(attack=0.7, decay=0.4, brightness=0.8, richness=0.3,
                          texture=0.4, density=0.7, intensity=0.5, temperature=0.1),
        'water': SoundVector(attack=0.3, decay=0.6, brightness=0.4, richness=0.5,
                            texture=0.6, density=0.6, intensity=0.5, temperature=0.3),
        'earth': SoundVector(attack=0.4, decay=0.7, brightness=0.2, richness=0.6,
                            texture=0.5, density=0.9, intensity=0.6, temperature=0.4),
        'wind': SoundVector(attack=0.5, decay=0.8, brightness=0.6, richness=0.4,
                           texture=0.7, density=0.2, intensity=0.4, temperature=0.5),
        'nature': SoundVector(attack=0.4, decay=0.6, brightness=0.5, richness=0.7,
                             texture=0.6, density=0.5, intensity=0.4, temperature=0.6),
        'arcane': SoundVector(attack=0.6, decay=0.5, brightness=0.8, richness=0.9,
                             texture=0.5, density=0.4, intensity=0.7, temperature=0.6),
        'light': SoundVector(attack=0.8, decay=0.3, brightness=1.0, richness=0.5,
                            texture=0.3, density=0.3, intensity=0.8, temperature=0.7),
        'shadow': SoundVector(attack=0.3, decay=0.9, brightness=0.1, richness=0.6,
                             texture=0.6, density=0.7, intensity=0.5, temperature=0.3),
        'impact': SoundVector(attack=1.0, decay=0.9, brightness=0.5, richness=0.4,
                             texture=0.6, density=0.8, intensity=0.9, temperature=0.5),
        'heal': SoundVector(attack=0.3, decay=0.4, brightness=0.7, richness=0.8,
                           texture=0.2, density=0.3, intensity=0.5, temperature=0.6),
        'explosion': SoundVector(attack=0.9, decay=0.8, brightness=0.6, richness=0.9,
                                texture=0.9, density=0.9, intensity=1.0, temperature=0.8),
    }

    def __init__(self):
        """Initialize mapping function"""
        # Mapping weights: 8D sound → 12D spell space
        # Each spell dimension is weighted combination of sound dimensions
        # These can be tuned or learned from data

        self.mapping = {
            # Spell property: [attack, decay, brightness, richness, texture, density, intensity, temperature]
            'temperature':        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.8],  # Dominated by temperature
            'energy':             [0.3, -0.2, 0.0, 0.0, 0.0, 0.0, 0.7, 0.0],  # Attack + intensity
            'density':            [0.0, 0.0, -0.2, 0.2, 0.0, 0.8, 0.0, 0.0],  # Mostly density dimension
            'volatility':         [0.5, 0.3, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0],  # Attack + decay + texture
            'mass_flux':          [0.0, 0.5, 0.0, 0.0, 0.2, 0.3, 0.0, 0.0],  # Decay + texture + density
            'charge_density':     [0.0, 0.0, 0.7, 0.3, 0.0, 0.0, 0.0, 0.0],  # Brightness + richness
            'phase_complexity':   [0.0, 0.0, 0.0, 0.8, 0.2, 0.0, 0.0, 0.0],  # Richness + texture
            'elemental_diversity':[0.0, 0.0, 0.2, 0.6, 0.2, 0.0, 0.0, 0.0],  # Richness dominant
            'tag_resonance':      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # Computed from tags separately
            'opposition_strength':[0.0, 0.0, 0.0, 0.0, 0.4, 0.4, 0.0, 0.2],  # Texture + density conflict
            'combo_synergy':      [0.2, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0, 0.0],  # Balanced mix
            'magnitude':          [0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.0]   # Mostly intensity
        }

        # Precompute as matrix for fast projection
        self.mapping_matrix = np.array([
            self.mapping[dim] for dim in [
                'temperature', 'energy', 'density', 'volatility',
                'mass_flux', 'charge_density', 'phase_complexity',
                'elemental_diversity', 'tag_resonance', 'opposition_strength',
                'combo_synergy', 'magnitude'
            ]
        ])

    def project_to_spell_space(self, sound_vector: SoundVector) -> np.ndarray:
        """
        Project 8D sound vector → 12D spell manifold.

        Returns:
            12D numpy array in spell PropertyVector space
        """
        sound_array = sound_vector.to_array()

        # Matrix multiplication: (12x8) @ (8,) = (12,)
        spell_vector = self.mapping_matrix @ sound_array

        # Normalize to 0-1 range (mapping can produce values outside)
        spell_vector = np.clip(spell_vector, 0.0, 1.0)

        return spell_vector

    def distance_to_spell(self, sound_vector: SoundVector, spell_property_vector) -> float:
        """
        Compute Euclidean distance from sound to spell in spell manifold.

        Args:
            sound_vector: SoundVector (8D)
            spell_property_vector: PropertyVector from magic system (12D)

        Returns:
            Distance (lower = better match)
        """
        # Project sound to spell space
        projected_sound = self.project_to_spell_space(sound_vector)

        # Convert spell PropertyVector to numpy array
        spell_array = np.array([
            spell_property_vector.temperature,
            spell_property_vector.energy,
            spell_property_vector.density,
            spell_property_vector.volatility,
            spell_property_vector.mass_flux,
            spell_property_vector.charge_density,
            spell_property_vector.phase_complexity,
            spell_property_vector.elemental_diversity,
            spell_property_vector.tag_resonance,
            spell_property_vector.opposition_strength,
            spell_property_vector.combo_synergy,
            spell_property_vector.magnitude
        ])

        # Euclidean distance
        distance = np.linalg.norm(projected_sound - spell_array)

        return distance

    @classmethod
    def get_category_prototype(cls, category_name):
        """
        Get sound vector prototype for a category.

        Args:
            category_name: Category key (e.g., 'lightning', 'fire', 'ice')

        Returns:
            SoundVector prototype, or None if category not found
        """
        return cls.CATEGORY_PROTOTYPES.get(category_name.lower())

    @classmethod
    def list_categories(cls):
        """Get list of all available category prototypes"""
        return list(cls.CATEGORY_PROTOTYPES.keys())
