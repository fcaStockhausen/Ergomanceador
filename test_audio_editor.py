"""
Test audio editor components without running full game.
"""

import pygame
import numpy as np
from audio.sample_loader import AudioSample, SampleLibrary
from audio.adsr_envelope import ADSREnvelope, PRESETS, get_preset

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

def test_adsr_envelope():
    """Test ADSR envelope generation"""
    print("Testing ADSR Envelope...")

    # Create envelope
    envelope = ADSREnvelope(
        attack_time=0.1,
        decay_time=0.2,
        sustain_level=0.6,
        release_time=0.3
    )

    # Generate curve
    duration = 1.0
    sample_rate = 22050
    curve = envelope.generate_envelope(duration, sample_rate)

    print(f"  ✓ Generated envelope: {len(curve)} samples")
    print(f"  ✓ Max value: {np.max(curve):.3f}")
    print(f"  ✓ Min value: {np.min(curve):.3f}")

    # Test apply to waveform
    test_waveform = np.sin(2 * np.pi * 440 * np.arange(sample_rate) / sample_rate)
    processed = envelope.apply(test_waveform, sample_rate)

    print(f"  ✓ Applied to waveform: {len(processed)} samples")

    # Test serialization
    data = envelope.to_dict()
    restored = ADSREnvelope.from_dict(data)
    print(f"  ✓ Serialization: attack={restored.attack_time:.3f}")

    print("✓ ADSR Envelope tests passed!\n")

def test_presets():
    """Test preset envelopes"""
    print("Testing ADSR Presets...")

    for name, preset in PRESETS.items():
        print(f"  ✓ {name}: A={preset.attack_time:.3f}, D={preset.decay_time:.3f}, "
              f"S={preset.sustain_level:.3f}, R={preset.release_time:.3f}")

    # Test get_preset
    pluck = get_preset('pluck')
    print(f"  ✓ get_preset('pluck') works: {pluck.attack_time:.3f}s attack")

    print("✓ Preset tests passed!\n")

def test_sample_library():
    """Test sample library (without actual audio files)"""
    print("Testing Sample Library...")

    library = SampleLibrary()
    print(f"  ✓ Created library with sample_dir: {library.sample_dir}")
    print(f"  ✓ Samples loaded: {len(library.samples)}")

    # Test scan (will warn about missing directory)
    loaded = library.scan_directory()
    print(f"  ✓ Scanned directory: {len(loaded)} samples found")

    print("✓ Sample Library tests passed!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Audio Editor Component Tests")
    print("=" * 60)
    print()

    test_adsr_envelope()
    test_presets()
    test_sample_library()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
