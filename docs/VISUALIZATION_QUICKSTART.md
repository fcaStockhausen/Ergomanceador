# 🎨 Visualization & Particle System Quickstart

## What You Now Have

✅ **Behavior Space Visualizer** - See the 12D manifold as a 2D map
✅ **Particle System** - Visual effects for each spell behavior
✅ **Emergent Behavior Tools** - Discover new spell types geometrically

---

## 🚀 Quick Start

### 1. View the Behavior Space

See where all behavior prototypes are located in 12D space (projected to 2D):

```bash
python magic/behavior_space_visualizer.py
```

**Controls:**
- **SPACE**: Cycle through test spells (Fire, Fire+Water, Nature, etc.)
- **MOUSE HOVER**: See prototype properties
- **ESC**: Quit

**What you'll see:**
- **Colored circles** = Behavior prototypes (projectile, beam, AOE, etc.)
- **Yellow dot** = Current spell position
- **Lines** = Connections between prototypes
- **Gaps between circles** = Emergent behavior opportunities!

---

## 🔍 Understanding the Visualization

### Behavior Prototypes (Circles)

| Color | Behavior | Key Property |
|-------|----------|-------------|
| 🔵 Light Blue | Projectile | Moderate energy, low volatility |
| 🟠 Orange | Beam | High energy density, instant |
| 🔴 Red | AOE | High volatility, explosive |
| 🟣 Purple | Chain | High thermal flux, branching |
| 🔷 Cyan | Homing | Moderate chaos, tracking |
| ⚪ Gray | Area Denial | Low energy, persistent |
| 🟢 Green | Heal | High positive polarity |
| 🟡 Yellow | Buff | Low chaos, defensive |

### Current Spell (Yellow Dot)

The yellow dot shows where your queued elements land in the 12D property space. Watch it move as you add elements!

**Examples:**
- **Fire** → Lands on Projectile (single element, moderate energy)
- **Fire + Water** → Moves toward Chain (high thermal flux from temperature diff)
- **Nature** → Lands on Heal (high positive polarity)

### Emergent Regions (Gaps)

Any space **between** prototypes is an emergent behavior opportunity:

```
    Projectile ●─────────────● AOE
                    ↑
                    │
              What happens here?
              (Maybe a "Scatter Shot"?)
```

---

## 💥 Adding Particle Effects to Spells

### Step 1: Check Current Projectile Rendering

Your game currently renders spells in [combat/projectile.py](combat/projectile.py). Let's add particles!

### Step 2: Read the Current Projectile Code

<function_calls>
<invoke name="Read">
<parameter name="file_path">/Users/fcaraneda/Documents/8_Proyectos_4/Karaokeficador/combat/projectile.py