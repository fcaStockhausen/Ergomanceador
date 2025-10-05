"""
Interaction engine using MANIFOLD-BASED classification.

This is the NEW version - uses PropertyVector + BehaviorManifold
instead of if-else chains for spell classification.

OLD version backed up as: interaction_engine_OLD.py
"""

from magic.element_loader import load_elements_from_json
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
from magic.spell_formulas import SpellFormulas
from magic.behavior_composer import BehaviorComposer
import os


class InteractionEngine:
    """
    Computes spell effects using manifold-based classification.

    NEW: Uses geometric classification in property space.
    Backwards compatible with old API.
    """

    def __init__(self):
        # Load elements from JSON
        self.elements = load_elements_from_json()

        # NEW: Manifold-based systems
        self.manifold = BehaviorManifold()
        self.formulas = SpellFormulas()
        self.composer = BehaviorComposer(self.manifold)  # Multi-label classification

        # Enable emergent blending (can be toggled via environment variable)
        self.use_emergent_blending = os.environ.get('EMERGENT_BLENDING', '1') == '1'

        # Keep old opposing pairs for reference (not used in classification anymore)
        self.opposing_pairs = [
            ('fire', 'water'),
            ('fire', 'ice'),
            ('earth', 'air'),
            ('lightning', 'earth'),
            ('light', 'shadow')
        ]

    def compute_interaction(self, element_names):
        """
        Generate spell effect from element properties.

        NEW: Uses manifold classification instead of if-else chains.

        Returns complete spell descriptor with behavior, damage, speed, area, etc.
        """
        if not element_names:
            return None

        # Get element objects (maintain order for queueing)
        elems = [self.elements[name] for name in element_names if name in self.elements]
        if not elems:
            return None

        # ===== NEW: MANIFOLD-BASED CLASSIFICATION =====

        # 1. Compute property vector (12D space)
        vector = PropertyVectorComputer.compute(elems)

        # 2. Multi-label classification (if enabled)
        if self.use_emergent_blending:
            # EMERGENT: Multiple behaviors activate, blend stats
            activations = self.composer.classify_multi(vector)
            weights = self.composer.get_behavior_weights(activations)

            # Primary behavior for game logic
            behavior = self.composer.get_primary_behavior(activations)
            modifiers = self.composer.get_modifiers(activations)

            # EMERGENT STAT BLENDING: Weighted average from all activated behaviors
            damage = sum(weights[b] * self.formulas.compute_damage(vector, b) for b in weights)
            speed = sum(weights[b] * self.formulas.compute_speed(vector, b) for b in weights)
            area = sum(weights[b] * self.formulas.compute_area(vector, b) for b in weights)
            duration = sum(weights[b] * self.formulas.compute_duration(vector, b) for b in weights)
            mana_cost = sum(weights[b] * self.formulas.compute_mana_cost(vector, b) for b in weights)
            knockback = self.formulas.compute_knockback(vector)  # Not blended (always from vector)

            probabilities = {b: act.strength for act in activations for b in [act.behavior]}
        else:
            # SINGLE-LABEL: Nearest prototype wins
            behavior = self.manifold.classify(vector)
            probabilities = self.manifold.get_behavior_probabilities(vector)
            modifiers = []
            activations = []
            weights = {behavior: 1.0}

            # Stats from single behavior
            damage = self.formulas.compute_damage(vector, behavior)
            speed = self.formulas.compute_speed(vector, behavior)
            area = self.formulas.compute_area(vector, behavior)
            duration = self.formulas.compute_duration(vector, behavior)
            mana_cost = self.formulas.compute_mana_cost(vector, behavior)
            knockback = self.formulas.compute_knockback(vector)

        # ===== KEEP OLD: Spell naming and visuals =====

        # 5. Generate procedural spell name (keep old logic)
        states = [e.state for e in elems]
        all_tags = set()
        for e in elems:
            all_tags.update(e.tags)
        spell_name = self._generate_name(elems, behavior, vector.temp_differential, states, all_tags)

        # 6. Blend element colors (keep old logic)
        spell_color = self._blend_colors(elems)

        # Return complete spell descriptor (enhanced with multi-label data)
        return {
            'name': spell_name,
            'behavior': behavior,  # Primary behavior (backward compatible)
            'modifiers': modifiers,  # NEW: Secondary behaviors
            'activations': activations,  # NEW: Full activation data
            'weights': weights,  # NEW: Behavior weights for advanced use
            'damage': damage,  # EMERGENT if blending enabled
            'speed': speed,  # EMERGENT if blending enabled
            'area': area,  # EMERGENT if blending enabled
            'duration': duration,  # EMERGENT if blending enabled
            'mana_cost': mana_cost,  # EMERGENT if blending enabled
            'knockback': knockback,
            'color': spell_color,
            'effects': list(all_tags),
            'elements': element_names,
            'emergent_blending': self.use_emergent_blending,  # NEW: Flag for UI
            'property_vector': vector,  # NEW: Property vector for emergent behaviors (split count, etc)
            'properties': {
                'temperature': vector.avg_temperature,
                'energy': vector.total_energy,
                'temp_differential': vector.temp_differential,
                'density': vector.avg_density,
                'volatility': vector.volatility_index,
                'cancellation_mult': 1.0,  # Not used anymore
                'polarity_mult': 1.0 + abs(vector.polarity_tension),
            },
            # NEW: Include property vector and probabilities
            'property_vector': vector,
            'behavior_probabilities': probabilities,
            'knockback': knockback,
        }

    def _generate_name(self, elems, behavior, temp_diff, states, tags):
        """
        Generate procedural spell name from properties.
        (KEPT FROM OLD VERSION - same naming logic)
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

        if behavior == 'heal':
            if 'nature' in [e.name for e in elems]:
                return 'Healing Touch'
            if 'light' in [e.name for e in elems]:
                return 'Divine Heal'
            return 'Restoration'

        if behavior == 'buff':
            if 'earth' in [e.name for e in elems]:
                return 'Stone Skin'
            if 'nature' in [e.name for e in elems]:
                return "Nature's Blessing"
            return 'Protective Ward'

        if behavior == 'homing':
            if 'arcane' in [e.name for e in elems]:
                return 'Arcane Seeker'
            return 'Tracking Bolt'

        if behavior == 'chain':
            if 'lightning' in [e.name for e in elems]:
                return 'Chain Lightning'
            return 'Bouncing Orb'

        # Single element spells
        if len(elems) == 1:
            elem = elems[0]
            spell_names = {
                'fire': 'Fire Blast',
                'lightning': 'Lightning Strike',
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

        # AOE default
        if behavior == 'aoe':
            return 'Explosive Blast'

        # Projectile default
        return 'Elemental Projectile'

    def _blend_colors(self, elems):
        """
        Blend element colors for spell visual.
        Returns RGB tuple (average of all element colors).
        (KEPT FROM OLD VERSION)
        """
        if not elems:
            return (255, 255, 255)  # White default

        # Average RGB values
        r = sum(e.color[0] for e in elems) // len(elems)
        g = sum(e.color[1] for e in elems) // len(elems)
        b = sum(e.color[2] for e in elems) // len(elems)

        return (r, g, b)
