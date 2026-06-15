# Manifold-Based Core Systems

## Overview

The core systems use manifold theory to provide a mathematically rigorous, engine-agnostic foundation for the magic engine. The design goals are:

1. **Portability** — Pure math with no rendering dependencies, enabling straightforward ports to Godot or Unity.
2. **Tunability** — All coefficients are explicit and can be externalized to JSON for balance changes without code deployment.
3. **Geometric classification** — Spell behaviors emerge from distance calculations in property space, not if-else chains.
4. **Testability** — Unit tests validate every component independently.

---

## 1. Magic Interaction Engine

### Architecture

```
Element Combination
        ↓
PropertyVector (R^12)
        ↓
BehaviorManifold ──── BehaviorComposer
  (single-label)        (multi-label)
        ↓                      ↓
  Nearest prototype    Weighted activation
        ↓                      ↓
SpellFormulas ←──── behavior weights
        ↓
Spell descriptor (damage, area, speed, duration, ...)
```

### PropertyVector

**File:** [magic/property_vector.py](../magic/property_vector.py)

Converts a list of elements into a 12-dimensional property vector. This is the sole point where raw element properties are read — all downstream logic operates on the vector.

```python
PropertyVector(
    thermal_flux: float,             # Rate of temperature equilibration
    avg_temperature: float,          # Mean temperature (K)
    temp_differential: float,        # Temperature range (K)
    state_transition_energy: float,  # Energy required for phase change
    phase_diversity: float,          # Fraction of distinct states (0–1)
    density_gradient: float,         # Density std dev (0–1)
    avg_density: float,              # Mean density (0–1)
    volatility_index: float,         # Mean volatility (0–1)
    chaos_factor: float,             # Cross-property variance
    total_energy: float,             # Sum of element energies
    energy_density: float,           # Energy per element
    polarity_tension: float,         # Polarity imbalance (−1 to +1)
    element_count: int               # Number of elements
)
```

Key characteristics:
- Contains no behavior information — purely physical properties.
- Temperature-derived dimensions are normalized with **log scale** (`log10`) because element temperatures span three orders of magnitude (100K to 30000K).
- Computed via `PropertyVectorComputer.compute(elements)`.

### BehaviorManifold

**File:** [magic/behavior_manifold.py](../magic/behavior_manifold.py)

The property space R^12 is treated as a Riemannian manifold partitioned into behavior regions.

**Mathematical structure:**
- **Manifold:** M = R^12
- **Metric:** Diagonal metric tensors (per-dimension weights) define distance for each behavior
- **Partition:** M = ⋃ R_i (union of 10 behavior regions)
- **Classification:** Find region R_i minimizing Riemannian distance to the property vector

**10 Behavior Regions:**

| Behavior | Defining Properties |
|---|---|
| Projectile | Moderate energy density, moderate volatility |
| Beam | High energy density, low volatility, moderate flux |
| AOE | High total energy, high volatility (stacked elements) |
| Area Denial | High density, low volatility, moderate persistence |
| Buff | Positive polarity, low chaos, moderate density |
| Heal | Very high positive polarity, low thermal activity |
| Shield | Very high density, very low volatility, high persistence |
| Homing | Low density, high energy concentration |
| Chain | Very high thermal flux, moderate energy |
| Split | High chaos, high temperature, low density |

**Distance formula:**

```
d(v, p) = sqrt((v − p)^T · G · (v − p))
```

where G is the diagonal metric tensor for the behavior region. Each behavior uses a **weighted metric tensor** so that its defining dimensions dominate the distance calculation. For example, the HEAL prototype weights `polarity_tension` at 5.0× to ensure only high-polarity spells match.

**Normalization:** All 12 dimensions are mapped to [0, 1] (polarity stays [−1, 1]). Temperature dimensions use log scale; all others use linear clipping. This is critical — without log normalization, elements like lightning (30000K) produce distance values of 15+ to every prototype, making them unclassifiable.

### BehaviorComposer

**File:** [magic/behavior_composer.py](../magic/behavior_composer.py)

Multi-label classifier that allows multiple behaviors to activate simultaneously based on distance thresholds.

- Activation strength: `exp(−distance / 1.2)`
- Minimum activation: 0.1 (below this, behavior is inactive)
- Primary behavior: highest activation strength
- Modifiers: secondary behaviors with ≥30% of primary's strength

The composer uses the same `_vector_to_array()` method as the manifold (single source of truth for normalization).

### SpellFormulas

**File:** [magic/spell_formulas.py](../magic/spell_formulas.py)

All spell stats are computed from the property vector using tunable formulas:

```
damage   = saturation × tanh((energy × mult + thermal × factor) × polarity × behavior_mod / saturation)
area     = base + volatility × (exp(vol × 2) − 1) + diversity × factor + chaos × factor − density × penalty
speed    = base + (1 − density) × mult + tanh(energy_density / 50) × factor + flux × factor
duration = base + tanh(state_energy / 500) × persistence + (1 − volatility) × stability + (1 − chaos) × control
```

All coefficients are explicit and tunable. Each behavior has its own multipliers (e.g., AOE damage modifier = 0.7, projectile = 1.0).

---

## 2. Spatial Manifold System

**File:** [world/spatial_manifold.py](../world/spatial_manifold.py)

Provides topology-independent geometric operations for the game world:

| Topology | Distance | Geodesic | Use Case |
|---|---|---|---|
| Flat | Euclidean | Straight line | Standard arena |
| Toroidal | Wrapped Euclidean | Wrapping line | Pac-Man style, no boundaries |
| Spherical | Great circle | Slerp arc | Planetary surface |

Distance, geodesic pathfinding, and point wrapping respect the active topology. The topology can be changed at runtime.

---

## 3. Diagnostic Tools

### Chord Lab

**File:** [tools/chord_lab.py](../tools/chord_lab.py)

Standalone CLI tool for testing chord classification without launching the game:

```bash
python tools/chord_lab.py                      # Full diagnostic report
python tools/chord_lab.py fire nature shadow   # Analyze a specific chord
python tools/chord_lab.py --interactive        # REPL mode
python tools/chord_lab.py --sweep 4            # Sweep up to 4 elements
```

Reports: normalized 12D vector, distances to all prototypes, multi-label activations, computed stats, single vs multi-label consistency, prototype spacing, and behavior reachability across all combinations.

---

## 4. Testing

```bash
python -m pytest tests/unit/test_property_vector.py -v
python -m pytest tests/unit/test_behavior_manifold.py -v
python -m pytest tests/unit/test_spatial_manifold.py -v
```

---

## 5. Engine-Agnostic Design

The core systems contain zero rendering or input dependencies. The same property vector computation, manifold classification, and formula evaluation can be translated directly to GDScript (Godot) or C# (Unity) — only the rendering and input layers need rewriting.

Coefficient externalization to JSON is supported by the constructor signatures (`coefficients` parameter) but defaults are currently hardcoded for development convenience.
