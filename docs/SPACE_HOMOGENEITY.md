# Making the Behavior Manifold Space More Homogeneous

## 🎯 **The Problem You Identified**

Your visualization shows **all behaviors clustered on the left** (Thermal Axis 0-2), with Lightning isolated far right (Thermal Axis ~30). This looks highly imbalanced.

**Why this happens:**
1. The **visualization axes** use raw property values (thermal flux, volatility)
2. But the **classification** uses **normalized** vectors (all scaled to 0-1)
3. The 2D projection doesn't show the true 12D manifold structure

## ✅ **What's Already Fixed**

The code **already normalizes** all dimensions in `_vector_to_array()`:

```python
# OLD (was imbalanced)
vector.thermal_flux          # Range: 0-2+
vector.avg_temperature       # Range: 0-2000
vector.total_energy          # Range: 0-400

# NEW (balanced)
vector.thermal_flux / 2.0        # Range: 0-1 ✓
vector.avg_temperature / 2000.0  # Range: 0-1 ✓
vector.total_energy / 400.0      # Range: 0-1 ✓
```

**All 12 dimensions now contribute equally to distance calculations.**

## 🔧 **Additional Improvements**

### **Option 1: Use Weighted Metric Tensor** (Advanced)

Instead of identity metric `I`, use a **weighted metric** that emphasizes important dimensions:

```python
# Give more weight to volatility and thermal flux
weighted_metric = np.diag([
    2.0,  # thermal_flux - IMPORTANT
    1.0,  # avg_temperature
    1.0,  # temp_differential
    1.0,  # state_transition_energy
    1.0,  # phase_diversity
    1.0,  # density_gradient
    1.0,  # avg_density
    2.0,  # volatility_index - IMPORTANT
    1.5,  # chaos_factor - IMPORTANT
    1.0,  # total_energy
    1.0,  # energy_density
    3.0   # polarity_tension - VERY IMPORTANT (heal vs damage)
])
```

**Effect:** Polarity differences count 3x more than temperature differences.

### **Option 2: Spread Prototypes More** (Simple)

Move prototypes further apart in key dimensions:

```python
# OLD: Projectile and Beam too close
projectile: [0.3, 0.4, 0.3, ...]  # thermal_flux = 0.3
beam:       [0.8, 0.6, 0.5, ...]  # thermal_flux = 0.8
# Difference: only 0.5

# NEW: Spread them out more
projectile: [0.2, 0.3, 0.2, ...]  # thermal_flux = 0.2
beam:       [0.9, 0.8, 0.7, ...]  # thermal_flux = 0.9
# Difference: 0.7 (40% increase in separation)
```

### **Option 3: Add Non-Linear Metric** (Expert)

Use a **Mahalanobis distance** or **learned metric** from example spells:

```python
# Compute covariance of training data
# Use inverse covariance as metric tensor
metric = np.linalg.inv(covariance_matrix)
```

This automatically weights dimensions by their variance in real spells.

## 📊 **How to Verify Homogeneity**

### **Test 1: Pairwise Prototype Distances**

```python
from magic.behavior_manifold import BehaviorManifold

manifold = BehaviorManifold()

# Compute all pairwise distances
distances = {}
regions = manifold.regions
for i, r1 in enumerate(regions):
    for j, r2 in enumerate(regions[i+1:], start=i+1):
        dist = manifold._riemannian_distance(
            r1.prototype,
            r2.prototype,
            r1.metric_tensor
        )
        distances[f"{r1.name}-{r2.name}"] = dist

# Print sorted
for pair, dist in sorted(distances.items(), key=lambda x: x[1]):
    print(f"{pair}: {dist:.3f}")
```

**Ideal:** All distances should be roughly similar (e.g., 0.5-1.5 range).

**Bad:** Some pairs at 0.1, others at 5.0 (imbalanced).

### **Test 2: Classification Entropy**

```python
from magic.element_loader import load_elements_from_json
from magic.property_vector import PropertyVectorComputer
import numpy as np

elements = load_elements_from_json()

# Test many random combinations
entropies = []
for _ in range(1000):
    # Random 1-3 element combo
    combo = np.random.choice(list(elements.values()), size=np.random.randint(1, 4))
    vector = PropertyVectorComputer.compute(combo)
    probs = manifold.get_behavior_probabilities(vector)

    # Compute entropy
    p_values = np.array(list(probs.values()))
    entropy = -np.sum(p_values * np.log(p_values + 1e-10))
    entropies.append(entropy)

print(f"Average entropy: {np.mean(entropies):.3f}")
print(f"Max entropy (uniform): {np.log(8):.3f}")
```

**Ideal:** Entropy close to max → using all behaviors evenly.

**Bad:** Low entropy → always classifying as same 2-3 behaviors.

## 🚀 **Recommended Action Plan**

### **Phase 1: Verify Current Balance** (Do this first!)

```bash
# Run this test
python -c "
from magic.behavior_manifold import BehaviorManifold
import numpy as np

manifold = BehaviorManifold()
regions = manifold.regions

# Compute mean distance between prototypes
distances = []
for i, r1 in enumerate(regions):
    for j, r2 in enumerate(regions[i+1:], start=i+1):
        dist = np.linalg.norm(r1.prototype - r2.prototype)
        distances.append(dist)

print(f'Mean prototype distance: {np.mean(distances):.3f}')
print(f'Std dev: {np.std(distances):.3f}')
print(f'Min/Max: {np.min(distances):.3f} / {np.max(distances):.3f}')
"
```

If `std_dev / mean > 0.5`, the space is imbalanced.

### **Phase 2: If Needed, Spread Prototypes**

Edit `behavior_manifold.py` prototypes to be more extreme:

```python
# Example: Make Heal more distinct
regions.append(BehaviorRegion(
    name=self.HEAL,
    prototype=np.array([
        0.1,   # thermal_flux (VERY LOW - was 0.2)
        0.2,   # avg_temperature (VERY LOW - was 0.3)
        0.05,  # temp_differential (VERY LOW - was 0.1)
        0.2,   # state_transition_energy
        0.1,   # phase_diversity (VERY SIMPLE - was 0.2)
        0.1,   # density_gradient
        0.3,   # avg_density
        0.1,   # volatility (VERY LOW - was 0.2)
        0.05,  # chaos_factor (VERY LOW - was 0.1)
        0.3,   # total_energy (LOW - was 0.4)
        0.3,   # energy_density
        0.95   # polarity_tension (VERY HIGH - was 0.9)
    ]),
    ...
))
```

### **Phase 3: Validate with Tests**

```bash
# Re-run tests
python -m pytest tests/unit/test_behavior_manifold.py -v

# Re-run interactive demo
python test_manifolds_interactive.py
```

## 📈 **Expected Results**

**Before fixes:**
- Most spells classify as 2-3 behaviors
- Probability distributions very peaked (one behavior 80%+)
- Some behaviors never used

**After fixes:**
- Spells spread across all 8 behaviors
- Probability distributions more balanced (e.g., 40%, 30%, 20%)
- All behaviors get used for appropriate spells

## 💡 **Why This Matters for Godot Port**

A balanced manifold means:
- ✅ **Predictable gameplay** - Players can understand spell classification
- ✅ **Diverse spell pool** - All behaviors get used, not just projectile
- ✅ **Easy tuning** - Adjust one prototype → changes classification smoothly
- ✅ **JSON-tunable** - Ship prototypes as JSON, update without rebuild

---

**TL;DR:**
1. Run Phase 1 verification script
2. If imbalanced, spread prototypes in Phase 2
3. Re-test with Phase 3

The normalization is already correct - you just need to verify the prototypes are well-distributed.
