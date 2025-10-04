"""Unit tests for Health component"""

import pytest


class TestHealthBasics:
    """Test basic health functionality"""

    def test_health_initialization(self, health_component):
        """Should initialize with max health"""
        assert health_component.max_health == 100
        assert health_component.current_health == 100
        assert health_component.is_alive is True

    def test_take_damage(self, health_component):
        """Should reduce health when damaged"""
        health_component.damage(30)

        assert health_component.current_health == 70, "Should have 70 HP left"
        assert health_component.is_alive is True, "Should still be alive"

    def test_take_fatal_damage(self, health_component):
        """Should die when health reaches 0"""
        health_component.damage(100)

        assert health_component.current_health == 0, "Should have 0 HP"
        assert health_component.is_alive is False, "Should be dead"

    def test_take_overkill_damage(self, health_component):
        """Health should not go below 0"""
        health_component.damage(150)

        assert health_component.current_health == 0, "Should cap at 0"
        assert health_component.is_alive is False, "Should be dead"

    def test_multiple_damage_instances(self, health_component):
        """Should accumulate damage correctly"""
        health_component.damage(20)
        health_component.damage(30)
        health_component.damage(10)

        assert health_component.current_health == 40, "Should have 40 HP left"

    def test_health_percentage(self, health_component):
        """Should calculate health percentage correctly"""
        health_component.damage(25)

        percentage = health_component.get_health_percentage()
        assert percentage == 0.75, "Should be 75% health"

    def test_health_percentage_at_zero(self, health_component):
        """Health percentage should be 0 when dead"""
        health_component.damage(100)

        percentage = health_component.get_health_percentage()
        assert percentage == 0.0, "Should be 0% when dead"


class TestHealthCallbacks:
    """Test health callback system"""

    def test_on_damage_callback(self):
        """on_damage callback should fire when damaged"""
        damage_taken = []

        def record_damage(amount):
            damage_taken.append(amount)

        from components.health import Health
        health = Health(max_health=100, on_damage=record_damage)

        health.damage(25)
        health.damage(10)

        assert len(damage_taken) == 2, "Should have 2 damage events"
        assert damage_taken == [25, 10], "Should record correct damage amounts"

    def test_on_death_callback(self):
        """on_death callback should fire once when killed"""
        death_count = []

        def record_death():
            death_count.append(1)

        from components.health import Health
        health = Health(max_health=100, on_death=record_death)

        health.damage(50)
        assert len(death_count) == 0, "Should not trigger death yet"

        health.damage(50)
        assert len(death_count) == 1, "Should trigger death"

    def test_death_callback_only_once(self):
        """Death callback should only fire once"""
        death_count = []

        def record_death():
            death_count.append(1)

        from components.health import Health
        health = Health(max_health=100, on_death=record_death)

        health.damage(100)
        health.damage(50)  # Damage after death
        health.damage(50)  # More damage after death

        assert len(death_count) == 1, "Should only trigger death once"

    def test_damage_after_death_does_nothing(self):
        """Damaging a dead entity should do nothing"""
        from components.health import Health
        health = Health(max_health=100)

        health.damage(100)  # Kill
        result = health.damage(50)  # Damage corpse

        assert result is False, "Should return False when damaging dead entity"
        assert health.current_health == 0, "Health should stay at 0"


class TestHealthDamageFlash:
    """Test damage flash visual effect"""

    def test_damage_flash_timer_set(self, health_component):
        """damage_flash_timer should be set when damaged"""
        health_component.damage(10)

        assert health_component.damage_flash_timer > 0, "Flash timer should be active"

    def test_is_flashing_after_damage(self, health_component):
        """is_flashing() should return True immediately after damage"""
        health_component.damage(10)

        assert health_component.is_flashing() is True, "Should be flashing after damage"

    def test_flash_timer_decreases(self, health_component):
        """Flash timer should decrease over time"""
        health_component.damage(10)
        initial_timer = health_component.damage_flash_timer

        health_component.update(0.05)  # Update 50ms

        assert health_component.damage_flash_timer < initial_timer, "Timer should decrease"

    def test_flash_ends_after_duration(self, health_component):
        """Flash should end after timer expires"""
        health_component.damage(10)

        health_component.update(0.2)  # Update 200ms (longer than flash duration)

        assert health_component.is_flashing() is False, "Flash should end"
        assert health_component.damage_flash_timer == 0, "Timer should be 0"
