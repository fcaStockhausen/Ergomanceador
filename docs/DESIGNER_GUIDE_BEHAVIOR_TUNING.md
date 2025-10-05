# Designer Guide: Finding and Tuning Spell Behaviors

## 🎯 Purpose

This guide helps you (the designer) **discover emergent behaviors** in the property manifold and **tune prototypes** to improve spell classification.

**No coding required!** Just running Python scripts and editing JSON (eventually).

---

## 📋 Quick Start

### 1. Visualize Current Behavior Space

Run the interactive visualizer to see where behaviors are in 2D:

```bash
python magic/behavior_space_visualizer.py
```

**What you'll see:**
- 8 colored circles = Current behavior prototypes
- Gaps between circles = Potential new behaviors
- Press SPACE to test spell combinations

**Look for:**
- ✅ **Well-separated behaviors** (good)
- ❌ **Overlapping circles** (too similar - merge or adjust)
- 🎯 **Large empty gaps** (opportunities for new behaviors)

### 2. Test Element Combinations

Run the distance analyzer to see how spells classify:

```bash
python test_spell_distances.py
```

This shows **distances from any spell to ALL prototypes**, helping you understand:
- Why a spell classified the way it did
- Which prototypes are too close/far
- Where new prototypes should go

### 3. Find Emergent Behaviors

Look for spells that:
- Land far from all prototypes (distance > 1.5 to nearest)
- Feel unique when you play them
- Create interesting combinations

**Example:**
```
Fire + Shadow + Shadow:
  Distance to all prototypes > 1.3
  → Feels like a "draining flame" (life steal)
  → Add new "lifesteal" prototype here!
```

---

## 🔍 Understanding Distances

### What Do Distances Mean?

Distances are computed in **12-dimensional property space** using the Riemannian metric:

| Distance | Meaning | Action |
|----------|---------|--------|
| **< 0.8** | Very close match | Spell strongly fits this behavior |
| **0.8 - 1.2** | Moderate match | Spell partially fits (multi-label) |
| **1.2 - 1.6** | Weak match | Minor influence |
| **> 1.6** | No match | Behavior not relevant |

### Example Analysis

```
Fire + Fire + Fire:
  projectile:     1.324  ← Nearest (primary behavior)
  homing:         1.439  ← Close (secondary influence)
  aoe:            1.698  ← Far (minimal influence)
  heal:           2.089  ← Very far (not relevant)

Classification: PROJECTILE with homing tendencies
```

**Good:** Clear primary, reasonable secondary
**Bad:** All distances similar (unclear classification)

---

## 🎨 Finding New Behaviors: Step-by-Step

### Step 1: Play the Game and Take Notes

Queue different element combinations and note:
1. What does the spell feel like?
2. Is it unique or similar to existing behaviors?
3. Does the classification match your intuition?

**Template:**
```
Spell: Shadow + Ice + Ice
Feel: Slow-moving freezing cloud that lingers
Current: Classified as "area_denial" (correct!)
Notes: Perfect match, no changes needed
```

```
Spell: Lightning + Nature + Nature
Feel: Fast healing zap that chains to allies
Current: Classified as "heal" (partially correct)
Notes: Should have "chain" and "beam" influence!
      → Distances show chain=1.8 (too far)
      → Need to create "chain_heal" prototype
```

### Step 2: Identify Gaps in Behavior Space

Run the visualizer and look for **large empty regions**:

```bash
python magic/behavior_space_visualizer.py
```

**Signs of a gap:**
- Large distance between existing prototypes
- Multiple spells land in this region
- Feels like a distinct behavior when you play it

**Example gaps to look for:**
- Between Heal and Buff → "Regeneration" (heal over time)
- Between Projectile and Chain → "Splitting Shot"
- Between AOE and Area Denial → "Expanding Wall"

### Step 3: Test the Spell Systematically

Use the distance analyzer to get exact measurements:

```bash
python test_spell_distances.py
```

Add your spell to the `test_cases` list:

```python
test_cases = [
    # ... existing cases ...
    (['lightning', 'nature', 'nature'], "Lightning + Nature x2 (chain heal?)"),
]
```

Run again and check:
- Distance to all prototypes
- Which properties are causing the distances
- Where it would fit best

### Step 4: Decide: New Prototype or Tune Existing?

**Create NEW prototype if:**
- Spell is far from all existing prototypes (> 1.2 to nearest)
- Represents a genuinely new mechanic
- Multiple element combos land in this region
- Players would recognize it as distinct

**Tune EXISTING prototype if:**
- Spell should match existing behavior but doesn't
- Distance is close but not closest (wrong priority)
- Properties need slight adjustment

---

## 🔧 Tuning Existing Prototypes

### When to Tune

**Symptoms of bad prototypes:**
1. Spell feels like behavior X but classifies as Y
2. Two prototypes too close together (distance < 0.5)
3. Prototype in wrong region of property space
4. Unexpected spells matching this prototype

### How to Tune

Prototypes are defined in `magic/behavior_manifold.py`:

```python
# Current projectile prototype (example)
BehaviorRegion(
    name='projectile',
    prototype=np.array([
        0.3,   # thermal_flux
        0.4,   # avg_temperature
        0.3,   # temp_differential
        0.4,   # state_transition_energy
        0.3,   # phase_diversity
        0.3,   # density_gradient
        0.5,   # avg_density
        0.4,   # volatility_index
        0.3,   # chaos_factor
        0.4,   # total_energy
        0.4,   # energy_density
        0.2    # polarity_tension
    ]),
    metric_tensor=np.eye(12)
)
```

### Tuning Strategy

**To make prototype match spell better:**

1. **Check spell's property vector** (from distance analyzer)
2. **Compare to prototype values**
3. **Adjust prototype toward spell's properties**

**Example:**

```
Problem: Fire should be projectile, but it's not matching well

Fire properties:
  thermal_flux: 0.000 (normalized)
  avg_temperature: 0.600 (1200K / 2000)
  volatility: 0.700
  energy: 0.250 (100 / 400)
  polarity: -0.500 (negative)

Projectile prototype (before):
  thermal_flux: 0.300  ← Too high for single element
  avg_temperature: 0.400  ← Too low for fire
  volatility: 0.400  ← Too low for fire
  polarity: 0.200  ← Wrong sign!

Adjusted projectile prototype:
  thermal_flux: 0.100  ← Lower (single element has no flux)
  avg_temperature: 0.500  ← Higher (fire is hot)
  volatility: 0.500  ← Higher (fire is volatile)
  polarity: -0.200  ← Negative (damage)
```

### Prototype Dimension Guide

| Dimension | Low Value (0-0.3) | Medium (0.3-0.7) | High (0.7-1.0) |
|-----------|-------------------|------------------|----------------|
| **thermal_flux** | Single element | Mixed temps | Extreme temp difference |
| **avg_temperature** | Cold (ice, shadow) | Room temp | Hot (fire, lightning) |
| **temp_differential** | Homogeneous | Some variation | Wild extremes |
| **volatility** | Stable (earth, ice) | Moderate | Explosive (fire, lightning) |
| **chaos_factor** | Predictable | Some variance | Highly random |
| **polarity_tension** | Damaging (-1) | Neutral (0) | Healing (+1) |
| **total_energy** | Weak spells | Medium | Strong/multi-element |
| **avg_density** | Gaseous (beam) | Medium | Solid (earth) |

---

## ➕ Adding New Prototypes

### Step 1: Define the Behavior

Answer these questions:
1. **What does it do?** (e.g., "Splits into multiple projectiles after traveling")
2. **What elements create it?** (e.g., "Lightning + Arcane")
3. **What properties does it have?** (high energy, high chaos, instant)

### Step 2: Find a Spell That Represents It

Test element combinations until you find one that:
- Feels right for this behavior
- Lands in a gap in the visualizer
- Isn't well-represented by existing prototypes

**Example:**
```
Behavior: "Splitting Projectile"
Test spell: Lightning + Arcane + Arcane
Properties: High energy, high chaos, medium speed
```

### Step 3: Get the Property Vector

Run distance analyzer with your test spell:

```bash
python test_spell_distances.py
```

Add your spell to test cases and check its property vector:

```
Lightning + Arcane + Arcane:
  thermal_flux: 0.850
  avg_temperature: 0.650
  volatility: 0.750
  chaos_factor: 0.600
  energy_density: 0.700
  polarity: -0.333
  ...
```

### Step 4: Create the Prototype

Edit `magic/behavior_manifold.py` and add your new region:

```python
regions.append(BehaviorRegion(
    name='splitting',  # Your new behavior name
    prototype=np.array([
        0.85,  # thermal_flux (from your test spell)
        0.65,  # avg_temperature
        0.40,  # temp_differential
        0.60,  # state_transition_energy
        0.55,  # phase_diversity
        0.40,  # density_gradient
        0.30,  # avg_density
        0.75,  # volatility_index
        0.60,  # chaos_factor (HIGH - key for splitting)
        0.70,  # total_energy
        0.70,  # energy_density
        -0.33  # polarity_tension (damaging)
    ]),
    metric_tensor=np.eye(12)
))
```

### Step 5: Add Behavior to Formulas

In `magic/spell_formulas.py`, add behavior-specific multipliers:

```python
def compute_damage(self, vector, behavior):
    # ... existing code ...

    behavior_multipliers = {
        'projectile': 1.0,
        'aoe': 1.2,
        'splitting': 0.8,  # NEW: Lower damage per split
        # ...
    }
```

### Step 6: Test and Iterate

1. Run visualizer - Does your new prototype appear?
2. Test spell classification - Does your test spell now match?
3. Play in game - Does it feel right?
4. Adjust prototype position if needed

---

## 📊 Validation Checklist

After adding/tuning a prototype, verify:

### Distance Check
```bash
python test_spell_distances.py
```

✅ Test spells classify to correct behavior
✅ Distances are reasonable (< 1.2 to primary)
✅ No unexpected spells matching this prototype

### Visualization Check
```bash
python magic/behavior_space_visualizer.py
```

✅ Prototype appears in expected region
✅ Not overlapping with others (distance > 0.5)
✅ Test spells land near it

### Spacing Check

Run this to check prototype separation:

```python
python -c "
from magic.behavior_manifold import BehaviorManifold
import numpy as np

manifold = BehaviorManifold()
regions = manifold.regions

print('Prototype Distances:')
for i, r1 in enumerate(regions):
    for r2 in regions[i+1:]:
        dist = np.linalg.norm(r1.prototype - r2.prototype)
        print(f'{r1.name:15s} ↔ {r2.name:15s}: {dist:.3f}')
"
```

**Good:** All distances > 0.4
**Warning:** Any distance < 0.3 (too close, behaviors overlap)

### Gameplay Check

Play the game and test:
- ✅ Spell feels like the behavior name suggests
- ✅ Stats match expectations
- ✅ Distinct from other behaviors
- ✅ Fun to use!

---

## 🎮 Example Workflow: Adding "Chain Heal"

### Discovery

Playing the game, you notice:
```
Lightning + Nature + Nature feels like it should chain-heal allies
But it classifies as just "heal" (no chaining)
```

### Analysis

```bash
python test_spell_distances.py
```

Add test case:
```python
(['lightning', 'nature', 'nature'], "Chain Heal"),
```

Results:
```
Chain Heal:
  heal:  0.85  ← Closest (makes sense)
  chain: 1.65  ← Too far! (should be closer)
  beam:  1.40  ← Far

Properties:
  thermal_flux: 0.50 (moderate - lightning + nature mix)
  polarity: 0.67 (positive - mostly healing)
  chaos: 0.45 (moderate)
```

### Decision

**Create new "chain_heal" prototype** (combination of heal + chain properties)

### Implementation

Edit `magic/behavior_manifold.py`:

```python
regions.append(BehaviorRegion(
    name='chain_heal',
    prototype=np.array([
        0.50,  # thermal_flux (from lightning)
        0.40,  # avg_temperature
        0.30,  # temp_differential
        0.35,  # state_transition_energy
        0.40,  # phase_diversity
        0.35,  # density_gradient
        0.25,  # avg_density (low like chain)
        0.40,  # volatility
        0.45,  # chaos_factor (moderate - chain-like)
        0.45,  # total_energy
        0.50,  # energy_density
        0.67   # polarity_tension (HIGH - healing!)
    ]),
    metric_tensor=np.eye(12)
))
```

### Validation

Re-run analyzer:
```
Lightning + Nature + Nature:
  chain_heal: 0.68  ← NOW CLOSEST! ✓
  heal: 0.85
  chain: 1.20
```

Perfect! Now it classifies as chain_heal.

---

## 🗺️ Behavior Discovery Map

### Current Behaviors (v1.0)

1. **Projectile** - Standard ranged attack
2. **Beam** - Instant hitscan
3. **AOE** - Area explosion
4. **Chain** - Jumps between targets
5. **Homing** - Seeks target
6. **Area Denial** - Persistent zone
7. **Heal** - Restore health
8. **Buff** - Temporary enhancement

### Suggested New Behaviors (To Discover)

Based on property space gaps:

1. **Chain Heal** - Healing that jumps to allies
   - High polarity + medium chaos
   - Lightning + Nature combos

2. **Splitting** - Projectile that fragments
   - High chaos + moderate energy
   - Arcane + Lightning combos

3. **Regeneration** - Heal over time
   - High polarity + low volatility
   - Nature + Earth combos

4. **Wall** - Linear barrier
   - Low chaos + high density + area denial
   - Ice + Earth combos

5. **Nova** - Radial pulse from self
   - AOE + zero speed
   - Light combos

6. **Dot** (Damage Over Time) - Lingering damage
   - Negative polarity + duration + area denial
   - Shadow + Fire combos

7. **Drain** - Life steal
   - Negative polarity + heal hybrid
   - Shadow + Nature combos

8. **Ricochet** - Bounces off walls
   - High energy + low chaos + projectile
   - Earth + Fire combos

---

## 📝 Testing Template

Use this when testing new element combinations:

```
=== SPELL TEST ===

Elements: _______________
Feels Like: _______________
Current Classification: _______________

Property Vector (from analyzer):
  thermal_flux: _______
  avg_temperature: _______
  volatility: _______
  chaos: _______
  polarity: _______
  energy: _______

Distances:
  [behavior_1]: _______
  [behavior_2]: _______
  [behavior_3]: _______

Decision:
[ ] Correctly classified
[ ] Should be different behavior: _______________
[ ] New behavior needed: _______________
[ ] Tune prototype: _______________

Notes:
_________________________________
_________________________________
```

---

## 🚀 Advanced: Metric Tensor Tuning

For advanced users who want behaviors to prioritize certain dimensions:

Instead of identity matrix `np.eye(12)`, use weighted diagonal:

```python
metric_tensor=np.diag([
    2.0,  # thermal_flux - IMPORTANT for this behavior
    1.0,  # avg_temperature
    1.0,  # temp_differential
    1.0,  # state_transition_energy
    1.0,  # phase_diversity
    1.0,  # density_gradient
    1.0,  # avg_density
    3.0,  # volatility - VERY IMPORTANT
    1.5,  # chaos - IMPORTANT
    1.0,  # total_energy
    1.0,  # energy_density
    4.0   # polarity - CRITICAL (heal vs damage)
])
```

**Effect:** Differences in weighted dimensions count more toward distance.

**Use when:** Certain properties are critical for a behavior (e.g., polarity for heal)

---

## 📚 Quick Reference Commands

```bash
# Visualize behavior space (interactive)
python magic/behavior_space_visualizer.py

# Analyze spell distances
python test_spell_distances.py

# Test emergent blending
python test_emergent_blending.py

# Check prototype spacing
python -c "from magic.behavior_manifold import BehaviorManifold; import numpy as np; m = BehaviorManifold(); [print(f'{r1.name} ↔ {r2.name}: {np.linalg.norm(r1.prototype - r2.prototype):.3f}') for i, r1 in enumerate(m.regions) for r2 in m.regions[i+1:]]"
```

---

## ✅ Summary

**To find and tag new behaviors:**

1. **Play** → Notice unique spell combinations
2. **Analyze** → Run `test_spell_distances.py` to see where it lands
3. **Decide** → New prototype or tune existing?
4. **Implement** → Add to `behavior_manifold.py`
5. **Validate** → Re-test and visualize
6. **Iterate** → Adjust until it feels right

**Key principle:** Let the geometry guide you! The manifold will show you where behaviors naturally cluster - you just need to label them.

---

**Happy behavior hunting! 🎯**
