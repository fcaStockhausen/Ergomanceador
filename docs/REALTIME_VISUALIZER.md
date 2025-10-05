# Real-Time Behavior Space Visualizer

## 🎯 What Is This?

A **dual-window system** that shows you exactly where your spells are in the 12D property manifold as you queue elements in real-time!

## 🚀 Quick Start

```bash
# Run game with visualizer
python main_with_visualizer.py
```

**Two windows will open:**
- **LEFT**: Main game (play normally)
- **RIGHT**: Behavior space visualizer (12D → 2D projection)

## 🎮 How It Works

1. **Play the game normally** in the left window
2. **Queue elements** (Q/E/R/F/U/O/P/;)
3. **Watch the yellow dot** in the right window move through 12D space!
4. **The dot shows where your spell is** relative to behavior prototypes

## 🎨 Visual Features (High-DPI)

### Improvements Over Previous Version:
- ✅ **2x higher resolution** - Retina/HiDPI displays fully supported
- ✅ **Smooth anti-aliased graphics** - No more jagged circles
- ✅ **Pulsing glow effects** - Current spell pulses to track it easily
- ✅ **Property bars** - See prototype properties as visual bars when hovering
- ✅ **Text shadows** - Better readability
- ✅ **Gradient backgrounds** - Professional look

### What You See:

**8 Colored Circles** = Behavior Prototypes
- 🔵 Light Blue = Projectile
- 🟠 Orange = Beam
- 🔴 Red = AOE
- 🟣 Purple = Chain
- 🔷 Cyan = Homing
- ⚫ Gray = Area Denial
- 🟢 Green = Heal
- 🟡 Yellow = Buff

**Yellow Pulsing Dot** = Your Current Spell
- Moves in real-time as you queue elements
- Shows element names above it
- Connects to nearest prototype with a line

**Hover Over Prototypes** = See Properties
- Thermal Flux, Temperature, Volatility, Chaos, Energy, Polarity
- Visual bars show property values (0-1 normalized)

## 📊 Reading the Visualization

### Distance = Classification

The **nearest prototype** to the yellow dot is what behavior your spell will become:

```
Fire: 🟡 (yellow dot appears near 🔵 Projectile)
→ Classified as Projectile

Fire + Water: 🟡 (yellow dot between 🟣 Chain and 🔴 AOE)
→ Classified as Chain (closer to it)

Nature: 🟡 (yellow dot ON 🟢 Heal)
→ Classified as Heal (perfect match)
```

### Gaps = Emergent Behaviors

**Empty space between prototypes** is where new behaviors can emerge!

If you find a spell that lands in a gap and feels unique, you can:
1. Note the element combination
2. Add a new prototype in that region
3. Name the new behavior
4. Now that combination always gives the new behavior!

## 🔍 Understanding the 12D → 2D Projection

The visualizer uses **PCA (Principal Component Analysis)** to compress 12 dimensions into 2D:

**12 Dimensions (Property Vector):**
1. Thermal Flux
2. Average Temperature
3. Temperature Differential
4. State Transition Energy
5. Phase Diversity
6. Density Gradient
7. Average Density
8. Volatility Index
9. Chaos Factor
10. Total Energy
11. Energy Density
12. Polarity Tension

**2 Dimensions (PCA):**
- PC1 (horizontal axis) = "Energy/Chaos" spectrum
- PC2 (vertical axis) = "Thermal/Polarity" spectrum

**Important:** The 2D projection is approximate! Distances in 2D don't perfectly match distances in 12D, but they're close enough for intuition.

## 🎯 Use Cases

### 1. **Spell Discovery**
Queue random element combos and see where they land. Look for interesting positions!

### 2. **Balance Tuning**
If spells feel wrong, check their position in the visualizer. Maybe the prototype needs adjustment.

### 3. **Behavior Gap Analysis**
Find large empty regions between prototypes. These are opportunities for new behaviors!

### 4. **Player Education**
Show players how the property-based system works geometrically instead of with hard-coded rules.

## 🛠️ Technical Details

### High-DPI Rendering

The visualizer renders at **2x internal resolution** then scales down smoothly:

```python
# Internal: 2400x1800
# Display: 1200x900
# Result: Crystal clear on Retina displays
```

### Real-Time Updates

The visualizer updates **instantly** when you queue elements:

```python
# In main game loop
def _update_visualizer(self):
    self.visualizer.update_current_spell(self.magic.active_elements)

# Called whenever:
# - Element queued
# - Element removed (backspace)
# - Queue cleared
```

### Performance

- **60 FPS** for both windows
- **No lag** - visualizer runs in same thread
- **Minimal overhead** - PCA computed once at startup

## 🎨 Customization

### Change Visualizer Size

Edit `main_with_visualizer.py`:

```python
self.visualizer = BehaviorSpaceVisualizer(
    width=1200,   # Change this
    height=900,   # And this
    high_dpi=True # Keep True for crisp graphics
)
```

### Disable High-DPI (If Performance Issues)

```python
self.visualizer = BehaviorSpaceVisualizer(
    width=1200,
    height=900,
    high_dpi=False  # Set to False
)
```

### Change Prototype Colors

Edit `magic/behavior_space_visualizer.py`:

```python
self.behavior_colors = {
    'projectile': (100, 200, 255),  # Change RGB values
    'beam': (255, 200, 100),
    # ... etc
}
```

## 📝 Controls Summary

**Game Window (Left):**
- WASD: Move
- IJKL: Aim
- Q/E/R/F: Fire/Water/Ice/Earth
- U/O/P/;: Nature/Arcane/Light/Shadow
- Space: Cast
- Backspace: Remove last element

**Visualizer Window (Right):**
- Mouse: Hover over prototypes for info
- (No keyboard controls - just visual)

## 🚀 Next Steps

### Short Term
- ✅ Visualizer works in real-time
- ⏸️ Test with all 9 elements
- ⏸️ Find gaps and document emergent behaviors

### Medium Term
- ⏸️ Add "trail" showing spell's path through space as you queue
- ⏸️ Show distance numbers to each prototype
- ⏸️ Click prototype to show example element combinations

### Long Term
- ⏸️ 3D visualization (12D → 3D with rotation)
- ⏸️ Save/load custom prototypes
- ⏸️ Export behavior space as JSON for balance tuning

## 🎓 Learning Resources

- [MANIFOLD_SYSTEMS.md](MANIFOLD_SYSTEMS.md) - Math behind the manifold
- [EMERGENT_BEHAVIORS.md](EMERGENT_BEHAVIORS.md) - How emergent behaviors work
- [SPACE_HOMOGENEITY.md](SPACE_HOMOGENEITY.md) - Prototype distribution analysis
- [VISUALIZATION_SUMMARY.md](VISUALIZATION_SUMMARY.md) - Complete visualization guide

---

**Built with ❤️ using differential geometry and real-time data visualization**
