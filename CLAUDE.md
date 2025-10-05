# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Karaokeficador - A Magicka/Warcraft 3 Warlocks-inspired arena combat game with property-based magic system, dual-hand controls, Xbox controller support, and deathmatch AI bots. Features emergent spell interactions, expanding AOE effects, and frame-rate independent movement.

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

**IMPORTANT for Claude Code:**
Always use the conda environment when running Python commands or installing packages:
```bash
source /Users/fcaraneda/anaconda3/bin/activate karaokeficador && python <script>
source /Users/fcaraneda/anaconda3/bin/activate karaokeficador && pip install <package>
```

## Debug Mode

Debug interface enabled by default (`DEBUG_MODE = True` in [config/settings.py](config/settings.py)):
- Real-time coordinate display (bottom-right panel)
- Movement vector arrows
- Input → Cartesian transformation visualization
- Logs written to `game_debug.log` (events only, not per-frame)

## Modular Architecture

The codebase is organized into specialized modules (~5,200 LOC):

```
karaokeficador/
├── main.py                          # Entry point
├── config/                          # Configuration & constants
│   ├── settings.py                  # Screen size, FPS, movement speed (BASE_MOVEMENT_SPEED=200)
│   ├── colors.py                    # Color constants, element colors
│   └── controller_config.py         # Xbox controller mappings (macOS D-pad buttons)
├── core/                            # Game loop & camera
│   ├── game.py                      # Main Game class, 3-second countdown, scoreboard
│   └── camera.py                    # Camera follow system
├── magic/                           # Property-based magic system
│   ├── element.py                   # Element class (9 elements with properties)
│   ├── interaction_engine.py        # Automatic spell computation from properties
│   └── magic_system.py              # Element queueing (max 5), spell generation
├── entities/                        # Game entities
│   ├── player.py                    # Player entity (300 HP, frame-rate independent movement)
│   ├── enemy.py                     # Enemy bots with Health component
│   ├── target_cursor.py             # Aiming cursor (keyboard/controller)
│   └── components/
│       └── health.py                # Health component with death handling
├── ai/                              # Bot AI system
│   └── bot_controller.py            # Attack/flee/wander behaviors, destination-based fleeing
├── combat/                          # Combat systems
│   ├── projectile.py                # Spell projectiles (1.2 units/sec, 2.5x damage)
│   ├── collision_detector.py        # Projectile-entity collision detection
│   └── damage_calculator.py         # Damage computation with knockback
├── rendering/                       # All rendering code
│   ├── isometric.py                 # Coordinate transforms (cart↔iso↔screen)
│   ├── grid_renderer.py             # Isometric grid drawing
│   ├── effects/
│   │   ├── expanding_aoe.py         # Radially expanding AOE (15 units/sec expansion)
│   │   ├── damage_number.py         # Floating damage/heal numbers
│   │   └── effect_manager.py        # Manages all visual effects
│   └── ui/                          # UI components
│       ├── hud.py                   # Element queue, health bars
│       ├── spell_preview.py         # Real-time spell stats preview
│       ├── debug_panel.py           # Debug overlay with coordinates
│       ├── controller_hud.py        # Controller element page display (3 pages)
│       └── scoreboard.py            # Deathmatch scoreboard (Q3-style)
├── input/                           # Input handling
│   ├── input_manager.py             # Unified keyboard + controller input
│   └── controller_handler.py        # Xbox controller (D-pad buttons, rumble feedback)
├── audio/                           # Procedural audio generation
│   ├── sound_generator.py           # Runtime waveform synthesis
│   └── sound_library.py             # Sound effect manager
├── tests/                           # TAS testing framework
│   ├── test_runner.py               # Test execution engine
│   └── tas/                         # Test scripts (14 verified tests)
└── utils/
    └── logger.py                    # Event-based logging
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

   **Xbox Controller Layout (Page-Based Element Selection):**
   - **Left Stick:** Player movement (analog)
   - **Right Stick:** Aim direction (analog)
   - **A Button:** Jump
   - **Face Buttons (X/Y/B):** Queue elements from current page (slots 0/1/2)
   - **LB (Left Bumper):** Queue 4th element from current page (slot 3)
   - **RB (Right Bumper):** Cast spell (aimed)
   - **D-Pad Up/Down:** Cycle element pages (3 pages total)
     - Page 1: Fire, Water, Earth, Nature
     - Page 2: Lightning, Ice, Arcane, Light
     - Page 3: Shadow, Nature, Fire, Water
   - **RT (Right Trigger):** Aimed cast
   - **LT (Left Trigger):** Self-cast
   - **Back Button:** Clear queue
   - **Start Button:** Quit game
   - **Rumble Feedback:** Haptic vibration on spell cast and page changes

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
- ✅ Isometric rendering with 20x20 diamond grid (1280x720 window)
- ✅ Player as 3D cylinder with ground shadow
- ✅ Camera follow system (player centered, world moves)
- ✅ Jump mechanics with gravity and Z-axis
- ✅ Dual-hand keyboard controls (WASD + IJKL)
- ✅ Xbox controller support (analog movement, page-based element selection)
- ✅ Frame-rate independent movement (dt-based, 200 units/second base speed)
- ✅ Deathmatch arena with 3 AI bots
- ✅ 3-second countdown before game start
- ✅ Q3-style scoreboard with kill tracking

**Property-Based Magic System:**
- ✅ 9 elements with physical properties (temperature, energy, density, volatility, tags)
- ✅ Automatic interaction engine - no hard-coded spell combinations
- ✅ Emergent spell effects from property combinations
- ✅ Element queueing system (max 5 elements, ordered combinations)
- ✅ Real-time spell preview UI showing computed damage/area/duration/temperature
- ✅ Multiple spell behaviors: projectile, beam, AOE, heal, shield
- ✅ Procedural spell naming based on property interactions
- ✅ Nature element healing with visual feedback (green/cyan +numbers)

**Combat System:**
- ✅ Projectile system with collision detection
- ✅ Expanding AOE effects (radial wave expansion at 15 units/sec)
- ✅ Damage calculation with knockback
- ✅ Floating damage/heal numbers
- ✅ Health component with death/respawn (3-second cooldown)
- ✅ Screen shake and impact effects
- ✅ Procedural audio (cast/impact/death sounds)

**AI System:**
- ✅ Bot behavior state machine (attack/flee/wander)
- ✅ Destination-based fleeing (picks safe spot, not random running)
- ✅ Preferred combat distance with dead zones (prevents jitter)
- ✅ Behavior change cooldowns (smooth transitions)
- ✅ Bots fight each other (not just player)
- ✅ Spell casting with cooldowns (3.5 seconds)

**Controller Features:**
- ✅ Page-based element selection (3 pages, 4 elements each)
- ✅ D-pad page cycling (macOS button events, not hat events)
- ✅ Visual page indicator with element layout
- ✅ Rumble feedback on cast and page changes
- ✅ Analog stick aiming and movement
- ✅ LT self-cast, RT aimed cast

**Technical Implementation:**
- ✅ Modular architecture (~5,200 LOC, 17 modules)
- ✅ Screen-space to cartesian coordinate transformation
- ✅ Camera offset system for all renderables
- ✅ Debug interface with coordinate visualization, bot position tracing
- ✅ Event-based logging (not per-frame spam)
- ✅ Cross-platform quit commands (ESC, Cmd+Q, Ctrl+Q)
- ✅ TAS testing framework (14 verified tests)
- ✅ Pytest integration (70 tests)
- ✅ Centralized movement speed (BASE_MOVEMENT_SPEED with multipliers)

**Tuned Parameters:**
- Base movement speed: 200 units/second (frame-rate independent)
- Player health: 300 HP (higher TTK)
- Projectile speed: 1.2 units/sec (50% slower than original)
- Projectile damage: 2.5x multiplier
- AOE expansion: 15 units/sec, 0.8s duration
- Jump strength: -10 with gravity 0.5
- Grid bounds: 20x20 cartesian units
- Bot cast cooldown: 3.5 seconds
- Bot flee threshold: 30% health
- Behavior change cooldown: 0.5 seconds

### 🚧 Known Issues & Future Work

**Current Known Issues:**
- Target cursor movement uses cartesian directions (not screen-space transformed like player)
- Grid boundaries hard-coded (entities can't leave 20x20 area)
- Bot wander behavior could be smoother (direction interpolation not implemented)
- No terrain obstacles or collision with environment
- Controller triggers should still work but unverified after D-pad button fix

**Future Development:**
- **Polish:**
  - Spell visual effects (particles, trails)
  - Arena terrain with obstacles
  - Victory/defeat conditions and match end screen
  - Element unlock progression system

- **Gameplay:**
  - More spell behaviors (channeled beams, area denial, buffs)
  - Element cancellation/amplification (Fire+Water reduces damage, Light+Shadow amplifies)
  - Combo system (bonus for specific sequences)

- **Technical:**
  - Externalize elements to JSON (easier balancing)
  - Network multiplayer (local or online)
  - Replay system using TAS framework
  - Performance optimization for more entities

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
