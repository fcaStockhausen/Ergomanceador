# Integration Guide: New Manifold Systems → Existing Game

## 🎯 Current Status

**What exists:**
- ✅ **Old System**: `magic/interaction_engine.py` (if-else based)
- ✅ **New System**: `magic/behavior_manifold.py` (geometric manifold)
- ❌ **Integration**: NOT YET DONE

**The new systems are tested and working, but the game still uses the old code.**

---

## 🚀 Integration Options

### **Option 1: Side-by-Side Testing** (Recommended First Step)

Compare old vs new without breaking anything:

```python
# In core/game.py or wherever spells are cast

# OLD system (existing)
old_spell = self.magic_system.generate_spell()

# NEW system (add this)
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
from magic.spell_formulas import SpellFormulas

vector = PropertyVectorComputer.compute(
    [self.magic_system.elements[name] for name in self.magic_system.active_elements]
)
manifold = BehaviorManifold()
formulas = SpellFormulas()

new_behavior = manifold.classify(vector)
new_damage = formulas.compute_damage(vector, new_behavior)
new_area = formulas.compute_area(vector, new_behavior)

# Compare
print(f"OLD: {old_spell['behavior']}, DMG={old_spell['damage']}")
print(f"NEW: {new_behavior}, DMG={new_damage}")
```

### **Option 2: Full Replacement** (When confident)

Replace `magic/interaction_engine.py` with new system:

**Step 1:** Backup old engine
```bash
cp magic/interaction_engine.py magic/interaction_engine_OLD.py
```

**Step 2:** Create new wrapper
```python
# magic/interaction_engine.py (REWRITE)

from magic.element_loader import load_elements_from_json
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
from magic.spell_formulas import SpellFormulas


class InteractionEngine:
    """
    NEW VERSION: Uses manifold-based classification.
    Backwards compatible with old API.
    """

    def __init__(self):
        self.elements = load_elements_from_json()
        self.manifold = BehaviorManifold()
        self.formulas = SpellFormulas()

    def compute_interaction(self, element_names):
        """Generate spell effect (SAME API as before)"""
        if not element_names:
            return None

        # Get element objects
        elems = [self.elements[name] for name in element_names
                 if name in self.elements]
        if not elems:
            return None

        # NEW: Use manifold classification
        vector = PropertyVectorComputer.compute(elems)
        behavior = self.manifold.classify(vector)

        # NEW: Use formula-based stats
        damage = self.formulas.compute_damage(vector, behavior)
        speed = self.formulas.compute_speed(vector, behavior)
        area = self.formulas.compute_area(vector, behavior)
        duration = self.formulas.compute_duration(vector, behavior)
        mana_cost = self.formulas.compute_mana_cost(vector, behavior)

        # Generate name (keep old logic for now)
        spell_name = self._generate_name(elems, behavior, vector.temp_differential)

        # Blend colors (keep old logic)
        spell_color = self._blend_colors(elems)

        # Return same format as before
        return {
            'name': spell_name,
            'behavior': behavior,
            'damage': damage,
            'speed': speed,
            'area': area,
            'duration': duration,
            'mana_cost': mana_cost,
            'color': spell_color,
            'effects': list(elems[0].tags),  # Simplified
            'elements': element_names,
            'properties': {
                'temperature': vector.avg_temperature,
                'energy': vector.total_energy,
                'temp_differential': vector.temp_differential,
                'density': vector.avg_density,
                'volatility': vector.volatility_index,
            }
        }

    def _generate_name(self, elems, behavior, temp_diff):
        # Keep old spell naming logic
        # (or copy from old interaction_engine.py)
        return f"{elems[0].name.title()} {behavior.title()}"

    def _blend_colors(self, elems):
        # Keep old color blending
        r = sum(e.color[0] for e in elems) // len(elems)
        g = sum(e.color[1] for e in elems) // len(elems)
        b = sum(e.color[2] for e in elems) // len(elems)
        return (r, g, b)
```

**Step 3:** Test
```bash
python main.py
# Play and verify spells work
```

---

## 🌐 Spatial Manifold Integration

The spatial manifold is for the **world topology**, not magic.

### **Option 1: Keep Flat (Current)**

Do nothing - current isometric rendering works fine.

### **Option 2: Enable Toroidal World**

```python
# In core/game.py

from world.spatial_manifold import SpatialManifold, Topology, ManifoldPoint

class Game:
    def __init__(self):
        # ... existing code ...

        # NEW: Create world manifold
        self.world = SpatialManifold(
            topology=Topology.TOROIDAL,  # Wrap-around!
            width=GRID_SIZE,
            height=GRID_SIZE
        )

    def update(self):
        # ... existing code ...

        # NEW: Wrap entities when they leave bounds
        player_pos = ManifoldPoint(self.player.cart_x, self.player.cart_y)
        wrapped = self.world.wrap_point(player_pos)
        self.player.cart_x = wrapped.u
        self.player.cart_y = wrapped.v
```

### **Option 3: Use Geodesics for Projectiles**

```python
# In rendering/effects/projectile.py

def update(self, dt):
    # OLD: Straight line movement
    # self.cart_x += self.velocity_x * dt
    # self.cart_y += self.velocity_y * dt

    # NEW: Follow geodesic
    from world.spatial_manifold import ManifoldPoint

    start = ManifoldPoint(self.cart_x, self.cart_y)
    end = ManifoldPoint(self.target_x, self.target_y)

    path = self.world.geodesic(start, end, num_points=100)
    current_step = min(int(self.age * 10), len(path)-1)

    self.cart_x = path[current_step].u
    self.cart_y = path[current_step].v
```

---

## 📝 Step-by-Step Integration Plan

### **Week 1: Test Without Breaking**

1. ✅ Run `python test_manifolds_interactive.py` (verify it works)
2. ✅ Run tests: `python -m pytest tests/unit/test_behavior_manifold.py -v`
3. ⬜ Add side-by-side comparison in `core/game.py` (see Option 1)
4. ⬜ Play game, compare old vs new classifications in console
5. ⬜ Tune prototypes if needed

### **Week 2: Replace Magic Engine**

1. ⬜ Backup `magic/interaction_engine.py`
2. ⬜ Implement new wrapper (see Option 2)
3. ⬜ Test game thoroughly
4. ⬜ Fix any edge cases
5. ⬜ Commit changes

### **Week 3: Optional - Spatial Manifold**

1. ⬜ Add `SpatialManifold` to `core/game.py`
2. ⬜ Test toroidal wrapping
3. ⬜ Update projectile movement to use geodesics
4. ⬜ Test, tune, commit

### **Week 4: Polish & Balance**

1. ⬜ Load coefficients from JSON
2. ⬜ Tune behavior prototypes based on playtesting
3. ⬜ Update documentation
4. ⬜ Prepare for Godot port

---

## ⚠️ Breaking Changes

If you replace `interaction_engine.py`, these may break:

1. **Spell naming** - New system has different procedural names
2. **Behavior classification** - Some spells may change behavior
3. **Damage values** - Formula-based stats vs hard-coded
4. **Tag-based logic** - Old code checked tags directly

**Solution:** Keep spell naming and color blending from old code, only replace classification + stat computation.

---

## 🧪 Quick Integration Test

```bash
# Add this to main.py at the top of Game class

from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold

def test_new_system(self):
    """Quick test of new manifold system"""
    # Get current active elements
    if not self.magic_system.active_elements:
        return

    element_list = [self.magic_system.elements[name]
                    for name in self.magic_system.active_elements]

    # Compute with new system
    vector = PropertyVectorComputer.compute(element_list)
    manifold = BehaviorManifold()
    behavior = manifold.classify(vector)

    print(f"✨ NEW SYSTEM: {self.magic_system.active_elements} → {behavior}")
    print(f"   Thermal flux: {vector.thermal_flux:.2f}")
    print(f"   Volatility: {vector.volatility_index:.2f}")

# Call in update loop
if self.magic_system.active_elements:
    self.test_new_system()
```

---

## 📚 Files to Modify

| File | Change | Difficulty |
|------|--------|------------|
| `magic/interaction_engine.py` | Replace with manifold wrapper | Medium |
| `core/game.py` | Add side-by-side testing | Easy |
| `rendering/effects/projectile.py` | Optional geodesic movement | Hard |
| `magic/spell_formulas.py` | Load coefficients from JSON | Easy |

---

**Next Step:** Run side-by-side comparison (Option 1) to see the difference without breaking anything!
