"""
Ability Features Module
Handles ability-aware coin patterns and ability-specific challenge subrooms.
"""

import random
import pygame
from typing import List

from settings import (
    TILE_SIZE,
    ROOM_COLS, ROOM_ROWS,
    ROOM_W, ROOM_H,
    WORLD_W, WORLD_H,
)

from .constants import (
    CHALLENGE_ATTEMPTS,
    SUBROOM_EMPTY_THRESHOLD,
)


def add_ability_challenges(
    world: List[List[int]],
    coins: List[pygame.Rect],
    rng: random.Random,
    abilities: List[str]
) -> None:
    """
    Add optional coin patterns that reward specific abilities.

    Args:
        world: 2D level array
        coins: List of coin rectangles (will be modified in-place)
        rng: Random number generator
        abilities: List of enabled ability strings
    """
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


def add_ability_subrooms(
    world: List[List[int]],
    path_mask: List[List[bool]],
    rng: random.Random,
    abilities: List[str],
    intensity: float
) -> None:
    """
    Add optional ability-specific challenge subrooms.
    These reward players who have unlocked specific abilities.

    Args:
        world: 2D level array (modified in-place)
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
