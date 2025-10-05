"""
Auto-generate metadata for audio samples.

Analyzes audio files and creates initial metadata/documentation files.
"""

import os
import json
import numpy as np
from pathlib import Path


class MetadataGenerator:
    """
    Auto-generate metadata for audio samples based on analysis.

    Creates .json sidecar files with:
    - Auto-detected category (based on duration, envelope shape)
    - Suggested tags (based on filename, audio characteristics)
    - Template description
    """

    def __init__(self):
        # Category detection rules (based on duration and characteristics)
        self.category_rules = {
            'impact': {'max_duration': 0.5, 'keywords': ['hit', 'impact', 'boom', 'crash', 'bang']},
            'loop': {'min_duration': 2.0, 'keywords': ['loop', 'ambient', 'background', 'sustain']},
            'spell_cast': {'max_duration': 1.5, 'keywords': ['cast', 'spell', 'magic', 'whoosh']},
            'projectile': {'max_duration': 2.0, 'keywords': ['arrow', 'shot', 'fire', 'throw', 'projectile']},
            'explosion': {'max_duration': 3.0, 'keywords': ['explode', 'explosion', 'blast', 'detonate']},
            'electric': {'keywords': ['electric', 'lightning', 'shock', 'zap', 'tesla', 'thunder']},
            'heal': {'keywords': ['heal', 'restore', 'regen', 'life', 'cure']},
            'shield': {'keywords': ['shield', 'barrier', 'protect', 'block', 'absorb']},
            'ambient': {'min_duration': 3.0, 'keywords': ['ambient', 'atmosphere', 'wind', 'rain']},
        }

        # Tag suggestions based on filename/category
        self.tag_suggestions = {
            'impact': ['hit', 'impact', 'collision'],
            'electric': ['lightning', 'electric', 'shock', 'chain'],
            'spell_cast': ['magic', 'spell', 'cast'],
            'explosion': ['aoe', 'blast', 'explosive'],
            'heal': ['positive', 'restoration', 'buff'],
            'shield': ['defensive', 'barrier', 'protection'],
            'projectile': ['ranged', 'weapon'],
            'loop': ['continuous', 'ambient'],
        }

    def analyze_waveform(self, waveform, sample_rate):
        """
        Analyze waveform to determine characteristics.

        Returns:
            dict with: duration, peak_amplitude, attack_time, decay_time, is_percussive
        """
        duration = len(waveform) / sample_rate

        # Peak amplitude
        peak_amplitude = np.max(np.abs(waveform))

        # Estimate attack time (time to reach 90% of peak)
        peak_idx = np.argmax(np.abs(waveform))
        threshold = peak_amplitude * 0.9
        attack_samples = 0
        for i in range(min(peak_idx, len(waveform))):
            if abs(waveform[i]) >= threshold:
                attack_samples = i
                break
        attack_time = attack_samples / sample_rate

        # Estimate decay time (time from peak to 10% of peak)
        threshold_low = peak_amplitude * 0.1
        decay_samples = 0
        for i in range(peak_idx, len(waveform)):
            if abs(waveform[i]) <= threshold_low:
                decay_samples = i - peak_idx
                break
        if decay_samples == 0:
            decay_samples = len(waveform) - peak_idx
        decay_time = decay_samples / sample_rate

        # Is percussive? (fast attack, short decay)
        is_percussive = attack_time < 0.05 and decay_time < 0.5

        return {
            'duration': duration,
            'peak_amplitude': float(peak_amplitude),
            'attack_time': attack_time,
            'decay_time': decay_time,
            'is_percussive': is_percussive
        }

    def detect_category(self, filename, audio_analysis):
        """
        Auto-detect category based on filename and audio analysis.

        Args:
            filename: Name of audio file (without extension)
            audio_analysis: Dict from analyze_waveform()

        Returns:
            str category name
        """
        filename_lower = filename.lower()
        duration = audio_analysis['duration']
        is_percussive = audio_analysis['is_percussive']

        # Check keyword matches
        for category, rules in self.category_rules.items():
            keywords = rules.get('keywords', [])
            for keyword in keywords:
                if keyword in filename_lower:
                    return category

        # Fallback to duration-based detection
        if is_percussive and duration < 0.5:
            return 'impact'
        elif duration > 3.0:
            return 'ambient'
        elif duration < 1.5:
            return 'spell_cast'
        else:
            return 'effect'

    def generate_tags(self, filename, category):
        """
        Generate suggested tags based on filename and category.

        Args:
            filename: Audio file name
            category: Detected category

        Returns:
            List of tag strings
        """
        filename_lower = filename.lower()
        tags = []

        # Add category-specific tags
        if category in self.tag_suggestions:
            tags.extend(self.tag_suggestions[category])

        # Extract words from filename
        words = filename_lower.replace('_', ' ').replace('-', ' ').split()
        for word in words:
            if len(word) > 3 and word not in tags:
                # Add descriptive words from filename
                if word in ['fire', 'water', 'ice', 'lightning', 'earth', 'wind',
                           'light', 'dark', 'shadow', 'arcane', 'nature',
                           'cast', 'impact', 'loop', 'ambient', 'magic']:
                    tags.append(word)

        return tags

    def generate_description(self, filename, category, audio_analysis):
        """
        Generate template description text.

        Args:
            filename: Audio file name
            category: Detected category
            audio_analysis: Audio characteristics

        Returns:
            str description text
        """
        duration = audio_analysis['duration']
        is_percussive = audio_analysis['is_percussive']

        # Category-specific description templates
        templates = {
            'impact': f"Impact sound effect ({duration:.2f}s). Sharp transient suitable for collision, hit, or explosion impacts.",
            'electric': f"Electric sound effect ({duration:.2f}s). Suitable for lightning spells, electric impacts, or chain effects.",
            'spell_cast': f"Spell casting sound ({duration:.2f}s). Magical effect suitable for spell activation.",
            'explosion': f"Explosion sound ({duration:.2f}s). Suitable for AOE blasts, explosive impacts.",
            'heal': f"Healing sound effect ({duration:.2f}s). Positive, restorative audio suitable for healing spells.",
            'shield': f"Shield sound ({duration:.2f}s). Defensive barrier activation or absorption effect.",
            'projectile': f"Projectile sound ({duration:.2f}s). Suitable for arrow, bolt, or spell projectile travel/impact.",
            'ambient': f"Ambient sound loop ({duration:.2f}s). Continuous atmospheric background.",
            'loop': f"Looping sound effect ({duration:.2f}s). Designed for continuous playback.",
        }

        description = templates.get(category, f"Sound effect ({duration:.2f}s).")

        # Add percussive note if applicable
        if is_percussive:
            description += " Fast attack, percussive character."

        # Add usage suggestions
        description += f"\n\nSuitable for: {category} events in particle behaviors."

        return description

    def generate_metadata_file(self, audio_sample, output_path=None, overwrite=False):
        """
        Generate .json metadata file for an audio sample.

        Args:
            audio_sample: AudioSample instance
            output_path: Where to write .json (None = same dir as audio file)
            overwrite: If True, overwrite existing metadata

        Returns:
            Path to generated file, or None if skipped
        """
        if output_path is None:
            base_path = os.path.splitext(audio_sample.file_path)[0]
            output_path = base_path + '.json'

        # Don't overwrite existing metadata unless requested
        if os.path.exists(output_path) and not overwrite:
            return None

        # Analyze waveform
        analysis = self.analyze_waveform(audio_sample.waveform, audio_sample.sample_rate)

        # Detect category
        filename = os.path.splitext(os.path.basename(audio_sample.file_path))[0]
        category = self.detect_category(filename, analysis)

        # Generate tags
        tags = self.generate_tags(filename, category)

        # Generate description
        description = self.generate_description(filename, category, analysis)

        # Create metadata dict
        metadata = {
            'category': category,
            'tags': tags,
            'description': description,
            'metadata': {
                'auto_generated': True,
                'duration': round(analysis['duration'], 2),
                'peak_amplitude': round(analysis['peak_amplitude'], 3),
                'attack_time': round(analysis['attack_time'], 3),
                'decay_time': round(analysis['decay_time'], 3),
                'is_percussive': analysis['is_percussive']
            }
        }

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        return output_path

    def batch_generate(self, sample_library, overwrite=False):
        """
        Generate metadata for all samples in library that don't have it.

        Args:
            sample_library: SampleLibrary instance
            overwrite: If True, regenerate even if metadata exists

        Returns:
            List of generated file paths
        """
        generated = []

        for name, sample in sample_library.samples.items():
            # Skip if already has metadata (unless overwrite=True)
            if sample.description and not overwrite:
                continue

            output_path = self.generate_metadata_file(sample, overwrite=overwrite)
            if output_path:
                generated.append(output_path)
                print(f"Generated metadata: {os.path.basename(output_path)}")

        return generated


def auto_generate_metadata_for_directory(directory, overwrite=False):
    """
    Convenience function to auto-generate metadata for all audio files in a directory.

    Args:
        directory: Path to directory containing audio files
        overwrite: If True, regenerate existing metadata

    Returns:
        Number of metadata files generated
    """
    import pygame
    pygame.mixer.init()

    from audio.sample_loader import SampleLibrary

    library = SampleLibrary()
    library.sample_dir = directory
    library.scan_directory()

    generator = MetadataGenerator()
    generated = generator.batch_generate(library, overwrite=overwrite)

    return len(generated)
