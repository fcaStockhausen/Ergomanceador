# 🎮 Real-Time Behavior Manifold Visualizer - Quick Start

## ✨ What You Have Now

A **real-time in-game HUD panel** that shows your spells moving through 12D property space as you queue elements!

## 🚀 How to Use

```bash
# Run game with manifold HUD panel
python main_manifold_hud.py
```

The game will launch with a **manifold panel in the top-right corner** showing:
- **8 colored circles** = Behavior prototypes (projectile, beam, AOE, etc.)
- **Yellow pulsing dot** = Your current spell in 12D space
- **Blue line** = Connection to nearest behavior
- **Element queue** = Abbreviated element names (F+W+I = Fire+Water+Ice)

## 🎯 Try It Out

1. **Queue some elements** (Q/E/R/F keys)
2. **Watch the yellow dot appear** in the manifold panel
3. **Queue more elements** and watch it move!
4. **See which behavior it's classified as** (shown at bottom of panel)

### Examples:

| Queue | Yellow Dot Position | Classified As |
|-------|---------------------|---------------|
| Fire (Q) | Near blue circle | → PROJECTILE |
| Fire + Water | Between purple/red | → CHAIN or AOE |
| Nature (U) | On green circle | → HEAL |
| Fire + Fire + Fire | Near red circle | → AOE |

## 📊 Understanding the Visualization

### PCA Projection (12D → 2D)

The 12 property dimensions are compressed into 2D using Principal Component Analysis:

**Horizontal axis (PC1)** ≈ Energy/Volatility spectrum
- Left = Low energy, stable
- Right = High energy, chaotic

**Vertical axis (PC2)** ≈ Thermal/Polarity spectrum
- Top = Hot, destructive
- Bottom = Cold, defensive

### Behavior Circles

Each colored circle represents a **behavior prototype** in the 12D space:

- 🔵 **PROJ** (Light Blue) - Standard projectile (balanced properties)
- 🟠 **BEAM** (Orange) - Instant beam (high energy density)
- 🔴 **AOE** (Red) - Area explosion (high volatility)
- 🟣 **CHAI** (Purple) - Chain lightning (high thermal flux)
- 🔷 **HOMI** (Cyan) - Homing missile (moderate chaos)
- ⚫ **AREA** (Gray) - Area denial (low volatility, persistent)
- 🟢 **HEAL** (Green) - Healing (very high positive polarity)
- 🟡 **BUFF** (Yellow) - Buff/shield (low chaos, defensive)

### Classification

Your spell is classified as whichever prototype it's **geometrically closest** to in 12D space!

## 🎨 Features

### High-Quality Rendering
- ✅ Anti-aliased lines (smooth Voronoi connections)
- ✅ Pulsing glow effect on current spell
- ✅ Clean panel design with dark background
- ✅ Abbreviated labels to save space

### Real-Time Updates
- ✅ Updates instantly when you queue/remove elements
- ✅ Clears when you cast a spell
- ✅ Shows classified behavior at bottom

### Minimal Performance Impact
- PCA computed once at startup
- Only updates when element queue changes
- No lag or frame drops

## 🔍 Finding Emergent Behaviors

### Look for Gaps!

Empty spaces between prototypes are where **new behaviors** can emerge:

1. **Queue random element combinations**
2. **Look for dots that land far from all prototypes**
3. **Note the element combination**
4. **Does it feel like a unique behavior?**
5. **If yes, add a new prototype there!**

### Example Discovery Process:

```
Test: Shadow + Shadow + Ice
→ Dot lands between AREA_DENIAL and BUFF (but closer to neither)
→ Feels like a "slow field" effect
→ Add new prototype: "SLOW" at that position
→ Now Shadow+Shadow+Ice always gives SLOW behavior!
```

## 🛠️ Customization

### Disable Manifold HUD

Just run the normal game:
```bash
python main.py
```

The manifold panel only appears when launched via `main_manifold_hud.py` or when `DEBUG_MODE=True`.

### Change Panel Position

Edit `core/game.py` line ~90:

```python
panel_x = SCREEN_WIDTH - panel_width - 10  # Top-right
panel_y = 10

# Move to top-left:
panel_x = 10
panel_y = 10

# Move to bottom-right:
panel_x = SCREEN_WIDTH - panel_width - 10
panel_y = SCREEN_HEIGHT - panel_height - 10
```

### Change Panel Size

Edit `core/game.py` line ~88:

```python
panel_width = 320  # Make wider
panel_height = 280  # Make taller
```

## 📝 Controls

**Game Controls (same as normal):**
- **WASD**: Move player
- **IJKL**: Aim target
- **Q/E/R/F**: Fire/Water/Ice/Earth
- **U/O/P/;**: Nature/Arcane/Light/Shadow
- **Space**: Cast spell
- **Backspace**: Remove last element
- **ESC**: Clear queue (double-press to quit)

**Manifold Panel (automatic):**
- Updates when you queue elements
- Clears when you cast
- No manual controls needed!

## 🚀 Advanced Features

### Standalone Visualizer (Testing)

For testing without the game:

```bash
python magic/behavior_space_visualizer.py
```

This opens a **large high-DPI window** (1200x900) with:
- Same manifold visualization
- SPACE to cycle test spells
- Mouse hover for prototype properties
- Higher resolution for screenshots

### Integration with Other Systems

The manifold panel can be integrated anywhere:

```python
from rendering.ui.manifold_panel import ManifoldPanel

# Create panel
panel = ManifoldPanel(x=10, y=10, width=400, height=300)

# Update with element queue (list of element names)
panel.update_current_spell(['fire', 'water'])

# Draw to screen
panel.draw(screen)
```

## 📚 Learn More

- [MANIFOLD_SYSTEMS.md](MANIFOLD_SYSTEMS.md) - Math behind the system
- [EMERGENT_BEHAVIORS.md](EMERGENT_BEHAVIORS.md) - How to discover new behaviors
- [VISUALIZATION_SUMMARY.md](VISUALIZATION_SUMMARY.md) - Complete visualization guide
- [REALTIME_VISUALIZER.md](REALTIME_VISUALIZER.md) - Technical details

## 🎯 Next Steps

1. ✅ Play with the manifold HUD
2. ⏸️ Try all element combinations
3. ⏸️ Find gaps in the behavior space
4. ⏸️ Document emergent behaviors you discover
5. ⏸️ Add new prototypes for unique spell types

---

**Built with ❤️ using differential geometry and real-time visualization**

Now you can **see** the magic system's geometric structure while you play!
