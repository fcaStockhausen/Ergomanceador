# Emergent Behaviors & Particle System Design

## 🌟 What Are Emergent Behaviors?

**Emergent behaviors** are spell types that arise naturally from the geometry of the behavior manifold, **without being explicitly programmed**.

### How It Works

1. **Prototypes Define Regions**: Each behavior (projectile, beam, AOE, etc.) has a prototype point in 12D space
2. **Spells Are Classified By Distance**: When you queue elements, the spell's property vector is computed and classified by finding the nearest prototype
3. **Gaps = Emergent Behaviors**: Any spell that falls **between** prototypes creates a hybrid behavior

### Example: Fire + Water

```
Fire:  temp=1200K, energy=100
Water: temp=293K,  energy=10

Property Vector:
  thermal_flux = 1.21   (HIGH - rapid temp change)
  chaos_factor = 0.35   (MODERATE - mixed properties)
  polarity = 0.05       (NEUTRAL - neither defensive nor offensive)

Classification:
  Distance to Projectile: 0.45
  Distance to Chain: 0.32  ← NEAREST!
  Distance to AOE: 0.58

Result: CHAIN behavior (emergent lightning-like effect)
```

**Why Chain?** The high thermal flux + moderate chaos creates a property vector that's closer to the Chain prototype than others. This wasn't explicitly coded - it emerged from the geometry!

---

## 🎨 Creating New Behaviors

### Method 1: Find Gaps in the Space

1. **Run the Behavior Space Visualizer**:
   ```bash
   python magic/behavior_space_visualizer.py
   ```

2. **Look for empty regions** between prototypes (gaps in the 2D projection)

3. **Add a new prototype** in that region:
   ```python
   # In magic/behavior_manifold.py

   BehaviorRegion(
       name='tornado',  # NEW BEHAVIOR
       prototype=np.array([
           0.8,   # thermal_flux (HIGH - swirling motion)
           0.4,   # avg_temperature (moderate)
           0.6,   # temp_differential (mixed)
           0.3,   # state_transition_energy (low persistence)
           0.7,   # phase_diversity (HIGH - gas/plasma mix)
           0.5,   # density_gradient (moderate)
           0.3,   # avg_density (LOW - gaseous)
           0.9,   # volatility (VERY HIGH)
           0.6,   # chaos_factor (HIGH - turbulent)
           0.5,   # total_energy (moderate)
           0.4,   # energy_density
           0.1    # polarity_tension (NEUTRAL)
       ]),
       metric_tensor=np.eye(12)
   )
   ```

4. **Test combinations** that might hit this region (e.g., Air + Fire + Air)

### Method 2: Tune Existing Prototypes

If a behavior feels wrong (e.g., Fire+Water should be Steam, not Chain):

1. **Check the property vector**:
   ```bash
   python magic/manifold_visualizer.py
   # Look at Fire+Water output
   ```

2. **Adjust the prototype** to better match your intent:
   ```python
   # Move Chain prototype to emphasize lightning (not steam)
   'chain': [0.6, 0.8, 0.5, ...]  # Higher temp for electrical effects
   ```

3. **Create a new Steam prototype** if needed:
   ```python
   'steam': [1.2, 0.5, 0.9, ...]  # Very high thermal flux, moderate temp
   ```

---

## 💥 Particle System Design

### Step 1: Map Behaviors to Visual Styles

Each behavior needs distinct particle characteristics:

| Behavior | Particle Style | Key Properties |
|----------|---------------|----------------|
| **Projectile** | Single streak | Linear motion, trail effect |
| **Beam** | Continuous ray | Instant, no particles (just line render) |
| **AOE** | Radial burst | Expanding ring, fading alpha |
| **Chain** | Branching arcs | Jump between targets, electric crackle |
| **Homing** | Curved trail | Bezier path, target tracking |
| **Area Denial** | Lingering cloud | Slow drift, pulsing alpha |
| **Heal** | Rising sparkles | Upward drift, green/gold glow |
| **Buff** | Orbiting particles | Circular motion around target |

### Step 2: Create Particle Base Class

```python
# combat/particles/particle.py

class Particle:
    """Base particle for spell effects"""

    def __init__(self, x, y, color, lifetime, velocity=(0,0)):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.velocity = velocity
        self.alpha = 255

    def update(self, dt):
        self.age += dt
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        # Fade out near end of life
        self.alpha = int(255 * (1 - self.age / self.lifetime))

        return self.age < self.lifetime  # Return True if alive

    def render(self, screen, camera_offset):
        # Render with alpha blending
        surf = pygame.Surface((4, 4))
        surf.set_alpha(self.alpha)
        surf.fill(self.color)
        screen.blit(surf, (self.x - camera_offset[0], self.y - camera_offset[1]))
```

### Step 3: Behavior-Specific Particle Generators

```python
# combat/particles/particle_factory.py

class ParticleFactory:
    """Generates particles based on spell behavior"""

    @staticmethod
    def create_projectile_particles(x, y, velocity, color):
        """Trailing particles for projectile"""
        particles = []

        for i in range(5):
            offset = (random.uniform(-2, 2), random.uniform(-2, 2))
            particles.append(Particle(
                x + offset[0],
                y + offset[1],
                color,
                lifetime=0.3,
                velocity=(-velocity[0]*0.3, -velocity[1]*0.3)  # Trail behind
            ))

        return particles

    @staticmethod
    def create_aoe_particles(x, y, radius, color):
        """Radial burst for AOE"""
        particles = []

        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            speed = random.uniform(50, 100)

            particles.append(Particle(
                x, y,
                color,
                lifetime=0.5,
                velocity=(math.cos(rad)*speed, math.sin(rad)*speed)
            ))

        return particles

    @staticmethod
    def create_chain_particles(start, end, color):
        """Branching arc for chain lightning"""
        particles = []

        # Bezier curve points
        dx, dy = end[0]-start[0], end[1]-start[1]
        ctrl = (start[0] + dx*0.5 + random.uniform(-20,20),
                start[1] + dy*0.5 + random.uniform(-20,20))

        for t in np.linspace(0, 1, 20):
            # Quadratic Bezier
            x = (1-t)**2*start[0] + 2*(1-t)*t*ctrl[0] + t**2*end[0]
            y = (1-t)**2*start[1] + 2*(1-t)*t*ctrl[1] + t**2*end[1]

            particles.append(Particle(x, y, color, lifetime=0.2))

        return particles
```

### Step 4: Integration with Spell System

```python
# In magic/interaction_engine.py

def compute_interaction(self, element_names):
    # ... existing code ...

    return {
        'name': spell_name,
        'behavior': behavior,
        'damage': damage,
        # ...

        # NEW: Particle metadata
        'particle_style': self._get_particle_style(behavior),
        'particle_color': spell_color,
        'particle_density': self._compute_particle_density(vector),
    }

def _get_particle_style(self, behavior):
    """Map behavior to particle style"""
    styles = {
        'projectile': 'trail',
        'aoe': 'burst',
        'chain': 'arc',
        'heal': 'sparkle',
        'buff': 'orbit',
        # ... etc
    }
    return styles.get(behavior, 'default')

def _compute_particle_density(self, vector):
    """More volatile spells = more particles"""
    return int(20 + vector.volatility_index * 30)
```

### Step 5: Render Particles in Game Loop

```python
# In core/game.py

def update(self, dt):
    # ... existing updates ...

    # Update particles
    for particle in self.particles[:]:
        if not particle.update(dt):
            self.particles.remove(particle)

def render(self):
    # ... existing renders ...

    # Render particles (after world, before UI)
    for particle in self.particles:
        particle.render(self.screen, self.camera.offset)
```

---

## 🔬 Discovering Emergent Behaviors

### Workflow:

1. **Queue elements in game** (e.g., Fire, Fire, Water)

2. **Watch the Behavior Space Visualizer** - see the yellow dot (your spell) move through 12D space

3. **Notice where it lands**:
   - **On a prototype** → Standard behavior
   - **Between prototypes** → Emergent hybrid behavior!

4. **Test the spell** - does it feel right?

5. **If needed, add a new prototype** to formalize the emergent behavior

### Example Discovery Process:

```
Test: Fire + Fire + Water
→ Property vector lands between CHAIN and AOE
→ Distance to CHAIN: 0.42
→ Distance to AOE: 0.48
→ Classified as CHAIN (but close to AOE)

Observation: Feels like it should be a steam explosion (AOE), not chain

Action: Create new "STEAM" prototype at that location
→ Now Fire+Fire+Water → STEAM behavior (radial burst with knockback)
```

---

## 🎮 Using the Visualizer

### Standalone Mode:
```bash
python magic/behavior_space_visualizer.py
```

Controls:
- **SPACE**: Cycle test spells
- **MOUSE HOVER**: See prototype properties
- **ESC**: Quit

### Integrated Mode (TODO):
1. Add `BehaviorSpaceVisualizer` as second window in [main.py](main.py)
2. Update visualizer in real-time as you queue elements
3. See spells move through space while playing!

---

## 📊 Prototype Design Principles

### Good Prototypes:
- **Well-separated** (distance > 0.5 to nearest neighbor)
- **Distinct key properties** (e.g., Heal has polarity=0.95, Projectile has polarity=0.2)
- **Tuned for intended combinations** (e.g., Nature → Heal, Fire → Projectile)

### Bad Prototypes:
- **Too close together** (distance < 0.3 causes confusion)
- **Generic properties** (all dimensions near 0.5 = undefined behavior)
- **Redundant** (two prototypes in same region)

### Balancing Tool:
```bash
python magic/manifold_visualizer.py
# Check "Balance Ratio" - aim for > 0.3
# Check "Closest pairs" - fix any distance < 0.4
```

---

## 🚀 Next Steps

1. **Run visualizer** to see current behavior space
2. **Identify gaps** where new behaviors could emerge
3. **Test element combinations** to find emergent hybrids
4. **Add prototypes** to formalize useful emergent behaviors
5. **Build particle system** to visualize behaviors in-game

**Key insight**: The manifold system gives you a **geometric playground** for spell design. You're not writing if-else chains - you're sculpting a 12D space where spells naturally emerge!
