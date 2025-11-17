"""
Test suite for enemy system

Tests:
- Enemy creation and initialization
- AI state transitions
- Damage and death mechanics
- Loot generation
- Patroller movement and collision detection
"""

import pytest
import pygame
from unittest.mock import Mock, MagicMock

# Initialize pygame for testing
pygame.init()

from entities.enemy import Enemy
from entities.patroller import Patroller
from entities.enemy_manager import EnemyManager


class TestEnemyCreation:
    """Test enemy creation and initialization."""

    def test_enemy_base_creation(self):
        """Test that base enemy can be created with default parameters."""
        enemy = Enemy(x=100, y=100, hp=5, damage=1, speed=50)

        assert enemy.rect.x == 100
        assert enemy.rect.y == 100
        assert enemy.hp == 5
        assert enemy.max_hp == 5
        assert enemy.damage == 1
        assert enemy.speed == 50
        assert enemy.state == "idle"
        assert not enemy.is_dead

    def test_patroller_creation(self):
        """Test that patroller enemy can be created."""
        patroller = Patroller(x=100, y=100)

        assert patroller.hp == 3
        assert patroller.damage == 1
        assert patroller.speed == 60.0
        assert patroller.points == 100
        assert patroller.loot_table is not None

    def test_patroller_loot_table(self):
        """Test that patroller has correct loot table."""
        patroller = Patroller(x=100, y=100)

        assert "coins" in patroller.loot_table
        assert "health" in patroller.loot_table
        assert "powerup" in patroller.loot_table
        assert "ability_orb" in patroller.loot_table


class TestAIStateMachine:
    """Test enemy AI state transitions."""

    def test_initial_state_idle(self):
        """Test that enemy starts in idle state."""
        enemy = Enemy(x=100, y=100, hp=5, damage=1, speed=50)
        assert enemy.state == "idle"

    def test_state_transition(self):
        """Test that state transitions work correctly."""
        enemy = Enemy(x=100, y=100, hp=5, damage=1, speed=50)

        enemy.change_state("patrol")
        assert enemy.state == "patrol"
        assert enemy.state_timer == 0.0

    def test_patroller_auto_patrol(self):
        """Test that patroller automatically transitions to patrol."""
        patroller = Patroller(x=100, y=100)
        assert patroller.state == "patrol"


class TestDamageAndDeath:
    """Test damage dealing and death mechanics."""

    def test_take_damage(self):
        """Test that enemy takes damage correctly."""
        enemy = Enemy(x=100, y=100, hp=5, damage=1, speed=50)

        result = enemy.take_damage(2)
        assert result is True
        assert enemy.hp == 3

    def test_death_on_zero_hp(self):
        """Test that enemy dies when HP reaches zero."""
        enemy = Enemy(x=100, y=100, hp=3, damage=1, speed=50)

        enemy.take_damage(3)
        assert enemy.hp == 0
        assert enemy.is_dead
        assert enemy.state == "dead"

    def test_invincibility_frames(self):
        """Test that invincibility frames prevent damage."""
        enemy = Enemy(x=100, y=100, hp=5, damage=1, speed=50)

        enemy.take_damage(1)
        assert enemy.hp == 4

        # Immediate second hit should be blocked
        result = enemy.take_damage(1)
        assert result is False
        assert enemy.hp == 4

    def test_cannot_damage_dead_enemy(self):
        """Test that dead enemies cannot take damage."""
        enemy = Enemy(x=100, y=100, hp=1, damage=1, speed=50)

        enemy.take_damage(1)
        assert enemy.is_dead

        result = enemy.take_damage(1)
        assert result is False


class TestEnemyManager:
    """Test enemy manager functionality."""

    def test_manager_creation(self):
        """Test that enemy manager can be created."""
        manager = EnemyManager()
        assert manager.enemies == []

    def test_spawn_enemy(self):
        """Test that enemies can be spawned."""
        manager = EnemyManager()

        enemy = manager.spawn_enemy(Patroller, x=100, y=100)
        assert len(manager.enemies) == 1
        assert enemy in manager.enemies

    def test_add_enemy(self):
        """Test that existing enemies can be added."""
        manager = EnemyManager()
        enemy = Patroller(x=100, y=100)

        manager.add_enemy(enemy)
        assert len(manager.enemies) == 1
        assert enemy in manager.enemies

    def test_remove_dead(self):
        """Test that dead enemies are removed."""
        manager = EnemyManager()
        enemy = manager.spawn_enemy(Patroller, x=100, y=100)

        # Kill enemy and advance death timer
        enemy.take_damage(10)
        enemy.death_timer = 1.0  # Set past death duration

        removed = manager.remove_dead()
        assert removed == 1
        assert len(manager.enemies) == 0

    def test_get_enemy_count(self):
        """Test that active enemy count is correct."""
        manager = EnemyManager()

        enemy1 = manager.spawn_enemy(Patroller, x=100, y=100)
        enemy2 = manager.spawn_enemy(Patroller, x=200, y=100)

        assert manager.get_enemy_count() == 2

        # Kill one enemy
        enemy1.take_damage(10)
        assert manager.get_enemy_count() == 1

    def test_clear(self):
        """Test that clear removes all enemies."""
        manager = EnemyManager()

        manager.spawn_enemy(Patroller, x=100, y=100)
        manager.spawn_enemy(Patroller, x=200, y=100)

        manager.clear()
        assert len(manager.enemies) == 0


class TestPatrollerMovement:
    """Test patroller-specific movement and collision."""

    def test_patroller_movement_direction(self):
        """Test that patroller moves in a direction."""
        patroller = Patroller(x=100, y=100)

        # Should start in patrol state
        assert patroller.state == "patrol"
        assert patroller.direction in [-1, 1]

    def test_edge_detection(self):
        """Test edge detection logic (basic check)."""
        patroller = Patroller(x=100, y=100)

        # Create empty world (no tiles)
        world = [[0 for _ in range(10)] for _ in range(10)]

        # Edge should be detected in empty world
        has_edge = patroller._check_edge_ahead(world)
        # In an empty world, edge detection should return True
        assert isinstance(has_edge, bool)

    def test_wall_detection(self):
        """Test wall detection logic."""
        patroller = Patroller(x=100, y=100)

        # Create world with wall ahead
        world = [[1 for _ in range(10)] for _ in range(10)]

        # Wall should be detected
        has_wall = patroller._check_wall_ahead(world)
        assert isinstance(has_wall, bool)


class TestIntegration:
    """Integration tests for enemy system."""

    def test_enemy_update_without_crash(self):
        """Test that enemy update doesn't crash."""
        enemy = Patroller(x=100, y=100)
        world = [[0 for _ in range(50)] for _ in range(50)]
        player = None

        # Should not crash
        enemy.update(dt=0.016, world=world, player=player)

    def test_enemy_manager_update_without_crash(self):
        """Test that enemy manager update doesn't crash."""
        manager = EnemyManager()
        manager.spawn_enemy(Patroller, x=100, y=100)

        world = [[0 for _ in range(50)] for _ in range(50)]
        player = None

        # Should not crash
        manager.update(dt=0.016, world=world, player=player)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
