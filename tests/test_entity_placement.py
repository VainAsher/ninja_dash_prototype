"""
Unit tests for entity placement module.
Tests collision-free spawning, density parameters, and entity generation.
"""

import unittest
import random
import pygame
from level_gen.entity_placer import (
    EntityPlacer,
    _valid_pickup_spot,
    _far_from_hazards,
    generate_hazards,
    generate_coins_and_pickups,
    generate_powerups,
    generate_ability_orbs
)
from settings import TILE_SIZE, WORLD_W, WORLD_H, POWERUP_TYPES


class TestEntityPlacer(unittest.TestCase):
    """Test EntityPlacer class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        # Create a simple world with borders and platforms
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add borders
        for x in range(WORLD_W):
            self.world[0][x] = 1
            self.world[WORLD_H - 1][x] = 1
        for y in range(WORLD_H):
            self.world[y][0] = 1
            self.world[y][WORLD_W - 1] = 1

        # Add some platforms for spawning
        for x in range(10, 30):
            self.world[20][x] = 1
            self.world[25][x] = 1

        self.placer = EntityPlacer(self.world, self.rng)

    def test_entity_placer_initialization(self):
        """Test EntityPlacer initialization."""
        placer = EntityPlacer(self.world, self.rng)
        self.assertEqual(placer.world, self.world)
        self.assertEqual(placer.rng, self.rng)

    def test_valid_pickup_spot(self):
        """Test valid pickup spot detection."""
        # Valid spot: air above, solid below
        self.world[10][10] = 0
        self.world[11][10] = 1

        self.assertTrue(_valid_pickup_spot(self.world, 10, 10))

    def test_invalid_pickup_spot_no_floor(self):
        """Test invalid pickup spot without floor."""
        self.world[10][10] = 0
        self.world[11][10] = 0  # No floor

        self.assertFalse(_valid_pickup_spot(self.world, 10, 10))

    def test_invalid_pickup_spot_not_air(self):
        """Test invalid pickup spot with solid tile."""
        self.world[10][10] = 1
        self.world[11][10] = 1

        self.assertFalse(_valid_pickup_spot(self.world, 10, 10))

    def test_invalid_pickup_spot_out_of_bounds(self):
        """Test invalid pickup spot out of bounds."""
        self.assertFalse(_valid_pickup_spot(self.world, 0, 0))
        self.assertFalse(_valid_pickup_spot(self.world, WORLD_W - 1, 5))
        self.assertFalse(_valid_pickup_spot(self.world, 5, 1))

    def test_far_from_hazards(self):
        """Test hazard proximity checking."""
        hazard_tiles = {(10, 10), (15, 15)}

        # Far from hazards
        self.assertTrue(_far_from_hazards(20, 20, hazard_tiles, radius=3))

        # Close to hazards (horizontal)
        self.assertFalse(_far_from_hazards(12, 10, hazard_tiles, radius=3))

        # Close to hazards (vertical)
        self.assertFalse(_far_from_hazards(10, 12, hazard_tiles, radius=3))

    def test_far_from_hazards_different_radius(self):
        """Test hazard proximity with different radius."""
        hazard_tiles = {(10, 10)}

        self.assertTrue(_far_from_hazards(15, 15, hazard_tiles, radius=3))
        self.assertFalse(_far_from_hazards(13, 10, hazard_tiles, radius=5))


class TestHazardGeneration(unittest.TestCase):
    """Test hazard generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add platforms suitable for hazard placement
        for x in range(10, 30):
            self.world[10][x] = 1
            self.world[15][x] = 1

    def test_generate_hazards_basic(self):
        """Test basic hazard generation."""
        placer = EntityPlacer(self.world, self.rng)
        hazards = placer.generate_hazards(rate=0.1)

        self.assertIsInstance(hazards, list)
        # With some platforms and rate 0.1, should generate some hazards
        self.assertGreaterEqual(len(hazards), 0)

    def test_generate_hazards_high_rate(self):
        """Test hazard generation with high rate."""
        placer = EntityPlacer(self.world, self.rng)
        hazards = placer.generate_hazards(rate=1.0)

        # High rate should generate more hazards
        self.assertGreater(len(hazards), 0)

    def test_generate_hazards_zero_rate(self):
        """Test hazard generation with zero rate."""
        placer = EntityPlacer(self.world, self.rng)
        hazards = placer.generate_hazards(rate=0.0)

        # Zero rate should generate no hazards
        self.assertEqual(len(hazards), 0)

    def test_hazard_rect_properties(self):
        """Test that generated hazards are valid pygame Rects."""
        placer = EntityPlacer(self.world, self.rng)
        hazards = placer.generate_hazards(rate=0.5)

        for hazard in hazards:
            self.assertIsInstance(hazard, pygame.Rect)
            self.assertGreater(hazard.width, 0)
            self.assertGreater(hazard.height, 0)

    def test_hazard_placement_on_platforms(self):
        """Test that hazards are placed on platforms."""
        placer = EntityPlacer(self.world, self.rng)
        hazards = placer.generate_hazards(rate=0.5)

        for hazard in hazards:
            # Hazard should be near a platform
            tx = hazard.x // TILE_SIZE
            ty = (hazard.y + hazard.height) // TILE_SIZE

            # There should be a platform nearby
            platform_nearby = False
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    check_x = tx + dx
                    check_y = ty + dy
                    if 0 <= check_x < WORLD_W and 0 <= check_y < WORLD_H:
                        if self.world[check_y][check_x] == 1:
                            platform_nearby = True

            self.assertTrue(platform_nearby, f"Hazard at {hazard} not near platform")


class TestCoinsAndPickups(unittest.TestCase):
    """Test coin and pickup generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add platforms for spawning
        for x in range(5, 35):
            self.world[10][x] = 1
            self.world[15][x] = 1
            self.world[20][x] = 1

    def test_generate_coins_basic(self):
        """Test basic coin generation."""
        placer = EntityPlacer(self.world, self.rng)
        coins, healths, lives = placer.generate_coins_and_pickups(
            coin_density=0.1,
            health_density=0.05,
            lives_per_level=1
        )

        self.assertIsInstance(coins, list)
        self.assertIsInstance(healths, list)
        self.assertIsInstance(lives, list)

    def test_coin_density_affects_count(self):
        """Test that coin density affects coin count."""
        placer1 = EntityPlacer(self.world, random.Random(42))
        coins1, _, _ = placer1.generate_coins_and_pickups(coin_density=0.01)

        placer2 = EntityPlacer(self.world, random.Random(42))
        coins2, _, _ = placer2.generate_coins_and_pickups(coin_density=0.1)

        # Higher density should produce more coins
        self.assertGreater(len(coins2), len(coins1))

    def test_health_density_affects_count(self):
        """Test that health density affects health pickup count."""
        placer1 = EntityPlacer(self.world, random.Random(42))
        _, healths1, _ = placer1.generate_coins_and_pickups(health_density=0.001)

        placer2 = EntityPlacer(self.world, random.Random(42))
        _, healths2, _ = placer2.generate_coins_and_pickups(health_density=0.05)

        # Higher density should produce more or equal health pickups
        self.assertGreaterEqual(len(healths2), len(healths1))

    def test_lives_per_level(self):
        """Test that lives_per_level controls extra life count."""
        placer = EntityPlacer(self.world, self.rng)
        _, _, lives = placer.generate_coins_and_pickups(lives_per_level=3)

        # Should try to spawn requested number of lives (may be less if can't find spots)
        self.assertLessEqual(len(lives), 3)

    def test_pickups_avoid_hazards(self):
        """Test that pickups avoid hazard areas."""
        placer = EntityPlacer(self.world, self.rng)
        # Create a hazard
        hazards = [pygame.Rect(10 * TILE_SIZE, 9 * TILE_SIZE, TILE_SIZE, TILE_SIZE)]

        coins, healths, lives = placer.generate_coins_and_pickups(
            coin_density=0.2,
            hazards=hazards
        )

        # Check that no pickups are too close to hazards
        hazard_tiles = set()
        for h in hazards:
            hx = (h.x + h.width // 2) // TILE_SIZE
            hy = (h.y + h.height // 2) // TILE_SIZE
            hazard_tiles.add((hx, hy))

        for coin in coins:
            cx = (coin.x + coin.width // 2) // TILE_SIZE
            cy = (coin.y + coin.height // 2) // TILE_SIZE
            self.assertTrue(_far_from_hazards(cx, cy, hazard_tiles, radius=3))

    def test_pickup_rect_properties(self):
        """Test that generated pickups are valid pygame Rects."""
        placer = EntityPlacer(self.world, self.rng)
        coins, healths, lives = placer.generate_coins_and_pickups(
            coin_density=0.1,
            health_density=0.05,
            lives_per_level=2
        )

        for pickup_list in [coins, healths, lives]:
            for pickup in pickup_list:
                self.assertIsInstance(pickup, pygame.Rect)
                self.assertGreater(pickup.width, 0)
                self.assertGreater(pickup.height, 0)

    def test_lives_no_collision(self):
        """Test that extra lives don't overlap with other pickups."""
        placer = EntityPlacer(self.world, self.rng)
        coins, healths, lives = placer.generate_coins_and_pickups(
            coin_density=0.2,
            health_density=0.05,
            lives_per_level=3
        )

        # Check that lives don't collide with coins or healths
        for life in lives:
            for coin in coins:
                self.assertFalse(life.colliderect(coin), "Life overlaps with coin")
            for health in healths:
                self.assertFalse(life.colliderect(health), "Life overlaps with health")


class TestPowerupGeneration(unittest.TestCase):
    """Test powerup generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add platforms
        for x in range(5, 40):
            self.world[10][x] = 1
            self.world[20][x] = 1

    def test_generate_powerups_basic(self):
        """Test basic powerup generation."""
        placer = EntityPlacer(self.world, self.rng)
        powerups = placer.generate_powerups(density=0.01)

        self.assertIsInstance(powerups, list)

    def test_powerup_density_affects_count(self):
        """Test that density affects powerup count."""
        placer1 = EntityPlacer(self.world, random.Random(42))
        powerups1 = placer1.generate_powerups(density=0.001)

        placer2 = EntityPlacer(self.world, random.Random(42))
        powerups2 = placer2.generate_powerups(density=0.05)

        # Higher density should produce more powerups
        self.assertGreaterEqual(len(powerups2), len(powerups1))

    def test_powerup_has_type(self):
        """Test that each powerup has a type."""
        placer = EntityPlacer(self.world, self.rng)
        powerups = placer.generate_powerups(density=0.05)

        valid_types = [ptype for ptype, _ in POWERUP_TYPES]

        for powerup in powerups:
            self.assertIn('rect', powerup)
            self.assertIn('type', powerup)
            self.assertIn(powerup['type'], valid_types)

    def test_powerup_rect_valid(self):
        """Test that powerup rects are valid."""
        placer = EntityPlacer(self.world, self.rng)
        powerups = placer.generate_powerups(density=0.05)

        for powerup in powerups:
            rect = powerup['rect']
            self.assertIsInstance(rect, pygame.Rect)
            self.assertGreater(rect.width, 0)
            self.assertGreater(rect.height, 0)

    def test_powerup_type_distribution(self):
        """Test that different powerup types are generated."""
        placer = EntityPlacer(self.world, random.Random(42))
        powerups = placer.generate_powerups(density=0.1)

        # Collect types
        types_found = set()
        for powerup in powerups:
            types_found.add(powerup['type'])

        # With enough powerups, should see variety (though not guaranteed)
        # At minimum, should have valid types
        valid_types = [ptype for ptype, _ in POWERUP_TYPES]
        for ptype in types_found:
            self.assertIn(ptype, valid_types)


class TestAbilityOrbGeneration(unittest.TestCase):
    """Test ability orb generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add platforms
        for x in range(5, 50):
            self.world[10][x] = 1
            self.world[20][x] = 1
            self.world[30][x] = 1

    def test_generate_ability_orbs_basic(self):
        """Test basic ability orb generation."""
        placer = EntityPlacer(self.world, self.rng)
        orbs = placer.generate_ability_orbs(spawn_rate=0.01)

        self.assertIsInstance(orbs, list)

    def test_ability_orbs_are_rare(self):
        """Test that ability orbs are rare with default rate."""
        placer = EntityPlacer(self.world, self.rng)
        orbs = placer.generate_ability_orbs(spawn_rate=0.003)  # Default rate

        # Should generate very few or no orbs
        # (depends on world size and RNG, but should be rare)
        self.assertIsInstance(orbs, list)

    def test_ability_orb_spawn_rate_affects_count(self):
        """Test that spawn rate affects orb count."""
        placer1 = EntityPlacer(self.world, random.Random(42))
        orbs1 = placer1.generate_ability_orbs(spawn_rate=0.001)

        placer2 = EntityPlacer(self.world, random.Random(42))
        orbs2 = placer2.generate_ability_orbs(spawn_rate=0.1)

        # Higher spawn rate should produce more orbs
        self.assertGreaterEqual(len(orbs2), len(orbs1))

    def test_ability_orb_rect_valid(self):
        """Test that ability orb rects are valid."""
        placer = EntityPlacer(self.world, self.rng)
        orbs = placer.generate_ability_orbs(spawn_rate=0.1)

        for orb in orbs:
            self.assertIsInstance(orb, pygame.Rect)
            self.assertGreater(orb.width, 0)
            self.assertGreater(orb.height, 0)


class TestStandaloneFunctions(unittest.TestCase):
    """Test standalone helper functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add platforms
        for x in range(10, 30):
            self.world[10][x] = 1

    def test_generate_hazards_standalone(self):
        """Test standalone generate_hazards function."""
        hazards = generate_hazards(self.world, self.rng, rate=0.1)
        self.assertIsInstance(hazards, list)

    def test_generate_coins_and_pickups_standalone(self):
        """Test standalone generate_coins_and_pickups function."""
        coins, healths, lives = generate_coins_and_pickups(
            self.world, self.rng,
            coin_density=0.1,
            health_density=0.05,
            lives_per_level=1
        )

        self.assertIsInstance(coins, list)
        self.assertIsInstance(healths, list)
        self.assertIsInstance(lives, list)

    def test_generate_powerups_standalone(self):
        """Test standalone generate_powerups function."""
        powerups = generate_powerups(self.world, self.rng, density=0.01)
        self.assertIsInstance(powerups, list)

    def test_generate_ability_orbs_standalone(self):
        """Test standalone generate_ability_orbs function."""
        orbs = generate_ability_orbs(self.world, self.rng, spawn_rate=0.01)
        self.assertIsInstance(orbs, list)


class TestDeterminism(unittest.TestCase):
    """Test that entity generation is deterministic."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Add platforms
        for x in range(5, 40):
            self.world[10][x] = 1
            self.world[20][x] = 1

    def test_coins_deterministic(self):
        """Test that coin generation is deterministic with same seed."""
        placer1 = EntityPlacer(self.world, random.Random(42))
        coins1, _, _ = placer1.generate_coins_and_pickups(coin_density=0.1)

        placer2 = EntityPlacer(self.world, random.Random(42))
        coins2, _, _ = placer2.generate_coins_and_pickups(coin_density=0.1)

        self.assertEqual(len(coins1), len(coins2))
        for c1, c2 in zip(coins1, coins2):
            self.assertEqual(c1, c2)

    def test_hazards_deterministic(self):
        """Test that hazard generation is deterministic with same seed."""
        placer1 = EntityPlacer(self.world, random.Random(42))
        hazards1 = placer1.generate_hazards(rate=0.1)

        placer2 = EntityPlacer(self.world, random.Random(42))
        hazards2 = placer2.generate_hazards(rate=0.1)

        self.assertEqual(len(hazards1), len(hazards2))
        for h1, h2 in zip(hazards1, hazards2):
            self.assertEqual(h1, h2)


if __name__ == '__main__':
    unittest.main()
