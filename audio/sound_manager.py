"""Sound effect manager with procedural audio generation"""

import pygame
import numpy as np
import logging


class SoundManager:
    """
    Manages sound effects using pygame.mixer.
    Generates simple procedural sounds if audio files are missing.
    """

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.sounds = {}

        if not self.enabled:
            return

        try:
            # Initialize pygame mixer for sound
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._generate_procedural_sounds()
            logging.info("Sound system initialized with procedural audio")
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
            self.sounds['cast'] = self._numpy_to_sound(wave, sample_rate)

            # Impact sound - short noise burst
            duration = 0.1
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples)
            # White noise with sharp attack/decay
            noise = np.random.uniform(-1, 1, samples)
            envelope = np.exp(-t * 50)
            wave = noise * envelope * 0.4
            self.sounds['impact'] = self._numpy_to_sound(wave, sample_rate)

            # Death sound - descending pitch
            duration = 0.3
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples)
            pitch_sweep = 220 * (1 - t * 0.8)  # Descending
            wave = np.sin(2 * np.pi * pitch_sweep * t)
            envelope = np.exp(-t * 5)
            wave = wave * envelope * 0.3
            self.sounds['death'] = self._numpy_to_sound(wave, sample_rate)

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

    def play(self, sound_name, volume=1.0):
        """Play a sound effect

        Args:
            sound_name: Name of sound to play ('cast', 'impact', 'death')
            volume: Volume multiplier (0.0 to 1.0)
        """
        if not self.enabled:
            return

        sound = self.sounds.get(sound_name)
        if sound:
            sound.set_volume(volume)
            sound.play()
        else:
            logging.warning(f"Sound '{sound_name}' not found")

    def set_enabled(self, enabled):
        """Enable or disable sound effects"""
        self.enabled = enabled
