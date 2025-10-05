# Designer Mode: In-Game Behavior Toolkit

## 🎨 What is Designer Mode?

Designer Mode is an **in-game toolkit** for discovering, defining, and tuning spell behaviors in the 12-dimensional property manifold. No Python coding required!

**You can:**
- ✅ Experiment with 1-6 element combinations (keyboard supports chords!)
- ✅ See your spell's position in 12D behavior space
- ✅ Analyze distances to all behavior prototypes
- ✅ Create new prototypes by tagging interesting spells
- ✅ Tune existing prototypes with visual sliders
- ✅ Validate changes with automatic checks
- ✅ Save custom prototypes to JSON

---

## 🚀 Getting Started

### Launching Designer Mode

**Option 1: From Menu**
```bash
python main.py
# Select "Designer Mode" from the menu
```

**Option 2: Direct Launch**
```bash
python main.py --designer
```

**Option 3: From Game (F1 Toggle)**
```bash
python main.py --play
# Press F1 during gameplay to enter Designer Mode
# Press F1 again to return to game
```

---

## 🎮 Interface Overview

Designer Mode has **two main panels**:

### Left Panel: 🧪 Spell Testing Lab
- **Step 1: Queue Elements** - Queue 1-6 elements to create spells
- **Step 2: Property Vector** - View the 12D property vector
- **Step 3: Distance Analysis** - See distances to all prototypes
- **Step 4: Decision Helper** - Get recommendations (create new / tune existing)

### Right Panel: ⚙️ Prototype Editor
- **Prototype List** - Select from core + custom prototypes
- **12D Sliders** - Visual editing of property vectors
- **Actions** - Create, update, delete, validate prototypes
- **Validation** - Live warnings about prototype spacing

---

## 🔑 Keyboard Controls

### Global (Any Mode)
- **F1** - Toggle Designer Mode ON/OFF
- **ESC** - Exit Designer Mode (return to game/menu)

### Testing Lab (Left Panel)
- **Q/E/R/F** - Queue Fire/Water/Ice/Earth
- **U/O/P/;** - Queue Nature/Arcane/Light/Shadow
- **BACKSPACE** - Remove last element from queue
- **F2** - Quick-tag current spell as new prototype

### Prototype Editor (Right Panel)
- **TAB** - Switch between Testing Lab and Editor
- **U** - Update selected prototype (save changes)
- **N** - Create new prototype from current sliders
- **D** - Delete selected custom prototype
- **V** - Validate current prototype (check distances)
- **F4** - Save all custom prototypes to JSON

### Mouse Controls
- **Click** on prototype names to select them
- **Drag** sliders to edit property values

---

## 📋 Workflow: Following the Designer Guide

Designer Mode implements the workflow from [DESIGNER_GUIDE_BEHAVIOR_TUNING.md](DESIGNER_GUIDE_BEHAVIOR_TUNING.md):

### 1. Play and Experiment
Queue different element combinations (1-6 elements):
```
Fire + Fire + Fire        → Strong projectile
Shadow + Ice + Ice        → Freezing cloud
Lightning + Nature x2     → Chain heal?
Fire + Shadow + Shadow    → Draining flame?
```

### 2. Analyze Properties
The Testing Lab shows:
- **12D Property Vector** - Normalized values (0-1 range, polarity -1 to 1)
- **Distance to ALL Prototypes** - Sorted by nearest
- **Color Coding:**
  - 🟢 Green (<0.8): Strong match
  - 🟡 Yellow (0.8-1.2): Medium match
  - 🟠 Orange (1.2-1.6): Weak match
  - ⚪ Gray (>1.6): No match

### 3. Decision Helper
Based on distances, you'll see one of:

**A) "WELL CLASSIFIED"** (distance < 0.8)
- Spell strongly matches existing behavior
- No action needed!

**B) "CREATE NEW PROTOTYPE"** (distance > 1.2)
- Spell is far from all prototypes
- Press **F2** to tag it as new prototype
- Or switch to Editor (TAB) and press **N**

**C) "CONSIDER TUNING"** (distance 0.8-1.2)
- Spell is moderately close to a prototype
- Switch to Editor (TAB) and select the prototype
- Adjust sliders to move it closer

### 4. Create New Prototype

**Method 1: Quick Tag (F2)**
1. Queue your spell (e.g., `Fire + Shadow + Shadow`)
2. Press **F2**
3. Prototype is auto-named and saved

**Method 2: Manual Create (Editor)**
1. Queue your spell
2. Switch to Editor (TAB)
3. Adjust sliders to fine-tune the 12D vector
4. Press **N** to create
5. Press **F4** to save to JSON

### 5. Tune Existing Prototype

1. Switch to Editor (TAB)
2. Click on a prototype name (custom prototypes only)
3. Adjust sliders to change property values
4. Press **V** to validate (check distances to other prototypes)
5. Press **U** to update
6. Press **F4** to save

**Warning:** Core prototypes (like `projectile`, `heal`) are **read-only**. You can only edit custom prototypes.

---

## 🎯 Understanding the 12D Property Space

Each spell is a point in **12-dimensional property space**:

| Dimension | Range | Meaning |
|-----------|-------|---------|
| **Thermal Flux** | 0-1 | Energy transfer rate (0=single element, 1=extreme mixing) |
| **Avg Temperature** | 0-1 | Average heat (0=cold, 1=2000K) |
| **Temp Differential** | 0-1 | Temperature variation (0=uniform, 1=extreme gradient) |
| **State Transition** | 0-1 | Phase change energy (0=quick, 1=persistent) |
| **Phase Diversity** | 0-1 | State variety (0=pure, 1=multi-state chaos) |
| **Density Gradient** | 0-1 | Density variation (0=uniform, 1=high gradient) |
| **Avg Density** | 0-1 | Average density (0=gas/beam, 1=solid/earth) |
| **Volatility** | 0-1 | Explosive tendency (0=stable, 1=explosive) |
| **Chaos Factor** | 0-1 | Randomness (0=controlled, 1=chaotic) |
| **Total Energy** | 0-1 | Combined energy (0=weak, 1=400+) |
| **Energy Density** | 0-1 | Concentrated power (0=spread, 1=concentrated) |
| **Polarity** | -1 to +1 | Effect type (-1=damage, 0=neutral, +1=heal) |

**Normalized to [0, 1]** (except polarity) for homogeneous distance calculation.

---

## ⚠️ Validation Warnings

When you press **V** (validate), you'll see:

### Errors (Red ❌)
- **Must be 12-dimensional** - Vector is wrong size
- Prevents saving until fixed

### Warnings (Yellow ⚠️)
- **Some values outside typical range** - Values < -1 or > 1.5
- **Very close to '[prototype]'** - Distance < 0.3 (behaviors will overlap)
- **Close to '[prototype]'** - Distance < 0.5 (may cause confusion)

**Best Practice:** Keep prototypes at least **0.4 distance** apart.

---

## 💾 Saving and Loading

### Automatic Saving
- Custom prototypes are saved to `data/custom_prototypes.json`
- Press **F4** to save manually
- Auto-saves when exiting Designer Mode

### File Format
```json
{
  "prototypes": [
    {
      "name": "chain_heal",
      "prototype": [0.50, 0.40, 0.30, 0.35, 0.40, 0.35, 0.25, 0.40, 0.45, 0.45, 0.50, 0.67],
      "threshold": 1.0,
      "is_custom": true
    }
  ]
}
```

### Resetting
To reset all custom prototypes:
1. Delete `data/custom_prototypes.json`
2. Or manually clear the `prototypes` array

---

## 📊 Example Workflow: Adding "Chain Heal"

### Discovery
Playing the game, you notice:
```
Lightning + Nature + Nature feels like it should chain-heal allies
But it classifies as just "heal" (no chaining)
```

### Analysis (Testing Lab)
1. Queue `Lightning + Nature + Nature`
2. Check distances:
   ```
   heal:  0.85  ← Closest (makes sense)
   chain: 1.65  ← Too far! (should be closer)
   ```
3. Decision Helper says: **"CONSIDER TUNING 'HEAL'"**

### But wait... you want a NEW behavior!
Since this is a distinct mechanic (chaining heal), create new prototype:

### Create Prototype (Editor)
1. Switch to Editor (TAB)
2. Adjust sliders based on spell properties:
   - Thermal Flux: 0.50 (moderate - lightning + nature mix)
   - Polarity: 0.67 (high positive - healing!)
   - Chaos: 0.45 (moderate - chain-like)
   - Others: balanced
3. Press **N** to create → Auto-named `custom_1`
4. Press **F4** to save

### Validate
1. Queue `Lightning + Nature + Nature` again
2. Now distances show:
   ```
   custom_1: 0.68  ← NOW CLOSEST! ✓
   heal: 0.85
   chain: 1.20
   ```
3. Perfect! Spell now classifies as `custom_1`

### Rename (Manual Edit)
1. Open `data/custom_prototypes.json`
2. Change `"name": "custom_1"` → `"name": "chain_heal"`
3. Reload game

---

## 🎓 Tips and Best Practices

### For Finding New Behaviors
1. **Use 6-element chords** - Keyboard supports simultaneous presses!
   - Try: `Fire + Fire + Fire + Shadow + Shadow + Shadow`
2. **Look for gaps** - Large distances (>1.2) to all prototypes
3. **Test edge cases** - All Fire? All Nature? Mixed opposites?
4. **Follow your intuition** - If it "feels" different, it probably is!

### For Tuning Prototypes
1. **Start with the spell** - Queue it, then adjust sliders toward its values
2. **Validate often** - Press **V** after each change
3. **Watch for clustering** - Keep prototypes >0.4 apart
4. **Test in game** - Use **F1** to toggle back to game and try the spell

### For Collaboration
1. **Share `custom_prototypes.json`** - Send to teammates
2. **Document your prototypes** - Add comments in JSON (manual edit)
3. **Test systematically** - Use distance analyzer for verification

---

## 🐛 Troubleshooting

### "Cannot edit prototype 'projectile'"
- Core prototypes are read-only
- Create a custom variant instead

### "Prototype already exists"
- Choose a different name
- Or delete the existing custom prototype first (press **D**)

### "Values outside typical range"
- Keep most values in [0, 1]
- Polarity can be [-1, 1]
- Warning only - still saveable

### Sliders not responding
- Make sure you're in Editor panel (TAB to switch)
- Click and drag on the slider bar

### Custom prototypes not loading
- Check `data/custom_prototypes.json` syntax (valid JSON)
- Look for errors in console log

---

## 🔗 Related Documentation

- [DESIGNER_GUIDE_BEHAVIOR_TUNING.md](DESIGNER_GUIDE_BEHAVIOR_TUNING.md) - Detailed tuning guide
- [MANIFOLD_SYSTEMS.md](MANIFOLD_SYSTEMS.md) - Core manifold concepts
- [EMERGENT_VS_HARDCODED.md](EMERGENT_VS_HARDCODED.md) - Philosophy explanation
- [SPACE_HOMOGENEITY.md](SPACE_HOMOGENEITY.md) - Why dimensions are normalized

---

## 🎉 Quick Reference Card

```
═══════════════════════════════════════════════════════════════
  DESIGNER MODE QUICK REFERENCE
═══════════════════════════════════════════════════════════════

LAUNCH:          python main.py → Select "Designer Mode"
TOGGLE:          F1 (from game)
EXIT:            ESC or F1

TESTING LAB (Left Panel):
  Queue:         Q/E/R/F/U/O/P/; (1-6 elements)
  Clear:         BACKSPACE
  Quick Tag:     F2

PROTOTYPE EDITOR (Right Panel):
  Switch:        TAB
  Select:        Click prototype name
  Update:        U
  Create:        N
  Delete:        D (custom only)
  Validate:      V
  Save All:      F4

WORKFLOW:
  1. Queue elements
  2. Check distances
  3. Follow Decision Helper
  4. Create or Tune
  5. Validate (V)
  6. Save (F4)

═══════════════════════════════════════════════════════════════
```

---

**Happy Behavior Hunting! 🎯**
