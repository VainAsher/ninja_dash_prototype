"""
Entity Placement Module - Handles spawning of coins, pickups, powerups, hazards, and ability orbs
Separated from generator.py for better separation of concerns.
"""

import random
import pygame
from typing import List, Tuple, Set, Optional, Dict, Any

from settings import (
    TILE_SIZE,
    WORLD_W, WORLD_H,
    POWERUP_TYPES,
)

from .constants import (
    DEFAULT_HAZARD_RATE,
    DEFAULT_COIN_DENSITY,
    DEFAULT_HEALTH_DENSITY,
    DEFAULT_LIVES_PER_LEVEL,
    DEFAULT_POWERUP_DENSITY,
    DEFAULT_ABILITY_ORB_SPAWN_RATE,
)


class EntityPlacer:
    """Handles placement of all entities (coins, pickups, powerups, hazards, ability orbs)."""

    def __init__(self, world: List[List[int]], rng: random.Random) -> None:
        """
        Initialize the entity placer.

        Args:
            world: 2D level array
            rng: Random number generator
        """
        self.world = world
        self.rng = rng

    @staticmethod
    def _valid_pickup_spot(world: List[List[int]], tx: int, ty: int) -> bool:
        """Check if (tx,ty) is a valid pickup spawn location."""
        if not (1 <= tx < WORLD_W - 1 and 2 <= ty < WORLD_H - 1):
            return False
        return world[ty][tx] == 0 and world[ty + 1][tx] == 1

    @staticmethod
    def _far_from_hazards(tx: int, ty: int, hazard_tiles: Set[Tuple[int, int]], radius: int = 3) -> bool:
        """Check if tile is far enough from hazards."""
        for hx, hy in hazard_tiles:
            if abs(hx - tx) <= radius and hy == ty:
                return False
            if abs(hy - ty) <= radius and hx == tx:
                return False
        return True

    def generate_hazards(self, rate: float = DEFAULT_HAZARD_RATE) -> List[pygame.Rect]:
        """
        Generate spike hazards on platforms.

        Args:
            rate: Spawn rate for hazards

        Returns:
            List of hazard rectangles
        """
        hazards = []
        for y in range(2, WORLD_H - 1):
            for x in range(1, WORLD_W - 1):
                if self.world[y][x] == 1 and self.world[y - 1][x] == 0 and self.world[y - 2][x] == 0:
                    if self.rng.random() < rate:
                        hx = x * TILE_SIZE + 2
                        hy = (y - 1) * TILE_SIZE + TILE_SIZE // 2
                        hazards.append(pygame.Rect(hx, hy, TILE_SIZE - 4, TILE_SIZE // 2))
        return hazards

    def generate_coins_and_pickups(
        self,
        coin_density: float = DEFAULT_COIN_DENSITY,
        health_density: float = DEFAULT_HEALTH_DENSITY,
        lives_per_level: int = DEFAULT_LIVES_PER_LEVEL,
        hazards: Optional[List[pygame.Rect]] = None
    ) -> Tuple[List[pygame.Rect], List[pygame.Rect], List[pygame.Rect]]:
        """
        Generate coins, health, and lives.

        Args:
            coin_density: Spawn rate for coins
            health_density: Spawn rate for health pickups
            lives_per_level: Number of extra lives to spawn
            hazards: List of hazard rectangles to avoid

        Returns:
            Tuple of (coins, healths, lives) - lists of rectangles
        """
        hazards = hazards or []
        coins = []
        healths = []
        lives = []

        # Build hazard tile set for proximity checks
        hazard_tiles = set()
        if hazards:
            for h in hazards:
                hx = (h.x + h.w // 2) // TILE_SIZE
                hy = (h.y + h.h // 2) // TILE_SIZE
                hazard_tiles.add((hx, hy))

        # Generate coins and health pickups
        for ty in range(2, WORLD_H - 1):
            for tx in range(1, WORLD_W - 1):
                if not self._valid_pickup_spot(self.world, tx, ty):
                    continue
                if not self._far_from_hazards(tx, ty, hazard_tiles, radius=3):
                    continue

                if self.rng.random() < coin_density:
                    cx = tx * TILE_SIZE + TILE_SIZE // 4
                    cy = ty * TILE_SIZE + TILE_SIZE // 4
                    coins.append(pygame.Rect(cx, cy, TILE_SIZE // 2, TILE_SIZE // 2))
                elif self.rng.random() < health_density:
                    hx = tx * TILE_SIZE + TILE_SIZE // 4
                    hy = ty * TILE_SIZE + TILE_SIZE // 4
                    healths.append(pygame.Rect(hx, hy, TILE_SIZE // 2, TILE_SIZE // 2))

        # Generate extra lives (random placement)
        attempts = 0
        while len(lives) < max(0, int(lives_per_level)):
            attempts += 1
            if attempts > 10000:
                break
            tx = self.rng.randint(1, WORLD_W - 2)
            ty = self.rng.randint(2, WORLD_H - 2)
            if self._valid_pickup_spot(self.world, tx, ty) and self._far_from_hazards(tx, ty, hazard_tiles, radius=3):
                lx = tx * TILE_SIZE + TILE_SIZE // 4
                ly = ty * TILE_SIZE + TILE_SIZE // 4
                rect = pygame.Rect(lx, ly, TILE_SIZE // 2, TILE_SIZE // 2)
                if any(rect.colliderect(c) for c in coins + healths + lives):
                    continue
                lives.append(rect)

        return coins, healths, lives

    def generate_powerups(self, density: float = DEFAULT_POWERUP_DENSITY) -> List[Dict[str, Any]]:
        """
        Generate typed power-ups (speed, shadow, triple, magnet).

        Args:
            density: Spawn rate for powerups

        Returns:
            List of powerup dictionaries with 'rect' and 'type' keys
        """
        powerups = []

        # Build weighted list
        types_list = []
        for ptype, weight in POWERUP_TYPES:
            types_list.extend([ptype] * weight)

        for ty in range(2, WORLD_H - 1):
            for tx in range(1, WORLD_W - 1):
                if not self._valid_pickup_spot(self.world, tx, ty):
                    continue

                if self.rng.random() < density:
                    px = tx * TILE_SIZE + TILE_SIZE // 4
                    py = ty * TILE_SIZE + TILE_SIZE // 4
                    ptype = self.rng.choice(types_list)
                    powerups.append({
                        'rect': pygame.Rect(px, py, TILE_SIZE // 2, TILE_SIZE // 2),
                        'type': ptype
                    })

        return powerups

    def generate_ability_orbs(self, spawn_rate: float = DEFAULT_ABILITY_ORB_SPAWN_RATE) -> List[pygame.Rect]:
        """
        Generate rare Ability Orb spawn points (0.3% rate by default).

        Args:
            spawn_rate: Probability per valid location (default 0.3%)

        Returns:
            List of ability orb spawn rectangles
        """
        orbs = []

        for ty in range(2, WORLD_H - 1):
            for tx in range(1, WORLD_W - 1):
                # Must be valid spawn location (same as other pickups)
                if not self._valid_pickup_spot(self.world, tx, ty):
                    continue

                # Random chance for orb spawn (very rare!)
                if self.rng.random() < spawn_rate:
                    ox = tx * TILE_SIZE + TILE_SIZE // 4
                    oy = ty * TILE_SIZE + TILE_SIZE // 4
                    orbs.append(pygame.Rect(ox, oy, TILE_SIZE // 2, TILE_SIZE // 2))

        return orbs


# Standalone helper functions (for backward compatibility if needed)
def _valid_pickup_spot(world: List[List[int]], tx: int, ty: int) -> bool:
    """Check if (tx,ty) is a valid pickup spawn location."""
    return EntityPlacer._valid_pickup_spot(world, tx, ty)


def _far_from_hazards(tx: int, ty: int, hazard_tiles: Set[Tuple[int, int]], radius: int = 3) -> bool:
    """Check if tile is far enough from hazards."""
    return EntityPlacer._far_from_hazards(tx, ty, hazard_tiles, radius)


def generate_hazards(world: List[List[int]], rng: random.Random, rate: float = DEFAULT_HAZARD_RATE) -> List[pygame.Rect]:
    """Generate spike hazards on platforms."""
    placer = EntityPlacer(world, rng)
    return placer.generate_hazards(rate)


def generate_coins_and_pickups(
    world: List[List[int]],
    rng: random.Random,
    coin_density: float = DEFAULT_COIN_DENSITY,
    health_density: float = DEFAULT_HEALTH_DENSITY,
    lives_per_level: int = DEFAULT_LIVES_PER_LEVEL,
    hazards: Optional[List[pygame.Rect]] = None
) -> Tuple[List[pygame.Rect], List[pygame.Rect], List[pygame.Rect]]:
    """Generate coins, health, and lives."""
    placer = EntityPlacer(world, rng)
    return placer.generate_coins_and_pickups(coin_density, health_density, lives_per_level, hazards)


def generate_powerups(world: List[List[int]], rng: random.Random, density: float = DEFAULT_POWERUP_DENSITY) -> List[Dict[str, Any]]:
    """Generate typed power-ups (speed, shadow, triple, magnet)."""
    placer = EntityPlacer(world, rng)
    return placer.generate_powerups(density)


def generate_ability_orbs(world: List[List[int]], rng: random.Random, spawn_rate: float = DEFAULT_ABILITY_ORB_SPAWN_RATE) -> List[pygame.Rect]:
    """Generate rare Ability Orb spawn points."""
    placer = EntityPlacer(world, rng)
    return placer.generate_ability_orbs(spawn_rate)
