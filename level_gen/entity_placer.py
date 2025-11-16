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
    HAZARD_SAFE_RADIUS,
    MAX_SPAWN_ATTEMPTS,
)

from .utils import valid_pickup_spot, enhanced_valid_pickup_spot, far_from_hazards, pixel_to_tile


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

    def _find_nearby_magnets(
        self,
        tx: int,
        ty: int,
        powerups: List[Dict[str, Any]],
        radius: int = 15
    ) -> bool:
        """
        Check if there are any magnet powerups near a given tile position.

        This enables strategic "risky" coin placement near magnets, creating
        risk/reward gameplay where players who find magnets can access more coins.

        Args:
            tx: Tile x-coordinate
            ty: Tile y-coordinate
            powerups: List of powerup dictionaries with 'rect' and 'type'
            radius: Search radius in tiles (default 15 tiles)

        Returns:
            True if at least one magnet powerup is within radius
        """
        if not powerups:
            return False

        for powerup in powerups:
            if powerup.get('type') != 'magnet':
                continue

            # Convert powerup pixel position to tile coordinates
            powerup_rect = powerup['rect']
            powerup_tx = powerup_rect.centerx // TILE_SIZE
            powerup_ty = powerup_rect.centery // TILE_SIZE

            # Calculate Manhattan distance
            distance = abs(powerup_tx - tx) + abs(powerup_ty - ty)

            if distance <= radius:
                return True

        return False

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
        hazards: Optional[List[pygame.Rect]] = None,
        powerups: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[List[pygame.Rect], List[pygame.Rect], List[pygame.Rect]]:
        """
        Generate coins, health, and lives with enhanced placement validation.

        NEW BEHAVIOR:
        - Uses enhanced_valid_pickup_spot() for better safety
        - Checks for nearby magnet powerups
        - Allows "risky" placement near magnets for strategic gameplay

        Args:
            coin_density: Spawn rate for coins
            health_density: Spawn rate for health pickups
            lives_per_level: Number of extra lives to spawn
            hazards: List of hazard rectangles to avoid
            powerups: List of powerup dicts (for magnet proximity check)

        Returns:
            Tuple of (coins, healths, lives) - lists of rectangles
        """
        hazards = hazards or []
        powerups = powerups or []
        coins = []
        healths = []
        lives = []

        # Build hazard tile set for proximity checks
        hazard_tiles = set()
        if hazards:
            for h in hazards:
                # Get center point of hazard and convert to tile coordinates
                center_x = h.x + h.w // 2
                center_y = h.y + h.h // 2
                hx, hy = pixel_to_tile(center_x, center_y)
                hazard_tiles.add((hx, hy))

        # Generate coins and health pickups with ENHANCED validation
        for ty in range(2, WORLD_H - 1):
            for tx in range(1, WORLD_W - 1):
                # Check if there's a magnet powerup nearby
                magnet_nearby = self._find_nearby_magnets(tx, ty, powerups, radius=15)

                # Use enhanced validation (allow risky spots near magnets)
                if not enhanced_valid_pickup_spot(
                    self.world, tx, ty, allow_risky=magnet_nearby
                ):
                    continue

                # Standard hazard proximity check
                if not far_from_hazards(tx, ty, hazard_tiles, radius=HAZARD_SAFE_RADIUS):
                    continue

                if self.rng.random() < coin_density:
                    cx = tx * TILE_SIZE + TILE_SIZE // 4
                    cy = ty * TILE_SIZE + TILE_SIZE // 4
                    coins.append(pygame.Rect(cx, cy, TILE_SIZE // 2, TILE_SIZE // 2))
                elif self.rng.random() < health_density:
                    hx = tx * TILE_SIZE + TILE_SIZE // 4
                    hy = ty * TILE_SIZE + TILE_SIZE // 4
                    healths.append(pygame.Rect(hx, hy, TILE_SIZE // 2, TILE_SIZE // 2))

        # Generate extra lives (random placement with enhanced validation)
        attempts = 0
        while len(lives) < max(0, int(lives_per_level)):
            attempts += 1
            if attempts > MAX_SPAWN_ATTEMPTS:
                break
            tx = self.rng.randint(1, WORLD_W - 2)
            ty = self.rng.randint(2, WORLD_H - 2)

            # Check for nearby magnets for this life pickup too
            magnet_nearby = self._find_nearby_magnets(tx, ty, powerups, radius=15)

            if (enhanced_valid_pickup_spot(self.world, tx, ty, allow_risky=magnet_nearby) and
                far_from_hazards(tx, ty, hazard_tiles, radius=HAZARD_SAFE_RADIUS)):
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
                if not valid_pickup_spot(self.world, tx, ty):
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
                if not valid_pickup_spot(self.world, tx, ty):
                    continue

                # Random chance for orb spawn (very rare!)
                if self.rng.random() < spawn_rate:
                    ox = tx * TILE_SIZE + TILE_SIZE // 4
                    oy = ty * TILE_SIZE + TILE_SIZE // 4
                    orbs.append(pygame.Rect(ox, oy, TILE_SIZE // 2, TILE_SIZE // 2))

        return orbs


# Standalone helper functions (for backward compatibility)
# These now delegate to the utils module
def _valid_pickup_spot(world: List[List[int]], tx: int, ty: int) -> bool:
    """Check if (tx,ty) is a valid pickup spawn location."""
    return valid_pickup_spot(world, tx, ty)


def _far_from_hazards(tx: int, ty: int, hazard_tiles: Set[Tuple[int, int]], radius: int = HAZARD_SAFE_RADIUS) -> bool:
    """Check if tile is far enough from hazards."""
    return far_from_hazards(tx, ty, hazard_tiles, radius)


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
    hazards: Optional[List[pygame.Rect]] = None,
    powerups: Optional[List[Dict[str, Any]]] = None
) -> Tuple[List[pygame.Rect], List[pygame.Rect], List[pygame.Rect]]:
    """Generate coins, health, and lives with enhanced validation."""
    placer = EntityPlacer(world, rng)
    return placer.generate_coins_and_pickups(coin_density, health_density, lives_per_level, hazards, powerups)


def generate_powerups(world: List[List[int]], rng: random.Random, density: float = DEFAULT_POWERUP_DENSITY) -> List[Dict[str, Any]]:
    """Generate typed power-ups (speed, shadow, triple, magnet)."""
    placer = EntityPlacer(world, rng)
    return placer.generate_powerups(density)


def generate_ability_orbs(world: List[List[int]], rng: random.Random, spawn_rate: float = DEFAULT_ABILITY_ORB_SPAWN_RATE) -> List[pygame.Rect]:
    """Generate rare Ability Orb spawn points."""
    placer = EntityPlacer(world, rng)
    return placer.generate_ability_orbs(spawn_rate)
