"""Pytest configuration and fixtures for Karaokeficador tests"""

import os
import sys
import pytest

# Suppress pygame welcome message in tests
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame

# Initialize pygame once for all tests
pygame.init()


@pytest.fixture
def magic_system():
    """Create a fresh MagicSystem instance"""
    from magic.magic_system import MagicSystem
    return MagicSystem()


@pytest.fixture
def player():
    """Create a fresh Player instance at default position"""
    from entities.player import Player
    return Player()


@pytest.fixture
def target():
    """Create a fresh Target instance"""
    from entities.target_cursor import Target
    return Target()


@pytest.fixture
def enemy():
    """Create a fresh Enemy instance"""
    from entities.enemy import Enemy
    return Enemy(15, 15, max_health=100)


@pytest.fixture
def camera():
    """Create a fresh Camera instance"""
    from core.camera import Camera
    return Camera()


@pytest.fixture
def health_component():
    """Create a fresh Health component"""
    from components.health import Health
    return Health(max_health=100)


@pytest.fixture
def effect_manager():
    """Create a fresh EffectManager"""
    from rendering.effects.effect_manager import EffectManager
    return EffectManager()


@pytest.fixture
def interaction_engine():
    """Create a fresh InteractionEngine"""
    from magic.interaction_engine import InteractionEngine
    return InteractionEngine()


@pytest.fixture
def element_loader():
    """Get ElementLoader instance (singleton)"""
    from magic.element_loader import ElementLoader
    return ElementLoader()


# Cleanup after all tests
def pytest_sessionfinish(session, exitstatus):
    """Cleanup pygame after all tests"""
    pygame.quit()
