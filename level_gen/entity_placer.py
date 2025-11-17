"""
Entity Placement Module - Handles spawning of coins, pickups, powerups, hazards, and ability orbs
Separated from generator.py for better separation of concerns.
"""

import random
import pygame
import math
from typing import List, Tuple, Set, Optional, Dict, Any

from settings import (
    TILE_SIZE,
    WORLD_W, WORLD_H,
    POWERUP_TYPES,
    POWERUP_MAGNET_RADIUS,
)

from .constants import (
    DEFAULT_HAZARD_RATE,
    DEFAULT_COIN_DENSITY,
    DEFAULT_COIN_COUNT_RANGE,
    DEFAULT_HEALTH_DENSITY,
    DEFAULT_LIVES_PER_LEVEL,
    DEFAULT_POWERUP_DENSITY,
    DEFAULT_ABILITY_ORB_SPAWN_RATE,
    DEFAULT_ENEMY_DENSITY,
    HAZARD_SAFE_RADIUS,
    ENEMY_MIN_SEPARATION,
    MAX_SPAWN_ATTEMPTS,
)

from .utils import valid_pickup_spot, far_from_hazards, pixel_to_tile


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

    def _has_nearby_magnet(
        self,
        position: Tuple[int, int],
        magnet_positions: List[Tuple[int, int]],
        radius: float
    ) -> bool:
        """
        Check if there's a magnet powerup within radius of the given position.

        Args:
            position: (x, y) position to check
            magnet_positions: List of (x, y) positions of magnet powerups
            radius: Search radius in pixels

        Returns:
            True if a magnet powerup is within radius
        """
        px, py = position
        for mx, my in magnet_positions:
            dx = px - mx
            dy = py - my
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= radius:
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
        powerups: Optional[List[Dict[str, Any]]] = None,
        tiles: Optional[List[pygame.Rect]] = None,
        coin_count_range: Optional[Tuple[int, int]] = None
    ) -> Tuple[List[pygame.Rect], List[pygame.Rect], List[pygame.Rect]]:
        """
        Generate coins, health, and lives with collision detection.

        Args:
            coin_density: Spawn rate for coins (deprecated - use coin_count_range)
            health_density: Spawn rate for health pickups
            lives_per_level: Number of extra lives to spawn
            hazards: List of hazard rectangles to avoid
            powerups: List of powerup dictionaries (to check for nearby magnet powerups)
            tiles: List of solid tile rectangles (to check for collision)
            coin_count_range: Target range for coin count (min, max) - if provided, overrides density-based spawning

        Returns:
            Tuple of (coins, healths, lives) - lists of rectangles
        """
        hazards = hazards or []
        powerups = powerups or []
        tiles = tiles or []
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

        # Extract magnet powerup positions for proximity checks
        magnet_positions = []
        for powerup in powerups:
            if powerup.get('type') == 'magnet':
                magnet_positions.append(powerup['rect'].center)

        # Collect all valid spawn locations
        valid_locations = []
        for ty in range(2, WORLD_H - 1):
            for tx in range(1, WORLD_W - 1):
                if not valid_pickup_spot(self.world, tx, ty):
                    continue
                if not far_from_hazards(tx, ty, hazard_tiles, radius=HAZARD_SAFE_RADIUS):
                    continue
                valid_locations.append((tx, ty))

        # Use count-based spawning if coin_count_range is provided
        if coin_count_range is not None:
            min_coins, max_coins = coin_count_range
            target_coin_count = self.rng.randint(min_coins, max_coins)

            # Shuffle valid locations and pick first N for coins
            self.rng.shuffle(valid_locations)

            for i, (tx, ty) in enumerate(valid_locations):
                if len(coins) >= target_coin_count:
                    break

                cx = tx * TILE_SIZE + TILE_SIZE // 4
                cy = ty * TILE_SIZE + TILE_SIZE // 4
                coin_rect = pygame.Rect(cx, cy, TILE_SIZE // 2, TILE_SIZE // 2)

                # Check for collision with hazards or solid tiles
                has_collision = False
                if any(coin_rect.colliderect(h) for h in hazards):
                    has_collision = True
                if any(coin_rect.colliderect(t) for t in tiles):
                    has_collision = True

                # If collision detected, only allow if there's a nearby magnet powerup
                if has_collision:
                    has_nearby_magnet = self._has_nearby_magnet(
                        coin_rect.center,
                        magnet_positions,
                        POWERUP_MAGNET_RADIUS
                    )
                    if not has_nearby_magnet:
                        continue  # Skip this coin

                coins.append(coin_rect)

            # Generate health pickups from remaining locations
            for tx, ty in valid_locations[len(coins):]:
                if self.rng.random() < health_density:
                    hx = tx * TILE_SIZE + TILE_SIZE // 4
                    hy = ty * TILE_SIZE + TILE_SIZE // 4
                    healths.append(pygame.Rect(hx, hy, TILE_SIZE // 2, TILE_SIZE // 2))
        else:
            # Legacy probability-based spawning
            for tx, ty in valid_locations:
                if self.rng.random() < coin_density:
                    cx = tx * TILE_SIZE + TILE_SIZE // 4
                    cy = ty * TILE_SIZE + TILE_SIZE // 4
                    coin_rect = pygame.Rect(cx, cy, TILE_SIZE // 2, TILE_SIZE // 2)

                    # Check for collision with hazards or solid tiles
                    has_collision = False
                    if any(coin_rect.colliderect(h) for h in hazards):
                        has_collision = True
                    if any(coin_rect.colliderect(t) for t in tiles):
                        has_collision = True

                    # If collision detected, only allow if there's a nearby magnet powerup
                    if has_collision:
                        has_nearby_magnet = self._has_nearby_magnet(
                            coin_rect.center,
                            magnet_positions,
                            POWERUP_MAGNET_RADIUS
                        )
                        if not has_nearby_magnet:
                            continue  # Skip this coin

                    coins.append(coin_rect)
                elif self.rng.random() < health_density:
                    hx = tx * TILE_SIZE + TILE_SIZE // 4
                    hy = ty * TILE_SIZE + TILE_SIZE // 4
                    healths.append(pygame.Rect(hx, hy, TILE_SIZE // 2, TILE_SIZE // 2))

        # Generate extra lives (random placement)
        attempts = 0
        while len(lives) < max(0, int(lives_per_level)):
            attempts += 1
            if attempts > MAX_SPAWN_ATTEMPTS:
                break
            tx = self.rng.randint(1, WORLD_W - 2)
            ty = self.rng.randint(2, WORLD_H - 2)
            if valid_pickup_spot(self.world, tx, ty) and far_from_hazards(tx, ty, hazard_tiles, radius=HAZARD_SAFE_RADIUS):
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

    def generate_enemies(
        self,
        enemy_density: float = 0.05,
        spawn_pos: Optional[Tuple[int, int]] = None,
        min_separation: int = 20
    ) -> List[Tuple[int, int]]:
        """
        Generate enemy spawn positions on platforms with proximity checking.

        Args:
            enemy_density: Spawn rate for enemies (probability per valid location)
            spawn_pos: Player spawn position to avoid (pixel coordinates)
            min_separation: Minimum distance between enemies in tiles (default: 20)

        Returns:
            List of (x, y) enemy spawn positions in pixel coordinates
        """
        enemy_positions = []
        enemy_tiles = []  # Track enemy positions in tile coordinates

        # Define safe zone around player spawn (first room)
        safe_zone_radius = 5  # tiles
        player_spawn_tile = None

        if spawn_pos:
            px, py = spawn_pos
            player_spawn_tile = (px // TILE_SIZE, py // TILE_SIZE)

        # Scan for valid enemy spawn locations
        for ty in range(2, WORLD_H - 1):
            for tx in range(1, WORLD_W - 1):
                # Must be valid spawn location (on a platform)
                if not valid_pickup_spot(self.world, tx, ty):
                    continue

                # Skip if too close to player spawn
                if player_spawn_tile:
                    ptx, pty = player_spawn_tile
                    distance = abs(tx - ptx) + abs(ty - pty)  # Manhattan distance
                    if distance < safe_zone_radius:
                        continue

                # Check if too close to any existing enemy
                too_close = False
                for etx, ety in enemy_tiles:
                    # Calculate Euclidean distance for better circular spacing
                    dx = tx - etx
                    dy = ty - ety
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < min_separation:
                        too_close = True
                        break

                if too_close:
                    continue

                # Random chance for enemy spawn
                if self.rng.random() < enemy_density:
                    # Convert tile to pixel coordinates (centered on platform)
                    ex = tx * TILE_SIZE
                    # Spawn enemy so its bottom is slightly embedded in platform
                    # This ensures collision detection triggers on first frame
                    # Platform top is at (ty + 1) * TILE_SIZE
                    # Enemy bottom should be at platform_top + 2 for guaranteed overlap
                    ey = (ty + 1) * TILE_SIZE - TILE_SIZE + 2
                    enemy_positions.append((ex, ey))
                    enemy_tiles.append((tx, ty))

        return enemy_positions


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
    powerups: Optional[List[Dict[str, Any]]] = None,
    tiles: Optional[List[pygame.Rect]] = None,
    coin_count_range: Optional[Tuple[int, int]] = None
) -> Tuple[List[pygame.Rect], List[pygame.Rect], List[pygame.Rect]]:
    """Generate coins, health, and lives with collision detection."""
    placer = EntityPlacer(world, rng)
    return placer.generate_coins_and_pickups(coin_density, health_density, lives_per_level, hazards, powerups, tiles, coin_count_range)


def generate_powerups(world: List[List[int]], rng: random.Random, density: float = DEFAULT_POWERUP_DENSITY) -> List[Dict[str, Any]]:
    """Generate typed power-ups (speed, shadow, triple, magnet)."""
    placer = EntityPlacer(world, rng)
    return placer.generate_powerups(density)


def generate_ability_orbs(world: List[List[int]], rng: random.Random, spawn_rate: float = DEFAULT_ABILITY_ORB_SPAWN_RATE) -> List[pygame.Rect]:
    """Generate rare Ability Orb spawn points."""
    placer = EntityPlacer(world, rng)
    return placer.generate_ability_orbs(spawn_rate)
