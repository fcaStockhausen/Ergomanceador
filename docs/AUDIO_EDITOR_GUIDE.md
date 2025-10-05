# Audio Editor Guide

## Overview

The Audio Editor allows you to load custom audio samples (WAV/OGG files), edit them with synth-style ADSR envelopes, and assign them to game sound effects.

## Features

- **Load Custom Samples**: Import WAV/OGG audio files
- **Waveform Visualization**: See your audio waveform in a grid display
- **ADSR Envelope Editing**: Control Attack, Decay, Sustain, Release parameters
- **Sample Trimming**: Select specific portions of audio files
- **Effect Assignment**: Assign samples to cast/impact/death sounds
- **Real-time Preview**: Hear your edited samples instantly
- **Preset Library**: Quick-apply common envelope shapes

## Getting Started

### 1. Access the Audio Editor

From the main menu, select **"Audio Editor"** (option 3).

### 2. Load a Sample

Place your WAV or OGG files in the `data/sounds/` directory. The editor will auto-scan this folder on startup.

Supported formats:
- WAV (uncompressed, any sample rate)
- OGG (Vorbis compressed)

### 3. Edit ADSR Envelope

The ADSR envelope shapes how the sound plays over time:

- **Attack (A)**: Time to ramp from 0 to maximum volume (0-1 seconds)
- **Decay (D)**: Time to ramp from max to sustain level (0-1 seconds)
- **Sustain (S)**: Level to hold during the middle of the sound (0.0-1.0)
- **Release (R)**: Time to fade from sustain to silence (0-1 seconds)

**Visual Representation:**
```
Volume
  1.0 |    /\
      |   /  \___________
      |  /   |           \
  0.0 |_/____|____________\___
      | A   D   Sustain    R
                 Time →
```

### 4. Use Presets

Quick-apply common envelope shapes:
- **Instant** (I): No attack, quick release (good for impacts)
- **Pluck** (P): Sharp attack, quick decay (plucked instruments)
- **Organ** (O): Instant attack, full sustain (organ-like)
- **Pad**: Slow attack, long sustain (ambient pads)
- **Percussive**: Sharp attack, no sustain (drums)

### 5. Select Region

Click and drag on the waveform display to select a portion of the sample. Only the selected region will be used when assigned to an effect.

### 6. Preview

Press **SPACE** to hear your edited sample with the current envelope applied.

### 7. Assign to Effect

1. Switch effect type using number keys:
   - **1**: Cast sound (when casting spell)
   - **2**: Impact sound (when projectile hits)
   - **3**: Death sound (when entity dies)

2. Press **ENTER** to assign the current sample + envelope to the selected effect type.

## Controls

| Key | Action |
|-----|--------|
| **SPACE** | Preview sample with envelope |
| **ENTER** | Assign to current effect type |
| **1/2/3** | Switch effect type (cast/impact/death) |
| **P** | Apply "Pluck" preset |
| **I** | Apply "Instant" preset |
| **O** | Apply "Organ" preset |
| **Click & Drag** | Select waveform region |
| **ESC** | Exit audio editor |

## Mouse Controls

- **ADSR Sliders**: Click or drag to adjust envelope parameters
- **Waveform**: Click and drag to select audio region
- **Preset Buttons**: Click to apply preset envelopes

## Configuration

Custom sample assignments are saved to `data/custom_samples.json`:

```json
{
  "custom_sounds": {
    "cast": {
      "file": "data/sounds/my_cast_sound.wav",
      "start_time": 0.0,
      "end_time": 0.5,
      "adsr": {
        "attack_time": 0.01,
        "decay_time": 0.1,
        "sustain_level": 0.7,
        "release_time": 0.2
      },
      "volume": 0.7
    },
    "impact": { ... },
    "death": { ... }
  },
  "sample_directory": "data/sounds"
}
```

## Technical Details

### Waveform Processing

- Samples are loaded as NumPy arrays
- Stereo files are converted to mono for visualization (averaged channels)
- Waveforms are normalized to -1.0 to 1.0 range
- Downsampling used for efficient screen rendering

### ADSR Implementation

The envelope is applied by multiplying the waveform by an envelope curve:

```python
envelope_curve = generate_adsr_envelope(duration, sample_rate)
processed_waveform = original_waveform * envelope_curve
```

Each phase:
1. **Attack**: Linear ramp from 0.0 to 1.0
2. **Decay**: Linear ramp from 1.0 to sustain_level
3. **Sustain**: Constant at sustain_level
4. **Release**: Linear ramp from sustain_level to 0.0

### Performance

- Waveforms are downsampled to screen resolution (1-2 pixels per sample)
- ADSR envelopes generated on-demand
- Efficient NumPy array operations

## Tips

1. **Short impacts**: Use "instant" or "percussive" presets with fast attack/release
2. **Magical casts**: Try "pluck" or "brass" presets with medium attack
3. **Death sounds**: Use "pad" or longer release times for dramatic effect
4. **Trim silence**: Select only the active portion of samples to reduce memory
5. **Test volume**: Preview before assigning - adjust source file if too loud/quiet

## Troubleshooting

**No sound when previewing:**
- Check that pygame.mixer is initialized (game handles this)
- Verify sample file is valid WAV/OGG
- Check system volume

**Waveform looks clipped:**
- Your sample may be too loud (normalize in audio editor before importing)
- Or it's a square wave (intended for synth sounds)

**Editor crashes on load:**
- Check that pygame-sndarray is installed: `pip install numpy`
- Verify sample file isn't corrupted

**Changes don't apply in-game:**
- Make sure you pressed ENTER to save assignment
- Check `data/custom_samples.json` was written
- Restart game to load new configuration

## Example Workflow

1. Record/download cast spell sound effect (e.g., "magic_whoosh.wav")
2. Place in `data/sounds/magic_whoosh.wav`
3. Open Audio Editor from main menu
4. Editor auto-loads sample from directory
5. Click and drag waveform to select the "whoosh" portion (trim silence)
6. Press **P** to apply "Pluck" preset (sharp attack)
7. Adjust Decay slider to make it fade faster
8. Press **SPACE** to preview
9. Press **1** to select "cast" effect type
10. Press **ENTER** to assign
11. Press **ESC** to return to menu
12. Start game and cast a spell - hear your custom sound!

## Module Reference

### `audio/sample_loader.py`
- `AudioSample`: Loads and manages audio file + waveform data
- `SampleLibrary`: Collection manager, directory scanning

### `audio/adsr_envelope.py`
- `ADSREnvelope`: Envelope generator and applicator
- `PRESETS`: Dictionary of common envelope shapes
- `get_preset(name)`: Retrieve preset by name

### `rendering/ui/waveform_display.py`
- `WaveformDisplay`: Visual waveform + envelope rendering
- Handles mouse selection, grid display, time markers

### `rendering/ui/sample_editor.py`
- `SampleEditor`: Main editor UI integrating all components
- Event handling, rendering, configuration management

## Future Enhancements

Potential improvements:
- Pitch shifting / time stretching
- Multi-sample layering
- Real-time filters (lowpass, highpass, reverb)
- Waveform synthesis (sine, square, saw, triangle)
- MIDI keyboard support for preview
- Batch processing multiple samples
- Undo/redo for envelope edits
