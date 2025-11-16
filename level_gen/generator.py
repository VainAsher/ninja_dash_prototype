"""
Level Generation Module - Enhanced with ability-aware patterns and power-ups
Procedural generation with optional challenges that reward enabled abilities.
"""

import random
import pygame
from collections import deque
from typing import List, Tuple, Optional, Dict, Any

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
from .decorations import decorate_world, build_solid_rects
from .ability_features import add_ability_challenges, add_ability_subrooms
from .entity_placer import (
    generate_hazards,
    generate_coins_and_pickups,
    generate_powerups,
    generate_ability_orbs,
)
from .structures import Room


def build_world_from_path(path: List[Tuple[int, int]]) -> Tuple[List[List[int]], List[List[bool]]]:
    """Build tile world from room path.

    Args:
        path: List of (x, y) tuples representing the room path

    Returns:
        Tuple of (world, path_mask) where world is a 2D tile array and path_mask marks critical path tiles
    """
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


def find_spawn(path: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Find player spawn point at start of path.

    Args:
        path: List of (x, y) tuples representing the room path

    Returns:
        Tuple of (spawn_x, spawn_y) in pixel coordinates
    """
    start_rx, start_ry = path[0]
    base_x = start_rx * ROOM_W; base_y = start_ry * ROOM_H
    floor_y = base_y + ROOM_H - 3
    sx = base_x + 3; sy = floor_y - 2
    return sx * TILE_SIZE, sy * TILE_SIZE


def mark_phaseable_walls(
    tiles: List[pygame.Rect],
    world: List[List[int]],
    rng: random.Random,
    phaseable_wall_chance: float = DEFAULT_PHASEABLE_WALL_CHANCE
) -> List[pygame.Rect]:
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


def generate_level(
    seed: Optional[int] = None,
    diff_cfg: Optional[Dict[str, Any]] = None,
    abilities: Optional[List[str]] = None
) -> Tuple[
    List[List[int]],
    List[pygame.Rect],
    pygame.Rect,
    Tuple[int, int],
    List[pygame.Rect],
    List[pygame.Rect],
    List[pygame.Rect],
    List[pygame.Rect],
    List[Dict[str, Any]],
    List[pygame.Rect],
    List[pygame.Rect]
]:
    """
    Generate a complete level with ability-aware features.

    Args:
        seed: Random seed
        diff_cfg: Difficulty configuration dictionary
        abilities: List of enabled ability strings

    Returns:
        Tuple of (world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs)
        - world: 2D tile array
        - tiles: List of solid tile rectangles
        - exit_rect: Exit rectangle
        - spawn: Player spawn point (x, y) in pixels
        - coins: List of coin rectangles
        - hazards: List of hazard rectangles
        - healths: List of health pickup rectangles
        - lives: List of extra life rectangles
        - powerups: List of powerup dictionaries with 'rect' and 'type' keys
        - phaseable_walls: List of phaseable wall rectangles (for Shadow Step)
        - ability_orbs: List of ability orb rectangles
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
        add_ability_challenges(world, coins, rng, abilities)

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
