# Documentation Index

## Getting Started

- **[Quick Start — Manifold HUD](QUICKSTART_MANIFOLD.md)** — Running the game with real-time behavior visualization
- **[Quick Start — Testing](QUICKSTART_TESTING.md)** — TAS and unit test overview
- **[Designer Mode Guide](DESIGNER_MODE_GUIDE.md)** — In-game behavior design toolkit (F1)

## Core Concepts

- **[Manifold Systems](MANIFOLD_SYSTEMS.md)** — Architecture: property vectors, behavior manifold, spell formulas, spatial system
- **[Emergent vs Hardcoded](EMERGENT_VS_HARDCODED.md)** — Design philosophy: weighted stat blending vs name-based dispatch
- **[Emergent Behaviors](EMERGENT_BEHAVIORS.md)** — How behaviors emerge from properties, discovery workflow
- **[Behavior Composition](BEHAVIOR_COMPOSITION.md)** — Multi-label classification, distance thresholds, composable behaviors

## Design and Tuning

- **[Designer Guide — Behavior Tuning](DESIGNER_GUIDE_BEHAVIOR_TUNING.md)** — Prototype tuning workflow, dimension reference, validation checklist
- **[Space Homogeneity](SPACE_HOMOGENEITY.md)** — Prototype spacing analysis, balance validation

## Tools

- **[Audio Editor Guide](AUDIO_EDITOR_GUIDE.md)** — Custom sound loading with ADSR envelopes
- **[Chord Lab](../tools/chord_lab.py)** — CLI diagnostic tool for testing chord classification without launching the game
- **[Visualization Summary](VISUALIZATION_SUMMARY.md)** — Visualizer tools overview

## Visualization

- **[Real-Time Visualizer](REALTIME_VISUALIZER.md)** — In-game manifold HUD, standalone high-DPI visualizer
- **[Visualization Quick Start](VISUALIZATION_QUICKSTART.md)** — Running and interpreting visualizers

## Integration

- **[Integration Guide](INTEGRATION_GUIDE.md)** — Replacing the old interaction engine, migration steps
- **[Integration Summary](INTEGRATION_SUMMARY.md)** — System status and next steps
- **[Particle Integration](PARTICLE_INTEGRATION.md)** — Behavior-specific particle effects

## Testing

- **[Testing Framework](TESTING.md)** — TAS system, unit tests, manifold tests

---

## Reading Paths

### Designers (no coding)

1. [Designer Mode Guide](DESIGNER_MODE_GUIDE.md) — In-game toolkit
2. [Manifold Systems](MANIFOLD_SYSTEMS.md) — Understand the 12D space
3. [Designer Guide — Behavior Tuning](DESIGNER_GUIDE_BEHAVIOR_TUNING.md) — Advanced workflow
4. [Behavior Composition](BEHAVIOR_COMPOSITION.md) — Multi-label concepts

### Developers

1. [Manifold Systems](MANIFOLD_SYSTEMS.md) — Core architecture
2. [Emergent vs Hardcoded](EMERGENT_VS_HARDCODED.md) — Design philosophy
3. [Integration Guide](INTEGRATION_GUIDE.md) — How it connects to the game
4. [Testing Framework](TESTING.md) — How to test

### Players

1. [Quick Start — Manifold HUD](QUICKSTART_MANIFOLD.md) — Try the visualization
2. [Emergent Behaviors](EMERGENT_BEHAVIORS.md) — Discover spell combinations

---

## Quick Commands

```bash
# Run game
python main.py

# Run game with manifold HUD
python main.py --manifold-hud

# Run designer mode
python main.py --designer

# Chord lab diagnostic
python tools/chord_lab.py

# Standalone visualizer
python magic/behavior_space_visualizer.py

# Run unit tests
python -m pytest tests/unit/ -v
```
