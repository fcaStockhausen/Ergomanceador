"""Unit tests for MagicSystem - element queueing and spell casting"""

import pytest


class TestElementQueueing:
    """Test element queue management"""

    def test_queue_single_element(self, magic_system):
        """Should queue a single element"""
        result = magic_system.queue_element('fire')

        assert result is True, "Should successfully queue fire"
        assert len(magic_system.element_queue) == 1, "Queue should have 1 element"
        assert magic_system.element_queue[0] == 'fire', "First element should be fire"

    def test_queue_multiple_elements(self, magic_system):
        """Should queue multiple elements up to max"""
        magic_system.queue_element('fire')
        magic_system.queue_element('water')
        magic_system.queue_element('earth')
        magic_system.queue_element('nature')

        assert len(magic_system.element_queue) == 4, "Should have 4 elements queued"
        assert magic_system.element_queue == ['fire', 'water', 'earth', 'nature']

    def test_queue_exceeds_max(self, magic_system):
        """Should not queue beyond max queue size"""
        # Fill queue to max (4)
        for elem in ['fire', 'water', 'earth', 'nature']:
            magic_system.queue_element(elem)

        # Try to add 5th element
        result = magic_system.queue_element('arcane')

        assert result is False, "Should reject 5th element"
        assert len(magic_system.element_queue) == 4, "Queue should still be 4"
        assert 'arcane' not in magic_system.element_queue, "Arcane should not be queued"

    def test_queue_invalid_element(self, magic_system):
        """Should reject invalid element names"""
        result = magic_system.queue_element('invalid_element_xyz')

        assert result is False, "Should reject invalid element"
        assert len(magic_system.element_queue) == 0, "Queue should be empty"

    def test_remove_last_element(self, magic_system):
        """Should remove last element from queue"""
        magic_system.queue_element('fire')
        magic_system.queue_element('water')

        magic_system.remove_last_element()

        assert len(magic_system.element_queue) == 1, "Should have 1 element left"
        assert magic_system.element_queue[0] == 'fire', "Fire should remain"

    def test_clear_queue(self, magic_system):
        """Should clear entire queue"""
        magic_system.queue_element('fire')
        magic_system.queue_element('water')
        magic_system.queue_element('earth')

        magic_system.clear_queue()

        assert len(magic_system.element_queue) == 0, "Queue should be empty"


class TestSpellCasting:
    """Test spell generation and casting"""

    def test_cast_single_element_spell(self, magic_system):
        """Should generate spell data from single element"""
        magic_system.queue_element('fire')
        spell = magic_system.cast_spell()

        assert spell is not None, "Should return spell data"
        assert 'name' in spell, "Should have spell name"
        assert 'damage' in spell, "Should have damage"
        assert 'behavior' in spell, "Should have behavior"
        assert 'color' in spell, "Should have color"
        assert spell['damage'] > 0, "Damage should be positive"

    def test_cast_combination_spell(self, magic_system):
        """Should generate combined spell from multiple elements"""
        magic_system.queue_element('fire')
        magic_system.queue_element('water')
        spell = magic_system.cast_spell()

        assert spell is not None, "Should return combination spell"
        assert 'fire' in spell['name'].lower() or 'water' in spell['name'].lower() or 'steam' in spell['name'].lower(), \
            "Spell name should reference elements or interaction"

    def test_cast_clears_queue(self, magic_system):
        """Should clear queue after casting"""
        magic_system.queue_element('fire')
        magic_system.queue_element('earth')

        magic_system.cast_spell()

        assert len(magic_system.element_queue) == 0, "Queue should be cleared after cast"

    def test_cast_empty_queue(self, magic_system):
        """Should return None when queue is empty"""
        spell = magic_system.cast_spell()

        assert spell is None, "Should return None with empty queue"

    def test_spell_damage_scales_with_elements(self, magic_system):
        """More elements should generally increase damage"""
        # Single element
        magic_system.queue_element('fire')
        spell1 = magic_system.cast_spell()
        damage1 = spell1['damage']

        # Three elements
        magic_system.queue_element('fire')
        magic_system.queue_element('fire')
        magic_system.queue_element('fire')
        spell3 = magic_system.cast_spell()
        damage3 = spell3['damage']

        assert damage3 > damage1, "3 elements should deal more damage than 1"

    def test_opposite_elements_create_interaction(self, magic_system):
        """Fire + Water should create steam/temperature interaction"""
        magic_system.queue_element('fire')
        magic_system.queue_element('water')
        spell = magic_system.cast_spell()

        assert spell is not None, "Should generate interaction spell"
        # Check that spell data exists (actual interaction verification is in integration tests)
        assert spell['damage'] > 0, "Interaction should have damage"


class TestElementCombinations:
    """Test specific element combinations"""

    @pytest.mark.parametrize("element", ['fire', 'water', 'earth', 'nature', 'arcane', 'light', 'shadow', 'lightning', 'ice'])
    def test_all_elements_can_be_queued(self, magic_system, element):
        """All valid elements should be queueable"""
        result = magic_system.queue_element(element)
        assert result is True, f"{element} should be queueable"

    def test_four_element_maximum(self, magic_system):
        """Should enforce 4 element maximum"""
        elements = ['fire', 'water', 'earth', 'nature', 'arcane']

        for i, elem in enumerate(elements):
            result = magic_system.queue_element(elem)
            if i < 4:
                assert result is True, f"Element {i+1} should queue"
            else:
                assert result is False, f"Element {i+1} should be rejected (over max)"
