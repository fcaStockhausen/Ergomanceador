# Manifold HUD Quick Start

## Overview

The manifold HUD is an in-game panel that visualizes how queued elements map to spell behaviors in real time. It projects the 12-dimensional property space onto a 2D plane using PCA, showing prototype positions and the current spell's location.

## Running

```bash
python main.py --manifold-hud
```

A panel appears in the top-right corner showing:
- Colored circles representing the 10 behavior prototypes
- A pulsing dot for the current spell's position in property space
- A line connecting to the nearest prototype
- The classified behavior at the bottom

## Interpretation

### PCA Projection

The 12 property dimensions are compressed to 2D via Principal Component Analysis:

- **Horizontal axis (PC1):** Energy and volatility spectrum (left = low/stable, right = high/chaotic)
- **Vertical axis (PC2):** Thermal and polarity spectrum (top = hot/destructive, bottom = cold/defensive)

### Prototype Reference

| Label | Behavior | Color |
|---|---|---|
| PROJ | Projectile | Light blue |
| BEAM | Beam | Orange |
| AOE | Area of effect | Red |
| CHAI | Chain | Purple |
| HOMI | Homing | Cyan |
| AREA | Area denial | Gray |
| HEAL | Heal | Green |
| BUFF | Buff | Yellow |
| SHLD | Shield | Dark gray |
| SPLT | Split | Magenta |

### Example Positions

| Queue | Expected Position | Classification |
|---|---|---|
| Fire | Near projectile | Projectile |
| Fire + Water | Between chain/AOE | Chain |
| Nature | On heal | Heal |
| Fire + Fire + Fire | Near AOE | AOE |
| Earth + Earth | On shield | Shield |

## Finding Gaps

Empty regions between prototypes indicate where new behaviors could emerge. To investigate:

1. Queue element combinations that land in gaps.
2. Use the chord lab to get exact distances:
   ```bash
   python tools/chord_lab.py fire shadow
   ```
3. If the chord is far from all prototypes (>1.2 distance) and feels distinct in gameplay, consider adding a new prototype at that position.

## Configuration

### Panel Position

Edit `core/game.py` where the manifold panel is instantiated:

```python
panel = ManifoldPanel(
    x=SCREEN_WIDTH - panel_width - 10,  # Top-right
    y=10,
    width=320,
    height=280
)
```

### Standalone Visualizer

For analysis without running the game:

```bash
python magic/behavior_space_visualizer.py
```

Opens a 1200×900 high-DPI window with the same projection, SPACE to cycle test spells, and mouse hover for prototype details.

## Related

- [Manifold Systems](MANIFOLD_SYSTEMS.md) — Architecture and math
- [Designer Guide](DESIGNER_GUIDE_BEHAVIOR_TUNING.md) — Prototype tuning workflow
- [Chord Lab](../tools/chord_lab.py) — CLI diagnostic tool
