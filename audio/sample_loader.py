"""
Audio sample loader for custom sound effects.

Loads WAV/OGG/OPUS audio files and extracts waveform data for visualization and playback.
Also parses embedded metadata and sidecar documentation files.
"""

import pygame
import numpy as np
import logging
import os
import json
from audio.sound_manifold import SoundVector


class AudioSample:
    """Represents a loaded audio sample with waveform data"""

    def __init__(self, file_path):
        """
        Load audio sample from file.

        Args:
            file_path: Path to audio file (WAV, OGG, OPUS supported)
        """
        self.file_path = file_path
        self.sound = None
        self.waveform = None  # numpy array of amplitude values
        self.sample_rate = 22050  # Default
        self.duration = 0.0
        self.channels = 1

        # Metadata and documentation
        self.metadata = {}  # Embedded tags/metadata
        self.description = None  # From sidecar .txt/.md file
        self.tags = []  # User-defined tags
        self.category = None  # e.g., 'impact', 'ambient', 'voice'

        # Playback settings (saved in metadata JSON)
        self.adsr = None  # ADSR envelope settings dict: {attack, decay, sustain, release}
        self.trim_start = 0.0  # Start offset in seconds
        self.volume_db = 0.0  # Volume adjustment in dB (-12 to +6, 0 = normalized level)

        # Normalization metadata (auto-computed on load)
        self.original_peak = 1.0  # Peak amplitude before normalization
        self.normalized = False  # Whether waveform has been normalized

        # Sound manifold vector (8D audio property space)
        # Projects to spell manifold for geometric matching
        self.sound_vector = SoundVector()

        self._load()
        self._load_metadata()

    def _load(self):
        """Load audio file and extract waveform data"""
        try:
            # Load as pygame Sound for playback
            self.sound = pygame.mixer.Sound(self.file_path)

            # Get raw audio data
            # pygame.sndarray gives us numpy array
            sound_array = pygame.sndarray.array(self.sound)

            # sound_array shape: (samples, channels) or just (samples,)
            if len(sound_array.shape) == 2:
                # Stereo - average channels to mono for visualization
                self.waveform = np.mean(sound_array, axis=1)
                self.channels = sound_array.shape[1]
            else:
                # Already mono
                self.waveform = sound_array
                self.channels = 1

            # Normalize to -1.0 to 1.0 range, then to target RMS
            max_val = np.max(np.abs(self.waveform))
            self.original_peak = max_val

            if max_val > 0:
                # First normalize to -1.0 to 1.0
                self.waveform = self.waveform.astype(np.float32) / max_val

                # Then normalize to target RMS level (-3dB = 0.707)
                # This ensures consistent loudness across samples
                current_rms = np.sqrt(np.mean(self.waveform ** 2))
                if current_rms > 0:
                    target_rms = 0.707  # -3dB reference level
                    self.waveform = self.waveform * (target_rms / current_rms)
                    self.normalized = True

            # Calculate duration
            self.duration = len(self.waveform) / self.sample_rate

            norm_status = "normalized" if self.normalized else "raw"
            logging.info(f"Loaded audio sample: {os.path.basename(self.file_path)} "
                        f"({self.duration:.2f}s, {self.channels} ch, {self.sample_rate}Hz, {norm_status}, peak={self.original_peak:.3f})")

        except Exception as e:
            logging.error(f"Failed to load audio sample {self.file_path}: {e}")
            # Create silent waveform as fallback
            self.waveform = np.zeros(int(self.sample_rate * 0.5))
            self.duration = 0.5

    def get_sample_range(self, start_time=0.0, end_time=None):
        """
        Get a portion of the waveform.

        Args:
            start_time: Start time in seconds
            end_time: End time in seconds (None = end of sample)

        Returns:
            numpy array of waveform samples
        """
        if end_time is None:
            end_time = self.duration

        start_sample = int(start_time * self.sample_rate)
        end_sample = int(end_time * self.sample_rate)

        # Clamp to valid range
        start_sample = max(0, min(start_sample, len(self.waveform)))
        end_sample = max(start_sample, min(end_sample, len(self.waveform)))

        return self.waveform[start_sample:end_sample]

    def _load_metadata(self):
        """
        Load metadata from:
        1. Sidecar documentation files (.txt, .md, .json)
        2. Embedded audio tags (if available)
        """
        base_path = os.path.splitext(self.file_path)[0]

        # Check for sidecar .txt file
        txt_path = base_path + '.txt'
        if os.path.exists(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    self.description = f.read().strip()
                logging.info(f"Loaded description from {os.path.basename(txt_path)}")
            except Exception as e:
                logging.warning(f"Failed to read {txt_path}: {e}")

        # Check for sidecar .md file
        md_path = base_path + '.md'
        if os.path.exists(md_path) and not self.description:
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    self.description = f.read().strip()
                logging.info(f"Loaded description from {os.path.basename(md_path)}")
            except Exception as e:
                logging.warning(f"Failed to read {md_path}: {e}")

        # Check for sidecar .json metadata file
        json_path = base_path + '.json'
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    self.metadata = meta.get('metadata', {})
                    self.tags = meta.get('tags', [])
                    self.category = meta.get('category')
                    if 'description' in meta and not self.description:
                        self.description = meta['description']

                    # Load playback settings
                    self.adsr = meta.get('adsr')  # None if not set
                    self.trim_start = meta.get('trim_start', 0.0)
                    self.volume_db = meta.get('volume_db', 0.0)

                    # Load sound manifold vector (8D audio space)
                    if 'sound_vector' in meta:
                        self.sound_vector = SoundVector.from_dict(meta['sound_vector'])

                logging.info(f"Loaded metadata from {os.path.basename(json_path)}")
            except Exception as e:
                logging.warning(f"Failed to read {json_path}: {e}")

        # Try to extract embedded metadata (OGG/OPUS support this)
        # Note: pygame.mixer.Sound doesn't expose tags, would need mutagen library
        # For now, we rely on sidecar files

    def save_metadata(self):
        """
        Save metadata, ADSR, and trim settings to sidecar JSON file.
        """
        base_path = os.path.splitext(self.file_path)[0]
        json_path = base_path + '.json'

        # Build metadata dict
        data = {
            'category': self.category,
            'tags': self.tags,
            'description': self.description,
            'metadata': self.metadata
        }

        # Add playback settings if configured
        if self.adsr:
            data['adsr'] = self.adsr
        if self.trim_start > 0.0:
            data['trim_start'] = self.trim_start
        if self.volume_db != 0.0:
            data['volume_db'] = self.volume_db

        # Save sound manifold vector (8D audio space)
        data['sound_vector'] = self.sound_vector.to_dict()

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Saved metadata to {os.path.basename(json_path)}")
            return True
        except Exception as e:
            logging.error(f"Failed to save metadata to {json_path}: {e}")
            return False

    def get_display_info(self):
        """
        Get formatted display info for UI.

        Returns:
            dict with display-friendly information
        """
        return {
            'filename': os.path.basename(self.file_path),
            'duration': f"{self.duration:.2f}s",
            'channels': 'Stereo' if self.channels == 2 else 'Mono',
            'sample_rate': f"{self.sample_rate}Hz",
            'category': self.category or 'Uncategorized',
            'tags': ', '.join(self.tags) if self.tags else 'No tags',
            'description': self.description or 'No description available'
        }

    def play(self, volume=1.0, adsr_envelope=None, start_time=0.0, end_time=None):
        """
        Play the audio sample with optional ADSR envelope and trimming.

        Args:
            volume: Playback volume (0.0 to 1.0)
            adsr_envelope: Optional ADSREnvelope to apply
            start_time: Start time in seconds (for trimming)
            end_time: End time in seconds (None = end of sample)
        """
        if not self.sound:
            return

        # Stop any currently playing sounds first (prevent double-play)
        pygame.mixer.stop()

        # Apply volume_db gain (convert dB to linear)
        # volume_db is stored in metadata, volume parameter is from caller
        volume_gain = 10 ** (self.volume_db / 20.0)  # dB to linear
        final_volume = volume * volume_gain

        # If no envelope or trimming, play original
        if not adsr_envelope and start_time == 0.0 and end_time is None:
            self.sound.set_volume(final_volume)
            self.sound.play()
            return

        # Get trimmed waveform
        waveform = self.get_sample_range(start_time, end_time)

        # Apply volume gain to waveform
        waveform = waveform * volume_gain

        # Apply ADSR envelope if provided
        if adsr_envelope:
            waveform = adsr_envelope.apply(waveform, self.sample_rate)

        # Convert processed waveform back to pygame Sound
        try:
            # Ensure waveform is in correct format (int16)
            waveform_int16 = (waveform * 32767).astype(np.int16)

            # If mono, convert to stereo for pygame (some systems require it)
            if len(waveform_int16.shape) == 1:
                # Stack to stereo
                stereo = np.column_stack((waveform_int16, waveform_int16))
            else:
                stereo = waveform_int16

            # Create Sound from array
            processed_sound = pygame.sndarray.make_sound(stereo)
            processed_sound.set_volume(final_volume)
            processed_sound.play()

        except Exception as e:
            print(f"Failed to play processed audio: {e}")
            # Fallback to original
            self.sound.set_volume(volume)
            self.sound.play()


class SampleLibrary:
    """Manages collection of audio samples"""

    def __init__(self):
        self.samples = {}  # name -> AudioSample
        self.sample_dir = "data/sounds"  # Default directory for custom samples

    def load_sample(self, name, file_path):
        """
        Load an audio sample and add to library.

        Args:
            name: Identifier for this sample (e.g., 'cast', 'impact')
            file_path: Path to audio file

        Returns:
            AudioSample if successful, None otherwise
        """
        try:
            sample = AudioSample(file_path)
            self.samples[name] = sample
            return sample
        except Exception as e:
            logging.error(f"Failed to load sample '{name}' from {file_path}: {e}")
            return None

    def get_sample(self, name):
        """Get a loaded sample by name"""
        return self.samples.get(name)

    def list_samples(self):
        """Get list of all loaded sample names"""
        return list(self.samples.keys())

    def scan_directory(self, directory=None):
        """
        Scan directory for audio files and load them.
        Supports WAV, OGG, OPUS formats.

        Args:
            directory: Directory to scan (uses sample_dir if None)

        Returns:
            List of loaded sample names
        """
        if directory is None:
            directory = self.sample_dir

        if not os.path.exists(directory):
            logging.warning(f"Sample directory not found: {directory}")
            return []

        loaded = []
        # Support WAV, OGG, OPUS formats
        audio_extensions = ('.wav', '.ogg', '.opus', '.WAV', '.OGG', '.OPUS')

        for filename in os.listdir(directory):
            if filename.endswith(audio_extensions):
                # Use filename without extension as name
                name = os.path.splitext(filename)[0]
                file_path = os.path.join(directory, filename)

                if self.load_sample(name, file_path):
                    loaded.append(name)

        logging.info(f"Loaded {len(loaded)} samples from {directory}")
        return loaded

    def get_all_samples_with_info(self):
        """
        Get all samples with their display info for browser UI.

        Returns:
            List of dicts with sample name and display info
        """
        samples_info = []
        for name, sample in self.samples.items():
            info = sample.get_display_info()
            info['name'] = name
            samples_info.append(info)
        return samples_info
