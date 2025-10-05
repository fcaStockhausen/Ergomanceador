"""Procedural terrain system with element-aligned biomes"""

import random
import noise  # Perlin noise for procedural generation
from config.colors import ELEMENT_COLORS


class TerrainTile:
    """
    Single terrain tile with element affinity and properties.
    """

    def __init__(self, x, y, biome_type, element_affinity=None):
        """
        Create terrain tile.

        Args:
            x, y: Grid coordinates
            biome_type: 'plains', 'volcano', 'river', 'forest', 'cave', 'storm', 'desert', 'ruins'
            element_affinity: Element that gets bonuses here (fire, water, earth, etc)
        """
        self.x = x
        self.y = y
        self.biome_type = biome_type
        self.element_affinity = element_affinity

        # Biome properties
        self.color = self._get_biome_color()
        self.mana_bonus = self._get_mana_bonus()
        self.damage_bonus = self._get_damage_bonus()

    def _get_biome_color(self):
        """Get visual color for this biome"""
        colors = {
            'plains': (100, 140, 80),      # Green grass
            'volcano': (120, 40, 20),      # Dark red lava rock
            'river': (40, 80, 160),        # Blue water
            'forest': (34, 100, 34),       # Dark green trees
            'cave': (40, 40, 50),          # Dark gray stone
            'storm': (80, 80, 100),        # Gray storm clouds
            'desert': (200, 180, 120),     # Sandy yellow
            'ruins': (100, 100, 120),      # Gray ancient stone
        }
        return colors.get(self.biome_type, (100, 100, 100))

    def _get_mana_bonus(self):
        """Get mana regeneration bonus for aligned elements"""
        # Elemental biomes give 2x mana regen for their element
        if self.element_affinity:
            return 2.0
        return 1.0

    def _get_damage_bonus(self):
        """Get damage bonus for aligned elements"""
        # Elemental biomes give 1.5x damage for their element
        if self.element_affinity:
            return 1.5
        return 1.0

    def applies_to_element(self, element_name):
        """Check if this tile's bonuses apply to given element"""
        return self.element_affinity == element_name


class TerrainGenerator:
    """
    Procedural terrain generator using Perlin noise.
    Creates element-aligned biomes: volcanoes, rivers, forests, etc.
    """

    def __init__(self, width, height, seed=None):
        """
        Create terrain generator.

        Args:
            width, height: Map size in tiles
            seed: Random seed for reproducible maps
        """
        self.width = width
        self.height = height
        self.seed = seed if seed else random.randint(0, 10000)
        self.tiles = {}

        # Noise scales for different features
        self.elevation_scale = 0.1  # Large features (mountains, valleys)
        self.moisture_scale = 0.15  # Medium features (water, forests)
        self.temperature_scale = 0.08  # Large features (hot/cold regions)

    def generate(self):
        """Generate procedural terrain map"""
        for y in range(self.height):
            for x in range(self.width):
                tile = self._generate_tile(x, y)
                self.tiles[(x, y)] = tile

        return self.tiles

    def _generate_tile(self, x, y):
        """Generate single tile based on noise values"""
        # Sample multiple noise layers
        elevation = noise.pnoise2(
            x * self.elevation_scale,
            y * self.elevation_scale,
            octaves=4,
            base=self.seed
        )

        moisture = noise.pnoise2(
            x * self.moisture_scale,
            y * self.moisture_scale,
            octaves=3,
            base=self.seed + 1000
        )

        temperature = noise.pnoise2(
            x * self.temperature_scale,
            y * self.temperature_scale,
            octaves=3,
            base=self.seed + 2000
        )

        # Determine biome from noise values
        biome_type, element = self._classify_biome(elevation, moisture, temperature)

        return TerrainTile(x, y, biome_type, element)

    def _classify_biome(self, elevation, moisture, temperature):
        """
        Classify biome based on noise values.

        Returns:
            (biome_type, element_affinity)
        """
        # Very high elevation + hot = Volcano (fire)
        if elevation > 0.4 and temperature > 0.3:
            return ('volcano', 'fire')

        # Very high elevation + cold = Storm peaks (lightning)
        if elevation > 0.4 and temperature < -0.2:
            return ('storm', 'lightning')

        # Low elevation + high moisture = River (water)
        if elevation < -0.2 and moisture > 0.2:
            return ('river', 'water')

        # Low elevation + very high moisture = Frozen lake (ice)
        if elevation < -0.2 and moisture > 0.4 and temperature < -0.3:
            return ('river', 'ice')  # Frozen water

        # Medium elevation + high moisture = Forest (nature)
        if -0.1 < elevation < 0.2 and moisture > 0.3:
            return ('forest', 'nature')

        # High elevation = Cave (earth)
        if elevation > 0.3:
            return ('cave', 'earth')

        # Hot + dry = Desert (arcane - mystical heat)
        if temperature > 0.4 and moisture < -0.2:
            return ('desert', 'arcane')

        # Very low moisture + medium temp = Ruins (shadow)
        if moisture < -0.3 and -0.2 < temperature < 0.2:
            return ('ruins', 'shadow')

        # Default: Plains (no affinity)
        return ('plains', None)

    def get_tile(self, x, y):
        """Get tile at coordinates"""
        return self.tiles.get((x, y), None)

    def get_element_affinity_at(self, x, y):
        """Get element affinity at position (for mana bonus)"""
        tile = self.get_tile(int(x), int(y))
        if tile:
            return tile.element_affinity
        return None

    def get_mana_bonus_at(self, x, y, element_name):
        """Get mana bonus for element at position"""
        tile = self.get_tile(int(x), int(y))
        if tile and tile.applies_to_element(element_name):
            return tile.mana_bonus
        return 1.0

    def get_damage_bonus_at(self, x, y, elements):
        """
        Get damage bonus for spell at position.

        Args:
            x, y: Position
            elements: List of element names in spell

        Returns:
            Damage multiplier (1.0 to 1.5)
        """
        tile = self.get_tile(int(x), int(y))
        if not tile or not tile.element_affinity:
            return 1.0

        # Check if any spell element matches terrain
        for element in elements:
            if tile.applies_to_element(element):
                return tile.damage_bonus

        return 1.0
