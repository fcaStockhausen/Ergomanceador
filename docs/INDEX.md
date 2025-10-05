# Karaokeficador Documentation

**Property-Based Magic System with Manifold Classification**

---

## 📚 Table of Contents

### Getting Started

1. **[Designer Mode Guide](DESIGNER_MODE_GUIDE.md)** ⭐ IN-GAME TOOLKIT - **START HERE**
   - Complete in-game behavior design toolkit
   - No coding required - use F1 to launch
   - Create, test, and tune prototypes entirely in-game
   - Supports 1-6 element combinations (keyboard chords!)

2. **[Quick Start - Manifold HUD](QUICKSTART_MANIFOLD.md)**
   - Run the game with real-time behavior visualization
   - See spells move through 12D property space
   - 5-minute intro to the system

3. **[Quick Start - Testing Framework](QUICKSTART_TESTING.md)**
   - TAS testing system overview
   - Running and creating tests

### Core Concepts

4. **[Manifold Systems Overview](MANIFOLD_SYSTEMS.md)** ⭐ CORE CONCEPTS
   - What is the manifold-based magic system?
   - Property vectors (12D space)
   - Behavior classification
   - Spatial manifolds
   - Why this architecture?

5. **[Emergent vs Hardcoded Behavior](EMERGENT_VS_HARDCODED.md)** ⭐ PHILOSOPHY
   - What makes behavior truly emergent?
   - Weighted stat blending
   - Why names are just labels
   - The geometry of magic

6. **[Emergent Behaviors Guide](EMERGENT_BEHAVIORS.md)**
   - How behaviors emerge from properties
   - Finding gaps in behavior space
   - Particle system integration
   - Discovery workflow

### Behavior Tuning & Design

7. **[Designer Guide - Behavior Tuning](DESIGNER_GUIDE_BEHAVIOR_TUNING.md)** ⭐ DETAILED WORKFLOW
   - Step-by-step guide to finding new behaviors
   - Tuning existing prototypes
   - Adding new prototypes
   - Testing and validation
   - Advanced reference (complements Designer Mode)

8. **[Behavior Composition System](BEHAVIOR_COMPOSITION.md)**
   - Multi-label classification
   - Distance thresholds
   - Composable behaviors
   - Integration strategies

9. **[Space Homogeneity Analysis](SPACE_HOMOGENEITY.md)**
   - Prototype spacing
   - Balance validation
   - Distance distributions

### Visualization & Tools

10. **[Real-Time Visualizer](REALTIME_VISUALIZER.md)**
    - In-game manifold HUD
    - Standalone high-DPI visualizer
    - Tracking spells in 12D space
    - Customization options

11. **[Visualization Summary](VISUALIZATION_SUMMARY.md)**
    - Complete visualization guide
    - Particle system overview
    - File structure

12. **[Visualization Quick Start](VISUALIZATION_QUICKSTART.md)**
    - Running visualizers
    - Interpreting the display
    - Basic usage

### Integration & Development

13. **[Integration Guide](INTEGRATION_GUIDE.md)**
    - Replacing old interaction engine
    - Side-by-side testing
    - Spatial manifold integration
    - Migration steps

14. **[Integration Summary](INTEGRATION_SUMMARY.md)**
    - What's been created
    - Current status
    - Next steps

15. **[Particle Integration](PARTICLE_INTEGRATION.md)**
    - Adding particles to spells
    - Behavior-specific effects
    - Step-by-step integration

### Testing

16. **[Testing Framework](TESTING.md)**
    - TAS system
    - Unit tests
    - Manifold tests
    - Running tests

---

## 🎯 Reading Paths

### For Game Designers (No Coding Required!)

Want to create and tune spell behaviors **entirely in-game**?

1. ⭐ **[Designer Mode Guide](DESIGNER_MODE_GUIDE.md)** - In-game toolkit (Press F1!)
2. [Manifold Systems Overview](MANIFOLD_SYSTEMS.md) - Understand the 12D space
3. [Designer Guide - Behavior Tuning](DESIGNER_GUIDE_BEHAVIOR_TUNING.md) - Advanced workflow
4. [Real-Time Visualizer](REALTIME_VISUALIZER.md) - See it in action
5. [Behavior Composition](BEHAVIOR_COMPOSITION.md) - Multi-label concepts

### For Developers

Want to understand the code architecture?

1. [Manifold Systems Overview](MANIFOLD_SYSTEMS.md) - Core architecture
2. [Emergent vs Hardcoded](EMERGENT_VS_HARDCODED.md) - Design philosophy
3. [Integration Guide](INTEGRATION_GUIDE.md) - How it's integrated
4. [Testing Framework](TESTING.md) - How to test

### For Players

Want to understand how magic works?

1. [Quick Start - Manifold HUD](QUICKSTART_MANIFOLD.md) - Try it yourself
2. [Emergent Behaviors Guide](EMERGENT_BEHAVIORS.md) - Discover combos
3. [Real-Time Visualizer](REALTIME_VISUALIZER.md) - Watch the magic happen

---

## 📖 Documentation Structure

```
docs/
├── INDEX.md (this file)
│
├── Getting Started
│   ├── QUICKSTART_MANIFOLD.md
│   └── QUICKSTART_TESTING.md
│
├── Core Concepts
│   ├── MANIFOLD_SYSTEMS.md
│   ├── EMERGENT_VS_HARDCODED.md
│   └── EMERGENT_BEHAVIORS.md
│
├── Design & Tuning
│   ├── DESIGNER_GUIDE_BEHAVIOR_TUNING.md
│   ├── BEHAVIOR_COMPOSITION.md
│   └── SPACE_HOMOGENEITY.md
│
├── Visualization
│   ├── REALTIME_VISUALIZER.md
│   ├── VISUALIZATION_SUMMARY.md
│   └── VISUALIZATION_QUICKSTART.md
│
├── Integration
│   ├── INTEGRATION_GUIDE.md
│   ├── INTEGRATION_SUMMARY.md
│   └── PARTICLE_INTEGRATION.md
│
└── Testing
    └── TESTING.md
```

---

## 🔑 Key Concepts

### Property Vector (12D)

Every spell is represented as a point in 12-dimensional property space:

- Thermal properties (flux, temperature, differential)
- State/phase properties (transition energy, diversity)
- Density properties (gradient, average)
- Volatility/chaos properties
- Energy properties (total, density)
- Polarity (healing vs damaging)

### Behavior Manifold

The 12D property space is partitioned into behavior regions (prototypes).
Spells are classified by finding the **geometrically nearest** prototype.

### Emergent Behavior

Behaviors aren't hardcoded! They emerge from:
1. Element properties → Property vector
2. Property vector → Distances to prototypes
3. Distances → Weighted stat blending
4. Weighted stats → Natural spell behavior

### Multi-Label Classification

Instead of "nearest wins", multiple behaviors can activate based on distance:
- Distance < 0.8: Strong activation
- Distance < 1.2: Medium activation
- Result: Blended behavior (e.g., projectile + AOE = explosive projectile)

---

## 🚀 Quick Commands

```bash
# Run game (normal)
python main.py

# Run game with manifold HUD panel
python main.py --manifold-hud

# Standalone visualizer (high-DPI)
python magic/behavior_space_visualizer.py

# Analyze spell distances
python test_spell_distances.py

# Test emergent blending
python test_emergent_blending.py

# Run tests
python -m pytest tests/unit/test_behavior_manifold.py -v
```

---

## 📝 Contributing to Documentation

When adding new documentation:

1. Choose appropriate section (Getting Started, Core Concepts, etc.)
2. Add entry to this INDEX.md
3. Update relevant reading paths
4. Cross-reference related docs
5. Keep CLAUDE.md and README.md in sync

---

## 🎓 External Resources

- **Riemannian Geometry**: Understanding manifolds and metrics
- **PCA (Principal Component Analysis)**: 12D → 2D projection
- **Emergent Systems**: How complexity arises from simple rules
- **Game Design Patterns**: Property-based vs tag-based systems

---

**Last Updated:** 2025-10-05
**Version:** 1.0 - Manifold Integration Complete
