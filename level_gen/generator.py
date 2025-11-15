"""
Level Generation Module - Enhanced with ability-aware patterns and power-ups
Procedural generation with optional challenges that reward enabled abilities.
"""

import random
import pygame
from collections import deque

from settings import (
    TILE_SIZE,
    ROOM_COLS, ROOM_ROWS,
    ROOM_W, ROOM_H,
    WORLD_W, WORLD_H,
    POWERUP_TYPES,
    COLOR_POWERUP_SPEED,
    COLOR_POWERUP_TRIPLE, COLOR_POWERUP_MAGNET,
)

from .constants import (
    DEFAULT_VERTICALITY_BIAS,
    DEFAULT_BRANCHINESS,
    DEFAULT_PLATFORM_BAND_STEP,
    DEFAULT_PLATFORM_LEN_RANGE,
    DEFAULT_PILLAR_CHANCE,
    DEFAULT_HOLE_CHANCE,
    DEFAULT_HAZARD_RATE,
    DEFAULT_COIN_DENSITY,
    DEFAULT_HEALTH_DENSITY,
    DEFAULT_LIVES_PER_LEVEL,
    DEFAULT_POWERUP_DENSITY,
    DEFAULT_ABILITY_ORB_SPAWN_RATE,
    DEFAULT_PHASEABLE_WALL_CHANCE,
    DEFAULT_ENABLE_ABILITY_SUBROOMS,
    DEFAULT_SUBROOM_INTENSITY,
    DEFAULT_ENABLE_ABILITY_CHALLENGES,
    CHALLENGE_ATTEMPTS,
    SUBROOM_EMPTY_THRESHOLD,
)

from .maze_generator import generate_macro_maze, find_room_path


class Room:
    def __init__(self, rx, ry):
        self.rx = rx
        self.ry = ry
        self.open_up = self.open_down = False
        self.open_left = self.open_right = False


def build_world_from_path(path):
    """Build tile world from room path."""
    world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    path_mask = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]

    for x in range(WORLD_W):
        world[0][x] = 1; world[WORLD_H - 1][x] = 1
        path_mask[0][x] = path_mask[WORLD_H - 1][x] = True
    for y in range(WORLD_H):
        world[y][0] = 1; world[y][WORLD_W - 1] = 1
        path_mask[y][0] = path_mask[y][WORLD_W - 1] = True

    floor_y_for = {}
    for (rx, ry) in path:
        base_x = rx * ROOM_W
        base_y = ry * ROOM_H
        floor_y = base_y + ROOM_H - 3
        floor_y_for[(rx, ry)] = floor_y
        for x in range(base_x + 2, base_x + ROOM_W - 2):
            world[floor_y][x] = 1
            path_mask[floor_y][x] = True
            if floor_y - 1 > 0: world[floor_y - 1][x] = 0
            if floor_y - 2 > 0: world[floor_y - 2][x] = 0

    for (rx, ry), (nx, ny) in zip(path, path[1:]):
        base_x1 = rx * ROOM_W; base_y1 = ry * ROOM_H
        base_x2 = nx * ROOM_W; base_y2 = ny * ROOM_H
        fy1 = floor_y_for[(rx, ry)]; fy2 = floor_y_for[(nx, ny)]

        if ry == ny and abs(nx - rx) == 1:
            y = fy1
            if nx > rx: x_start = base_x1 + ROOM_W - 3; x_end = base_x2 + 2
            else:       x_start = base_x2 + ROOM_W - 3; x_end = base_x1 + 2
            if x_start > x_end: x_start, x_end = x_end, x_start
            for x in range(x_start, x_end + 1):
                world[y][x] = 1; path_mask[y][x] = True
                if y - 1 > 0: world[y - 1][x] = 0
                if y - 2 > 0: world[y - 2][x] = 0
        elif nx == rx and abs(ny - ry) == 1:
            x_mid = base_x1 + ROOM_W // 2
            if ny > ry: high = (rx, ry); low = (nx, ny)
            else: high = (nx, ny); low = (rx, ry)
            fy_high = floor_y_for[high]; fy_low = floor_y_for[low]
            shaft_top = fy_high - 2; shaft_bottom = fy_low - 1
            for y in range(shaft_top, shaft_bottom + 1):
                if 0 < y < WORLD_H - 1:
                    for dx in (-1, 0, 1):
                        xx = x_mid + dx
                        if 0 < xx < WORLD_W - 1: world[y][xx] = 0
            for dx in (-1, 0, 1):
                xx = x_mid + dx
                if 0 < xx < WORLD_W - 1:
                    if 0 < fy_high < WORLD_H - 1:
                        world[fy_high][xx] = 1; path_mask[fy_high][xx] = True
                    if 0 < fy_low < WORLD_H - 1:
                        world[fy_low][xx] = 1; path_mask[fy_low][xx] = True
            side = -1; step = 4
            for y in range(shaft_bottom - 2, shaft_top, -step):
                lx = x_mid + side * 3
                if 1 < lx < WORLD_W - 2 and 1 < y < WORLD_H - 2:
                    world[y][lx] = 1; world[y][lx + 1] = 1
                    path_mask[y][lx] = path_mask[y][lx + 1] = True
                side *= -1

    end_rx, end_ry = path[-1]
    base_x = end_rx * ROOM_W
    floor_y = floor_y_for[(end_rx, end_ry)]
    ex_x = base_x + ROOM_W - 3
    ex_y = floor_y - 1
    world[ex_y][ex_x] = 2
    if 0 < floor_y < WORLD_H: path_mask[floor_y][ex_x] = True

    return world, path_mask


def decorate_world(world, path_mask, rng, **kwargs):
    """Add platforms, pillars, and holes to world."""
    platform_band_step = kwargs.get('platform_band_step', DEFAULT_PLATFORM_BAND_STEP)
    platform_len_range = kwargs.get('platform_len_range', DEFAULT_PLATFORM_LEN_RANGE)
    pillar_chance = kwargs.get('pillar_chance', DEFAULT_PILLAR_CHANCE)
    hole_chance = kwargs.get('hole_chance', DEFAULT_HOLE_CHANCE)
    
    for ry in range(ROOM_ROWS):
        for rx in range(ROOM_COLS):
            base_x = rx * ROOM_W
            base_y = ry * ROOM_H

            for band in range(2, ROOM_H - 3, max(2, platform_band_step)):
                y = base_y + band
                if not (0 < y < WORLD_H - 1): continue
                segments = rng.randint(1, 3)
                for _ in range(segments):
                    L = rng.randint(*platform_len_range)
                    start_x = base_x + rng.randint(1, max(1, ROOM_W - L - 1))
                    for x in range(start_x, min(start_x + L, base_x + ROOM_W - 1)):
                        if 0 < x < WORLD_W - 1 and not path_mask[y][x] and world[y][x] != 2:
                            world[y][x] = 1
                            if y - 1 > 0 and not path_mask[y - 1][x] and world[y - 1][x] != 2:
                                world[y - 1][x] = 0

            if rng.random() < pillar_chance:
                pillars = rng.randint(1, 3)
                for _ in range(pillars):
                    vx = base_x + rng.randint(2, ROOM_W - 2)
                    if not (0 < vx < WORLD_W - 1): continue
                    top = base_y + rng.randint(2, max(2, ROOM_H - 8))
                    bottom = min(base_y + ROOM_H - 2, top + rng.randint(3, ROOM_H // 2))
                    gap_mod = rng.randint(3, 4)
                    for y in range(top, bottom):
                        if 0 < y < WORLD_H - 1 and not path_mask[y][vx] and world[y][vx] != 2 and (y - top) % gap_mod != 0:
                            world[y][vx] = 1

            if rng.random() < hole_chance:
                holes = rng.randint(1, 3)
                for _ in range(holes):
                    hx = base_x + rng.randint(1, ROOM_W - 2)
                    hy = base_y + rng.randint(1, ROOM_H - 2)
                    if 0 < hx < WORLD_W - 1 and 0 < hy < WORLD_H - 1 and not path_mask[hy][hx] and world[hy][hx] == 1:
                        for yy in range(hy, min(hy + 2, WORLD_H - 1)):
                            for xx in range(hx, min(hx + 2, WORLD_W - 1)):
                                if 0 < xx < WORLD_W - 1 and 0 < yy < WORLD_H - 1 and not path_mask[yy][xx] and world[yy][xx] != 2:
                                    world[yy][xx] = 0


def _valid_pickup_spot(world, tx, ty):
    """Check if (tx,ty) is a valid pickup spawn location."""
    if not (1 <= tx < WORLD_W - 1 and 2 <= ty < WORLD_H - 1): 
        return False
    return world[ty][tx] == 0 and world[ty + 1][tx] == 1


def _far_from_hazards(tx, ty, hazard_tiles, radius=3):
    """Check if tile is far enough from hazards."""
    for hx, hy in hazard_tiles:
        if abs(hx - tx) <= radius and hy == ty: 
            return False
        if abs(hy - ty) <= radius and hx == tx: 
            return False
    return True


def generate_hazards(world, rng, rate=DEFAULT_HAZARD_RATE):
    """Generate spike hazards on platforms."""
    hazards = []
    for y in range(2, WORLD_H - 1):
        for x in range(1, WORLD_W - 1):
            if world[y][x] == 1 and world[y - 1][x] == 0 and world[y - 2][x] == 0:
                if rng.random() < rate:
                    hx = x * TILE_SIZE + 2
                    hy = (y - 1) * TILE_SIZE + TILE_SIZE // 2
                    hazards.append(pygame.Rect(hx, hy, TILE_SIZE - 4, TILE_SIZE // 2))
    return hazards


def generate_coins_and_pickups(world, rng, coin_density=DEFAULT_COIN_DENSITY, health_density=DEFAULT_HEALTH_DENSITY, lives_per_level=DEFAULT_LIVES_PER_LEVEL, hazards=None):
    """Generate coins, health, and lives."""
    hazards = hazards or []
    coins = []; healths = []; lives = []
    
    hazard_tiles = set()
    if hazards:
        for h in hazards:
            hx = (h.x + h.w // 2) // TILE_SIZE
            hy = (h.y + h.h // 2) // TILE_SIZE
            hazard_tiles.add((hx, hy))

    for ty in range(2, WORLD_H - 1):
        for tx in range(1, WORLD_W - 1):
            if not _valid_pickup_spot(world, tx, ty): 
                continue
            if not _far_from_hazards(tx, ty, hazard_tiles, radius=3): 
                continue
            
            if rng.random() < coin_density:
                cx = tx * TILE_SIZE + TILE_SIZE // 4
                cy = ty * TILE_SIZE + TILE_SIZE // 4
                coins.append(pygame.Rect(cx, cy, TILE_SIZE // 2, TILE_SIZE // 2))
            elif rng.random() < health_density:
                hx = tx * TILE_SIZE + TILE_SIZE // 4
                hy = ty * TILE_SIZE + TILE_SIZE // 4
                healths.append(pygame.Rect(hx, hy, TILE_SIZE // 2, TILE_SIZE // 2))

    attempts = 0
    while len(lives) < max(0, int(lives_per_level)):
        attempts += 1
        if attempts > 10000: 
            break
        tx = rng.randint(1, WORLD_W - 2)
        ty = rng.randint(2, WORLD_H - 2)
        if _valid_pickup_spot(world, tx, ty) and _far_from_hazards(tx, ty, hazard_tiles, radius=3):
            lx = tx * TILE_SIZE + TILE_SIZE // 4
            ly = ty * TILE_SIZE + TILE_SIZE // 4
            rect = pygame.Rect(lx, ly, TILE_SIZE // 2, TILE_SIZE // 2)
            if any(rect.colliderect(c) for c in coins + healths + lives): 
                continue
            lives.append(rect)

    return coins, healths, lives


def _add_ability_challenges(world, coins, rng, abilities):
    """Add optional coin patterns that reward specific abilities."""
    if not abilities:
        return
    
    # Double Jump: vertical coin arcs
    if "DOUBLE_JUMP" in abilities:
        for _ in range(rng.randint(2, 4)):
            tx = rng.randint(5, WORLD_W - 6)
            ty = rng.randint(5, WORLD_H - 8)
            if world[ty][tx] == 0:
                # Place 3-5 coins in an arc
                for i in range(3 + rng.randint(0, 2)):
                    cx = (tx + i) * TILE_SIZE + TILE_SIZE // 4
                    cy = (ty - i // 2) * TILE_SIZE + TILE_SIZE // 4
                    if 0 < ty - i // 2 < WORLD_H:
                        coins.append(pygame.Rect(cx, cy, TILE_SIZE // 2, TILE_SIZE // 2))
    
    # Dash: horizontal coin lines
    if "DASH" in abilities:
        for _ in range(rng.randint(2, 4)):
            tx = rng.randint(5, WORLD_W - 15)
            ty = rng.randint(5, WORLD_H - 6)
            if world[ty][tx] == 0:
                # Place 5-8 coins in a line
                for i in range(5 + rng.randint(0, 3)):
                    cx = (tx + i * 2) * TILE_SIZE + TILE_SIZE // 4
                    cy = ty * TILE_SIZE + TILE_SIZE // 4
                    if tx + i * 2 < WORLD_W:
                        coins.append(pygame.Rect(cx, cy, TILE_SIZE // 2, TILE_SIZE // 2))
    
    # Wall Jump: vertical coin ladders
    if "WALL_JUMP" in abilities:
        for _ in range(rng.randint(1, 3)):
            tx = rng.randint(5, WORLD_W - 6)
            ty = rng.randint(8, WORLD_H - 6)
            if world[ty][tx] == 0:
                # Place coins going up
                for i in range(4):
                    cx = tx * TILE_SIZE + TILE_SIZE // 4
                    cy = (ty - i * 2) * TILE_SIZE + TILE_SIZE // 4
                    if 2 < ty - i * 2 < WORLD_H:
                        coins.append(pygame.Rect(cx, cy, TILE_SIZE // 2, TILE_SIZE // 2))


def generate_powerups(world, rng, density=DEFAULT_POWERUP_DENSITY):
    """Generate typed power-ups (speed, shadow, triple, magnet)."""
    powerups = []
    
    # Build weighted list
    types_list = []
    for ptype, weight in POWERUP_TYPES:
        types_list.extend([ptype] * weight)
    
    for ty in range(2, WORLD_H - 1):
        for tx in range(1, WORLD_W - 1):
            if not _valid_pickup_spot(world, tx, ty):
                continue
            
            if rng.random() < density:
                px = tx * TILE_SIZE + TILE_SIZE // 4
                py = ty * TILE_SIZE + TILE_SIZE // 4
                ptype = rng.choice(types_list)
                powerups.append({
                    'rect': pygame.Rect(px, py, TILE_SIZE // 2, TILE_SIZE // 2),
                    'type': ptype
                })
    
    return powerups


def add_ability_subrooms(world, path_mask, rng, abilities, intensity=DEFAULT_SUBROOM_INTENSITY):
    """
    Add optional ability-specific challenge subrooms.
    These reward players who have unlocked specific abilities.
    
    Args:
        world: 2D level array
        path_mask: 2D bool array marking critical path
        rng: Random number generator
        abilities: List of enabled ability strings
        intensity: How many subrooms to create (0.0-1.0)
    """
    if not abilities:
        return
    
    num_subrooms = int(2 + intensity * 3)
    
    for _ in range(num_subrooms):
        if not abilities:
            break
        
        ability = rng.choice(abilities)
        
        # Find a spot for a subroom
        attempts = 0
        while attempts < CHALLENGE_ATTEMPTS:
            attempts += 1
            rx = rng.randint(1, ROOM_COLS - 2)
            ry = rng.randint(1, ROOM_ROWS - 2)
            base_x = rx * ROOM_W
            base_y = ry * ROOM_H
            
            # Check if this area is mostly empty
            empty_count = sum(1 for y in range(base_y + 2, base_y + ROOM_H - 2)
                            for x in range(base_x + 2, base_x + ROOM_W - 2)
                            if world[y][x] == 0)
            
            if empty_count > (ROOM_W - 4) * (ROOM_H - 4) * SUBROOM_EMPTY_THRESHOLD:
                # Create subroom based on ability
                if ability == "DOUBLE_JUMP":
                    # High platform requiring double jump
                    platform_y = base_y + 3
                    for x in range(base_x + 3, base_x + ROOM_W - 3):
                        world[platform_y][x] = 1
                
                elif ability == "DASH":
                    # Long gap requiring dash
                    platform_y = base_y + ROOM_H - 4
                    for x in range(base_x + 2, base_x + 5):
                        world[platform_y][x] = 1
                    for x in range(base_x + ROOM_W - 5, base_x + ROOM_W - 2):
                        world[platform_y][x] = 1
                
                elif ability == "WALL_JUMP":
                    # Vertical shaft with walls
                    shaft_x = base_x + ROOM_W // 2
                    for y in range(base_y + 2, base_y + ROOM_H - 2):
                        world[y][shaft_x - 2] = 1
                        world[y][shaft_x + 2] = 1
                        world[y][shaft_x - 1] = 0
                        world[y][shaft_x] = 0
                        world[y][shaft_x + 1] = 0
                
                break


def build_solid_rects(world):
    """Convert world grid to solid rect list."""
    tiles = []; exit_rect = None
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            v = world[y][x]
            if v == 1:
                tiles.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif v == 2:
                exit_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    return tiles, exit_rect


def find_spawn(path):
    """Find player spawn point at start of path."""
    start_rx, start_ry = path[0]
    base_x = start_rx * ROOM_W; base_y = start_ry * ROOM_H
    floor_y = base_y + ROOM_H - 3
    sx = base_x + 3; sy = floor_y - 2
    return sx * TILE_SIZE, sy * TILE_SIZE


def mark_phaseable_walls(tiles, world, rng, phaseable_wall_chance=DEFAULT_PHASEABLE_WALL_CHANCE):
    """
    Mark certain walls as phaseable (can be passed through with Shadow Step).
    Excludes boundary walls to prevent escaping the level.
    
    Args:
        tiles: List of tile rectangles
        world: 2D world array
        rng: Random number generator
        phaseable_wall_chance: Probability of marking a wall as phaseable
        
    Returns:
        List of phaseable wall rectangles
    """
    phaseable = []
    
    for t in tiles:
        # Convert rect to tile coordinates
        tx = t.x // TILE_SIZE
        ty = t.y // TILE_SIZE
        
        # Skip boundary walls
        if tx == 0 or tx == WORLD_W - 1 or ty == 0 or ty == WORLD_H - 1:
            continue
        
        # Check if this is a vertical wall (has space on left or right)
        is_vertical_wall = False
        if 0 < tx < WORLD_W - 1:
            # Check if there's air on one side
            if world[ty][tx - 1] == 0 or world[ty][tx + 1] == 0:
                # Make sure it's actually a wall barrier
                if world[ty][tx] == 1:
                    is_vertical_wall = True
        
        # Only mark vertical walls as phaseable
        if is_vertical_wall and rng.random() < phaseable_wall_chance:
            phaseable.append(t)
    
    return phaseable


def generate_ability_orbs(world, rng, spawn_rate=DEFAULT_ABILITY_ORB_SPAWN_RATE):
    """
    Generate rare Ability Orb spawn points (0.3% rate).

    Args:
        world: 2D level array
        rng: Random number generator
        spawn_rate: Probability per valid location (default 0.3%)

    Returns:
        List of ability orb spawn rectangles
    """
    orbs = []

    for ty in range(2, WORLD_H - 1):
        for tx in range(1, WORLD_W - 1):
            # Must be valid spawn location (same as other pickups)
            if not _valid_pickup_spot(world, tx, ty):
                continue

            # Random chance for orb spawn (very rare!)
            if rng.random() < spawn_rate:
                ox = tx * TILE_SIZE + TILE_SIZE // 4
                oy = ty * TILE_SIZE + TILE_SIZE // 4
                orbs.append(pygame.Rect(ox, oy, TILE_SIZE // 2, TILE_SIZE // 2))

    return orbs


def generate_level(seed=None, diff_cfg=None, abilities=None):
    """
    Generate a complete level with ability-aware features.

    Args:
        seed: Random seed
        diff_cfg: Difficulty configuration
        abilities: List of enabled abilities

    Returns:
        Tuple of (world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs)
    """
    cfg = diff_cfg or {}
    abilities = abilities or []
    rng = random.Random(seed)

    # Generate maze
    rooms = generate_macro_maze(
        ROOM_COLS, ROOM_ROWS, rng,
        verticality_bias=cfg.get("verticality_bias", DEFAULT_VERTICALITY_BIAS),
        branchiness=cfg.get("branchiness", DEFAULT_BRANCHINESS),
    )

    # Find path
    start = (0, ROOM_ROWS - 1); goal = (ROOM_COLS - 1, 0)
    path = find_room_path(rooms, start, goal, ROOM_COLS, ROOM_ROWS)
    if not path:
        path = [(x, ROOM_ROWS - 1) for x in range(ROOM_COLS)] + [(ROOM_COLS - 1, y) for y in range(ROOM_ROWS - 2, -1, -1)]

    # Build world
    world, path_mask = build_world_from_path(path)

    # Decorate
    decorate_world(
        world, path_mask, rng,
        platform_band_step=cfg.get("platform_band_step", DEFAULT_PLATFORM_BAND_STEP),
        platform_len_range=cfg.get("platform_len_range", DEFAULT_PLATFORM_LEN_RANGE),
        pillar_chance=cfg.get("pillar_chance", DEFAULT_PILLAR_CHANCE),
        hole_chance=cfg.get("hole_chance", DEFAULT_HOLE_CHANCE),
    )

    # Add ability-gated subrooms
    if cfg.get('enable_ability_subrooms', DEFAULT_ENABLE_ABILITY_SUBROOMS):
        intensity = cfg.get('subroom_intensity', DEFAULT_SUBROOM_INTENSITY)
        add_ability_subrooms(world, path_mask, rng, abilities, intensity)

    # Build solids
    tiles, exit_rect = build_solid_rects(world)

    # Generate hazards
    hazards = generate_hazards(world, rng, rate=cfg.get("hazard_rate", DEFAULT_HAZARD_RATE))

    # Generate pickups
    coins, healths, lives = generate_coins_and_pickups(
        world, rng,
        coin_density=cfg.get("coin_density", DEFAULT_COIN_DENSITY),
        health_density=cfg.get("health_density", DEFAULT_HEALTH_DENSITY),
        lives_per_level=cfg.get("lives_per_level", DEFAULT_LIVES_PER_LEVEL),
        hazards=hazards
    )

    # Add ability-aware coin challenges
    if cfg.get('enable_ability_challenges', DEFAULT_ENABLE_ABILITY_CHALLENGES):
        _add_ability_challenges(world, coins, rng, abilities)

    # Generate power-ups
    powerups = generate_powerups(world, rng, density=cfg.get("powerup_density", DEFAULT_POWERUP_DENSITY))

    # Generate Ability Orbs (RARE - 0.3% spawn rate)
    ability_orbs = generate_ability_orbs(world, rng, spawn_rate=cfg.get("ability_orb_spawn_rate", DEFAULT_ABILITY_ORB_SPAWN_RATE))

    # Mark phaseable walls for Shadow Step ability
    phaseable_walls = []
    if "SHADOW_STEP" in abilities:
        phaseable_walls = mark_phaseable_walls(tiles, world, rng, cfg.get("phaseable_wall_chance", DEFAULT_PHASEABLE_WALL_CHANCE))

    spawn = find_spawn(path)

    return world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs
