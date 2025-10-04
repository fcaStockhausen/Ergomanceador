# Karaokeficador

A fast-paced arena game featuring **dual-hand keyboard controls**, an **Avatar-inspired elemental magic system**, and **procedural spell interactions**.

Built in Python/Pygame with isometric rendering and property-driven magic mechanics.

---

## 🎮 Core Features

### Dual-Hand Control System
- **Left Hand (WASD)**: Player movement in screen-space
- **Right Hand (IJKL)**: Independent cursor/targeting control
- **Element Selection**:
  - Left hand: Q (Fire) / E (Water)
  - Right hand: U (Earth) / O (Air)
- **Actions**:
  - SPACE: Cast spell
  - ALT: Jump
  - ESC / Cmd+Q / Ctrl+Q: Quit

### Xbox Controller Support
- **Left Stick**: Player movement
- **Right Stick**: Aim direction (Diablo 3-style)
- **Face Buttons (ABXY)**: Select primary elements
- **D-Pad**: Select secondary elements
- **Triggers**: Cast spells
- **Haptic Feedback**: Controller rumble on spell cast

### Property-Based Magic System
Spells are **emergent** - computed from element properties, not hard-coded:

```python
# Fire + Water = Steam Explosion (automatic!)
Fire:  temperature=1200K, state=plasma, energy=high
Water: temperature=293K,  state=liquid, energy=low
→ Temperature differential >500K → Phase change → "Steam Explosion"
```

**Element Properties**:
- `temperature` (K): Enables thermal interactions
- `energy`: Contributes to damage
- `state`: solid/liquid/gas/plasma (affects area & duration)
- `movement`: static/flowing/expanding/rising (behaviors)
- `tags`: hot/cold, defensive/destructive (synergies)

**Spell Effects** are procedurally generated:
- Damage = f(combined energy, temperature)
- Area = f(state combinations)
- Duration = f(volatility, state)

### Combat System
- **Projectile spells** with particle trails
- **Collision detection** (circle-circle)
- **Floating damage numbers** (color-coded by severity)
- **Screen shake** (scales with damage)
- **Knockback physics** (friction-based deceleration)
- **Procedural sound effects** (cast/impact/death)
- **Health bars** with damage flash

### Isometric Rendering
- **Coordinate systems**:
  - **Cartesian (manifold)**: Internal grid (20x20)
  - **Screen**: User input coordinates
  - **Isometric**: Display projection
- **Transforms**:
  - `screen_to_cart()`: Input → Movement
  - `cart_to_iso()`: Position → Render
- Players rendered as 3D cylinders with shadows

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
Karaokeficador/
├── audio/              # Sound system (procedural audio)
├── components/         # Reusable components (health, etc.)
├── config/             # Settings, keybinds, controller config
├── core/               # Game loop, camera system
├── data/               # Element definitions (JSON)
├── entities/           # Player, enemies, cursor
├── input/              # Keyboard + controller handling
├── magic/              # Element system + interaction engine
├── physics/            # Collision detection
├── rendering/          # Isometric rendering, UI, effects
│   ├── effects/        # Projectiles, particles
│   └── ui/             # HUD, damage numbers, spell preview
├── tests/              # TAS testing system
├── utils/              # Logging utilities
└── main.py             # Entry point
```

**Stats**: 3,410 lines of Python across 43 files

---

## 🎯 Development Roadmap

### ✅ Completed (Phase 1-5C)
- Modular architecture
- Property-based magic system
- Dual-hand keyboard + Xbox controller input
- Isometric rendering with camera follow
- Spell casting with projectiles and particles
- Enemy combat system
- Combat polish (damage numbers, screen shake, sound, knockback)

### 🚧 In Progress
- Wave system
- Enemy AI
- Progression system

### 📝 Planned
- Multiple enemy types
- Boss encounters
- Procedural arena generation
- Networked multiplayer (stretch goal)

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
Enable in [main.py](main.py) (`DEBUG_MODE = True`):
- Real-time coordinate display
- Movement vector arrows
- Input → Cartesian transformation visualization
- Event logging (`game_debug.log`)

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
