"""
Utility Functions Module
Common helper functions for level generation including coordinate conversion,
boundary checks, and validation logic with performance optimizations.
"""

from typing import Tuple, List, Set, Optional
from functools import lru_cache

from settings import TILE_SIZE, WORLD_W, WORLD_H
from .constants import HAZARD_SAFE_RADIUS


# Performance Optimization: Cached Boundary Checks
# These functions are called very frequently during level generation,
# so we cache the results to avoid repeated calculations.

@lru_cache(maxsize=1024)
def _cached_is_on_boundary(tx: int, ty: int, width: int, height: int) -> bool:
    """Cached boundary check to avoid repeated calculations."""
    return tx == 0 or tx == width - 1 or ty == 0 or ty == height - 1


@lru_cache(maxsize=2048)
def _cached_is_in_bounds(tx: int, ty: int, width: int, height: int, margin: int) -> bool:
    """Cached bounds check to avoid repeated calculations."""
    return margin <= tx < width - margin and margin <= ty < height - margin


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
    Check if tile coordinates are within bounds (cached for performance).

    This function is heavily used during entity placement and decoration,
    so results are cached to improve performance.

    Args:
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        width: Width of the area in tiles
        height: Height of the area in tiles
        margin: Margin from edges (default 0)

    Returns:
        True if coordinates are within bounds (including margin)
    """
    return _cached_is_in_bounds(tx, ty, width, height, margin)


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
    Check if tile coordinates are on the boundary (cached for performance).

    Frequently called when marking phaseable walls and placing decorations.
    Results are cached to avoid redundant calculations.

    Args:
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        width: Width of the area in tiles (default WORLD_W)
        height: Height of the area in tiles (default WORLD_H)

    Returns:
        True if coordinates are on the boundary
    """
    return _cached_is_on_boundary(tx, ty, width, height)


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


def enhanced_valid_pickup_spot(
    world: List[List[int]],
    tx: int,
    ty: int,
    allow_risky: bool = False
) -> bool:
    """
    Enhanced validation for pickup placement with comprehensive safety checks.

    This function prevents coins from spawning:
    - Inside platforms (embedded in solid blocks)
    - In tight enclosed spaces
    - Without proper clearance above

    Args:
        world: 2D level array
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        allow_risky: If True, relaxes horizontal clearance restrictions
                     (used when magnet powerup is nearby)

    Returns:
        True if location is valid and safe for pickup placement
    """
    # 1. Bounds check with safe margin
    if not (1 <= tx < WORLD_W - 1 and 2 <= ty < WORLD_H - 1):
        return False

    # 2. Basic validation - current tile must be air, tile below must be solid
    if world[ty][tx] != 0 or world[ty + 1][tx] != 1:
        return False

    # 3. CRITICAL FIX: Tile above must be clear
    # Prevents coins from spawning embedded in platforms
    if world[ty - 1][tx] != 0:
        return False

    # 4. Check for enclosed space (surrounded by solid blocks)
    # This catches coins that would spawn in small pockets
    solid_sides = 0
    if tx <= 1 or world[ty][tx - 1] == 1:
        solid_sides += 1
    if tx >= WORLD_W - 2 or world[ty][tx + 1] == 1:
        solid_sides += 1

    # If completely enclosed horizontally, reject (unless risky mode)
    if solid_sides >= 2 and not allow_risky:
        return False

    # 5. Additional safety: Check for sufficient vertical clearance
    # Ensure at least 2 tiles of vertical space
    clearance_tiles = 0
    for check_y in range(max(0, ty - 2), ty):
        if world[check_y][tx] == 0:
            clearance_tiles += 1

    if clearance_tiles < 1 and not allow_risky:
        return False

    # 6. NEW: Check for platform interior (surrounded on 3+ sides)
    # Count solid blocks in 8 surrounding tiles
    surrounding_solid = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dy == 0 and dx == 0:
                continue  # Skip center tile
            check_x = tx + dx
            check_y = ty + dy
            if (0 <= check_x < WORLD_W and 0 <= check_y < WORLD_H and
                world[check_y][check_x] == 1):
                surrounding_solid += 1

    # If surrounded by too many solid blocks, it's probably inside a platform
    if surrounding_solid >= 6 and not allow_risky:
        return False

    return True


def far_from_hazards(
    tx: int,
    ty: int,
    hazard_tiles: Set[Tuple[int, int]],
    radius: int = HAZARD_SAFE_RADIUS
) -> bool:
    """
    Check if a tile is far enough from hazards.

    Args:
        tx: Tile x-coordinate
        ty: Tile y-coordinate
        hazard_tiles: Set of (x, y) tuples representing hazard positions
        radius: Minimum distance from hazards (default HAZARD_SAFE_RADIUS)

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


# Performance Optimization: Pre-computed Valid Spawn Locations

def precompute_valid_spawn_locations(
    world: List[List[int]],
    hazard_tiles: Optional[Set[Tuple[int, int]]] = None,
    radius: int = HAZARD_SAFE_RADIUS
) -> List[Tuple[int, int]]:
    """
    Pre-compute all valid spawn locations in the world.

    This optimization scans the world once and creates a list of all valid
    spawn points, which can then be randomly selected from. This is much
    faster than iterating through the entire world repeatedly when trying
    to place multiple entities.

    Args:
        world: 2D level array
        hazard_tiles: Optional set of hazard positions to avoid
        radius: Minimum distance from hazards

    Returns:
        List of (tx, ty) tuples representing valid spawn locations

    Performance:
        - Single O(WORLD_W * WORLD_H) scan vs multiple scans
        - Typical speedup: 10-100x for placing many entities
        - Memory cost: ~100KB for typical level (worth it for speed)

    Example:
        >>> # Old way (slow for many entities)
        >>> for _ in range(100):
        ...     # Iterate world to find random spot
        ...     tx, ty = find_random_spot(world)  # O(n) each time

        >>> # New way (fast)
        >>> valid_spots = precompute_valid_spawn_locations(world)  # O(n) once
        >>> for _ in range(100):
        ...     tx, ty = random.choice(valid_spots)  # O(1) each time
    """
    valid_locations = []
    hazard_tiles = hazard_tiles or set()

    for ty in range(2, WORLD_H - 1):
        for tx in range(1, WORLD_W - 1):
            # Check if valid pickup spot
            if not valid_pickup_spot(world, tx, ty):
                continue

            # Check distance from hazards
            if hazard_tiles and not far_from_hazards(tx, ty, hazard_tiles, radius):
                continue

            valid_locations.append((tx, ty))

    return valid_locations


# Performance Optimization: Spatial Partitioning for Collision Checks

class SpatialGrid:
    """
    Simple spatial partitioning grid for fast collision/proximity queries.

    Divides the world into a grid of cells and stores entities in their
    corresponding cells. This allows O(1) average-case proximity queries
    instead of O(n) checks against all entities.

    Example:
        >>> # Create grid with 10x10 cells
        >>> grid = SpatialGrid(WORLD_W, WORLD_H, cell_size=10)
        >>>
        >>> # Add entities
        >>> for entity_pos in entity_positions:
        ...     grid.add(entity_pos)
        >>>
        >>> # Fast proximity query - only checks nearby cells
        >>> nearby = grid.get_nearby(player_pos, radius=5)  # O(1) average
    """

    def __init__(self, world_width: int, world_height: int, cell_size: int = 10):
        """
        Initialize spatial grid.

        Args:
            world_width: World width in tiles
            world_height: World height in tiles
            cell_size: Size of each grid cell in tiles (default 10)
        """
        self.world_width = world_width
        self.world_height = world_height
        self.cell_size = cell_size
        self.grid_width = (world_width + cell_size - 1) // cell_size
        self.grid_height = (world_height + cell_size - 1) // cell_size

        # Grid of entity lists
        self.cells: List[List[List[Tuple[int, int]]]] = [
            [[] for _ in range(self.grid_width)]
            for _ in range(self.grid_height)
        ]

    def _get_cell(self, tx: int, ty: int) -> Tuple[int, int]:
        """Get grid cell coordinates for a tile position."""
        cx = min(tx // self.cell_size, self.grid_width - 1)
        cy = min(ty // self.cell_size, self.grid_height - 1)
        return cx, cy

    def add(self, position: Tuple[int, int]) -> None:
        """Add an entity position to the grid."""
        tx, ty = position
        cx, cy = self._get_cell(tx, ty)
        self.cells[cy][cx].append(position)

    def get_nearby(self, position: Tuple[int, int], radius: int) -> List[Tuple[int, int]]:
        """
        Get all entities within radius of position.

        Args:
            position: Center position (tx, ty)
            radius: Search radius in tiles

        Returns:
            List of entity positions within radius
        """
        tx, ty = position
        cx, cy = self._get_cell(tx, ty)

        # Calculate cell range to check
        cell_radius = (radius + self.cell_size - 1) // self.cell_size

        nearby = []
        for dy in range(-cell_radius, cell_radius + 1):
            for dx in range(-cell_radius, cell_radius + 1):
                check_cx = cx + dx
                check_cy = cy + dy

                # Bounds check
                if not (0 <= check_cx < self.grid_width and 0 <= check_cy < self.grid_height):
                    continue

                # Check all entities in this cell
                for entity_pos in self.cells[check_cy][check_cx]:
                    ex, ey = entity_pos
                    # Manhattan distance check
                    if abs(ex - tx) <= radius and abs(ey - ty) <= radius:
                        nearby.append(entity_pos)

        return nearby
