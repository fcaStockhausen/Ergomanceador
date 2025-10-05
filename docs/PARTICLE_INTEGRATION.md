# Particle System Integration Guide

## Adding Particles to Projectiles

Your current projectiles are in [rendering/effects/projectile.py](rendering/effects/projectile.py). Here's how to add particles:

### Step 1: Import Particle System

```python
# In rendering/effects/projectile.py

from combat.particles import ParticleFactory, ParticleSystem
```

### Step 2: Add Particle System to Projectile

```python
class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, spell_data, owner='player'):
        # ... existing init code ...

        # NEW: Particle system
        self.particle_system = ParticleSystem()
        self.particle_spawn_timer = 0
        self.particle_spawn_interval = 0.05  # Spawn particles every 50ms

    def update(self, dt):
        """Update projectile position"""
        if not self.alive:
            return

        self.lifetime += dt
        self.particle_spawn_timer += dt

        # Die if too old
        if self.lifetime > self.max_lifetime:
            self.alive = False
            return

        # Move projectile
        if self.behavior == 'projectile' or self.behavior == 'homing':
            self.cart_x += self.vel_x
            self.cart_y += self.vel_y

            # NEW: Spawn trail particles periodically
            if self.particle_spawn_timer >= self.particle_spawn_interval:
                velocity = (self.vel_x, self.vel_y)
                particles = ParticleFactory.create_projectile_trail(
                    self.cart_x, self.cart_y,
                    velocity, self.color, density=5
                )
                self.particle_system.add_particles(particles)
                self.particle_spawn_timer = 0

            # Check if reached target
            dx = self.target_x - self.cart_x
            dy = self.target_y - self.cart_y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < 0.5:
                # NEW: Spawn burst particles on impact
                if self.behavior == 'projectile':
                    impact_particles = ParticleFactory.create_aoe_burst(
                        self.cart_x, self.cart_y,
                        self.area * 10, self.color, density=20
                    )
                    self.particle_system.add_particles(impact_particles)

                self.alive = False

        # Beams spawn particles once, then die
        elif self.behavior == 'beam':
            # NEW: Spawn beam particles
            if self.lifetime < 0.1:  # Only spawn once
                beam_particles = ParticleFactory.create_beam_particles(
                    (self.cart_x, self.cart_y),
                    (self.target_x, self.target_y),
                    self.color, density=30
                )
                self.particle_system.add_particles(beam_particles)

            self.alive = False

        # NEW: Update particles
        self.particle_system.update(dt)

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Draw projectile and particles"""
        if not self.alive and self.particle_system.count() == 0:
            return

        # NEW: Draw particles first (behind projectile)
        self.particle_system.render(screen, (camera_offset_x, camera_offset_y))

        # Draw projectile
        if self.alive:
            if self.behavior == 'beam':
                self._draw_beam(screen, camera_offset_x, camera_offset_y)
            elif self.behavior == 'projectile' or self.behavior == 'homing':
                self._draw_projectile(screen, camera_offset_x, camera_offset_y)
```

### Step 3: Update Effect Manager

If you have an effect manager that spawns projectiles, you may need to keep projectiles alive until particles finish:

```python
# In rendering/effects/effect_manager.py (or wherever projectiles are managed)

def update(self, dt):
    for projectile in self.projectiles[:]:
        projectile.update(dt)

        # Keep projectile alive if it still has particles
        if not projectile.alive and projectile.particle_system.count() == 0:
            self.projectiles.remove(projectile)
```

---

## Behavior-Specific Particles

### Chain Lightning (Branching Arc)

```python
# When chain lightning hits a target
if self.behavior == 'chain' and self.just_hit_target:
    # Find next target
    next_target = find_nearest_enemy(self.cart_x, self.cart_y)

    if next_target:
        # Create arc particles from current position to next target
        arc_particles = ParticleFactory.create_chain_arc(
            (self.cart_x, self.cart_y),
            (next_target.cart_x, next_target.cart_y),
            self.color, segments=20
        )
        self.particle_system.add_particles(arc_particles)
```

### AOE Expansion

```python
# In rendering/effects/expanding_aoe.py

from combat.particles import ParticleFactory

class ExpandingAOE:
    def __init__(self, x, y, spell_data):
        # ... existing init ...

        self.particle_system = ParticleSystem()

        # Spawn initial burst
        burst_particles = ParticleFactory.create_aoe_burst(
            x, y, spell_data['area'] * 10,
            spell_data['color'], density=50
        )
        self.particle_system.add_particles(burst_particles)

    def update(self, dt):
        # ... existing update ...
        self.particle_system.update(dt)

    def draw(self, screen, camera_offset):
        # Draw particles
        self.particle_system.render(screen, camera_offset)

        # Draw AOE ring (existing code)
        # ...
```

### Heal Sparkles

```python
# When casting heal spell
if self.behavior == 'heal':
    heal_particles = ParticleFactory.create_heal_sparkles(
        target.cart_x, target.cart_y,
        (100, 255, 100),  # Green
        density=20
    )
    self.particle_system.add_particles(heal_particles)
```

### Buff Orbit

```python
# When casting buff
if self.behavior == 'buff':
    # Spawn orbiting particles around target
    buff_particles = ParticleFactory.create_buff_orbit(
        target.cart_x, target.cart_y,
        (255, 255, 100),  # Yellow
        density=12
    )
    self.particle_system.add_particles(buff_particles)

    # Refresh particles every 0.5s to maintain orbit
    if self.buff_refresh_timer > 0.5:
        buff_particles = ParticleFactory.create_buff_orbit(...)
        self.particle_system.add_particles(buff_particles)
        self.buff_refresh_timer = 0
```

---

## Performance Tips

### Particle Pooling (Optional)

For better performance with many particles:

```python
class ParticlePool:
    """Reuse particle objects instead of creating new ones"""

    def __init__(self, max_particles=1000):
        self.particles = [Particle(0, 0, (255,255,255), 0) for _ in range(max_particles)]
        self.active = []
        self.inactive = self.particles.copy()

    def spawn(self, x, y, color, lifetime, velocity):
        if not self.inactive:
            return  # Pool exhausted

        particle = self.inactive.pop()
        particle.x = x
        particle.y = y
        particle.color = color
        particle.lifetime = lifetime
        particle.age = 0
        particle.velocity = velocity
        particle.alpha = 255

        self.active.append(particle)

    def update(self, dt):
        for particle in self.active[:]:
            if not particle.update(dt):
                self.active.remove(particle)
                self.inactive.append(particle)
```

### Particle Culling

Only render particles on screen:

```python
def render(self, screen, camera_offset):
    for particle in self.particles:
        # Check if particle is on screen
        screen_x = particle.x - camera_offset[0]
        screen_y = particle.y - camera_offset[1]

        if (0 <= screen_x <= SCREEN_WIDTH and
            0 <= screen_y <= SCREEN_HEIGHT):
            particle.render(screen, camera_offset)
```

---

## Testing Particles

### Test Single Behavior

```python
# In a test script or main game loop

# Test projectile particles
spell_data = {
    'behavior': 'projectile',
    'color': (255, 100, 50),
    'area': 2.0,
    'speed': 5.0
}

projectile = Projectile(10, 10, 15, 15, spell_data)

# Update/render in game loop
while True:
    dt = clock.tick(60) / 1000.0
    projectile.update(dt)
    projectile.draw(screen, camera_offset_x, camera_offset_y)
```

### Test All Behaviors

Use the visualizer to see which behaviors need which particle styles:

```bash
python magic/behavior_space_visualizer.py
```

Press SPACE to cycle through test spells and see their behaviors.

---

## Next Steps

1. ✅ **Integrate particles into projectiles** (code above)
2. ✅ **Add behavior-specific particles** (chain, AOE, heal, buff)
3. ⏸️ **Performance optimization** (pooling, culling)
4. ⏸️ **Tune particle density/lifetime** per behavior
5. ⏸️ **Add sound effects** (procedural audio already exists!)

**Key insight**: Particles are **emergent visuals** - they arise from the behavior classification, just like the behaviors emerge from the property manifold!
