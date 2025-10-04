"""Integration tests for combat system - full gameplay loop"""

import pytest


class TestCombatFlow:
    """Test complete combat loop: cast spell -> projectile -> hit enemy -> damage -> death"""

    def test_spell_damages_enemy(self, magic_system, enemy, effect_manager):
        """Full flow: queue element, cast, projectile hits, enemy takes damage"""
        # Arrange: Setup enemy and effect manager
        effect_manager.enemies = [enemy]
        initial_health = enemy.health.current_health

        # Queue fire element
        magic_system.queue_element('fire')

        # Cast spell at enemy position
        spell_data = magic_system.cast_spell()
        assert spell_data is not None, "Should generate spell"

        # Spawn projectile aimed at enemy
        effect_manager.spawn_spell_effect(
            player_x=10, player_y=10,
            target_x=enemy.cart_x, target_y=enemy.cart_y,
            spell_data=spell_data
        )

        # Act: Update projectile until it reaches enemy
        for _ in range(100):  # Max 100 frames
            effect_manager.update(0.016)  # ~60 FPS
            if enemy.health.current_health < initial_health:
                break  # Hit detected!

        # Assert: Enemy should have taken damage
        assert enemy.health.current_health < initial_health, "Enemy should be damaged"
        assert spell_data['damage'] > 0, "Spell should have damage"
        assert initial_health - enemy.health.current_health == spell_data['damage'], "Should deal correct damage"

    def test_multiple_hits_accumulate_damage(self, magic_system, enemy, effect_manager):
        """Multiple spell hits should accumulate damage"""
        effect_manager.enemies = [enemy]

        # Cast 3 fire spells
        for _ in range(3):
            magic_system.queue_element('fire')
            spell = magic_system.cast_spell()

            effect_manager.spawn_spell_effect(
                10, 10, enemy.cart_x, enemy.cart_y, spell
            )

            # Wait for hit
            for _ in range(100):
                effect_manager.update(0.016)

        # Enemy should have taken multiple hits
        assert enemy.health.current_health < 100, "Should be damaged"
        assert enemy.health.current_health > 0, "Should still be alive (fire does ~16 damage)"

    def test_enough_damage_kills_enemy(self, magic_system, enemy, effect_manager):
        """Enough damage should kill enemy"""
        effect_manager.enemies = [enemy]

        # Cast enough spells to kill (100 HP / ~16 dmg = ~7 spells)
        for _ in range(10):  # Cast more than needed to ensure death
            magic_system.queue_element('fire')
            magic_system.queue_element('fire')  # Double fire for more damage
            spell = magic_system.cast_spell()

            effect_manager.spawn_spell_effect(
                10, 10, enemy.cart_x, enemy.cart_y, spell
            )

            # Wait for hit
            for _ in range(100):
                effect_manager.update(0.016)

            if not enemy.health.is_alive:
                break

        # Assert: Enemy should be dead
        assert enemy.health.is_alive is False, "Enemy should be dead"
        assert enemy.health.current_health == 0, "Health should be 0"

    def test_enemy_death_triggers_callback(self):
        """Enemy death should trigger on_death callback"""
        from entities.enemy import Enemy

        death_triggered = []

        def custom_death():
            death_triggered.append(True)

        enemy = Enemy(15, 15, max_health=10)
        enemy.health.on_death_callback = custom_death

        # Deal fatal damage
        enemy.health.damage(10)

        assert len(death_triggered) == 1, "Death callback should fire"
        assert enemy.health.is_alive is False, "Enemy should be dead"


class TestProjectileCollision:
    """Test projectile collision detection"""

    def test_projectile_spawns_at_player_position(self, magic_system, effect_manager):
        """Projectile should spawn at player position"""
        magic_system.queue_element('fire')
        spell = magic_system.cast_spell()

        effect_manager.spawn_spell_effect(
            player_x=5, player_y=5,
            target_x=10, target_y=10,
            spell_data=spell
        )

        assert len(effect_manager.projectiles) == 1, "Should spawn 1 projectile"
        proj = effect_manager.projectiles[0]
        assert abs(proj.cart_x - 5.0) < 0.1, "Should start at player X"
        assert abs(proj.cart_y - 5.0) < 0.1, "Should start at player Y"

    def test_projectile_moves_toward_target(self, magic_system, effect_manager):
        """Projectile should move toward target"""
        magic_system.queue_element('fire')
        spell = magic_system.cast_spell()

        effect_manager.spawn_spell_effect(
            player_x=0, player_y=0,
            target_x=10, target_y=0,  # To the right
            spell_data=spell
        )

        proj = effect_manager.projectiles[0]
        initial_x = proj.cart_x

        effect_manager.update(0.1)  # Update

        assert proj.cart_x > initial_x, "Projectile should move right"

    def test_projectile_dies_on_hit(self, magic_system, enemy, effect_manager):
        """Projectile should be removed after hitting enemy"""
        effect_manager.enemies = [enemy]

        magic_system.queue_element('fire')
        spell = magic_system.cast_spell()

        effect_manager.spawn_spell_effect(
            10, 10, enemy.cart_x, enemy.cart_y, spell
        )

        # Update until hit
        for _ in range(100):
            effect_manager.update(0.016)
            if len(effect_manager.projectiles) == 0:
                break

        # Projectile should be removed
        assert len(effect_manager.projectiles) == 0, "Projectile should be removed after hit"

    def test_projectile_misses_distant_enemy(self, magic_system, enemy, effect_manager):
        """Projectile aimed away from enemy should miss"""
        effect_manager.enemies = [enemy]  # Enemy at (15, 15)

        magic_system.queue_element('fire')
        spell = magic_system.cast_spell()

        # Aim away from enemy (toward 0, 0)
        effect_manager.spawn_spell_effect(
            10, 10, 0, 0, spell
        )

        initial_health = enemy.health.current_health

        # Update for a while
        for _ in range(50):
            effect_manager.update(0.016)

        # Enemy should not be hit
        assert enemy.health.current_health == initial_health, "Enemy should not be damaged"


class TestCombatPolish:
    """Test combat polish features: damage numbers, knockback, etc."""

    def test_damage_number_spawns_on_hit(self, magic_system, enemy, effect_manager):
        """Damage number should spawn when enemy is hit"""
        effect_manager.enemies = [enemy]

        magic_system.queue_element('fire')
        spell = magic_system.cast_spell()

        effect_manager.spawn_spell_effect(
            10, 10, enemy.cart_x, enemy.cart_y, spell
        )

        # Update until hit
        for _ in range(100):
            effect_manager.update(0.016)
            if len(effect_manager.damage_numbers.numbers) > 0:
                break

        # Damage number should spawn
        assert len(effect_manager.damage_numbers.numbers) > 0, "Damage number should spawn on hit"

    def test_knockback_applied_on_hit(self, magic_system, enemy, effect_manager):
        """Enemy should be knocked back when hit"""
        effect_manager.enemies = [enemy]
        initial_x = enemy.cart_x
        initial_y = enemy.cart_y

        magic_system.queue_element('fire')
        spell = magic_system.cast_spell()

        # Cast from left of enemy (projectile travels right)
        effect_manager.spawn_spell_effect(
            enemy.cart_x - 5, enemy.cart_y,  # 5 units to the left
            enemy.cart_x, enemy.cart_y,
            spell
        )

        # Update until hit
        for _ in range(100):
            effect_manager.update(0.016)
            if enemy.knockback_velocity_x != 0 or enemy.knockback_velocity_y != 0:
                break

        # Enemy should have knockback velocity
        assert enemy.knockback_velocity_x != 0 or enemy.knockback_velocity_y != 0, \
            "Enemy should have knockback velocity"

        # Update enemy to move from knockback
        for _ in range(10):
            enemy.update(0.016)

        # Enemy should have moved
        assert enemy.cart_x != initial_x or enemy.cart_y != initial_y, \
            "Enemy should be knocked back"
