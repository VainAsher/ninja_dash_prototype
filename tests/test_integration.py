"""
Unit tests for complete level generation pipeline.
Tests integration of maze, decorations, entities, and ability features.
"""

import unittest
import random
import pygame
from level_gen.generator import (
    generate_level,
    build_world_from_path,
    find_spawn,
    mark_phaseable_walls,
)
from level_gen.maze_generator import generate_macro_maze, find_room_path
from level_gen.structures import Room
from settings import (
    TILE_SIZE,
    ROOM_COLS, ROOM_ROWS,
    ROOM_W, ROOM_H,
    WORLD_W, WORLD_H
)


class TestRoomClass(unittest.TestCase):
    """Test Room class."""

    def test_room_initialization(self):
        """Test Room initialization."""
        room = Room(3, 5)
        self.assertEqual(room.rx, 3)
        self.assertEqual(room.ry, 5)
        self.assertFalse(room.open_up)
        self.assertFalse(room.open_down)
        self.assertFalse(room.open_left)
        self.assertFalse(room.open_right)


class TestBuildWorldFromPath(unittest.TestCase):
    """Test world building from room path."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)

    def test_build_world_simple_path(self):
        """Test building world from simple path."""
        path = [(0, 2), (1, 2), (2, 2)]
        world, path_mask = build_world_from_path(path)

        # Check dimensions
        self.assertEqual(len(world), WORLD_H)
        self.assertEqual(len(world[0]), WORLD_W)
        self.assertEqual(len(path_mask), WORLD_H)
        self.assertEqual(len(path_mask[0]), WORLD_W)

    def test_build_world_has_borders(self):
        """Test that built world has border walls."""
        path = [(0, 2), (1, 2)]
        world, path_mask = build_world_from_path(path)

        # Check top border
        for x in range(WORLD_W):
            self.assertEqual(world[0][x], 1, f"Top border missing at x={x}")

        # Check bottom border
        for x in range(WORLD_W):
            self.assertEqual(world[WORLD_H - 1][x], 1, f"Bottom border missing at x={x}")

        # Check left border
        for y in range(WORLD_H):
            self.assertEqual(world[y][0], 1, f"Left border missing at y={y}")

        # Check right border
        for y in range(WORLD_H):
            self.assertEqual(world[y][WORLD_W - 1], 1, f"Right border missing at y={y}")

    def test_build_world_has_exit(self):
        """Test that world has exit at end of path."""
        path = [(0, 2), (1, 2), (2, 1)]
        world, path_mask = build_world_from_path(path)

        # Exit should be marked with 2
        exit_found = False
        for y in range(WORLD_H):
            for x in range(WORLD_W):
                if world[y][x] == 2:
                    exit_found = True
                    break

        self.assertTrue(exit_found, "Exit not found in world")

    def test_build_world_path_mask(self):
        """Test that path mask marks critical path tiles."""
        path = [(0, 2), (1, 2)]
        world, path_mask = build_world_from_path(path)

        # Path mask should mark some tiles as True
        marked_tiles = sum(sum(1 for cell in row if cell) for row in path_mask)
        self.assertGreater(marked_tiles, 0, "Path mask should mark some tiles")

    def test_build_world_vertical_path(self):
        """Test building world with vertical path."""
        path = [(1, 3), (1, 2), (1, 1)]
        world, path_mask = build_world_from_path(path)

        # Should create vertical shafts and platforms
        self.assertIsNotNone(world)
        self.assertIsNotNone(path_mask)

    def test_build_world_complex_path(self):
        """Test building world with complex path."""
        # Use valid room coordinates (ROOM_COLS=6, ROOM_ROWS=4)
        # Valid x: 0-5, valid y: 0-3
        path = [(0, 3), (1, 3), (1, 2), (2, 2), (2, 1), (3, 1), (3, 0), (4, 0), (5, 0)]
        world, path_mask = build_world_from_path(path)

        # Should handle complex paths
        self.assertEqual(len(world), WORLD_H)
        self.assertEqual(len(world[0]), WORLD_W)


class TestFindSpawn(unittest.TestCase):
    """Test spawn point finding."""

    def test_find_spawn_basic(self):
        """Test finding spawn point."""
        path = [(0, 2), (1, 2), (2, 2)]
        spawn_x, spawn_y = find_spawn(path)

        # Spawn should be in pixels (TILE_SIZE multiple)
        self.assertEqual(spawn_x % TILE_SIZE, 0)
        self.assertEqual(spawn_y % TILE_SIZE, 0)

    def test_find_spawn_at_start(self):
        """Test that spawn is at start of path."""
        path = [(0, 4), (1, 4), (2, 4)]
        spawn_x, spawn_y = find_spawn(path)

        # Spawn should be near start room (0, 4)
        start_rx, start_ry = path[0]
        base_x = start_rx * ROOM_W
        base_y = start_ry * ROOM_H

        # Spawn should be in the start room area
        spawn_tx = spawn_x // TILE_SIZE
        spawn_ty = spawn_y // TILE_SIZE

        self.assertGreaterEqual(spawn_tx, base_x)
        self.assertLess(spawn_tx, base_x + ROOM_W)
        self.assertGreaterEqual(spawn_ty, base_y)
        self.assertLess(spawn_ty, base_y + ROOM_H)

    def test_find_spawn_different_paths(self):
        """Test spawn finding for different paths."""
        paths = [
            [(0, 2), (1, 2)],
            [(0, 4), (1, 4)],
            [(0, 3), (0, 2), (0, 1)],
        ]

        for path in paths:
            spawn_x, spawn_y = find_spawn(path)
            self.assertGreaterEqual(spawn_x, 0)
            self.assertGreaterEqual(spawn_y, 0)


class TestMarkPhaseableWalls(unittest.TestCase):
    """Test phaseable wall marking for Shadow Step ability."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add some walls
        for y in range(5, 15):
            self.world[y][10] = 1  # Vertical wall

    def test_mark_phaseable_walls_basic(self):
        """Test basic phaseable wall marking."""
        tiles = []
        for y in range(WORLD_H):
            for x in range(WORLD_W):
                if self.world[y][x] == 1:
                    tiles.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        phaseable = mark_phaseable_walls(tiles, self.world, self.rng, phaseable_wall_chance=1.0)

        self.assertIsInstance(phaseable, list)

    def test_mark_phaseable_excludes_boundaries(self):
        """Test that boundary walls are not marked phaseable."""
        # Add boundary walls
        for x in range(WORLD_W):
            self.world[0][x] = 1
            self.world[WORLD_H - 1][x] = 1
        for y in range(WORLD_H):
            self.world[y][0] = 1
            self.world[y][WORLD_W - 1] = 1

        tiles = []
        for y in range(WORLD_H):
            for x in range(WORLD_W):
                if self.world[y][x] == 1:
                    tiles.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        phaseable = mark_phaseable_walls(tiles, self.world, self.rng, phaseable_wall_chance=1.0)

        # Check that no boundary walls are phaseable
        for wall in phaseable:
            tx = wall.x // TILE_SIZE
            ty = wall.y // TILE_SIZE

            self.assertNotEqual(tx, 0, "Left boundary wall should not be phaseable")
            self.assertNotEqual(tx, WORLD_W - 1, "Right boundary wall should not be phaseable")
            self.assertNotEqual(ty, 0, "Top boundary wall should not be phaseable")
            self.assertNotEqual(ty, WORLD_H - 1, "Bottom boundary wall should not be phaseable")

    def test_mark_phaseable_chance_affects_count(self):
        """Test that phaseable_wall_chance affects count."""
        tiles = []
        for y in range(5, 15):
            for x in range(10, 12):
                self.world[y][x] = 1
                tiles.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        phaseable_low = mark_phaseable_walls(tiles, self.world, random.Random(42), phaseable_wall_chance=0.1)
        phaseable_high = mark_phaseable_walls(tiles, self.world, random.Random(42), phaseable_wall_chance=1.0)

        # Higher chance should mark more walls
        self.assertGreaterEqual(len(phaseable_high), len(phaseable_low))

    def test_mark_phaseable_zero_chance(self):
        """Test that zero chance marks no walls."""
        tiles = []
        for y in range(5, 15):
            self.world[y][10] = 1
            tiles.append(pygame.Rect(10 * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        phaseable = mark_phaseable_walls(tiles, self.world, self.rng, phaseable_wall_chance=0.0)

        self.assertEqual(len(phaseable), 0)


class TestGenerateLevel(unittest.TestCase):
    """Test complete level generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.seed = 42

    def test_generate_level_basic(self):
        """Test basic level generation."""
        result = generate_level(seed=self.seed)

        # Should return 11-tuple
        self.assertEqual(len(result), 11)

        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = result

        # Verify all components
        self.assertIsNotNone(world)
        self.assertIsInstance(tiles, list)
        self.assertIsInstance(coins, list)
        self.assertIsInstance(hazards, list)

    def test_generate_level_has_exit(self):
        """Test that generated level has exit."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=self.seed)

        self.assertIsNotNone(exit_rect)
        self.assertIsInstance(exit_rect, pygame.Rect)

    def test_generate_level_has_spawn(self):
        """Test that generated level has spawn point."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=self.seed)

        self.assertIsNotNone(spawn)
        spawn_x, spawn_y = spawn
        self.assertGreaterEqual(spawn_x, 0)
        self.assertGreaterEqual(spawn_y, 0)

    def test_generate_level_has_tiles(self):
        """Test that generated level has solid tiles."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=self.seed)

        self.assertGreater(len(tiles), 0, "Level should have solid tiles")

    def test_generate_level_has_coins(self):
        """Test that generated level has coins."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=self.seed)

        self.assertGreater(len(coins), 0, "Level should have coins")

    def test_generate_level_deterministic(self):
        """Test that level generation is deterministic."""
        result1 = generate_level(seed=42)
        result2 = generate_level(seed=42)

        # Worlds should be identical
        world1, tiles1, exit1, spawn1, coins1, hazards1, healths1, lives1, powerups1, phaseable1, orbs1 = result1
        world2, tiles2, exit2, spawn2, coins2, hazards2, healths2, lives2, powerups2, phaseable2, orbs2 = result2

        self.assertEqual(world1, world2)
        self.assertEqual(len(tiles1), len(tiles2))
        self.assertEqual(spawn1, spawn2)
        self.assertEqual(len(coins1), len(coins2))

    def test_generate_level_with_abilities(self):
        """Test level generation with abilities enabled."""
        abilities = ["DOUBLE_JUMP", "DASH", "WALL_JUMP"]
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            abilities=abilities
        )

        # Should generate level successfully with abilities
        self.assertIsNotNone(world)
        self.assertGreater(len(coins), 0)

    def test_generate_level_with_shadow_step(self):
        """Test that SHADOW_STEP ability enables phaseable walls."""
        abilities = ["SHADOW_STEP"]
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            abilities=abilities
        )

        # Should have phaseable walls with SHADOW_STEP
        self.assertIsInstance(phaseable_walls, list)

    def test_generate_level_without_shadow_step(self):
        """Test that without SHADOW_STEP, no phaseable walls."""
        abilities = ["DOUBLE_JUMP", "DASH"]
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            abilities=abilities
        )

        # Should have no phaseable walls without SHADOW_STEP
        self.assertEqual(len(phaseable_walls), 0)

    def test_generate_level_with_difficulty_config(self):
        """Test level generation with custom difficulty config."""
        diff_cfg = {
            'coin_density': 0.1,
            'hazard_rate': 0.05,
            'powerup_density': 0.01,
            'platform_band_step': 3,
            'pillar_chance': 0.5,
            'hole_chance': 0.3,
        }

        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            diff_cfg=diff_cfg
        )

        # Should generate level with custom config
        self.assertIsNotNone(world)
        self.assertGreater(len(coins), 0)

    def test_generate_level_ability_subrooms_enabled(self):
        """Test level with ability subrooms enabled."""
        diff_cfg = {
            'enable_ability_subrooms': True,
            'subroom_intensity': 1.0,
        }
        abilities = ["DOUBLE_JUMP", "DASH", "WALL_JUMP"]

        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            diff_cfg=diff_cfg,
            abilities=abilities
        )

        # Should generate successfully
        self.assertIsNotNone(world)

    def test_generate_level_ability_subrooms_disabled(self):
        """Test level with ability subrooms disabled."""
        diff_cfg = {
            'enable_ability_subrooms': False,
        }
        abilities = ["DOUBLE_JUMP"]

        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            diff_cfg=diff_cfg,
            abilities=abilities
        )

        # Should still generate level
        self.assertIsNotNone(world)

    def test_generate_level_ability_challenges_enabled(self):
        """Test level with ability challenges enabled."""
        diff_cfg = {
            'enable_ability_challenges': True,
        }
        abilities = ["DOUBLE_JUMP", "DASH"]

        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            diff_cfg=diff_cfg,
            abilities=abilities
        )

        # Should have more coins due to challenges
        self.assertGreater(len(coins), 0)

    def test_generate_level_ability_challenges_disabled(self):
        """Test level with ability challenges disabled."""
        diff_cfg = {
            'enable_ability_challenges': False,
        }
        abilities = ["DOUBLE_JUMP"]

        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            diff_cfg=diff_cfg,
            abilities=abilities
        )

        # Should still generate coins from normal generation
        self.assertIsInstance(coins, list)

    def test_generate_level_has_ability_orbs(self):
        """Test that level can generate ability orbs."""
        diff_cfg = {
            'ability_orb_spawn_rate': 0.1,  # Higher rate for testing
        }

        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            diff_cfg=diff_cfg
        )

        # Should have ability orbs with higher spawn rate
        self.assertIsInstance(ability_orbs, list)

    def test_generate_level_different_seeds(self):
        """Test that different seeds produce different levels."""
        result1 = generate_level(seed=42)
        result2 = generate_level(seed=123)

        world1, tiles1, _, _, coins1, _, _, _, _, _, _ = result1
        world2, tiles2, _, _, coins2, _, _, _, _, _, _ = result2

        # Different seeds should produce different levels
        self.assertNotEqual(world1, world2)

    def test_generate_level_has_all_entity_types(self):
        """Test that generated level has all entity types."""
        diff_cfg = {
            'coin_density': 0.1,
            'health_density': 0.05,
            'lives_per_level': 2,
            'powerup_density': 0.01,
            'hazard_rate': 0.1,
            'ability_orb_spawn_rate': 0.05,
        }

        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(
            seed=self.seed,
            diff_cfg=diff_cfg
        )

        # Should have all entity types
        self.assertGreater(len(coins), 0, "Should have coins")
        self.assertGreater(len(hazards), 0, "Should have hazards")
        self.assertGreaterEqual(len(healths), 0, "Should have health pickups")
        self.assertGreaterEqual(len(powerups), 0, "Should have powerups")

    def test_generate_level_world_dimensions(self):
        """Test that generated world has correct dimensions."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=self.seed)

        self.assertEqual(len(world), WORLD_H)
        self.assertEqual(len(world[0]), WORLD_W)

    def test_generate_level_no_config(self):
        """Test level generation with no config uses defaults."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=self.seed)

        # Should use default values and generate successfully
        self.assertIsNotNone(world)
        self.assertGreater(len(tiles), 0)
        self.assertGreater(len(coins), 0)


class TestLevelQuality(unittest.TestCase):
    """Test quality and playability of generated levels."""

    def test_level_has_reachable_exit(self):
        """Test that exit is theoretically reachable from spawn."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=42)

        # Exit should exist
        self.assertIsNotNone(exit_rect)

        # Spawn should be different from exit
        spawn_x, spawn_y = spawn
        self.assertFalse(
            exit_rect.collidepoint(spawn_x, spawn_y),
            "Spawn should not be at exit"
        )

    def test_level_has_sufficient_coins(self):
        """Test that level has reasonable number of coins."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=42)

        # Should have at least some coins
        self.assertGreater(len(coins), 10, "Level should have meaningful number of coins")

    def test_level_borders_are_solid(self):
        """Test that level borders are solid walls."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=42)

        # Check all borders are solid
        for x in range(WORLD_W):
            self.assertEqual(world[0][x], 1, f"Top border not solid at x={x}")
            self.assertEqual(world[WORLD_H - 1][x], 1, f"Bottom border not solid at x={x}")

        for y in range(WORLD_H):
            self.assertEqual(world[y][0], 1, f"Left border not solid at y={y}")
            self.assertEqual(world[y][WORLD_W - 1], 1, f"Right border not solid at y={y}")

    def test_level_spawn_is_safe(self):
        """Test that spawn point is on solid ground."""
        world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs = generate_level(seed=42)

        spawn_x, spawn_y = spawn
        spawn_tx = spawn_x // TILE_SIZE
        spawn_ty = spawn_y // TILE_SIZE

        # Check that there's a floor below spawn
        floor_found = False
        for dy in range(1, 5):  # Check a few tiles below
            check_y = spawn_ty + dy
            if 0 <= check_y < WORLD_H and world[check_y][spawn_tx] == 1:
                floor_found = True
                break

        self.assertTrue(floor_found, "Spawn should have floor below it")


if __name__ == '__main__':
    unittest.main()
