# Emergent Behavior vs Hardcoded Composition

## Design Principle

The magic system classifies spells using **weighted property blending**, not name-based dispatch. Spell names are cosmetic labels for the UI. The actual behavior — damage, area, speed, duration — emerges from mathematical formulas applied to the property vector, weighted by each behavior's activation strength.

## The Problem with Name-Based Dispatch

A hardcoded approach ties behavior to a name:

```python
if behavior_name == "explosive_projectile":
    damage = 200
    area = 10
    speed = 150
elif behavior_name == "area_heal":
    damage = -50
    area = 15
    speed = 0
```

This reintroduces if-else chains, requires manual coding for every combination, and prevents smooth transitions between behaviors.

## The Emergent Alternative

Stats are computed as weighted blends across all activated behaviors:

```python
weights = composer.get_behavior_weights(activations)
# e.g. {'projectile': 0.60, 'aoe': 0.40}

damage = sum(weights[b] * formulas.compute_damage(vector, b) for b in weights)
area   = sum(weights[b] * formulas.compute_area(vector, b)   for b in weights)
speed  = sum(weights[b] * formulas.compute_speed(vector, b)  for b in weights)
```

Each behavior's formula contributes proportionally to its activation strength. A spell that is 60% projectile and 40% AOE naturally inherits high speed from the projectile weight and large area from the AOE weight — without any code that explicitly handles the combination.

## How Multi-Label Classification Works

### Example: Fire + Fire + Fire

**Step 1 — Distance Computation**

The property vector is compared against every prototype in the manifold:

| Behavior | Distance | Activation Strength |
|---|---|---|
| Projectile | 1.324 | 0.33 |
| Beam | 1.540 | 0.28 |
| AOE | 1.698 | 0.24 |
| ... | ... | ... |

**Step 2 — Weight Normalization**

Strengths are normalized so they sum to 1.0:

| Behavior | Raw Strength | Normalized Weight |
|---|---|---|
| Projectile | 0.33 | 0.38 |
| Beam | 0.28 | 0.32 |
| AOE | 0.24 | 0.27 |
| Other | 0.03 | 0.03 |

**Step 3 — Stat Blending**

Each behavior's formula is computed independently against the property vector, then blended:

```
final_damage = 0.38 × damage(projectile) + 0.32 × damage(beam) + 0.27 × damage(aoe)
final_area   = 0.38 × area(projectile)   + 0.32 × area(beam)   + 0.27 × area(aoe)
final_speed  = 0.38 × speed(projectile)  + 0.32 × speed(beam)  + 0.27 × speed(aoe)
```

The result is a spell that naturally has medium-high speed (projectile influence), medium area (AOE influence), and medium-high damage (beam influence). No hardcoded values for the combination exist anywhere in the codebase.

## Spell Naming

Spell names are descriptive, not prescriptive. The name `projectile_aoe` simply lists which behaviors activated — it does not determine the spell's stats. The interaction engine can also generate procedural names from the final computed stats (e.g., "Explosive Projectile" when area > threshold and speed > threshold).

## Single-Label vs Multi-Label

| Approach | Mechanism | Transition | Composable |
|---|---|---|---|
| Single-label (Voronoi) | Nearest prototype wins | Discrete jump at boundary | No |
| Multi-label (weighted) | All prototypes contribute by distance | Smooth interpolation | Yes |

The system uses multi-label classification by default (`EMERGENT_BLENDING=1`). Single-label mode is available for debugging and comparison.

## What Is and Isn't Emergent

**Emergent:**
- Weighted stat blending from activated behaviors
- Distance-based activation strengths (geometry determines everything)
- Formula-computed stats per behavior (no hardcoded values)
- Procedural naming from final stats

**Designed (acceptable):**
- Behavior prototype positions — chosen by the designer, grounded in property theory
- Formula coefficients — tunable values that define how properties map to stats

**Avoided:**
- If-else chains for behavior determination
- Hardcoded stat values for specific element combinations
- Special cases like "if Fire+Water then steam explosion with these exact stats"
