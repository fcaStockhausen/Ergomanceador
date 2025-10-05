# Emergent Behavior vs Hardcoded Composition

## ❓ Your Question

> "Isn't `compose_behavior_name()` hardcoded? Doesn't that go against emergent behavior?"

**YES, you're absolutely right to question this!** Let me clarify the philosophy.

---

## 🎯 The Core Principle: Properties Define Behavior, Not Names

### ❌ WRONG Way (Hardcoded)

```python
# BAD: Name determines behavior
if behavior_name == "explosive_projectile":
    damage = 200
    area = 10
    speed = 150
elif behavior_name == "area_heal":
    damage = -50  # negative = healing
    area = 15
    speed = 0
```

**Problem:** We're back to if-else chains! Not emergent!

### ✅ RIGHT Way (Emergent)

```python
# GOOD: Weighted properties determine behavior
weights = {
    'projectile': 0.60,  # 60% projectile-like
    'aoe': 0.40          # 40% AOE-like
}

# Blend stats from each activated behavior
damage = sum(weights[b] * formulas.compute_damage(vector, b) for b in weights)
area = sum(weights[b] * formulas.compute_area(vector, b) for b in weights)
speed = sum(weights[b] * formulas.compute_speed(vector, b) for b in weights)

# The spell NATURALLY becomes "explosive projectile" because:
# - High speed (from projectile)
# - Large area (from AOE)
# - The math blends them emergently!
```

**The name "projectile_aoe" is just a LABEL. The actual behavior emerges from weighted stats.**

---

## 📊 How Multi-Label ACTUALLY Works (Emergent)

### Example: Fire + Fire + Fire

**Step 1: Compute Distances**
```
Projectile: 1.324  → strength = 0.33 (33%)
AOE:        1.698  → strength = 0.24 (24%)
Beam:       1.540  → strength = 0.28 (28%)
...
```

**Step 2: Get Weights (normalized)**
```
weights = {
    'projectile': 0.33 / total = 0.38  (38%)
    'beam':       0.28 / total = 0.32  (32%)
    'aoe':        0.24 / total = 0.27  (27%)
    'other':      0.03                  (3%)
}
```

**Step 3: Blend Stats (EMERGENT!)**
```python
# Each behavior has its own formula-computed stats
projectile_damage = formulas.compute_damage(vector, 'projectile')  # e.g., 150
beam_damage = formulas.compute_damage(vector, 'beam')              # e.g., 180
aoe_damage = formulas.compute_damage(vector, 'aoe')                # e.g., 200

# Weighted blend (THIS IS EMERGENT!)
final_damage = (
    0.38 * 150 +  # projectile contribution
    0.32 * 180 +  # beam contribution
    0.27 * 200    # AOE contribution
) = 175

# Same for ALL stats
final_area = 0.38 * projectile_area + 0.32 * beam_area + 0.27 * aoe_area
final_speed = 0.38 * projectile_speed + 0.32 * beam_speed + 0.27 * aoe_speed
final_duration = ...
```

**Result:** A spell that's 38% projectile, 32% beam, 27% AOE. It naturally has:
- Medium-high speed (projectile influence)
- Medium area (AOE influence)
- Medium-high damage (beam influence)

**No hardcoding! The behavior emerges from the weighted blend of formulas!**

---

## 🏷️ What About the Name?

The name is **purely descriptive**, not prescriptive:

```python
# BEFORE (wrong mindset)
name = "explosive_projectile"
# → Developer thinks: "Now I need to code what explosive_projectile does"

# AFTER (correct mindset)
name = "projectile_aoe"  # Just lists what's activated
# → The spell's behavior already emerged from weighted stats
# → The name is just for the UI/tooltip
```

### Name Should Be Generated From Properties (Even Better!)

Instead of listing behaviors, generate name from **final stats**:

```python
def generate_procedural_name(vector, stats):
    """Generate spell name from emergent properties"""
    descriptors = []

    # Speed-based
    if stats['speed'] > 300:
        descriptors.append("Swift")
    elif stats['speed'] < 100:
        descriptors.append("Slow")

    # Area-based
    if stats['area'] > 10:
        descriptors.append("Explosive")
    elif stats['area'] < 3:
        descriptors.append("Focused")

    # Damage-based
    if stats['damage'] > 200:
        descriptors.append("Devastating")
    elif stats['damage'] < 0:
        descriptors.append("Healing")

    # Base type (from primary behavior)
    base = activations[0].behavior.title()

    return f"{' '.join(descriptors)} {base}"

# Examples:
# Fire x3 → stats: {speed: 250, area: 8, damage: 180}
# → "Explosive Projectile"  (emergent from stats!)

# Nature x2 → stats: {speed: 50, area: 12, damage: -80}
# → "Slow Healing Projectile" → Better: "Area Heal"
```

**Now the name DESCRIBES the emergent behavior, doesn't prescribe it!**

---

## 🎮 Integration Example

### Current System (Single-Label)

```python
# magic/interaction_engine.py
behavior = self.manifold.classify(vector)  # e.g., "projectile"
damage = self.formulas.compute_damage(vector, behavior)
area = self.formulas.compute_area(vector, behavior)
```

### Multi-Label System (Emergent Blending)

```python
# magic/interaction_engine.py
from magic.behavior_composer import BehaviorComposer

# Classify with multiple behaviors
activations = composer.classify_multi(vector)
weights = composer.get_behavior_weights(activations)

# EMERGENT: Blend stats using weights
damage = sum(
    weights[behavior] * self.formulas.compute_damage(vector, behavior)
    for behavior in weights
)
area = sum(
    weights[behavior] * self.formulas.compute_area(vector, behavior)
    for behavior in weights
)
speed = sum(
    weights[behavior] * self.formulas.compute_speed(vector, behavior)
    for behavior in weights
)

# Name is just descriptive (cosmetic)
primary = composer.get_primary_behavior(activations)
name = composer.compose_behavior_name(activations)  # e.g., "projectile_aoe"

# OR use procedural naming (even better!)
name = generate_procedural_name(vector, {'damage': damage, 'area': area, 'speed': speed})
```

---

## 🔍 The Philosophy

### Single-Label (Voronoi)

```
You are in THIS region → You get THIS behavior (hardcoded stats for region)
```

**Problem:** Discrete jumps at boundaries. Not smooth.

### Multi-Label (Weighted Manifold)

```
You are:
  - 40% in Projectile region → Get 40% of projectile stats
  - 35% in AOE region → Get 35% of AOE stats
  - 25% in Beam region → Get 25% of beam stats

Result = Weighted blend of all three (EMERGENT!)
```

**Benefit:** Smooth transitions. Composable. No hardcoding.

---

## ✅ Summary

### What IS Emergent

1. ✅ **Weighted stat blending** from activated behaviors
2. ✅ **Distance-based activation strengths** (geometry determines everything)
3. ✅ **Formula-computed stats** for each behavior (not hardcoded values)
4. ✅ **Procedural naming** from final stats

### What Is NOT Emergent (But Acceptable)

1. ⚠️ **Behavior names** - Just labels for UI (cosmetic)
2. ⚠️ **Prototype positions** - These ARE designed, but based on property theory
3. ⚠️ **Formula coefficients** - Tunable, but ultimately designer-set

### What WOULD BE Hardcoded (Avoid!)

1. ❌ **If-else chains** for behavior determination
2. ❌ **Hardcoded stat values** for composed behaviors
3. ❌ **Special cases** like "if Fire+Water then steam explosion with these exact stats"

---

## 🎯 The Bottom Line

**Question:** "Isn't compose_behavior_name hardcoded?"

**Answer:** The NAME is hardcoded (or better, procedurally generated), but that's just a label. The actual **behavior emerges from weighted stat blending**. As long as we use:

```python
damage = Σ (weight_i × formula_damage(behavior_i))
```

Instead of:

```python
if name == "explosive_projectile":
    damage = 200  # ← HARDCODED BAD!
```

We maintain **true emergent behavior**.

---

**Key Insight:** Names are just human-readable labels. The emergent magic happens in the **weighted formula blending**, which is pure geometry + math, no hardcoding!
