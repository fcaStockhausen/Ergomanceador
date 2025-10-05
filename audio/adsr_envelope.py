"""
ADSR Envelope for audio synthesis.

Applies Attack, Decay, Sustain, Release envelope to audio samples.
"""

import numpy as np


class ADSREnvelope:
    """
    ADSR (Attack, Decay, Sustain, Release) envelope generator.

    Used to shape audio samples with synth-style amplitude envelopes.
    """

    def __init__(self, attack_time=0.01, decay_time=0.1, sustain_level=0.7, release_time=0.2):
        """
        Create ADSR envelope.

        Args:
            attack_time: Time to ramp from 0 to 1 (seconds)
            decay_time: Time to ramp from 1 to sustain_level (seconds)
            sustain_level: Level to hold during sustain phase (0.0 to 1.0)
            release_time: Time to ramp from sustain_level to 0 (seconds)
        """
        self.attack_time = max(0.0, attack_time)
        self.decay_time = max(0.0, decay_time)
        self.sustain_level = max(0.0, min(1.0, sustain_level))
        self.release_time = max(0.0, release_time)

    def generate_envelope(self, total_duration, sample_rate=22050):
        """
        Generate envelope curve as numpy array.

        Args:
            total_duration: Total duration of envelope in seconds
            sample_rate: Sample rate in Hz

        Returns:
            numpy array of envelope values (same length as total_duration * sample_rate)
        """
        total_samples = int(total_duration * sample_rate)
        envelope = np.zeros(total_samples)

        attack_samples = int(self.attack_time * sample_rate)
        decay_samples = int(self.decay_time * sample_rate)
        release_samples = int(self.release_time * sample_rate)

        # Calculate sustain samples (remaining time after attack/decay/release)
        sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)

        current_idx = 0

        # Attack phase: 0 → 1
        if attack_samples > 0:
            attack_curve = np.linspace(0.0, 1.0, attack_samples)
            envelope[current_idx:current_idx + attack_samples] = attack_curve
            current_idx += attack_samples

        # Decay phase: 1 → sustain_level
        if decay_samples > 0:
            decay_curve = np.linspace(1.0, self.sustain_level, decay_samples)
            envelope[current_idx:current_idx + decay_samples] = decay_curve
            current_idx += decay_samples

        # Sustain phase: hold at sustain_level
        if sustain_samples > 0:
            envelope[current_idx:current_idx + sustain_samples] = self.sustain_level
            current_idx += sustain_samples

        # Release phase: sustain_level → 0
        if release_samples > 0:
            end_idx = min(current_idx + release_samples, total_samples)
            actual_release_samples = end_idx - current_idx
            release_curve = np.linspace(self.sustain_level, 0.0, actual_release_samples)
            envelope[current_idx:end_idx] = release_curve

        return envelope

    def apply(self, waveform, sample_rate=22050):
        """
        Apply ADSR envelope to waveform.

        Args:
            waveform: numpy array of audio samples (-1.0 to 1.0)
            sample_rate: Sample rate in Hz

        Returns:
            numpy array with envelope applied
        """
        duration = len(waveform) / sample_rate
        envelope = self.generate_envelope(duration, sample_rate)

        # Match envelope length to waveform (in case of rounding differences)
        if len(envelope) != len(waveform):
            envelope = envelope[:len(waveform)]

        # Multiply waveform by envelope
        return waveform * envelope

    def to_dict(self):
        """Export envelope parameters as dict (for JSON serialization)"""
        return {
            'attack_time': self.attack_time,
            'decay_time': self.decay_time,
            'sustain_level': self.sustain_level,
            'release_time': self.release_time
        }

    @staticmethod
    def from_dict(data):
        """Create envelope from dict (for JSON deserialization)"""
        return ADSREnvelope(
            attack_time=data.get('attack_time', 0.01),
            decay_time=data.get('decay_time', 0.1),
            sustain_level=data.get('sustain_level', 0.7),
            release_time=data.get('release_time', 0.2)
        )


# Preset envelopes for common use cases
PRESETS = {
    'instant': ADSREnvelope(0.0, 0.0, 1.0, 0.05),      # No attack, quick release (impacts)
    'pluck': ADSREnvelope(0.001, 0.05, 0.3, 0.2),      # Sharp attack, quick decay (plucked strings)
    'pad': ADSREnvelope(0.2, 0.3, 0.7, 0.5),           # Slow attack, long sustain (pads, ambience)
    'percussive': ADSREnvelope(0.001, 0.1, 0.0, 0.1),  # Sharp attack, no sustain (drums)
    'organ': ADSREnvelope(0.0, 0.0, 1.0, 0.1),         # Instant attack, full sustain (organ-like)
    'brass': ADSREnvelope(0.05, 0.1, 0.8, 0.2),        # Medium attack, high sustain (brass)
    'string': ADSREnvelope(0.1, 0.2, 0.6, 0.3),        # Soft attack, medium sustain (strings)
}


def get_preset(name):
    """Get preset envelope by name"""
    return PRESETS.get(name, PRESETS['instant'])
