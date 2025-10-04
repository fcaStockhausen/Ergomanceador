"""Interaction engine for computing spell effects from element properties"""

from magic.element_loader import load_elements_from_json


class InteractionEngine:
    """
    Computes spell effects from element property combinations.
    Supports cancellation, amplification, and emergent spell behaviors.
    """

    def __init__(self):
        # Load elements from JSON
        self.elements = load_elements_from_json()

        # Define opposing element pairs (cancel each other)
        self.opposing_pairs = [
            ('fire', 'water'),
            ('fire', 'ice'),
            ('earth', 'air'),
            ('lightning', 'earth'),  # Lightning grounded by earth
            ('light', 'shadow')      # Opposite polarities
        ]

    def compute_interaction(self, element_names):
        """
        Generate spell effect from element properties.
        Returns complete spell descriptor with behavior, damage, speed, area, etc.
        """
        if not element_names:
            return None

        # Get element objects (maintain order for queueing)
        elems = [self.elements[name] for name in element_names if name in self.elements]
        if not elems:
            return None

        # 1. Check element cancellations (opposing elements reduce damage)
        cancellation_mult = self._check_cancellation(elems)

        # 2. Compute polarity interactions (opposite polarities amplify)
        polarity_mult = self._compute_polarity_bonus(elems)

        # 3. Calculate combined physical properties
        avg_temp = sum(e.temperature for e in elems) / len(elems)
        total_energy = sum(e.energy for e in elems)
        avg_density = sum(e.density for e in elems) / len(elems)
        avg_volatility = sum(e.volatility for e in elems) / len(elems)
        states = [e.state for e in elems]
        all_tags = set()
        for e in elems:
            all_tags.update(e.tags)

        # Temperature differential for phase-change interactions
        temp_range = max(e.temperature for e in elems) - min(e.temperature for e in elems)

        # 4. Apply multipliers to energy
        modified_energy = total_energy * cancellation_mult * polarity_mult

        # 5. Determine spell behavior from properties
        behavior = self._determine_behavior(elems, states, all_tags, modified_energy, avg_volatility)

        # 6. Compute derived stats
        damage = int(modified_energy * 0.6)  # 60% of energy becomes damage
        projectile_speed = (1.0 - avg_density) * 10  # Low density = fast (0.1 density → 9 speed)
        area = self._compute_area(behavior, avg_volatility, states)
        duration = self._compute_duration(behavior, states)

        # 7. Generate procedural spell name
        spell_name = self._generate_name(elems, behavior, temp_range, states, all_tags)

        # 8. Calculate spell color (blend element colors)
        spell_color = self._blend_colors(elems)

        # Return complete spell descriptor
        return {
            'name': spell_name,
            'behavior': behavior,
            'damage': damage,
            'speed': projectile_speed,
            'area': area,
            'duration': duration,
            'color': spell_color,
            'effects': list(all_tags),
            'properties': {
                'temperature': avg_temp,
                'energy': modified_energy,
                'temp_differential': temp_range,
                'density': avg_density,
                'volatility': avg_volatility,
                'cancellation_mult': cancellation_mult,
                'polarity_mult': polarity_mult
            }
        }

    def _check_cancellation(self, elems):
        """
        Check if opposing elements cancel each other.
        Returns damage multiplier (0.5 per cancellation).
        """
        elem_names = set(e.name for e in elems)
        cancellation_count = 0

        for pair in self.opposing_pairs:
            if pair[0] in elem_names and pair[1] in elem_names:
                cancellation_count += 1

        # Each cancellation reduces damage by 50%
        return 0.5 ** cancellation_count

    def _compute_polarity_bonus(self, elems):
        """
        Opposite polarities amplify damage (positive + negative = 2x).
        Returns energy multiplier.
        """
        polarities = [e.polarity for e in elems]

        # Check if both positive and negative exist
        has_positive = 'positive' in polarities
        has_negative = 'negative' in polarities

        if has_positive and has_negative:
            return 2.0  # Polarity clash amplifies
        return 1.0  # No amplification

    def _determine_behavior(self, elems, states, tags, energy, volatility):
        """
        Determine spell behavior type from element properties.
        Returns: 'projectile', 'beam', 'aoe', 'area_denial', 'buff', 'homing'
        """
        # Self-buff if single element + defensive tag
        if len(elems) == 1 and 'defensive' in tags:
            return 'buff'

        # Beam if instant movement + high energy
        if any(e.movement == 'instant' for e in elems) and energy > 100:
            return 'beam'

        # Area denial if solid/liquid state + low volatility (persistent zones)
        if ('solid' in states or 'liquid' in states) and volatility < 0.3:
            return 'area_denial'

        # AoE explosion if high volatility
        if volatility > 0.6:
            return 'aoe'

        # Homing if has swift tag + air/gas element
        if 'swift' in tags and 'gas' in states:
            return 'homing'

        # Default: projectile
        return 'projectile'

    def _compute_area(self, behavior, volatility, states):
        """
        Compute area of effect based on behavior and properties.
        """
        base_area = 2.0

        # Behavior modifiers
        if behavior == 'aoe':
            base_area = 5.0 + (volatility * 5)  # High volatility = bigger explosion
        elif behavior == 'area_denial':
            base_area = 4.0
        elif behavior == 'beam':
            base_area = 1.0  # Narrow beam
        elif behavior == 'buff':
            base_area = 0.5  # Self-only

        # State modifiers
        if 'gas' in states:
            base_area += 2
        if 'plasma' in states:
            base_area += 1.5

        return round(base_area, 1)

    def _compute_duration(self, behavior, states):
        """
        Compute effect duration based on behavior and states.
        """
        base_duration = 1.0

        # Behavior modifiers
        if behavior == 'area_denial':
            base_duration = 5.0  # Long-lasting zones
        elif behavior == 'buff':
            base_duration = 3.0  # Buffs last a while
        elif behavior == 'aoe':
            base_duration = 0.5  # Instant explosion

        # State modifiers
        if 'solid' in states:
            base_duration += 2.0
        if 'liquid' in states:
            base_duration += 0.5

        return round(base_duration, 1)

    def _generate_name(self, elems, behavior, temp_diff, states, tags):
        """
        Generate procedural spell name from properties.
        """
        # Special combinations (temperature-based phase changes)
        if temp_diff > 500:
            if 'hot' in tags and 'cold' in tags:
                return 'Steam Explosion'
            if 'hot' in tags and 'solid' in states:
                return 'Lava Flow'

        # Behavior-specific names
        if behavior == 'beam':
            if 'lightning' in [e.name for e in elems]:
                return 'Lightning Bolt'
            if 'light' in [e.name for e in elems]:
                return 'Light Beam'
            return 'Arcane Ray'

        if behavior == 'area_denial':
            if 'ice' in [e.name for e in elems]:
                return 'Ice Wall'
            if 'fire' in [e.name for e in elems]:
                return 'Fire Wall'
            if 'earth' in [e.name for e in elems]:
                return 'Stone Barrier'
            return 'Elemental Zone'

        if behavior == 'buff':
            if 'earth' in [e.name for e in elems]:
                return 'Stone Skin'
            if 'nature' in [e.name for e in elems]:
                return "Nature's Blessing"
            return 'Protective Ward'

        # Single element spells
        if len(elems) == 1:
            elem = elems[0]
            spell_names = {
                'fire': 'Fire Blast',
                'lightning': 'Chain Lightning',
                'water': 'Water Stream',
                'ice': 'Ice Shard',
                'earth': 'Boulder Throw',
                'nature': 'Thorn Whip',
                'arcane': 'Arcane Missile',
                'light': 'Holy Light',
                'shadow': 'Shadow Bolt'
            }
            return spell_names.get(elem.name, 'Elemental Blast')

        # State combinations
        if 'plasma' in states and 'gas' in states:
            return 'Fire Tornado'
        if 'liquid' in states and 'gas' in states:
            if 'cold' in tags:
                return 'Ice Storm'
            return 'Mist Cloud'

        # Tag-based combinations
        if 'destructive' in tags and 'swift' in tags:
            return 'Destruction Gale'
        if 'healing' in tags and 'purifying' in tags:
            return 'Divine Restoration'
        if 'draining' in tags and 'obscuring' in tags:
            return 'Shadow Drain'

        # All elements chaos
        if len(elems) >= 4:
            return 'Elemental Chaos'

    def _blend_colors(self, elems):
        """
        Blend element colors for spell visual.
        Returns RGB tuple (average of all element colors).
        """
        if not elems:
            return (255, 255, 255)  # White default

        # Average RGB values
        r = sum(e.color[0] for e in elems) // len(elems)
        g = sum(e.color[1] for e in elems) // len(elems)
        b = sum(e.color[2] for e in elems) // len(elems)

        return (r, g, b)
