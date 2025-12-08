"""
Zone-Based Generation Integration

Integrates the zone-based room generation system with the existing
level generator, providing enhanced room customization while maintaining
compatibility with the current gameplay systems.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
import random

from level_gen.zone_generator import (
    RoomNode, assign_zone_roles_for_room, zone_rect,
    Z_WALK, Z_FILL, Z_PLAT, Z_SAVE, Z_SHOP, Z_LOOT, Z_SECRET,
    ZONES_W, ZONES_H, AIR, WALL, PLATFORM, EXIT, DOOR,
    ROOM_START, ROOM_EXIT, ROOM_SHOP, ROOM_COMBAT, ROOM_PLATFORM,
    ROOM_TREASURE, ROOM_BOSS, ROOM_SAFE,
    print_zone_roles, zone_center_tile
)

import pygame


# =========================================================
# PLATFORM PATTERN GENERATION
# =========================================================
def clamp_randint(rng: random.Random, a: int, b: int) -> int:
    """Safe randint that never throws."""
    return a if b < a else rng.randint(a, b)


def stamp_platform(tilemap: List[List[int]], x0: int, y: int, length: int) -> None:
    """Place a horizontal platform at the specified position."""
    h = len(tilemap)
    w = len(tilemap[0])

    if not (1 <= y < h - 1):
        return

    for x in range(max(1, x0), min(w - 1, x0 + length)):
        if tilemap[y][x] != WALL:
            tilemap[y][x] = PLATFORM


def clear_air(tilemap: List[List[int]], x0: int, y0: int, x1: int, y1: int) -> None:
    """Clear a rectangular area to air."""
    h = len(tilemap)
    w = len(tilemap[0])

    for y in range(max(1, y0), min(h - 1, y1)):
        for x in range(max(1, x0), min(w - 1, x1)):
            if tilemap[y][x] != WALL:
                tilemap[y][x] = AIR


def fill_wall(tilemap: List[List[int]], x0: int, y0: int, x1: int, y1: int) -> None:
    """Fill a rectangular area with walls."""
    h = len(tilemap)
    w = len(tilemap[0])

    for y in range(max(1, y0), min(h - 1, y1)):
        for x in range(max(1, x0), min(w - 1, x1)):
            tilemap[y][x] = WALL


def ensure_floor(tilemap: List[List[int]], y: int) -> None:
    """Ensure a solid floor exists at the specified y coordinate."""
    h = len(tilemap)
    w = len(tilemap[0])

    y = max(1, min(h - 2, y))
    for x in range(1, w - 1):
        if tilemap[y][x] != WALL:
            tilemap[y][x] = PLATFORM


# =========================================================
# ZONE-TO-TILE CONVERSION
# =========================================================
def generate_room_from_zones(room: RoomNode, roles: List[List[str]], rng: random.Random,
                              room_w: int, room_h: int) -> Tuple[List[List[int]], List[Tuple[str, Tuple[int, int], float]]]:
    """
    Convert zone roles to actual tile layout.

    This is the core function that turns high-level zone specifications
    into playable tile geometry.

    Args:
        room: Room node with metadata
        roles: 5x5 grid of zone roles
        rng: Random number generator
        room_w, room_h: Room dimensions in tiles

    Returns:
        Tuple of (tilemap, anchor_candidates)
    """
    # Initialize with air
    tilemap = [[AIR for _ in range(room_w)] for _ in range(room_h)]

    # Create borders
    for x in range(room_w):
        tilemap[0][x] = WALL
        tilemap[room_h - 1][x] = WALL

    for y in range(room_h):
        tilemap[y][0] = WALL
        tilemap[y][room_w - 1] = WALL

    # Ensure base floor
    ensure_floor(tilemap, room_h - 2)

    candidates: List[Tuple[str, Tuple[int, int], float]] = []

    # Phase 1: Fill zones with WALL
    for zy in range(ZONES_H):
        for zx in range(ZONES_W):
            if roles[zy][zx] == Z_FILL:
                x0, y0, x1, y1 = zone_rect(zx, zy, room_w, room_h)
                fill_wall(tilemap, x0, y0, x1, y1)

    # Phase 2: Decorate zones based on role
    for zy in range(ZONES_H):
        for zx in range(ZONES_W):
            role = roles[zy][zx]
            x0, y0, x1, y1 = zone_rect(zx, zy, room_w, room_h)

            # Interior bounds (avoid zone edges)
            x0i, y0i, x1i, y1i = x0 + 1, y0 + 1, x1 - 1, y1 - 1
            zone_w = max(1, x1i - x0i)
            zone_h = max(1, y1i - y0i)

            # Center of zone
            cx = (x0 + x1) // 2
            cy = (y0 + y1) // 2

            # Helper functions for safe random placement within zone
            def x_in(lo_pad: int = 0, hi_pad: int = 0) -> int:
                lo = max(2, x0i + lo_pad)
                hi = max(2, x1i - 1 - hi_pad)
                return clamp_randint(rng, lo, hi)

            def y_in(lo_pad: int = 0, hi_pad: int = 0) -> int:
                lo = max(3, y0i + lo_pad)
                hi = max(3, min(room_h - 4, y1i - 1 - hi_pad))
                return clamp_randint(rng, lo, hi)

            def place_len(max_cap: int = 10) -> int:
                max_len = max(3, min(max_cap, zone_w - 2))
                return clamp_randint(rng, 3, max_len)

            # WALK zones: Clear and add simple floor
            if role == Z_WALK:
                clear_air(tilemap, x0i, y0i, x1i, y1i)
                base = min(room_h - 3, y1i - 1)
                stamp_platform(tilemap, x0i + 1, base, max(4, zone_w - 2))

            # PLAT zones: Platform patterns based on room type
            elif role == Z_PLAT:
                clear_air(tilemap, x0i, y0i, x1i, y1i)

                # Select pattern based on room type
                if room.type == ROOM_PLATFORM:
                    kind_pool = ["zigzag", "stair", "islands", "bridge"]
                elif room.type == ROOM_COMBAT:
                    kind_pool = ["split", "islands", "bridge", "pillar"]
                elif room.type == ROOM_TREASURE:
                    kind_pool = ["pedestal", "bridge", "islands"]
                elif room.type == ROOM_BOSS:
                    kind_pool = ["arena_sides", "bridge", "split"]
                else:
                    kind_pool = ["bridge", "islands", "split"]

                kind = rng.choice(kind_pool)

                # Generate pattern
                if kind == "bridge":
                    yy = y_in(1, 1)
                    ln = max(4, min(12, zone_w - 2))
                    xx = clamp_randint(rng, max(2, x0i + 1), max(2, x1i - ln - 1))
                    stamp_platform(tilemap, xx, yy, ln)

                elif kind == "islands":
                    yy = y_in(1, 1)
                    for _ in range(clamp_randint(rng, 2, 3)):
                        ln = place_len(7)
                        xx = clamp_randint(rng, max(2, x0i + 1), max(2, x1i - ln - 1))
                        stamp_platform(tilemap, xx, yy + clamp_randint(rng, -1, 1), ln)

                elif kind == "split":
                    y1p = y_in(1, 2)
                    y2p = max(3, y1p - clamp_randint(rng, 2, 4))
                    ln1 = place_len(10)
                    ln2 = place_len(10)
                    x1s = clamp_randint(rng, max(2, x0i + 1), max(2, x1i - ln1 - 1))
                    x2s = clamp_randint(rng, max(2, x0i + 1), max(2, x1i - ln2 - 1))
                    stamp_platform(tilemap, x1s, y1p, ln1)
                    stamp_platform(tilemap, x2s, y2p, ln2)

                elif kind == "stair":
                    steps = clamp_randint(rng, 3, 5)
                    base_y = y_in(2, 1)
                    y = base_y
                    x = max(2, x0i + 1)
                    for i in range(steps):
                        ln = max(3, min(6, zone_w - 2))
                        stamp_platform(tilemap, x, y, ln)
                        x = min(max(2, x1i - ln - 1), x + clamp_randint(rng, 4, 7))
                        y = max(3, y - clamp_randint(rng, 2, 3))

                elif kind == "zigzag":
                    steps = clamp_randint(rng, 4, 6)
                    y = y_in(2, 1)
                    left_x = max(2, x0i + 1)
                    right_x = max(2, x1i - 8)
                    for i in range(steps):
                        ln = place_len(8)
                        xx = left_x if i % 2 == 0 else clamp_randint(rng, right_x, max(right_x, x1i - ln - 1))
                        stamp_platform(tilemap, xx, y, ln)
                        y = max(3, y - clamp_randint(rng, 1, 3))

                elif kind == "pedestal":
                    yy = y_in(2, 1)
                    cx2 = clamp_randint(rng, max(2, x0i + 3), max(2, x1i - 4))
                    stamp_platform(tilemap, cx2 - 2, yy, 5)
                    stamp_platform(tilemap, cx2 - 1, max(3, yy - 3), 3)

                elif kind == "arena_sides":
                    yy = y_in(3, 1)
                    stamp_platform(tilemap, max(2, x0i + 1), yy, max(6, min(10, zone_w - 2)))
                    stamp_platform(tilemap, max(2, x1i - 11), max(3, yy - 2), max(6, min(10, zone_w - 2)))

            # Special feature zones
            elif role == Z_SAVE:
                clear_air(tilemap, x0i, y0i, x1i, y1i)
                base = min(room_h - 3, y1i - 1)
                stamp_platform(tilemap, x0i + 2, base, max(6, zone_w - 4))
                stamp_platform(tilemap, cx - 2, max(3, base - 3), 5)
                candidates.append(("save_point", (cx, max(2, base - 4)), 1.0))

            elif role == Z_SHOP:
                clear_air(tilemap, x0i, y0i, x1i, y1i)
                base = min(room_h - 3, y1i - 1)
                stamp_platform(tilemap, x0i + 2, base, max(6, zone_w - 4))
                stamp_platform(tilemap, x0i + 3, max(3, base - 3), max(6, zone_w - 6))
                candidates.append(("shopkeeper", (cx, base - 1), 2.0))

            elif role == Z_LOOT:
                clear_air(tilemap, x0i, y0i, x1i, y1i)
                base = min(room_h - 3, y1i - 1)
                stamp_platform(tilemap, x0i + 2, base, max(6, zone_w - 4))
                stamp_platform(tilemap, cx - 3, max(3, base - 4), 7)
                candidates.append(("loot", (cx, max(2, base - 5)), 2.0))

            elif role == Z_SECRET:
                clear_air(tilemap, x0i, y0i, x1i, y1i)
                px = max(2, x0i + 2)
                py = max(3, y0i + 2)
                stamp_platform(tilemap, px, py, 5)
                candidates.append(("secret_stash", (px + 2, py - 1), 1.0))

    # Add spawn hint for start rooms
    candidates.append(("spawn_hint", (4, room_h - 4), 0.1))

    # Add special markers
    if room.type == ROOM_EXIT:
        candidates.append(("exit_portal", (room_w // 2, room_h // 2), 1.0))
    if room.type == ROOM_BOSS:
        candidates.append(("boss_spawn", (room_w // 2, room_h - 6), 1.0))

    return tilemap, candidates


# =========================================================
# CONSOLE LOGGING
# =========================================================
def log_generation_start(seed: int, config_name: str = "default") -> None:
    """Log the start of world generation."""
    print("\n" + "=" * 60)
    print(f"[WorldGen] Starting generation with seed={seed}")
    print(f"[WorldGen] Config: {config_name}")
    print("=" * 60)


def log_room_generation(room_coord: Tuple[int, int], room_type: str, room_count: int, total: int) -> None:
    """Log progress of room generation."""
    progress = (room_count / max(total, 1)) * 100
    print(f"[RoomGen] {room_coord} - {room_type:12s} [{room_count:2d}/{total:2d}] ({progress:5.1f}%)")


def log_zone_assignment(room_coord: Tuple[int, int], roles: List[List[str]], verbose: bool = False) -> None:
    """Log zone role assignments."""
    if verbose:
        from level_gen.zone_generator import print_zone_roles
        print_zone_roles(roles, "debug", room_coord)


def log_feature_placement(room_coord: Tuple[int, int], features: Dict[str, Tuple[int, int]]) -> None:
    """Log feature placement in a room."""
    if features:
        print(f"[Features] Room {room_coord}: {', '.join(features.keys())}")


def log_generation_complete(room_count: int, duration: float = 0.0) -> None:
    """Log completion of world generation."""
    print("\n" + "=" * 60)
    print(f"[WorldGen] Complete! Generated {room_count} rooms")
    if duration > 0:
        print(f"[WorldGen] Time: {duration:.3f}s")
    print("=" * 60 + "\n")


# =========================================================
# DOOR GENERATION
# =========================================================
def add_doors_between_rooms(tilemap: List[List[int]], room_nodes: Dict[Tuple[int, int], RoomNode],
                            room_w: int, room_h: int) -> None:
    """
    Add doors between connected rooms in the tilemap.

    Creates doorways where rooms connect, allowing player to traverse between rooms.

    Args:
        tilemap: World tilemap (modified in-place)
        room_nodes: Dictionary of room nodes with neighbor information
        room_w: Room width in tiles
        room_h: Room height in tiles
    """
    h = len(tilemap)
    w = len(tilemap[0])

    # Process each room
    for (rx, ry), room in room_nodes.items():
        # Calculate room offset in world
        ox = rx * room_w
        oy = ry * room_h

        # Check each potential neighbor direction
        for nb_coord in room.neighbors:
            nx, ny = nb_coord
            dx, dy = nx - rx, ny - ry

            # Only process each connection once (smaller coord processes it)
            if nb_coord < (rx, ry):
                continue

            # Horizontal connection (left/right)
            if dy == 0 and abs(dx) == 1:
                # Create vertical door at room edge
                if dx == 1:  # Neighbor to the right
                    door_x = ox + room_w - 1
                else:  # Neighbor to the left
                    door_x = ox

                # Place door in middle of edge (3 tiles tall)
                center_y = oy + room_h // 2
                for door_y in range(center_y - 1, center_y + 2):
                    if 0 <= door_x < w and 0 <= door_y < h:
                        tilemap[door_y][door_x] = DOOR
                        # Clear space next to door
                        if dx == 1 and door_x + 1 < w:
                            tilemap[door_y][door_x + 1] = AIR
                        elif dx == -1 and door_x - 1 >= 0:
                            tilemap[door_y][door_x - 1] = AIR

            # Vertical connection (up/down)
            elif dx == 0 and abs(dy) == 1:
                # Create horizontal door at room edge
                if dy == 1:  # Neighbor below
                    door_y = oy + room_h - 1
                else:  # Neighbor above
                    door_y = oy

                # Place door in middle of edge (5 tiles wide)
                center_x = ox + room_w // 2
                for door_x in range(center_x - 2, center_x + 3):
                    if 0 <= door_x < w and 0 <= door_y < h:
                        tilemap[door_y][door_x] = DOOR
                        # Clear space next to door
                        if dy == 1 and door_y + 1 < h:
                            tilemap[door_y + 1][door_x] = AIR
                        elif dy == -1 and door_y - 1 >= 0:
                            tilemap[door_y - 1][door_x] = AIR
