"""
Sound effect manager with manifold-based sample selection.

Philosophy:
- Sounds have 8D property vectors in audio manifold
- Spells have 12D property vectors in spell manifold
- Projection function maps 8D → 12D for geometric matching
- K-nearest samples selected, optionally layered
"""

import pygame
import numpy as np
import logging
from audio.sound_manifold import SoundManifold
from audio.sample_loader import SampleLibrary


class SoundManager:
    """
    Manages sound effects using manifold-based sample selection.

    Matches audio samples to spells by geometric distance in manifold space.
    Falls back to procedural generation if no samples available.
    """

    def __init__(self, sample_library=None, enabled=True):
        self.enabled = enabled
        self.library = sample_library
        self.manifold = SoundManifold()

        # Procedural fallback sounds (kept for backward compatibility)
        self.procedural_sounds = {}

        if not self.enabled:
            return

        try:
            # Initialize pygame mixer for sound
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

            if self.library and len(self.library.samples) > 0:
                logging.info(f"Sound system initialized with {len(self.library.samples)} manifold samples")
            else:
                # Generate procedural fallback
                self._generate_procedural_sounds()
                logging.info("Sound system initialized with procedural fallback")

        except Exception as e:
            logging.warning(f"Sound initialization failed: {e}")
            self.enabled = False

    def _generate_procedural_sounds(self):
        """Generate simple procedural sound effects using numpy"""
        try:
            sample_rate = 22050

            # Spell cast sound - rising pitch
            duration = 0.2
            frequency = 440  # A4
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples)
            # Rising pitch with envelope
            pitch_sweep = frequency * (1 + t * 2)
            wave = np.sin(2 * np.pi * pitch_sweep * t)
            envelope = np.exp(-t * 8)  # Decay
            wave = wave * envelope * 0.3
            self.procedural_sounds['cast'] = self._numpy_to_sound(wave, sample_rate)

            # Impact sound - short noise burst
            duration = 0.1
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples)
            # White noise with sharp attack/decay
            noise = np.random.uniform(-1, 1, samples)
            envelope = np.exp(-t * 50)
            wave = noise * envelope * 0.4
            self.procedural_sounds['impact'] = self._numpy_to_sound(wave, sample_rate)

            # Death sound - descending pitch
            duration = 0.3
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples)
            pitch_sweep = 220 * (1 - t * 0.8)  # Descending
            wave = np.sin(2 * np.pi * pitch_sweep * t)
            envelope = np.exp(-t * 5)
            wave = wave * envelope * 0.3
            self.procedural_sounds['death'] = self._numpy_to_sound(wave, sample_rate)

            logging.info("Procedural sounds generated: cast, impact, death")

        except Exception as e:
            logging.warning(f"Procedural sound generation failed: {e}")
            self.enabled = False

    def _numpy_to_sound(self, wave, sample_rate):
        """Convert numpy array to pygame Sound object"""
        # Convert to 16-bit integers
        wave = np.int16(wave * 32767)
        # Stereo (duplicate mono to both channels)
        stereo = np.column_stack((wave, wave))
        # Create Sound object
        sound = pygame.sndarray.make_sound(stereo)
        return sound

    def get_best_sample_for_spell(self, spell_property_vector, k=1):
        """
        Find K best matching audio samples for spell using manifold distance.

        Args:
            spell_property_vector: PropertyVector from magic system (12D)
            k: Number of samples to return (for layering)

        Returns:
            List of (AudioSample, distance) tuples, sorted by distance
        """
        if not self.library or len(self.library.samples) == 0:
            return []

        # Compute distances for all samples
        distances = []
        for name, sample in self.library.samples.items():
            distance = self.manifold.distance_to_spell(
                sample.sound_vector,
                spell_property_vector
            )
            distances.append((sample, distance))

        # Sort by distance (ascending)
        distances.sort(key=lambda x: x[1])

        # Return K nearest
        return distances[:k]

    def play_for_spell(self, spell_descriptor, volume=1.0, k=1):
        """
        Play sound(s) matched to spell via manifold distance.

        Args:
            spell_descriptor: Dict from InteractionEngine.compute_interaction()
                Must contain 'property_vector' key (PropertyVector)
            volume: Playback volume
            k: Number of samples to layer (1 = best match only)

        Returns:
            Number of sounds played
        """
        if not self.enabled:
            return 0

        # Extract property vector
        prop_vector = spell_descriptor.get('property_vector')
        if not prop_vector:
            logging.warning("Spell descriptor missing property_vector")
            return 0

        # Get K nearest samples
        matches = self.get_best_sample_for_spell(prop_vector, k=k)

        if not matches:
            # Fallback to procedural
            logging.debug("No samples available, using procedural fallback")
            return 0

        # Play matches (optionally layer multiple)
        played = 0
        for sample, distance in matches:
            # Volume falloff for layered sounds (first is loudest)
            layer_volume = volume * (1.0 / (played + 1))

            # Play with ADSR and trim if configured
            sample.play(
                volume=layer_volume,
                adsr_envelope=sample.adsr,
                start_time=sample.trim_start
            )
            played += 1

            logging.debug(f"Playing {sample.file_path} (distance={distance:.3f}, volume={layer_volume:.2f})")

        return played

    def play(self, sound_name, volume=1.0):
        """
        Legacy method: Play sound by name (for backward compatibility).

        Tries manifold samples first, falls back to procedural.
        """
        if not self.enabled:
            return

        # Try to find sample by name
        if self.library:
            sample = self.library.get_sample(sound_name)
            if sample:
                sample.play(volume=volume, adsr_envelope=sample.adsr, start_time=sample.trim_start)
                return

        # Fallback to procedural
        sound = self.procedural_sounds.get(sound_name)
        if sound:
            sound.set_volume(volume)
            sound.play()
        else:
            logging.warning(f"Sound '{sound_name}' not found")

    def set_enabled(self, enabled):
        """Enable or disable sound effects"""
        self.enabled = enabled
