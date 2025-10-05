# Karaokeficador

A Magicka/Warcraft 3 Warlocks-inspired arena combat game with a **property-based magic system**, **dual-hand controls**, **Xbox controller support**, and **AI deathmatch bots**.

Features emergent spell interactions, expanding AOE effects, and frame-rate independent movement.

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.6.1-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)

---

## 📚 Documentation

**All documentation is now organized in [docs/](docs/)**

- 🚀 **[Quick Start - Manifold HUD](docs/QUICKSTART_MANIFOLD.md)** - Run game with real-time behavior visualization
- 🎨 **[Designer Guide](docs/DESIGNER_GUIDE_BEHAVIOR_TUNING.md)** - Tune spell behaviors (no coding!)
- 🎵 **[Audio Editor Guide](AUDIO_EDITOR_GUIDE.md)** - Load custom sounds with ADSR envelopes
- 🧠 **[Manifold Systems](docs/MANIFOLD_SYSTEMS.md)** - Understand the property-based magic system
- 💡 **[Emergent vs Hardcoded](docs/EMERGENT_VS_HARDCODED.md)** - Design philosophy
- 📖 **[Complete Documentation Index](docs/INDEX.md)** - Full table of contents

---

## 🎮 Core Features

### Dual-Hand Control System
**Keyboard:**
- **Left Hand (WASD)**: Player movement in screen-space
- **Right Hand (IJKL)**: Independent cursor/targeting control
- **Element Selection**:
  - Left hand: Q/E/R/F (Fire, Water, Ice, Earth)
  - Right hand: U/O/P/; (Nature, Arcane, Light, Shadow)
- **Actions**:
  - SPACE: Cast spell
  - G: Jump
  - Backspace: Remove last element
  - ESC / Cmd+Q / Ctrl+Q: Quit

**Xbox Controller (Page-Based):**
- **Left Stick**: Player movement (analog)
- **Right Stick**: Aim direction (analog)
- **Face Buttons (X/Y/B/LB)**: Queue elements from current page
- **D-Pad Up/Down**: Cycle element pages (3 pages total)
  - Page 1: Fire, Water, Earth, Nature
  - Page 2: Lightning, Ice, Arcane, Light
  - Page 3: Shadow, Nature, Fire, Water
- **RT**: Aimed cast
- **LT**: Self-cast
- **A**: Jump
- **Back**: Clear queue
- **Start**: Quit
- **Rumble Feedback**: Haptic vibration on spell cast and page changes

### Property-Based Magic System
Spells are **emergent** - computed from element properties, not hard-coded:

```python
# Fire + Water = Steam Explosion (automatic!)
Fire:  temperature=1200K, state=plasma, energy=high
Water: temperature=293K,  state=liquid, energy=low
→ Temperature differential >500K → Phase change → "Steam Explosion"
```

**9 Elements** with physical properties:
- `temperature` (K): Enables thermal interactions
- `energy`: Contributes to damage
- `density`: Affects projectile speed
- `volatility`: Affects area/duration
- `tags`: hot/cold, defensive/destructive (synergies)

**Spell Effects** are procedurally generated:
- Damage = f(combined energy, temperature)
- Area = f(density, volatility)
- Duration = f(volatility, state)
- Behavior = f(tags, temperature differentials)

**Multiple Behaviors:**
- Projectile (fast-moving spell bolts)
- Beam (instant line damage)
- Expanding AOE (radial wave at 15 units/sec)
- Heal (self or allies)
- Shield (damage absorption)

### Combat & Arena System
- **Deathmatch arena** with 3 AI bots
- **Frame-rate independent** movement (200 units/second base speed)
- **Q3-style scoreboard** with kill tracking
- **3-second countdown** before game start
- **Projectile spells** with collision detection
- **Expanding AOE effects** with visual ring and wave damage
- **Floating damage/heal numbers** (color-coded)
- **Screen shake** and knockback effects
- **Procedural sound effects** (cast/impact/death)
- **Health bars** with damage flash (300 HP, higher TTK)

### AI System
- **Behavior state machine**: Attack, flee, wander
- **Smart fleeing**: Picks safe destinations 20 units away, not random running
- **Combat positioning**: Maintains preferred distance (8 units) with dead zones
- **Behavior change cooldowns**: Prevents jittery rapid switching (0.5s)
- **Bots vs bots**: AI enemies fight each other, not just player
- **Spell casting**: Cooldown-based spell use (3.5 seconds)

### Isometric Rendering
- **Coordinate systems**:
  - **Cartesian (manifold)**: Internal grid (20x20)
  - **Screen**: User input coordinates
  - **Isometric**: Display projection
- **Transforms**:
  - `screen_to_cart()`: Input → Movement (prevents "rotated 45°" feeling)
  - `cart_to_iso()`: Position → Render
- Players rendered as 3D cylinders with ground shadows
- Camera follow system (player-centered)

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd Karaokeficador

# Create conda environment
conda env create -f environment.yml
conda activate karaokeficador

# OR use pip
pip install -r requirements.txt
```

### Run Game

```bash
python main.py
```

### Testing

```bash
# Run TAS (Tool-Assisted Speedrun) tests
python tests/test_runner.py spell_casting
```

---

## 📁 Project Structure

```
karaokeficador/
├── main.py                          # Entry point
├── config/                          # Configuration & constants
│   ├── settings.py                  # Screen size, FPS, movement speed
│   ├── colors.py                    # Color constants, element colors
│   └── controller_config.py         # Xbox controller mappings
├── core/                            # Game loop & camera
│   ├── game.py                      # Main Game class, countdown, scoreboard
│   └── camera.py                    # Camera follow system
├── magic/                           # Property-based magic system
│   ├── element.py                   # Element class (9 elements)
│   ├── interaction_engine.py        # Automatic spell computation
│   └── magic_system.py              # Element queueing (max 5)
├── entities/                        # Game entities
│   ├── player.py                    # Player entity (300 HP)
│   ├── enemy.py                     # Enemy bots
│   ├── target_cursor.py             # Aiming cursor
│   └── components/
│       └── health.py                # Health component
├── ai/                              # Bot AI system
│   └── bot_controller.py            # Attack/flee/wander behaviors
├── combat/                          # Combat systems
│   ├── projectile.py                # Spell projectiles
│   ├── collision_detector.py        # Collision detection
│   └── damage_calculator.py         # Damage computation
├── rendering/                       # All rendering code
│   ├── isometric.py                 # Coordinate transforms
│   ├── grid_renderer.py             # Isometric grid drawing
│   ├── effects/
│   │   ├── expanding_aoe.py         # Radially expanding AOE
│   │   ├── damage_number.py         # Floating damage numbers
│   │   └── effect_manager.py        # Manages visual effects
│   └── ui/                          # UI components
│       ├── hud.py                   # Element queue, health bars
│       ├── spell_preview.py         # Real-time spell stats
│       ├── debug_panel.py           # Debug overlay
│       ├── controller_hud.py        # Controller element pages
│       └── scoreboard.py            # Deathmatch scoreboard
├── input/                           # Input handling
│   ├── input_manager.py             # Unified keyboard + controller
│   └── controller_handler.py        # Xbox controller support
├── audio/                           # Procedural audio generation
│   ├── sound_generator.py           # Runtime waveform synthesis
│   └── sound_library.py             # Sound effect manager
├── tests/                           # TAS testing framework
│   ├── test_runner.py               # Test execution engine
│   └── tas/                         # Test scripts (14 verified tests)
└── utils/
    └── logger.py                    # Event-based logging
```

**Stats**: ~5,200 lines of Python code across 17 modules

---

## 🎯 Current Status

### ✅ Completed Features
- **Core Gameplay**: Isometric arena, frame-rate independent movement, 3-second countdown
- **Property-Based Magic**: 9 elements, emergent interactions, element queueing (max 5)
- **Combat System**: Projectiles, expanding AOE, damage/heal, knockback, screen shake
- **AI System**: Attack/flee/wander behaviors, destination-based fleeing, bots vs bots
- **Dual-Input**: Keyboard + Xbox controller (page-based element selection)
- **Visual Polish**: Floating damage numbers, health bars, scoreboard, procedural audio
- **Testing**: TAS framework (14 tests), pytest integration (70 tests)
- **Modular Architecture**: ~5,200 LOC across 17 specialized modules

### 🚧 Known Issues
- Target cursor uses cartesian movement (not screen-space transformed)
- Grid boundaries hard-coded (20x20 area)
- Bot wander could be smoother (direction interpolation not implemented)
- No terrain obstacles or environment collision

### 📝 Future Development
- **Polish**: Spell particles, arena terrain, victory conditions, element unlocking
- **Gameplay**: More spell behaviors, element cancellation, combo system
- **Technical**: JSON element definitions, network multiplayer, replay system

---

## 🔧 Technical Details

### Coordinate Manifold Design
The isometric map is treated as a **manifold** with local coordinates:
1. User presses **W** (expecting "up" on screen)
2. `screen_to_cart()` transforms to cartesian movement
3. Player moves in cartesian grid
4. `cart_to_iso()` projects to screen for rendering

This prevents the common isometric bug where controls feel "rotated 45°".

### Debug Mode
Enabled by default in `config/settings.py` (`DEBUG_MODE = True`):
- Real-time coordinate display (bottom-right panel)
- Movement vector arrows
- Bot position tracing (every 0.5 seconds)
- Input → Cartesian transformation visualization
- Event logging to `game_debug.log`

### Platform Support
- **Primary**: macOS (ARM64)
- **Tested**: macOS with Pygame 2.6.1, Python 3.10
- **Keyboard modifiers**:
  - Mac: `pygame.KMOD_META` (Cmd key)
  - Windows/Linux: `pygame.KMOD_CTRL` (Ctrl key)

---

## 🤝 Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines and project philosophy.

Key principles:
- **Manifold thinking**: Coordinate transforms for intuitive controls
- **Dual-hand optimization**: No hand repositioning during gameplay
- **Property-driven emergence**: Magic system expands via data, not code

---

## 📄 License

*(License TBD - add your preferred license)*

---

## 🎨 Design Philosophy

> "The magic system uses a property-based interaction engine. Elements have physical properties (temperature, state, energy, tags) and the engine automatically computes spell effects from property combinations. This means adding new elements doesn't require coding all combinations manually - spell balance can be tuned by adjusting element properties, and players can experiment to discover emergent interactions."

Example: Fire (1200K, plasma) + Water (293K, liquid) → Temperature differential >500K → Phase change detected → **"Steam Explosion"** generated automatically.

---

Built with ❤️ using Python, Pygame, and emergent game design.
