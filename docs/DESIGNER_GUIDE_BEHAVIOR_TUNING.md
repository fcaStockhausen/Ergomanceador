# Designer Guide: Behavior Tuning

## Overview

This guide covers the workflow for tuning existing spell behavior prototypes and adding new ones. It complements the in-game Designer Mode (F1) with command-line diagnostic tools that provide precise numerical analysis.

## Tools

### Chord Lab (CLI)

The primary diagnostic tool. Runs without launching the game:

```bash
# Full diagnostic report (normalization, spacing, reachability, distribution)
python tools/chord_lab.py

# Analyze a specific chord
python tools/chord_lab.py fire water nature

# Interactive REPL
python tools/chord_lab.py --interactive

# Sweep all combinations up to N elements
python tools/chord_lab.py --sweep 4
```

Output includes:
- Normalized 12D property vector with out-of-range warnings
- Distances to all 10 prototypes
- Multi-label activations with strengths
- Computed spell stats (damage, speed, area, duration, mana)
- Single-label vs multi-label consistency check

### Standalone Visualizer

```bash
python magic/behavior_space_visualizer.py
```

Opens a 1200×900 PCA projection of property space with all prototypes and test spells. SPACE cycles through combinations.

### In-Game Designer Mode

Press F1 during gameplay to open the two-panel designer interface (Testing Lab + Prototype Editor). No coding required — uses visual sliders for all 12 dimensions.

---

## Distance Reference

Distances are computed in normalized 12D space using weighted Riemannian metrics:

| Distance | Meaning | Action |
|---|---|---|
| < 0.5 | Strong match | Primary behavior, dominant stats |
| 0.5 – 0.8 | Clear match | Primary behavior with modifiers |
| 0.8 – 1.2 | Moderate match | Contributes to blended stats |
| > 1.2 | Weak or no match | Minimal or no influence |

---

## Tuning Existing Prototypes

### When to Tune

- A spell feels like behavior X but classifies as Y
- Two prototypes are too close (inter-prototype distance < 0.5)
- A behavior never wins as primary (unreachable)
- Classification is inconsistent between single-label and multi-label

### How to Tune

Prototypes are defined in `magic/behavior_manifold.py` in `_create_behavior_regions()`. Each prototype has two adjustable components:

**1. Prototype position** (the ideal point in 12D space):

```python
regions.append(BehaviorRegion(
    name='projectile',
    prototype=np.array([
        0.15, 0.67, 0.15, 0.55, 0.25, 0.05,  # thermal + state dims
        0.30, 0.60, 0.05, 0.20, 0.65, -0.50  # density + energy + polarity
    ]),
    ...
))
```

**2. Metric tensor** (per-dimension weights for distance calculation):

```python
    metric_tensor=np.diag([1, 1, 1, 1, 1, 1, 1.5, 1.5, 1, 1.5, 2.0, 0.5])
```

Higher metric weights make a dimension count more toward distance. Use this to emphasize the defining properties of each behavior. For example:
- HEAL weights polarity at 5.0× (only high-polarity spells match)
- SHIELD weights density at 5.0× (only high-density spells match)
- CHAIN weights thermal flux at 4.0× (only high-flux spells match)

### Dimension Reference

| Dimension | Normalization | Low (0–0.3) | High (0.7–1.0) |
|---|---|---|---|
| thermal_flux | /2.0, clipped | Single element | Extreme temp mixing |
| avg_temperature | log10 / log10(30000) | Cold (ice, shadow) | Hot (fire, lightning) |
| temp_differential | log10 / log10(30000) | Homogeneous | Wild extremes |
| state_transition_energy | log10 / log10(20000) | Quick, dissipating | Persistent, stable |
| phase_diversity | Linear (0–1) | Single state | All 4 states |
| density_gradient | Linear (0–1) | Uniform density | Mixed densities |
| avg_density | Linear (0–1) | Gaseous (arcane) | Solid (earth) |
| volatility_index | Linear (0–1) | Stable (earth, ice) | Explosive (fire) |
| chaos_factor | Linear (0–1) | Predictable | Highly variable |
| total_energy | /600.0, clipped | Weak spells | Strong / multi-element |
| energy_density | /150.0, clipped | Low intensity | Concentrated power |
| polarity_tension | [−1, +1] | Negative (damage) | Positive (healing) |

---

## Adding New Prototypes

### Workflow

1. **Identify a gap** — Run `python tools/chord_lab.py` and check the diagnostic report for unreachable regions or chords that land far from all prototypes.

2. **Find a representative chord** — Use `python tools/chord_lab.py fire shadow` (interactive mode) to test combinations until you find one that feels like the new behavior.

3. **Get the property vector** — The chord lab output shows the normalized 12D position. Use this as the starting point for the prototype.

4. **Add the region** — Edit `magic/behavior_manifold.py`:

```python
regions.append(BehaviorRegion(
    name='YOUR_BEHAVIOR',
    prototype=_proto([... 12 values ...]),
    metric_tensor=_metric([... 12 weights ...]),
    threshold=1.0
))
```

5. **Add stat multipliers** — Edit `magic/spell_formulas.py` to add the behavior to all `behavior_*` dictionaries (damage modifiers, base areas, speeds, durations, mana multipliers, range).

6. **Validate** — Re-run the chord lab diagnostic:
```bash
python tools/chord_lab.py
```
Check that:
- The new behavior is reachable (best_strength > 0.3)
- No collisions with existing prototypes (distance > 0.5)
- Single-label and multi-label agree
- Classification distribution is reasonable

---

## Validation Checklist

After any prototype change, verify:

- [ ] `python tools/chord_lab.py` shows 0 single vs multi-label mismatches
- [ ] All 10 behaviors are reachable (best_strength > 0.1)
- [ ] No prototype collisions (inter-prototype distance > 0.5)
- [ ] No chord has nearest distance > 1.5 to all prototypes
- [ ] Classification distribution is not dominated by one behavior (>60%)
- [ ] `python -m pytest tests/unit/test_behavior_manifold.py -v` passes

---

## Current Behavior Distribution

As of the last diagnostic run (219 chords, 1–3 elements):

| Behavior | Share | Notes |
|---|---|---|
| Split | 32.4% | Fire+light, arcane+light combos |
| Chain | 23.7% | High-flux combinations |
| Area Denial | 16.0% | Earth, ice, water combos |
| Beam | 12.3% | Arcane-heavy combos |
| Buff | 5.0% | Nature + earth/water |
| AOE | 3.2% | Stacked fire/lightning |
| Homing | 2.7% | Pure arcane |
| Shield | 1.8% | Earth stacking |
| Projectile | 1.4% | Single fire/arcane |
| Heal | 1.4% | Nature stacking |

Run `python tools/chord_lab.py` for the current distribution.

---

## Related

- [Manifold Systems](MANIFOLD_SYSTEMS.md) — Architecture and math
- [Emergent vs Hardcoded](EMERGENT_VS_HARDCODED.md) — Design philosophy
- [Chord Lab](../tools/chord_lab.py) — CLI diagnostic tool
- [Designer Mode Guide](DESIGNER_MODE_GUIDE.md) — In-game toolkit
