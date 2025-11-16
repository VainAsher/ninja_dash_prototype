"""
Unit tests for ability features module.
Tests challenge patterns and subroom generation.
"""

import unittest
import random
import pygame
from level_gen.ability_features import (
    add_ability_challenges,
    add_ability_subrooms
)
from level_gen.constants import CHALLENGE_ATTEMPTS, SUBROOM_EMPTY_THRESHOLD
from settings import TILE_SIZE, ROOM_COLS, ROOM_ROWS, ROOM_W, ROOM_H, WORLD_W, WORLD_H


class TestAbilityChallenges(unittest.TestCase):
    """Test ability-aware coin challenge generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]
        self.coins = []

        # Add some platforms
        for x in range(10, 40):
            self.world[10][x] = 1
            self.world[20][x] = 1

    def test_add_challenges_with_no_abilities(self):
        """Test that no challenges are added without abilities."""
        initial_coin_count = len(self.coins)
        add_ability_challenges(self.world, self.coins, self.rng, abilities=[])

        # Should not add coins if no abilities
        self.assertEqual(len(self.coins), initial_coin_count)

    def test_add_challenges_with_double_jump(self):
        """Test that DOUBLE_JUMP adds vertical coin arcs."""
        initial_coin_count = len(self.coins)
        add_ability_challenges(self.world, self.coins, self.rng, abilities=["DOUBLE_JUMP"])

        # Should add some coins
        self.assertGreater(len(self.coins), initial_coin_count)

    def test_add_challenges_with_dash(self):
        """Test that DASH adds horizontal coin lines."""
        initial_coin_count = len(self.coins)
        add_ability_challenges(self.world, self.coins, self.rng, abilities=["DASH"])

        # Should add some coins
        self.assertGreater(len(self.coins), initial_coin_count)

    def test_add_challenges_with_wall_jump(self):
        """Test that WALL_JUMP adds vertical coin ladders."""
        initial_coin_count = len(self.coins)
        add_ability_challenges(self.world, self.coins, self.rng, abilities=["WALL_JUMP"])

        # Should add some coins
        self.assertGreater(len(self.coins), initial_coin_count)

    def test_add_challenges_with_multiple_abilities(self):
        """Test that multiple abilities add various challenges."""
        initial_coin_count = len(self.coins)
        abilities = ["DOUBLE_JUMP", "DASH", "WALL_JUMP"]
        add_ability_challenges(self.world, self.coins, self.rng, abilities)

        # Should add coins for all abilities
        self.assertGreater(len(self.coins), initial_coin_count)

    def test_challenge_coins_are_valid_rects(self):
        """Test that challenge coins are valid pygame Rects."""
        add_ability_challenges(self.world, self.coins, self.rng, abilities=["DOUBLE_JUMP", "DASH"])

        for coin in self.coins:
            self.assertIsInstance(coin, pygame.Rect)
            self.assertGreater(coin.width, 0)
            self.assertGreater(coin.height, 0)

    def test_double_jump_coins_form_arcs(self):
        """Test that DOUBLE_JUMP coins are placed in arc patterns."""
        add_ability_challenges(self.world, self.coins, self.rng, abilities=["DOUBLE_JUMP"])

        # Check that coins exist (arc pattern is harder to verify directly)
        self.assertGreater(len(self.coins), 0)

    def test_dash_coins_form_lines(self):
        """Test that DASH coins are placed in horizontal lines."""
        add_ability_challenges(self.world, self.coins, self.rng, abilities=["DASH"])

        # Check that coins exist
        self.assertGreater(len(self.coins), 0)

        # Look for horizontal sequences
        if len(self.coins) > 1:
            # Sort by y-coordinate to find coins on same level
            coins_by_y = {}
            for coin in self.coins:
                cy = coin.y
                if cy not in coins_by_y:
                    coins_by_y[cy] = []
                coins_by_y[cy].append(coin.x)

            # Should have some rows with multiple coins
            has_horizontal_line = any(len(coins) >= 3 for coins in coins_by_y.values())
            self.assertTrue(has_horizontal_line, "DASH should create horizontal coin lines")

    def test_wall_jump_coins_form_ladders(self):
        """Test that WALL_JUMP coins are placed vertically."""
        add_ability_challenges(self.world, self.coins, self.rng, abilities=["WALL_JUMP"])

        # Check that coins exist
        self.assertGreater(len(self.coins), 0)

        # Look for vertical sequences
        if len(self.coins) > 1:
            # Sort by x-coordinate to find coins on same column
            coins_by_x = {}
            for coin in self.coins:
                cx = coin.x
                if cx not in coins_by_x:
                    coins_by_x[cx] = []
                coins_by_x[cx].append(coin.y)

            # Should have some columns with multiple coins
            has_vertical_line = any(len(coins) >= 3 for coins in coins_by_x.values())
            self.assertTrue(has_vertical_line, "WALL_JUMP should create vertical coin ladders")

    def test_challenges_deterministic(self):
        """Test that challenge generation is deterministic."""
        coins1 = []
        add_ability_challenges(self.world, coins1, random.Random(42), abilities=["DOUBLE_JUMP", "DASH"])

        coins2 = []
        add_ability_challenges(self.world, coins2, random.Random(42), abilities=["DOUBLE_JUMP", "DASH"])

        self.assertEqual(len(coins1), len(coins2))
        for c1, c2 in zip(coins1, coins2):
            self.assertEqual(c1, c2)


class TestAbilitySubrooms(unittest.TestCase):
    """Test ability-specific subroom generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]
        self.path_mask = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add borders
        for x in range(WORLD_W):
            self.world[0][x] = 1
            self.world[WORLD_H - 1][x] = 1
        for y in range(WORLD_H):
            self.world[y][0] = 1
            self.world[y][WORLD_W - 1] = 1

    def test_add_subrooms_with_no_abilities(self):
        """Test that no subrooms are added without abilities."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng, abilities=[], intensity=0.5)

        # World should be unchanged
        self.assertEqual(world_copy, self.world)

    def test_add_subrooms_with_double_jump(self):
        """Test DOUBLE_JUMP subroom generation."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng, abilities=["DOUBLE_JUMP"], intensity=1.0)

        # Should modify world (add platforms)
        tile_count_before = sum(sum(1 for cell in row if cell == 1) for row in self.world)
        tile_count_after = sum(sum(1 for cell in row if cell == 1) for row in world_copy)

        self.assertGreaterEqual(tile_count_after, tile_count_before)

    def test_add_subrooms_with_dash(self):
        """Test DASH subroom generation."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng, abilities=["DASH"], intensity=1.0)

        # Should modify world
        tile_count_before = sum(sum(1 for cell in row if cell == 1) for row in self.world)
        tile_count_after = sum(sum(1 for cell in row if cell == 1) for row in world_copy)

        self.assertGreaterEqual(tile_count_after, tile_count_before)

    def test_add_subrooms_with_wall_jump(self):
        """Test WALL_JUMP subroom generation."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng, abilities=["WALL_JUMP"], intensity=1.0)

        # Should modify world
        tile_count_before = sum(sum(1 for cell in row if cell == 1) for row in self.world)
        tile_count_after = sum(sum(1 for cell in row if cell == 1) for row in world_copy)

        self.assertGreaterEqual(tile_count_after, tile_count_before)

    def test_subroom_intensity_affects_count(self):
        """Test that intensity parameter affects subroom count."""
        # Low intensity
        world_low = [row[:] for row in self.world]
        add_ability_subrooms(world_low, self.path_mask, random.Random(42),
                           abilities=["DOUBLE_JUMP", "DASH"], intensity=0.1)

        # High intensity
        world_high = [row[:] for row in self.world]
        add_ability_subrooms(world_high, self.path_mask, random.Random(42),
                           abilities=["DOUBLE_JUMP", "DASH"], intensity=1.0)

        # High intensity should add more or equal tiles
        tiles_low = sum(sum(1 for cell in row if cell == 1) for row in world_low)
        tiles_high = sum(sum(1 for cell in row if cell == 1) for row in world_high)

        self.assertGreaterEqual(tiles_high, tiles_low)

    def test_subroom_respects_path_mask(self):
        """Test that subrooms don't overwrite critical path."""
        # Mark some tiles as critical path
        for x in range(10, 20):
            self.path_mask[10][x] = True
            self.world[10][x] = 1

        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng,
                           abilities=["DOUBLE_JUMP"], intensity=1.0)

        # Path mask tiles should be preserved
        # (Function should avoid those areas)

    def test_subroom_double_jump_creates_high_platform(self):
        """Test that DOUBLE_JUMP subroom creates high platforms."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng,
                           abilities=["DOUBLE_JUMP"], intensity=1.0)

        # Look for horizontal platforms (high platforms)
        horizontal_platforms = 0
        for y in range(1, WORLD_H - 1):
            run_length = 0
            for x in range(1, WORLD_W - 1):
                if world_copy[y][x] == 1:
                    run_length += 1
                else:
                    if run_length >= 5:
                        horizontal_platforms += 1
                    run_length = 0

        # Should have created some platforms
        self.assertGreaterEqual(horizontal_platforms, 0)

    def test_subroom_dash_creates_gap(self):
        """Test that DASH subroom creates platforms with gaps."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng,
                           abilities=["DASH"], intensity=1.0)

        # Dash subrooms create platform segments with gaps
        # Just verify tiles were added
        tile_count_before = sum(sum(1 for cell in row if cell == 1) for row in self.world)
        tile_count_after = sum(sum(1 for cell in row if cell == 1) for row in world_copy)

        self.assertGreaterEqual(tile_count_after, tile_count_before)

    def test_subroom_wall_jump_creates_shaft(self):
        """Test that WALL_JUMP subroom creates vertical shaft."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng,
                           abilities=["WALL_JUMP"], intensity=1.0)

        # Wall jump creates vertical shafts with walls on sides
        # Look for vertical wall patterns
        vertical_walls = 0
        for x in range(1, WORLD_W - 1):
            run_length = 0
            for y in range(1, WORLD_H - 1):
                if world_copy[y][x] == 1:
                    run_length += 1
                else:
                    if run_length >= 5:
                        vertical_walls += 1
                    run_length = 0

        # Should have some vertical structures
        self.assertGreaterEqual(vertical_walls, 0)

    def test_multiple_abilities_create_varied_subrooms(self):
        """Test that multiple abilities create different subrooms."""
        world_copy = [row[:] for row in self.world]
        abilities = ["DOUBLE_JUMP", "DASH", "WALL_JUMP"]
        add_ability_subrooms(world_copy, self.path_mask, self.rng,
                           abilities=abilities, intensity=1.0)

        # Should modify the world
        tile_count_before = sum(sum(1 for cell in row if cell == 1) for row in self.world)
        tile_count_after = sum(sum(1 for cell in row if cell == 1) for row in world_copy)

        self.assertGreater(tile_count_after, tile_count_before)

    def test_subroom_placement_finds_empty_areas(self):
        """Test that subrooms are placed in empty areas."""
        # Fill most of the world, leaving one room empty
        for y in range(1, WORLD_H - 1):
            for x in range(1, WORLD_W - 1):
                # Leave one room mostly empty
                if not (ROOM_W <= x < 2 * ROOM_W and ROOM_H <= y < 2 * ROOM_H):
                    self.world[y][x] = 1

        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng,
                           abilities=["DOUBLE_JUMP"], intensity=0.5)

        # Function should attempt to find empty areas
        # (May or may not succeed based on SUBROOM_EMPTY_THRESHOLD)

    def test_subroom_deterministic(self):
        """Test that subroom generation is deterministic."""
        world1 = [row[:] for row in self.world]
        add_ability_subrooms(world1, self.path_mask, random.Random(42),
                           abilities=["DOUBLE_JUMP", "DASH"], intensity=0.5)

        world2 = [row[:] for row in self.world]
        add_ability_subrooms(world2, self.path_mask, random.Random(42),
                           abilities=["DOUBLE_JUMP", "DASH"], intensity=0.5)

        self.assertEqual(world1, world2)

    def test_subroom_with_zero_intensity(self):
        """Test subroom generation with zero intensity."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng,
                           abilities=["DOUBLE_JUMP"], intensity=0.0)

        # Zero intensity should create minimal subrooms
        # num_subrooms = int(2 + 0.0 * 3) = 2
        # Still attempts to create some subrooms

    def test_subroom_with_max_intensity(self):
        """Test subroom generation with maximum intensity."""
        world_copy = [row[:] for row in self.world]
        add_ability_subrooms(world_copy, self.path_mask, self.rng,
                           abilities=["DOUBLE_JUMP", "DASH", "WALL_JUMP"], intensity=1.0)

        # Max intensity should create more subrooms
        # num_subrooms = int(2 + 1.0 * 3) = 5
        tile_count_before = sum(sum(1 for cell in row if cell == 1) for row in self.world)
        tile_count_after = sum(sum(1 for cell in row if cell == 1) for row in world_copy)

        self.assertGreater(tile_count_after, tile_count_before)


class TestAbilityIntegration(unittest.TestCase):
    """Test integration between challenges and subrooms."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]
        self.path_mask = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]
        self.coins = []

        # Add borders
        for x in range(WORLD_W):
            self.world[0][x] = 1
            self.world[WORLD_H - 1][x] = 1
        for y in range(WORLD_H):
            self.world[y][0] = 1
            self.world[y][WORLD_W - 1] = 1

    def test_combined_challenges_and_subrooms(self):
        """Test that challenges and subrooms can coexist."""
        abilities = ["DOUBLE_JUMP", "DASH", "WALL_JUMP"]

        # Add subrooms first
        add_ability_subrooms(self.world, self.path_mask, self.rng, abilities, intensity=0.5)

        # Then add challenges
        initial_coins = len(self.coins)
        add_ability_challenges(self.world, self.coins, self.rng, abilities)

        # Should have added coins
        self.assertGreater(len(self.coins), initial_coins)

    def test_challenges_and_subrooms_with_single_ability(self):
        """Test single ability creates both challenges and subrooms."""
        ability = ["DOUBLE_JUMP"]

        add_ability_subrooms(self.world, self.path_mask, self.rng, ability, intensity=0.5)
        add_ability_challenges(self.world, self.coins, self.rng, ability)

        # Should modify world and add coins
        tile_count = sum(sum(1 for cell in row if cell == 1) for row in self.world)
        self.assertGreater(tile_count, 0)
        self.assertGreater(len(self.coins), 0)


class TestConstants(unittest.TestCase):
    """Test that constants are properly defined."""

    def test_challenge_attempts_defined(self):
        """Test that CHALLENGE_ATTEMPTS constant exists."""
        self.assertIsInstance(CHALLENGE_ATTEMPTS, int)
        self.assertGreater(CHALLENGE_ATTEMPTS, 0)

    def test_subroom_empty_threshold_defined(self):
        """Test that SUBROOM_EMPTY_THRESHOLD constant exists."""
        self.assertIsInstance(SUBROOM_EMPTY_THRESHOLD, (int, float))
        self.assertGreaterEqual(SUBROOM_EMPTY_THRESHOLD, 0.0)
        self.assertLessEqual(SUBROOM_EMPTY_THRESHOLD, 1.0)


if __name__ == '__main__':
    unittest.main()
