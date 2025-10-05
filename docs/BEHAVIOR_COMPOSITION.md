# Behavior Composition System - Design Document

## 🎯 The Problem with Single-Label Classification

### What You Observed

**Fire x4 was classified as Heal** (before fixing polarities)

This revealed a fundamental issue: **Voronoi partitioning assumes behaviors are mutually exclusive**, but they should be composable!

### Current Issues

1. **Either/Or Problem**: A spell is EITHER a projectile OR a heal, never both
2. **Unintentional Overlaps**: High energy fire has similar properties to some heal dimensions
3. **No Composability**: Can't have "healing projectile" or "explosive AOE beam"

## ✅ The Solution: Multi-Label Distance-Based Classification

### Core Concept

Instead of "nearest prototype wins", use **distance thresholds** where multiple behaviors activate:

```
Distance < 0.8  → STRONG activation (dominant behavior)
Distance < 1.2  → MEDIUM activation (modifier behavior)
Distance < 1.6  → WEAK activation (flavor only)
```

### Examples of Compositions

| Elements | Primary | Modifiers | Composed Behavior |
|----------|---------|-----------|-------------------|
| Fire x3 | Projectile | AOE | **Explosive Projectile** |
| Nature x2 | Heal | AOE, Buff | **Area Heal** |
| Fire + Water | Projectile | Chain, Beam | **Steam Jet** |
| Ice x2 | Area Denial | Projectile | **Ice Wall Projectile** |

## 📊 How It Works

### Step 1: Compute All Distances

For each prototype, compute Riemannian distance in 12D space:

```python
distances = {
    'projectile': 0.65,  # Close!
    'aoe': 0.95,         # Medium
    'heal': 1.85,        # Far
    ...
}
```

### Step 2: Convert to Activation Strengths

Use exponential decay: `strength = exp(-distance / threshold)`

```python
strengths = {
    'projectile': 0.56,  # 56% activation
    'aoe': 0.47,         # 47% activation
    'heal': 0.21,        # 21% activation (weak)
}
```

### Step 3: Filter by Minimum Strength

Only keep behaviors with `strength >= 0.10` (10% minimum)

### Step 4: Compose Behavior Name

- **Primary** = Strongest behavior
- **Modifiers** = Secondary behaviors >= 30% of primary strength

## 🎨 Integration Strategies

### Option 1: Replace Current System (Breaking Change)

Replace `BehaviorManifold.classify()` with multi-label system:

```python
# OLD
behavior = manifold.classify(vector)  # Returns single string

# NEW
activations = composer.classify_multi(vector)
behavior = composer.get_primary_behavior(activations)  # Backward compatible
modifiers = composer.get_modifiers(activations)  # New functionality
```

### Option 2: Parallel System (Non-Breaking)

Keep current single-label for compatibility, add composer for advanced features:

```python
# Current system (unchanged)
primary_behavior = manifold.classify(vector)

# New composer (opt-in)
if USE_MULTI_LABEL:
    activations = composer.classify_multi(vector)
    behavior_weights = composer.get_behavior_weights(activations)
    # Blend stats using weights
```

### Option 3: Hybrid Threshold System (Recommended)

Use single-label by default, but activate modifiers if close enough:

```python
def classify_hybrid(vector):
    # Primary: nearest prototype
    primary = min(distances, key=distances.get)

    # Modifiers: any behavior within threshold of primary
    primary_dist = distances[primary]
    modifiers = [
        name for name, dist in distances.items()
        if name != primary and dist < primary_dist + THRESHOLD
    ]

    return primary, modifiers
```

## 🔧 Tuning Recommendations

### Current Issues (as seen in tests)

- **Too many activations**: All behaviors get 10-20% weight
- **Weak differentiation**: Need higher threshold or stronger falloff

### Proposed Fixes

1. **Tighter Thresholds**:
   ```python
   THRESHOLD_STRONG = 0.6   # Only very close matches
   THRESHOLD_MEDIUM = 1.0   # Closer than current
   MIN_STRENGTH = 0.2       # Higher minimum (20%)
   ```

2. **Steeper Falloff**:
   ```python
   # Quadratic falloff instead of exponential
   strength = max(0, 1 - (distance / threshold)**2)
   ```

3. **Normalize by Prototype Spacing**:
   ```python
   # Scale threshold by average prototype separation
   avg_separation = compute_avg_prototype_distance()
   effective_threshold = THRESHOLD * avg_separation
   ```

## 📐 Manifold Theory Compatibility

### Is This Against Manifold Paradigm?

**NO!** This is actually MORE aligned with manifold theory:

1. **Manifolds allow overlap**: Behaviors are regions with fuzzy boundaries, not hard partitions
2. **Distance is continuous**: Close = strong influence, far = weak influence
3. **Multiple tangent spaces**: A point can have projections onto multiple submanifolds

### Voronoi vs. Fuzzy Regions

**Voronoi** (current): Discrete partitioning, hard boundaries
```
[Projectile Region] | [AOE Region] | [Heal Region]
        ^exact boundary
```

**Fuzzy** (proposed): Soft boundaries, gradual transitions
```
[Projectile ~~~~ blended zone ~~~~ AOE]
              ^spell here has both
```

## 🎮 Gameplay Implications

### Benefits

1. **Richer spell variety**: More unique combinations
2. **Smoother progression**: Adding elements gradually shifts behavior
3. **Emergent synergies**: Discover hybrid behaviors
4. **Better game feel**: No sudden behavior changes at prototype boundaries

### Challenges

1. **Complexity**: Players need to understand composability
2. **Balancing**: More combinations to tune
3. **UI**: Need to show multiple behaviors clearly

## 🚀 Implementation Plan

### Phase 1: Fix Fundamentals (Done!)

- ✅ Fix element polarities (Fire/Lightning = negative)
- ✅ Test current classification correctness
- ✅ Create multi-label composer prototype

### Phase 2: Tune Thresholds

- ⏸️ Adjust THRESHOLD values based on prototype spacing
- ⏸️ Test with all 9 elements, find sweet spot
- ⏸️ Validate that primary behaviors are correct

### Phase 3: Integration

- ⏸️ Add composer to interaction_engine.py (parallel to current system)
- ⏸️ Use weights to blend spell stats
- ⏸️ Update spell preview UI to show modifiers

### Phase 4: Polish

- ⏸️ Create composed behavior names dictionary
- ⏸️ Add visual indicators for hybrid spells
- ⏸️ Document all discovered compositions

## 📊 Test Cases for Validation

### Expected Behaviors

| Elements | Expected Primary | Expected Modifiers | Rationale |
|----------|------------------|-------------------|-----------|
| Fire | Projectile | None | Pure damage projectile |
| Fire x3 | Projectile | AOE | More fire = more explosive |
| Nature | Heal | None | Pure heal |
| Nature x2 | Heal | AOE | More healing = area effect |
| Fire + Ice | Projectile | AOE? | Steam explosion |
| Lightning | Beam | Chain | Instant chaining beam |
| Shadow x2 | Area Denial | Buff? | Defensive shadow field |

### Invalid Classifications to Avoid

❌ Fire → Heal (polarity mismatch)
❌ Nature → AOE (no explosion in healing)
❌ Ice → Beam (solid can't be instant)

## 💡 Alternative Approaches Considered

### Approach 1: Tag-Based (Rejected)

Use element tags to determine behavior (old system):

**Problem**: Hard-coded, not geometric, doesn't scale

### Approach 2: Neural Network (Overkill)

Train classifier on example spells:

**Problem**: Black box, hard to tune, requires training data

### Approach 3: Decision Tree (Too rigid)

if-else chains based on property thresholds:

**Problem**: Same as tag-based, loses geometric elegance

### Approach 4: Fuzzy Logic (Interesting!)

Use fuzzy membership functions for each behavior:

**Promising!** Similar to our distance-based approach but with explicit membership curves

## 🎯 Recommended Next Steps

1. **Test with fixed polarities** - Fire should now be Projectile
2. **Tune thresholds** - Find values that give 1-2 modifiers max
3. **Validate all element combinations** - Build reference table
4. **Integrate gradually** - Start with stat blending, then composed names
5. **Get player feedback** - Does multi-behavior feel good?

---

**Key Insight**: Multi-label classification via distance thresholds is **more aligned** with manifold theory than Voronoi partitioning. It allows smooth transitions and composable behaviors while maintaining geometric elegance.
