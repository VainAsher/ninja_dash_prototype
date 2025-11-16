"""
Utility Functions Module
Common helper functions for level generation including coordinate conversion,
boundary checks, and validation logic.
"""

from typing import Tuple, List, Set

from settings import TILE_SIZE, WORLD_W, WORLD_H


# Coordinate Conversion Functions

def tile_to_pixel(tx: int, ty: int, centered: bool = False) -> Tuple[int, int]:
    """
    Convert tile coordinates to pixel coordinates.

    Args:
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        centered: If True, return center of tile; if False, return top-left corner

    Returns:
        Tuple of (pixel_x, pixel_y)
    """
    px = tx * TILE_SIZE
    py = ty * TILE_SIZE

    if centered:
        px += TILE_SIZE // 2
        py += TILE_SIZE // 2

    return px, py


def pixel_to_tile(px: int, py: int) -> Tuple[int, int]:
    """
    Convert pixel coordinates to tile coordinates.

    Args:
        px: Pixel x-coordinate
        py: Pixel y-coordinate

    Returns:
        Tuple of (tile_x, tile_y)
    """
    return px // TILE_SIZE, py // TILE_SIZE


# Boundary Check Functions

def is_in_bounds(tx: int, ty: int, width: int, height: int, margin: int = 0) -> bool:
    """
    Check if tile coordinates are within bounds.

    Args:
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        width: Width of the area in tiles
        height: Height of the area in tiles
        margin: Margin from edges (default 0)

    Returns:
        True if coordinates are within bounds (including margin)
    """
    return margin <= tx < width - margin and margin <= ty < height - margin


def is_in_world_bounds(tx: int, ty: int, margin: int = 0) -> bool:
    """
    Check if tile coordinates are within world bounds.

    Args:
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        margin: Margin from edges (default 0)

    Returns:
        True if coordinates are within world bounds (including margin)
    """
    return is_in_bounds(tx, ty, WORLD_W, WORLD_H, margin)


def is_on_boundary(tx: int, ty: int, width: int = WORLD_W, height: int = WORLD_H) -> bool:
    """
    Check if tile coordinates are on the boundary.

    Args:
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        width: Width of the area in tiles (default WORLD_W)
        height: Height of the area in tiles (default WORLD_H)

    Returns:
        True if coordinates are on the boundary
    """
    return tx == 0 or tx == width - 1 or ty == 0 or ty == height - 1


# Validation Functions

def valid_pickup_spot(world: List[List[int]], tx: int, ty: int) -> bool:
    """
    Check if a tile position is valid for pickup placement.

    A valid pickup spot is:
    - Within bounds (with margin)
    - Currently air (0)
    - Has solid ground below (1)

    Args:
        world: 2D level array
        tx: Tile x-coordinate
        ty: Tile y-coordinate

    Returns:
        True if position is valid for pickup placement
    """
    # Check bounds with margin
    if not (1 <= tx < WORLD_W - 1 and 2 <= ty < WORLD_H - 1):
        return False

    # Check if current tile is air and tile below is solid
    return world[ty][tx] == 0 and world[ty + 1][tx] == 1


def far_from_hazards(
    tx: int,
    ty: int,
    hazard_tiles: Set[Tuple[int, int]],
    radius: int = 3
) -> bool:
    """
    Check if a tile is far enough from hazards.

    Args:
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        hazard_tiles: Set of (x, y) tuples representing hazard positions
        radius: Minimum distance from hazards (default 3)

    Returns:
        True if tile is far enough from all hazards
    """
    for hx, hy in hazard_tiles:
        # Check horizontal distance when on same row
        if abs(hx - tx) <= radius and hy == ty:
            return False
        # Check vertical distance when on same column
        if abs(hy - ty) <= radius and hx == tx:
            return False

    return True


def is_valid_platform(world: List[List[int]], tx: int, ty: int) -> bool:
    """
    Check if a tile is a valid platform (solid with air above).

    Args:
        world: 2D level array
        tx: Tile x-coordinate
        ty: Tile y-coordinate

    Returns:
        True if tile is a valid platform
    """
    if not is_in_world_bounds(tx, ty, margin=1):
        return False

    return world[ty][tx] == 1 and world[ty - 1][tx] == 0


def is_air_space(world: List[List[int]], tx: int, ty: int) -> bool:
    """
    Check if a tile is air/empty space.

    Args:
        world: 2D level array
        tx: Tile x-coordinate
        ty: Tile y-coordinate

    Returns:
        True if tile is air (value 0)
    """
    if not is_in_world_bounds(tx, ty):
        return False

    return world[ty][tx] == 0
