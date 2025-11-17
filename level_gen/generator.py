"""
Level Generation Module - Enhanced with ability-aware patterns and power-ups
Procedural generation with optional challenges that reward enabled abilities.
"""

import random
import pygame
from collections import deque
from typing import List, Tuple, Optional, Dict, Any, Union

from settings import (
    TILE_SIZE,
    ROOM_COLS, ROOM_ROWS,
    ROOM_W, ROOM_H,
    WORLD_W, WORLD_H,
    POWERUP_TYPES,
    COLOR_POWERUP_SPEED,
    COLOR_POWERUP_TRIPLE, COLOR_POWERUP_MAGNET,
)

from .config import LevelGenConfig
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
    ROOM_FLOOR_OFFSET,
)

from .maze_generator import generate_macro_maze, find_room_path
from .decorations import decorate_world, build_solid_rects
from .ability_features import add_ability_challenges, add_ability_subrooms
from .entity_placer import (
    generate_hazards,
    generate_coins_and_pickups,
    generate_powerups,
    generate_ability_orbs,
    EntityPlacer,
)
from .structures import Room
from .utils import pixel_to_tile, is_on_boundary


# Helper functions for world building

def _build_room_floors(
    world: List[List[int]],
    path_mask: List[List[bool]],
    path: List[Tuple[int, int]]
) -> Dict[Tuple[int, int], int]:
    """
    Build horizontal floors in each room along the critical path.

    Creates a solid floor near the bottom of each room, leaving space for
    decorations and vertical movement. Clears airspace above the floor.

    Args:
        world: 2D tile array (modified in-place)
        path_mask: 2D bool array marking critical path (modified in-place)
        path: List of (x, y) room coordinates

    Returns:
        Dictionary mapping room coordinates to their floor y-coordinate

    Visual Layout (single room):
        ║              ║  top of room
        ║              ║
        ║              ║  open space
        ║              ║
        ║              ║  cleared (floor_y - 2)
        ║              ║  cleared (floor_y - 1)
        ║══════════════║  floor (floor_y = base_y + ROOM_H - ROOM_FLOOR_OFFSET)
        ║##############║  (unused space below floor)
        ╚══════════════╝  room bottom

    Floor Properties:
        - Spans full room width minus 2-tile margin on each side
        - Height: ROOM_FLOOR_OFFSET tiles from room bottom
        - Clearance: 2 tiles above floor cleared for movement
    """
    floor_y_for = {}

    for (rx, ry) in path:
        base_x = rx * ROOM_W
        base_y = ry * ROOM_H
        floor_y = base_y + ROOM_H - ROOM_FLOOR_OFFSET
        floor_y_for[(rx, ry)] = floor_y

        # Create floor across room width
        for x in range(base_x + 2, base_x + ROOM_W - 2):
            world[floor_y][x] = 1
            path_mask[floor_y][x] = True
            # Clear space above floor
            if floor_y - 1 > 0:
                world[floor_y - 1][x] = 0
            if floor_y - 2 > 0:
                world[floor_y - 2][x] = 0

    return floor_y_for


def _connect_horizontal_rooms(
    world: List[List[int]],
    path_mask: List[List[bool]],
    rx: int,
    ry: int,
    nx: int,
    ny: int,
    floor_y: int
) -> None:
    """
    Connect two horizontally adjacent rooms with a floor corridor.

    Creates a horizontal walkway between two side-by-side rooms by extending
    the floor from one room's edge to the other, with clearance above.

    Args:
        world: 2D tile array (modified in-place)
        path_mask: 2D bool array marking critical path (modified in-place)
        rx: Current room x-coordinate
        ry: Current room y-coordinate
        nx: Next room x-coordinate (must be rx±1)
        ny: Next room y-coordinate (must equal ry)
        floor_y: Floor y-coordinate for the connection

    Visual Layout (moving right, rx=0 to nx=1):
        Room 0          Room 1
        ########║       ║########
        ........ ║       ║ ........
        ........ ║       ║ ........
        ========╬═══════╬======== floor_y
                └───────┘
                corridor

    Corridor extends from right edge of left room to left edge of right room.
    Two rows above floor are cleared for player movement.
    """
    base_x1 = rx * ROOM_W
    base_x2 = nx * ROOM_W

    # Determine connection span
    if nx > rx:
        x_start = base_x1 + ROOM_W - 3
        x_end = base_x2 + 2
    else:
        x_start = base_x2 + ROOM_W - 3
        x_end = base_x1 + 2

    if x_start > x_end:
        x_start, x_end = x_end, x_start

    # Build connecting floor
    for x in range(x_start, x_end + 1):
        world[floor_y][x] = 1
        path_mask[floor_y][x] = True
        # Clear space above
        if floor_y - 1 > 0:
            world[floor_y - 1][x] = 0
        if floor_y - 2 > 0:
            world[floor_y - 2][x] = 0


def _connect_vertical_rooms(
    world: List[List[int]],
    path_mask: List[List[bool]],
    rx: int,
    ry: int,
    nx: int,
    ny: int,
    fy_high: int,
    fy_low: int
) -> None:
    """
    Connect two vertically adjacent rooms with a climbable shaft.

    Creates a vertical passage with alternating platforms to allow the player
    to traverse between rooms at different heights. The shaft is carved through
    the middle of the room with platforms staggered for jumping.

    Args:
        world: 2D tile array (modified in-place)
        path_mask: 2D bool array marking critical path (modified in-place)
        rx: Current room x-coordinate (must equal nx)
        ry: Current room y-coordinate
        nx: Next room x-coordinate (must equal rx)
        ny: Next room y-coordinate (must be ry±1)
        fy_high: Floor y-coordinate of higher room (lower y value)
        fy_low: Floor y-coordinate of lower room (higher y value)

    Visual Layout (vertical shaft with alternating platforms):
        ════════════  fy_high (top room floor)
             ║║║       shaft opening
             ║║║
          ══╬║║╬══    platform (left side)
             ║║║
             ║║║
        ══╬║║╬       platform (right side)
           ║║║
           ║║║
        ══════════    fy_low (bottom room floor)

    Shaft Details:
        - Width: 3 tiles centered in room
        - Platforms: Alternating sides every 4 tiles vertically
        - Platform size: 2 tiles wide
        - Clearance: 2 tiles above each floor entrance
    """
    base_x = rx * ROOM_W
    x_mid = base_x + ROOM_W // 2

    shaft_top = fy_high - 2
    shaft_bottom = fy_low - 1

    # Carve out vertical shaft
    for y in range(shaft_top, shaft_bottom + 1):
        if 0 < y < WORLD_H - 1:
            for dx in (-1, 0, 1):
                xx = x_mid + dx
                if 0 < xx < WORLD_W - 1:
                    world[y][xx] = 0

    # Add platforms at shaft entrances
    for dx in (-1, 0, 1):
        xx = x_mid + dx
        if 0 < xx < WORLD_W - 1:
            if 0 < fy_high < WORLD_H - 1:
                world[fy_high][xx] = 1
                path_mask[fy_high][xx] = True
            if 0 < fy_low < WORLD_H - 1:
                world[fy_low][xx] = 1
                path_mask[fy_low][xx] = True

    # Add alternating platforms along shaft
    side = -1
    step = 4
    for y in range(shaft_bottom - 2, shaft_top, -step):
        lx = x_mid + side * 3
        if 1 < lx < WORLD_W - 2 and 1 < y < WORLD_H - 2:
            world[y][lx] = 1
            world[y][lx + 1] = 1
            path_mask[y][lx] = True
            path_mask[y][lx + 1] = True
        side *= -1


def _place_exit(
    world: List[List[int]],
    path_mask: List[List[bool]],
    end_room: Tuple[int, int],
    floor_y: int
) -> None:
    """
    Place the exit at the end of the path.

    Args:
        world: 2D tile array (modified in-place)
        path_mask: 2D bool array marking critical path (modified in-place)
        end_room: Tuple of (x, y) for the ending room
        floor_y: Floor y-coordinate of the ending room
    """
    end_rx, end_ry = end_room
    base_x = end_rx * ROOM_W

    ex_x = base_x + ROOM_W - 3
    ex_y = floor_y - 1

    world[ex_y][ex_x] = 2

    if 0 < floor_y < WORLD_H:
        path_mask[floor_y][ex_x] = True


def build_world_from_path(path: List[Tuple[int, int]]) -> Tuple[List[List[int]], List[List[bool]]]:
    """Build tile world from room path with floors, connections, and exit.

    Constructs a complete playable level from a sequence of room coordinates by:
    1. Creating bordered world with solid edges
    2. Building floors in each room at a consistent height
    3. Connecting adjacent rooms (horizontal hallways, vertical shafts)
    4. Placing exit gate at the end of the path

    Args:
        path: Ordered list of (x, y) room coordinate tuples defining the critical path
              from start to goal. Typically starts at (0, ROOM_ROWS-1) and ends
              at (ROOM_COLS-1, 0). Adjacent rooms must differ by exactly 1 in
              either x or y coordinate.

    Returns:
        Tuple of (world, path_mask):
        - world: 2D tile array [WORLD_H][WORLD_W] where:
          - 0 = air/empty space
          - 1 = solid tile/wall
          - 2 = exit gate
        - path_mask: 2D boolean array [WORLD_H][WORLD_W] marking tiles that are
          part of the critical path (should not be obstructed by decorations)

    Example:
        >>> # Generate simple 3-room horizontal path
        >>> path = [(0, 5), (1, 5), (2, 5)]
        >>> world, path_mask = build_world_from_path(path)
        >>> # world[y][x] contains tile values
        >>> # path_mask[y][x] is True for critical path tiles

    Edge Cases:
        - Empty path: Will create bordered world but no playable content
        - Single room path: Creates one room with exit but no connections
        - Non-adjacent rooms: Will skip invalid connections (rooms must be adjacent)
        - Path with loops: Each connection is processed in order; loops are fine

    Technical Details:
        - Room floors are placed at: room_base_y + ROOM_H - ROOM_FLOOR_OFFSET
        - Horizontal connections span the gap between room edges
        - Vertical connections create shaft with alternating platform steps
        - Exit is always placed at right edge of final room
    """
    # Initialize world and path mask
    world = [[0 for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    path_mask = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]

    # Build borders
    for x in range(WORLD_W):
        world[0][x] = 1
        world[WORLD_H - 1][x] = 1
        path_mask[0][x] = True
        path_mask[WORLD_H - 1][x] = True
    for y in range(WORLD_H):
        world[y][0] = 1
        world[y][WORLD_W - 1] = 1
        path_mask[y][0] = True
        path_mask[y][WORLD_W - 1] = True

    # Build room floors
    floor_y_for = _build_room_floors(world, path_mask, path)

    # Connect adjacent rooms
    for (rx, ry), (nx, ny) in zip(path, path[1:]):
        fy1 = floor_y_for[(rx, ry)]
        fy2 = floor_y_for[(nx, ny)]

        # Horizontal connection
        if ry == ny and abs(nx - rx) == 1:
            _connect_horizontal_rooms(world, path_mask, rx, ry, nx, ny, fy1)

        # Vertical connection
        elif nx == rx and abs(ny - ry) == 1:
            # Determine which room is higher
            if ny > ry:
                high_room = (rx, ry)
                low_room = (nx, ny)
            else:
                high_room = (nx, ny)
                low_room = (rx, ry)

            fy_high = floor_y_for[high_room]
            fy_low = floor_y_for[low_room]

            _connect_vertical_rooms(world, path_mask, rx, ry, nx, ny, fy_high, fy_low)

    # Place exit at end of path
    _place_exit(world, path_mask, path[-1], floor_y_for[path[-1]])

    return world, path_mask


def find_spawn(path: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Calculate safe player spawn point at the start of the level path.

    Places the player spawn at the beginning of the critical path (first room),
    positioned on the floor with clearance above for the player entity.

    Args:
        path: List of (x, y) room coordinate tuples. Only the first element is used.

    Returns:
        Tuple of (spawn_x, spawn_y) in pixel coordinates (not tile coordinates).
        Spawn point is positioned:
        - Horizontally: 3 tiles from left edge of starting room
        - Vertically: 2 tiles above the room floor

    Example:
        >>> path = [(0, 5), (1, 5), (2, 5)]
        >>> spawn_x, spawn_y = find_spawn(path)
        >>> # Returns pixel coordinates for player start position
        >>> spawn_x % TILE_SIZE == 0  # Aligned to tile grid
        True

    Edge Cases:
        - Empty path: Will cause IndexError (path must have at least 1 room)
        - Spawn coordinates are NOT bounds-checked against world dimensions

    Note:
        Spawn coordinates must match the floor height calculated in build_world_from_path()
        to ensure player starts on solid ground.
    """
    start_rx, start_ry = path[0]
    base_x = start_rx * ROOM_W; base_y = start_ry * ROOM_H
    floor_y = base_y + ROOM_H - ROOM_FLOOR_OFFSET
    sx = base_x + 3; sy = floor_y - 2
    return sx * TILE_SIZE, sy * TILE_SIZE


def mark_phaseable_walls(
    tiles: List[pygame.Rect],
    world: List[List[int]],
    rng: random.Random,
    phaseable_wall_chance: float = DEFAULT_PHASEABLE_WALL_CHANCE
) -> List[pygame.Rect]:
    """
    Designate vertical walls that can be phased through with Shadow Step ability.

    Randomly selects a subset of vertical interior walls to mark as phaseable,
    allowing players with the Shadow Step ability to pass through them. This
    creates shortcuts and alternate paths for advanced players.

    Args:
        tiles: List of all solid tile rectangles in the level
        world: 2D tile array where 1=solid, 0=air
        rng: Seeded random number generator for deterministic selection
        phaseable_wall_chance: Probability (0.0-1.0) of marking each eligible wall
                               as phaseable. Default: 0.35 (35%)

    Returns:
        List of pygame.Rect objects representing walls that can be phased through.
        Subset of input tiles list.

    Selection Criteria:
        - Must be a vertical wall (air on left OR right side)
        - Must NOT be on level boundary (prevents escaping)
        - Must be solid tile (world[ty][tx] == 1)
        - Randomly selected based on phaseable_wall_chance

    Example:
        >>> import random
        >>> tiles = [pygame.Rect(x*32, y*32, 32, 32) for ...]  # All walls
        >>> world = [[1, 0, 1], [1, 0, 1], ...]  # Level grid
        >>> rng = random.Random(42)
        >>> phaseable = mark_phaseable_walls(tiles, world, rng, 0.5)
        >>> len(phaseable) < len(tiles)  # Subset of original tiles
        True
        >>> all(t in tiles for t in phaseable)  # All are from original set
        True

    Edge Cases:
        - No eligible walls: Returns empty list
        - phaseable_wall_chance = 0.0: Returns empty list
        - phaseable_wall_chance = 1.0: Returns all eligible vertical walls
        - Boundary walls: Always excluded regardless of chance

    Performance:
        O(n) where n = len(tiles). Checks each tile once with simple boundary
        and adjacency tests.
    """
    phaseable = []

    for t in tiles:
        # Convert rect to tile coordinates
        tx, ty = pixel_to_tile(t.x, t.y)

        # Skip boundary walls
        if is_on_boundary(tx, ty):
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
    diff_cfg: Optional[Union[Dict[str, Any], LevelGenConfig]] = None,
    abilities: Optional[List[str]] = None,
    config: Optional[LevelGenConfig] = None,
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
    List[pygame.Rect],
    List[Tuple[int, int]]
]:
    """
    Generate a complete level with ability-aware features.

    Args:
        seed: Random seed for deterministic generation
        diff_cfg: (Deprecated) Difficulty configuration dictionary. Use `config` parameter instead.
        abilities: List of enabled ability strings (e.g., ['DOUBLE_JUMP', 'DASH'])
        config: Type-safe LevelGenConfig instance (recommended over diff_cfg)

    Returns:
        Tuple of (world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs, enemy_positions)
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
        - enemy_positions: List of enemy spawn positions (x, y) in pixels

    Example:
        >>> # Using new config parameter (recommended)
        >>> from level_gen.config import LevelGenConfig, HARD_CONFIG
        >>> world, *rest = generate_level(seed=42, config=HARD_CONFIG)

        >>> # Using old dict-based config (backward compatible)
        >>> old_cfg = {'hazard_rate': 0.05, 'coin_density': 0.04}
        >>> world, *rest = generate_level(seed=42, diff_cfg=old_cfg)

        >>> # With abilities enabled
        >>> abilities = ['DOUBLE_JUMP', 'WALL_JUMP', 'DASH']
        >>> world, *rest = generate_level(seed=42, config=HARD_CONFIG, abilities=abilities)
    """
    # Handle configuration parameter priority: config > diff_cfg > defaults
    if config is not None:
        cfg = config
    elif diff_cfg is not None:
        # Convert dict to LevelGenConfig for type safety
        if isinstance(diff_cfg, dict):
            cfg = LevelGenConfig.from_dict(diff_cfg)
        else:
            cfg = diff_cfg
    else:
        cfg = LevelGenConfig()

    abilities = abilities or []
    rng = random.Random(seed)

    # Generate maze
    rooms = generate_macro_maze(
        ROOM_COLS, ROOM_ROWS, rng,
        verticality_bias=cfg.verticality_bias,
        branchiness=cfg.branchiness,
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
        platform_band_step=cfg.platform_band_step,
        platform_len_range=cfg.platform_len_range,
        pillar_chance=cfg.pillar_chance,
        hole_chance=cfg.hole_chance,
    )

    # Add ability-gated subrooms
    if cfg.enable_ability_subrooms:
        add_ability_subrooms(world, path_mask, rng, abilities, cfg.subroom_intensity)

    # Build solids
    tiles, exit_rect = build_solid_rects(world)

    # Generate hazards
    hazards = generate_hazards(world, rng, rate=cfg.hazard_rate)

    # Generate power-ups BEFORE coins so coins can check for nearby magnet powerups
    powerups = generate_powerups(world, rng, density=cfg.powerup_density)

    # Generate pickups (coins can now check for nearby magnet powerups)
    coins, healths, lives = generate_coins_and_pickups(
        world, rng,
        coin_density=cfg.coin_density,
        health_density=cfg.health_density,
        lives_per_level=cfg.lives_per_level,
        hazards=hazards,
        powerups=powerups,
        tiles=tiles
    )

    # Add ability-aware coin challenges (with collision checking)
    if cfg.enable_ability_challenges:
        add_ability_challenges(world, coins, rng, abilities, hazards, tiles)

    # Generate Ability Orbs (RARE - 0.3% spawn rate)
    ability_orbs = generate_ability_orbs(world, rng, spawn_rate=cfg.ability_orb_spawn_rate)

    # Mark phaseable walls for Shadow Step ability
    phaseable_walls = []
    if "SHADOW_STEP" in abilities:
        phaseable_walls = mark_phaseable_walls(tiles, world, rng, cfg.phaseable_wall_chance)

    spawn = find_spawn(path)

    # Generate enemies (avoid player spawn area)
    enemy_density = cfg.enemy_density if hasattr(cfg, 'enemy_density') else 0.10
    entity_placer = EntityPlacer(world, rng)
    enemy_positions = entity_placer.generate_enemies(enemy_density, spawn)

    return world, tiles, exit_rect, spawn, coins, hazards, healths, lives, powerups, phaseable_walls, ability_orbs, enemy_positions
