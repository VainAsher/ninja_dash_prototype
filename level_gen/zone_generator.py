"""
Zone-Based World Generation System

This module implements granular room customization using a 5x5 zone grid system.
Each zone can have different roles (WALK, FILL, PLAT, DECOR, SAVE, SHOP, LOOT, SECRET).

Inspired by advanced procedural generation techniques with data-driven room design.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from collections import deque
import random

from settings import ROOM_W, ROOM_H, WORLD_W, WORLD_H

# =========================================================
# ZONE GRID CONFIGURATION
# =========================================================
ZONES_W = 5  # Zones per room horizontally
ZONES_H = 5  # Zones per room vertically

# =========================================================
# TILE IDs (matches existing system)
# =========================================================
AIR = 0
WALL = 1
EXIT = 2
PLATFORM = 3
DOOR = 4

def is_blocking(t: int) -> bool:
    """Check if a tile ID represents a blocking/solid tile."""
    return t in (WALL, PLATFORM)

def is_border_cell(x: int, y: int, w: int, h: int) -> bool:
    """Check if a tile coordinate is on the border of the grid."""
    return x == 0 or y == 0 or x == w-1 or y == h-1

# =========================================================
# ROOM TYPES (enhanced from existing system)
# =========================================================
ROOM_START = "start"
ROOM_EXIT = "exit"
ROOM_SHOP = "shop"
ROOM_COMBAT = "combat"
ROOM_PLATFORM = "platform"
ROOM_TREASURE = "treasure"
ROOM_BOSS = "boss"
ROOM_SAFE = "safe"  # No hazards

ROOM_SYMBOL = {
    ROOM_START: "S",
    ROOM_EXIT: "X",
    ROOM_SHOP: "$",
    ROOM_TREASURE: "T",
    ROOM_BOSS: "B",
    ROOM_PLATFORM: "P",
    ROOM_COMBAT: "C",
    ROOM_SAFE: ".",
}

# =========================================================
# ZONE ROLES (granular room subdivision)
# =========================================================
Z_WALK = "WALK"      # Keep open for travel
Z_FILL = "FILL"      # Fill with WALL (reshape room)
Z_PLAT = "PLAT"      # Platform-y areas
Z_DECOR = "DECOR"    # Decorative/empty
Z_SAVE = "SAVE"      # Save point location
Z_SHOP = "SHOPKEEPER"  # Shop NPC
Z_LOOT = "LOOT"      # Treasure chest
Z_SECRET = "SECRET"  # Secret area

# =========================================================
# ROOM NODE (enhanced)
# =========================================================
@dataclass
class RoomNode:
    """
    Represents a single room in the world grid with enhanced metadata.

    Attributes:
        x, y: Room grid coordinates
        type: Room type (combat, treasure, shop, etc.)
        seed: Random seed for this specific room
        neighbors: Set of neighboring room coordinates
        neighbor_dirs: Dict mapping direction names to neighbor coords
        door_centers: Dict mapping directions to door center positions
        tilemap: 2D array of tile IDs (generated)
        zone_roles: 2D array of zone roles (5x5 grid)
        anchor_candidates: List of feature placements (name, position, weight)
        resolved_anchors: Final feature positions
        dist_to_boss: Distance to nearest boss room
        dist_to_exit: Distance to exit room
    """
    x: int
    y: int
    type: str
    seed: int
    neighbors: Set[Tuple[int, int]] = field(default_factory=set)
    neighbor_dirs: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    door_centers: Dict[str, int] = field(default_factory=dict)
    tilemap: Optional[List[List[int]]] = None
    zone_roles: Optional[List[List[str]]] = None
    anchor_candidates: List[Tuple[str, Tuple[int, int], float]] = field(default_factory=list)
    resolved_anchors: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    dist_to_boss: int = 999
    dist_to_exit: int = 999

# =========================================================
# ZONE UTILITIES
# =========================================================
def zone_rect(zx: int, zy: int, room_w: int, room_h: int) -> Tuple[int, int, int, int]:
    """Get the tile rectangle for a zone."""
    zw = room_w // ZONES_W
    zh = room_h // ZONES_H
    x0 = zx * zw
    y0 = zy * zh
    x1 = (zx + 1) * zw if zx < ZONES_W - 1 else room_w
    y1 = (zy + 1) * zh if zy < ZONES_H - 1 else room_h
    return x0, y0, x1, y1

def zone_center_tile(zx: int, zy: int, room_w: int, room_h: int) -> Tuple[int, int]:
    """Get the center tile coordinate for a zone."""
    x0, y0, x1, y1 = zone_rect(zx, zy, room_w, room_h)
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    cx = max(2, min(room_w - 3, cx))
    cy = max(2, min(room_h - 3, cy))
    return cx, cy

def edge_zone_choices(direction: str) -> List[Tuple[int, int]]:
    """Get all zone coordinates along an edge for door placement."""
    if direction == "left":
        return [(0, zy) for zy in range(ZONES_H)]
    if direction == "right":
        return [(ZONES_W - 1, zy) for zy in range(ZONES_H)]
    if direction == "up":
        return [(zx, 0) for zx in range(ZONES_W)]
    if direction == "down":
        return [(zx, ZONES_H - 1) for zx in range(ZONES_W)]
    return []

def build_zone_path(blocked: Set[Tuple[int, int]], start: Tuple[int, int],
                    goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """Find a path through zones avoiding blocked zones."""
    q = deque([start])
    prev: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

    def neighbors(z):
        x, y = z
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < ZONES_W and 0 <= ny < ZONES_H and (nx, ny) not in blocked:
                yield (nx, ny)

    while q:
        z = q.popleft()
        if z == goal:
            path = [z]
            while prev[path[-1]] is not None:
                path.append(prev[path[-1]])
            path.reverse()
            return path
        for n in neighbors(z):
            if n not in prev:
                prev[n] = z
                q.append(n)
    return None

def ensure_zone_connectivity(roles: List[List[str]], must_connect: List[Tuple[int, int]]) -> bool:
    """Verify that all important zones are connected through non-FILL zones."""
    blocked = {(x, y) for y in range(ZONES_H) for x in range(ZONES_W) if roles[y][x] == Z_FILL}
    if not must_connect:
        return True

    start = must_connect[0]
    q = deque([start])
    seen = {start}

    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < ZONES_W and 0 <= ny < ZONES_H:
                if (nx, ny) not in blocked and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny))

    return all(z in seen for z in must_connect)

# =========================================================
# ZONE ROLE ASSIGNMENT (DATA-DRIVEN)
# =========================================================
def assign_zone_roles_for_room(room: RoomNode, rng: random.Random) -> List[List[str]]:
    """
    Assign 25 subzone roles based on room type and world context.

    This creates interesting, varied room layouts by treating each room
    as a 5x5 grid of customizable zones.

    Returns:
        5x5 grid of zone role strings
    """
    roles = [[Z_DECOR for _ in range(ZONES_W)] for _ in range(ZONES_H)]
    features: Dict[str, Tuple[int, int]] = {}

    # Data-driven feature placement based on room type
    if room.type == ROOM_SHOP:
        features["shopkeeper"] = (ZONES_W // 2, ZONES_H // 2)
        features["secret_stash"] = rng.choice([(0, 0), (0, ZONES_H - 1),
                                               (ZONES_W - 1, 0), (ZONES_W - 1, ZONES_H - 1)])
        features["save_point"] = (1, ZONES_H - 2)

    if room.type == ROOM_TREASURE:
        features["loot"] = (ZONES_W // 2, ZONES_H // 2)
        features["secret_stash"] = rng.choice([(0, 0), (0, ZONES_H - 1),
                                               (ZONES_W - 1, 0), (ZONES_W - 1, ZONES_H - 1)])

    if room.type == ROOM_EXIT:
        features["exit_portal"] = (ZONES_W // 2, ZONES_H // 2)

    if room.type in (ROOM_COMBAT, ROOM_PLATFORM, ROOM_TREASURE, ROOM_SHOP):
        if 1 <= room.dist_to_boss <= 2:
            # Place save point near boss rooms
            cand = [(x, y) for y in range(ZONES_H) for x in range(ZONES_W)]
            rng.shuffle(cand)
            for z in cand:
                if z not in features.values():
                    features.setdefault("save_point", z)
                    break

    if len(room.neighbors) == 1 and room.type not in (ROOM_START, ROOM_EXIT):
        # Dead end - add secret
        corners = [(0, 0), (0, ZONES_H - 1), (ZONES_W - 1, 0), (ZONES_W - 1, ZONES_H - 1)]
        features.setdefault("secret_stash", rng.choice(corners))

    if room.type == ROOM_START:
        features["spawn_hint"] = (1, ZONES_H - 2)

    if room.type == ROOM_BOSS:
        features["boss_spawn"] = (ZONES_W // 2, ZONES_H // 2)

    # Convert features to role assignments
    for kind, (zx, zy) in features.items():
        if kind == "shopkeeper":
            roles[zy][zx] = Z_SHOP
        elif kind == "save_point":
            roles[zy][zx] = Z_SAVE
        elif kind == "loot":
            roles[zy][zx] = Z_LOOT
        elif kind == "secret_stash":
            roles[zy][zx] = Z_SECRET
        else:
            roles[zy][zx] = Z_WALK

    # Mark door zones as WALK
    door_zones: List[Tuple[int, int]] = []
    for d in room.neighbor_dirs.keys():
        if d in ("left", "right"):
            cy = room.door_centers.get(d, ROOM_H // 2)
            best = None
            for z in edge_zone_choices(d):
                _, zy = z
                _, yc = zone_center_tile(z[0], zy, ROOM_W, ROOM_H)
                score = abs(yc - cy)
                if best is None or score < best[0]:
                    best = (score, z)
            pick = best[1] if best else edge_zone_choices(d)[ZONES_H // 2]
        else:
            cx = room.door_centers.get(d, ROOM_W // 2)
            best = None
            for z in edge_zone_choices(d):
                zx, _ = z
                xc, _ = zone_center_tile(zx, z[1], ROOM_W, ROOM_H)
                score = abs(xc - cx)
                if best is None or score < best[0]:
                    best = (score, z)
            pick = best[1] if best else edge_zone_choices(d)[ZONES_W // 2]

        door_zones.append(pick)
        x, y = pick
        if roles[y][x] == Z_DECOR:
            roles[y][x] = Z_WALK

    # Build connectivity requirements
    must: List[Tuple[int, int]] = list(door_zones)
    for kind, z in features.items():
        if kind in ("shopkeeper", "save_point", "loot", "exit_portal", "boss_spawn"):
            must.append(z)

    # Mark WALK paths between important zones
    if must:
        blocked: Set[Tuple[int, int]] = set()
        hub = must[0]
        for target in must[1:]:
            path = build_zone_path(blocked, hub, target)
            if path:
                for zx, zy in path:
                    if roles[zy][zx] == Z_DECOR:
                        roles[zy][zx] = Z_WALK

    # Add FILL zones for room shaping (but maintain connectivity)
    max_fills = 0
    if room.type in (ROOM_COMBAT, ROOM_PLATFORM):
        max_fills = rng.randint(3, 6)
    elif room.type == ROOM_TREASURE:
        max_fills = rng.randint(2, 4)
    elif room.type == ROOM_SHOP:
        max_fills = rng.randint(1, 2)
    elif room.type in (ROOM_START, ROOM_EXIT):
        max_fills = rng.randint(0, 2)
    elif room.type == ROOM_BOSS:
        max_fills = rng.randint(1, 3)

    must_set = set(must)
    fill_candidates = [(x, y) for y in range(ZONES_H) for x in range(ZONES_W)
                      if (x, y) not in must_set and roles[y][x] == Z_DECOR]
    rng.shuffle(fill_candidates)
    fills = 0
    for x, y in fill_candidates:
        if fills >= max_fills:
            break
        roles[y][x] = Z_FILL
        if not ensure_zone_connectivity(roles, must):
            roles[y][x] = Z_DECOR
        else:
            fills += 1

    # Convert remaining DECOR to PLAT with type-specific weights
    for y in range(ZONES_H):
        for x in range(ZONES_W):
            if roles[y][x] == Z_DECOR:
                p = 0.2
                if room.type in (ROOM_PLATFORM, ROOM_COMBAT):
                    p = 0.55
                elif room.type == ROOM_TREASURE:
                    p = 0.35

                if rng.random() < p:
                    roles[y][x] = Z_PLAT
                else:
                    roles[y][x] = Z_WALK if rng.random() < 0.25 else Z_DECOR

    return roles


def print_zone_roles(roles: List[List[str]], room_type: str, coords: Tuple[int, int]) -> None:
    """Print zone role grid for debugging."""
    print(f"\n[Zone Debug] Room {coords} ({room_type}):")
    role_chars = {
        Z_WALK: ".",
        Z_FILL: "#",
        Z_PLAT: "=",
        Z_DECOR: " ",
        Z_SAVE: "S",
        Z_SHOP: "$",
        Z_LOOT: "T",
        Z_SECRET: "?",
    }

    for row in roles:
        print("  " + "".join(role_chars.get(r, "?") for r in row))
