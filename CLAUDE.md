# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Karaokeficador - A game interaction engine with dual-hand keyboard controls, Xbox controller support, and an Avatar-style elemental magic system with procedural spell effects.

## Development Environment

**Primary Platform:** macOS (ARM64)
- Uses conda environment: `karaokeficador`
- Python 3.10
- Pygame 2.6.1+

**Platform-specific keyboard handling:**
- Mac uses `pygame.KMOD_META` for Cmd key
- Windows/Linux uses `pygame.KMOD_CTRL` for Ctrl key
- Code should support both modifiers where applicable

## Setup and Running

```bash
# Create conda environment
conda env create -f environment.yml
# OR
conda create -n karaokeficador python=3.10 -y
conda activate karaokeficador
pip install -r requirements.txt

# Run the game
python main.py

# Quit game: ESC or Cmd+Q (Mac) / Ctrl+Q (Windows/Linux)
```

## Debug Mode

Debug interface enabled by default (`DEBUG_MODE = True` in [config/settings.py](config/settings.py)):
- Real-time coordinate display (bottom-right panel)
- Movement vector arrows
- Input → Cartesian transformation visualization
- Logs written to `game_debug.log` (events only, not per-frame)

## Modular Architecture

The codebase is organized into specialized modules for scalability:

```
karaokeficador/
├── main.py                          # Entry point (~30 lines)
├── config/                          # Configuration & constants
│   ├── settings.py                  # Screen size, FPS, grid size
│   └── colors.py                    # Color constants, element colors
├── core/                            # Game loop & camera
│   ├── game.py                      # Main Game class with game loop
│   └── camera.py                    # Camera follow system
├── magic/                           # Magic interaction system
│   ├── element.py                   # Element class
│   ├── interaction_engine.py        # Property-based spell computation
│   ├── magic_system.py              # Player-facing spell API
│   └── behaviors/                   # (Future: spell behavior classes)
├── entities/                        # Game entities
│   ├── player.py                    # Player entity
│   └── target_cursor.py             # IJKL-controlled cursor
├── rendering/                       # All rendering code
│   ├── isometric.py                 # Coordinate transforms
│   ├── grid_renderer.py             # Isometric grid drawing
│   └── ui/                          # UI components
│       ├── hud.py                   # Controls, active elements
│       ├── spell_preview.py         # Real-time spell preview
│       └── debug_panel.py           # Debug overlay
├── input/                           # (Future: input management)
├── physics/                         # (Future: collision, projectiles)
├── utils/                           # Utilities
│   └── logger.py                    # Logging setup
└── data/                            # (Future: JSON data files)
```

## Architecture

### Core Systems

1. **Isometric Rendering System**
   - Diamond-shaped isometric grid (20x20 tiles)
   - Coordinate systems:
     - **Cartesian (manifold):** Internal grid coordinates (x, y)
     - **Screen (perspective):** User-facing screen coordinates
     - **Isometric:** Projected display coordinates
   - Transform functions:
     - `cart_to_iso()`: Cartesian → Isometric projection
     - `screen_to_cart()`: Screen input → Cartesian movement
     - Player rendered as 3D cylinder with shadow

2. **Dual-Input Control System** (Keyboard + Xbox Controller)

   **Keyboard Controls:**
   - **Left hand (WASD):** Player movement in screen-space
   - **Right hand (IJKL):** Target/cursor movement
   - **G:** Jump
   - **Spacebar:** Cast spell
   - **Q/E/R/F (left hand):** Fire/Water/Ice/Earth elements
   - **U/O/P/; (right hand):** Nature/Arcane/Light/Shadow elements
   - **Backspace:** Remove last element from queue
   - **ESC or Cmd+Q/Ctrl+Q:** Quit game

   **Xbox Controller Layout:**
   - **Left Stick:** Player movement (analog)
   - **Right Stick:** Target cursor (analog)
   - **R3 (click):** Jump
   - **Face Buttons (A/B/X/Y):** Fire/Water/Earth/Nature (quick access)
   - **D-Pad:** Arcane/Light/Shadow/Lightning (secondary elements)
   - **RB (Right Bumper):** Cast spell
   - **LB (Left Bumper):** Remove last element
   - **RT (Right Trigger):** Aimed cast (hold and release)
   - **LT (Left Trigger):** Self-cast (buffs)
   - **Back Button:** Clear queue
   - **Start Button:** Quit game
   - **Rumble Feedback:** Haptic vibration on spell cast

3. **Property-Based Magic System** ([magic/interaction_engine.py](magic/interaction_engine.py))
   - **Automatic Interaction Engine**: Spell effects computed from element properties, not hard-coded combinations
   - **Element Properties**:
     - `temperature`: Kelvin temperature (enables phase-change interactions)
     - `energy`: Power level (contributes to damage)
     - `state`: solid/liquid/gas/plasma (affects area & duration)
     - `movement`: static/flowing/expanding/rising (behavioral traits)
     - `tags`: descriptive properties for synergies (hot/cold, defensive/destructive, etc.)
   - **Emergent Interactions**:
     - Temperature differentials create phase changes (steam, lava, ice)
     - State combinations determine spell area and duration
     - Tag synergies create specialized effects
   - **Procedural Effect Generation**: Damage, area, duration computed from combined properties
   - Players discover combinations through experimentation

### Key Classes & Modules

- **[magic/element.py](magic/element.py)**: `Element` class - property container (temperature, energy, state, movement, tags)
- **[magic/interaction_engine.py](magic/interaction_engine.py)**: `InteractionEngine` - automatic property resolver, generates spell effects from element combinations
- **[magic/magic_system.py](magic/magic_system.py)**: `MagicSystem` - player-facing API, tracks active elements, queries InteractionEngine
- **[entities/player.py](entities/player.py)**: `Player` - handles cartesian position, jumping (Z-axis), cylinder rendering with shadow
- **[entities/target_cursor.py](entities/target_cursor.py)**: `Target` - crosshair/targeting system controlled independently (IJKL)
- **[core/game.py](core/game.py)**: `Game` - main game loop, event handling, rendering orchestration
- **[core/camera.py](core/camera.py)**: `Camera` - camera follow system for player
- **[rendering/isometric.py](rendering/isometric.py)**: Coordinate transformation functions (cart_to_iso, screen_to_cart, iso_to_cart)

### Coordinate Manifold Design

**Important:** The isometric map is a manifold with local (cartesian) coordinates. User input is in perspective (screen) coordinates and must be transformed:

- User presses **W** (expecting "up" on screen)
- `screen_to_cart()` transforms to cartesian movement
- Player moves in cartesian grid
- `cart_to_iso()` projects to screen for rendering

This prevents the common isometric movement bug where controls feel "rotated 45°".

## Current Project Status

### ✅ Completed Features

**Core Gameplay:**
- ✅ Isometric rendering with 20x20 diamond grid
- ✅ Player as 3D cylinder with ground shadow
- ✅ Camera follow system (player centered, world moves)
- ✅ Jump mechanics with gravity and Z-axis
- ✅ Dual-hand keyboard controls (WASD + IJKL)
- ✅ Independent target/crosshair aiming system

**Property-Based Magic System:**
- ✅ 4 elements with physical properties (temperature, energy, state, movement, tags)
- ✅ Automatic interaction engine - no hard-coded spell combinations
- ✅ Emergent spell effects from property combinations
- ✅ Real-time spell preview UI showing computed damage/area/duration/temperature
- ✅ Spell casting with SPACE
- ✅ Procedural spell naming based on property interactions

**Technical Implementation:**
- ✅ Modular architecture (config, core, magic, entities, rendering modules)
- ✅ Screen-space to cartesian coordinate transformation
- ✅ Camera offset system for all renderables
- ✅ Debug interface with coordinate visualization
- ✅ Event-based logging (not per-frame spam)
- ✅ Cross-platform quit commands (ESC, Cmd+Q, Ctrl+Q)
- ✅ Separation of concerns (rendering, game logic, input, magic system)

**Tuned Parameters:**
- Player speed: 0.5 (5x base speed for responsive movement)
- Target speed: 0.3 (slower for precision aiming)
- Jump strength: -10 with gravity 0.5
- Grid bounds: 20x20 cartesian units

### 🚧 Next Development Phases

**Phase 2: Magic Engine Expansion** (Priority: High)
- Add new element properties (density, volatility, polarity)
- Externalize elements to `data/elements.json` (8 elements: Fire, Lightning, Water, Ice, Earth, Nature, Arcane, Light, Shadow)
- Implement spell behavior system (projectile, beam, AoE, area denial, buff)
- Element cancellation/amplification (Fire+Water reduces damage, Light+Shadow amplifies)
- Change toggle system to element queueing (max 5 elements, ordered list)

**Phase 3: Dual-Hand Input Enhancement** (Priority: High)
- Expand to 8-element keyboard layout (Q/E/R/F + U/O/P/;)
- Implement Magicka-style element queueing
- Visual element queue display (5 slots with icons)
- Spell projectile rendering
- Enhanced real-time spell preview

**Phase 4: Arena Combat** (Priority: Medium)
- Health/damage system for entities
- AI opponent with basic spell casting
- Spell collision detection
- Match flow (start → fight → end)

**Phase 5: Minimal Progression** (Priority: Low)
- XP/level system (arena-focused, no grinding)
- Small talent tree (15 nodes, unlock mechanics not stats)
- Element unlocking progression (4 starting → 8 total)
- Post-match screen with XP gain

**Current Known Issues:**
- Target movement uses cartesian directions (not screen-space transformed)
- No collision detection
- No spell visual effects or projectiles (spells computed but not rendered)
- Grid boundaries are hard-coded (player can't leave 20x20 area)
- No enemies or targets to cast spells at

### 📝 Design Philosophy

**Manifold Thinking:** The game treats the isometric grid as a manifold with local coordinates. User input is always in screen-space (perspective coordinates) and transformed to the manifold's local (cartesian) coordinates before movement logic. This maintains intuitive controls regardless of projection.

**Dual-Hand Optimization:** Controls are positioned for hands to remain in home position (left: WASD, right: IJKL). No hand repositioning needed during gameplay. Elements split between hands (Q/E left, U/O right) for simultaneous movement + ability selection.

**Property-Driven Emergence:** The magic system uses a property-based interaction engine. Elements have physical properties (temperature, state, energy, tags) and the engine automatically computes spell effects from property combinations. This means:
- Adding new elements doesn't require coding all combinations manually
- Spell balance can be tuned by adjusting element properties
- Players can experiment to discover emergent interactions
- The system is transparent - debug UI shows WHY properties create specific effects

Example: Fire (1200K, plasma) + Water (293K, liquid) → Temperature differential > 500K → Phase change detected → "Steam Explosion" generated automatically.

**Arena-Focused Design:** The game is designed as a competitive arena combat system (inspired by Magicka and Warcraft 3 Warlocks):
- Fast-paced matches (3-5 minutes)
- Minimal progression (skill > stats)
- XP gained only from arena matches (no grinding)
- Talent tree unlocks mechanics, not power scaling
- 8 elements total (4 starting, 4 unlockable via progression)
- Dual-hand input optimized for rapid spell combinations
