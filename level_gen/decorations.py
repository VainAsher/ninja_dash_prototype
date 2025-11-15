"""
Decoration System Module
Handles platforms, pillars, holes, and ability-specific subrooms.
"""

import pygame

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
    DEFAULT_SUBROOM_INTENSITY,
    CHALLENGE_ATTEMPTS,
    SUBROOM_EMPTY_THRESHOLD,
)


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
