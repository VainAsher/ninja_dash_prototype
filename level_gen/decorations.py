"""
Decoration System Module
Handles platforms, pillars, holes, and ability-specific subrooms.
"""

import random
import pygame
from typing import List, Tuple, Optional, Any

from settings import (
    TILE_SIZE,
    ROOM_COLS, ROOM_ROWS,
    ROOM_W, ROOM_H,
    WORLD_W, WORLD_H,
)

from .constants import (
    DEFAULT_PLATFORM_BAND_STEP,
    DEFAULT_PLATFORM_LEN_RANGE,
    DEFAULT_PILLAR_CHANCE,
    DEFAULT_HOLE_CHANCE,
    ROOM_FLOOR_OFFSET,
)


def decorate_world(
    world: List[List[int]],
    path_mask: List[List[bool]],
    rng: random.Random,
    **kwargs: Any
) -> None:
    """Add environmental decorations to make levels more interesting and challenging.

    Enhances the basic room layout with procedurally placed platforms, pillars, and
    holes to create vertical traversal opportunities and environmental hazards. All
    decorations respect the critical path (path_mask) to ensure level completability.

    Decorations Added:
        1. Horizontal platforms: Layered at regular vertical intervals within rooms
        2. Vertical pillars: Tall obstacles with gaps for horizontal movement
        3. Floor holes: Gaps in solid surfaces creating pitfalls

    Args:
        world: 2D tile array [WORLD_H][WORLD_W] (modified in-place)
               - 0 = air, 1 = solid, 2 = exit
        path_mask: 2D boolean array [WORLD_H][WORLD_W] marking critical path tiles
                   that must not be obstructed
        rng: Seeded random number generator for deterministic decoration
        **kwargs: Optional configuration parameters:
            - platform_band_step (int): Vertical spacing between platform bands (default: 4)
            - platform_len_range (Tuple[int, int]): Platform length range (min, max) (default: (3, 7))
            - pillar_chance (float): Probability of adding pillars to each room (default: 0.3)
            - hole_chance (float): Probability of adding holes to each room (default: 0.2)

    Returns:
        None (modifies world in-place)

    Example:
        >>> world = [[0]*100 for _ in range(100)]
        >>> path_mask = [[False]*100 for _ in range(100)]
        >>> rng = random.Random(42)
        >>> decorate_world(world, path_mask, rng,
        ...                platform_band_step=3,
        ...                pillar_chance=0.5,
        ...                hole_chance=0.3)
        >>> # world now contains platforms, pillars, and holes

    Decoration Behavior:
        - Platforms: 1-3 segments per band, placed at regular intervals
        - Pillars: 1-3 per room with vertical gaps for movement
        - Holes: 1-3 per room, 2x2 tile gaps in existing floors
        - All respect path_mask and exit tiles (value 2)

    Edge Cases:
        - Empty rooms: Still attempts decoration (may place nothing)
        - Small rooms: May have limited decoration space
        - High decoration chances: Can create very dense environments
        - path_mask coverage: High coverage limits decoration opportunities

    Performance:
        O(ROOM_ROWS * ROOM_COLS * ROOM_W * ROOM_H) - processes each room
    """
    platform_band_step = kwargs.get('platform_band_step', DEFAULT_PLATFORM_BAND_STEP)
    platform_len_range = kwargs.get('platform_len_range', DEFAULT_PLATFORM_LEN_RANGE)
    pillar_chance = kwargs.get('pillar_chance', DEFAULT_PILLAR_CHANCE)
    hole_chance = kwargs.get('hole_chance', DEFAULT_HOLE_CHANCE)

    for ry in range(ROOM_ROWS):
        for rx in range(ROOM_COLS):
            base_x = rx * ROOM_W
            base_y = ry * ROOM_H

            for band in range(2, ROOM_H - ROOM_FLOOR_OFFSET, max(2, platform_band_step)):
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


def build_solid_rects(world: List[List[int]]) -> Tuple[List[pygame.Rect], Optional[pygame.Rect]]:
    """Convert tile-based world grid into renderable pygame rectangles.

    Scans the entire world grid and creates pygame.Rect objects for all solid
    tiles and the exit gate. This converts the abstract tile representation into
    concrete game objects for collision detection and rendering.

    Args:
        world: 2D tile array [WORLD_H][WORLD_W] where:
               - 0 = air/empty space (ignored)
               - 1 = solid tile (wall/platform)
               - 2 = exit gate

    Returns:
        Tuple of (tiles, exit_rect):
        - tiles: List of pygame.Rect for all solid tiles (value 1)
                 Each rect has dimensions TILE_SIZE x TILE_SIZE
        - exit_rect: Single pygame.Rect for exit gate (value 2), or None if no exit

    Example:
        >>> world = [
        ...     [1, 1, 1],
        ...     [1, 0, 2],
        ...     [1, 1, 1]
        ... ]
        >>> tiles, exit_rect = build_solid_rects(world)
        >>> len(tiles)  # 8 solid tiles
        8
        >>> exit_rect is not None  # Found exit at (2, 1)
        True

    Edge Cases:
        - No solid tiles: Returns empty tiles list
        - No exit (no value 2): Returns exit_rect = None
        - Multiple exits: Only last one found is returned (should not occur)
        - Empty world: Returns ([], None)

    Performance:
        O(WORLD_H * WORLD_W) - single pass through entire grid
    """
    tiles = []; exit_rect = None
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            v = world[y][x]
            if v == 1:
                tiles.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif v == 2:
                exit_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    return tiles, exit_rect
