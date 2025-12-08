"""
Minimal Rendering Integration

Adds tileset rendering to existing game without changing level generation.
This is the easiest way to get visual improvements from the zone system.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, List
import pygame

from level_gen.tileset import TileSet, draw_tiles as tileset_draw_tiles, validate_tiles
from settings import TILE_SIZE


class GameRenderer:
    """
    Enhanced renderer that can use either simple rects or tileset sprites.

    Drop-in replacement for the tile rendering portion of draw_world().
    """

    def __init__(self, biome: str = "lantern", enable_tileset: bool = True):
        """
        Initialize renderer.

        Args:
            biome: Current biome name
            enable_tileset: Whether to use tileset rendering (vs colored rects)
        """
        self.biome = biome
        self.enable_tileset = enable_tileset
        self.tileset: Optional[TileSet] = None

        if enable_tileset:
            self._load_tileset()

    def _load_tileset(self) -> None:
        """Load tileset for current biome."""
        try:
            assets_root = Path(__file__).parent.parent / "assets" / "tiles"
            self.tileset = TileSet(self.biome, TILE_SIZE, assets_root)
            validate_tiles(self.tileset)
            print(f"[Renderer] Loaded tileset for biome: {self.biome}")
        except Exception as e:
            print(f"[Renderer] Failed to load tileset: {e}")
            print(f"[Renderer] Falling back to colored rectangles")
            self.tileset = None
            self.enable_tileset = False

    def set_biome(self, biome: str) -> None:
        """Change biome and reload tileset."""
        if biome != self.biome:
            self.biome = biome
            if self.enable_tileset:
                self._load_tileset()

    def draw_tiles(self,
                   surface: pygame.Surface,
                   world: Optional[List[List[int]]],
                   tiles: List[pygame.Rect],
                   phaseable_walls: List[pygame.Rect],
                   camera: pygame.Rect,
                   seed: int,
                   ground_color: tuple,
                   phaseable_color: tuple,
                   debug_grid: bool = False) -> None:
        """
        Draw tiles using either tileset or colored rectangles.

        Args:
            surface: Target surface
            world: 2D tile array (if available)
            tiles: List of tile rectangles (fallback)
            phaseable_walls: List of phaseable wall rectangles
            camera: Camera rectangle
            seed: World seed for variant selection
            ground_color: Color for regular tiles (fallback mode)
            phaseable_color: Color for phaseable walls (fallback mode)
            debug_grid: Whether to draw grid lines
        """
        if self.enable_tileset and self.tileset and world:
            # Use tileset rendering
            cam_vec = pygame.Vector2(camera.x, camera.y)
            tileset_draw_tiles(surface, world, cam_vec, self.tileset, seed, debug_grid)
        else:
            # Fallback to colored rectangles
            for t in tiles:
                if camera.colliderect(t):
                    color = phaseable_color if t in phaseable_walls else ground_color
                    pygame.draw.rect(
                        surface,
                        color,
                        (t.x - camera.x, t.y - camera.y, t.w, t.h)
                    )


# =========================================================
# HELPER: Convert tile list to 2D world array
# =========================================================
def tiles_to_world(tiles: List[pygame.Rect], world_w: int, world_h: int,
                   tile_size: int) -> List[List[int]]:
    """
    Convert a list of tile rectangles to a 2D world array.

    This allows using tileset rendering with the existing generation system.

    Args:
        tiles: List of solid tile rectangles
        world_w: World width in tiles
        world_h: World height in tiles
        tile_size: Tile size in pixels

    Returns:
        2D array where 0=air, 1=solid
    """
    # Initialize with air
    world = [[0 for _ in range(world_w)] for _ in range(world_h)]

    # Mark solid tiles
    for t in tiles:
        tx = t.x // tile_size
        ty = t.y // tile_size

        if 0 <= tx < world_w and 0 <= ty < world_h:
            world[ty][tx] = 1

    return world


# =========================================================
# QUICK INTEGRATION EXAMPLE
# =========================================================
def integrate_tileset_rendering(game) -> None:
    """
    Quick integration: Add tileset rendering to existing game.

    Call this once during game initialization.

    Example:
        from level_gen.rendering_integration import integrate_tileset_rendering

        # In Game.__init__() or setup_level():
        integrate_tileset_rendering(self)
    """
    from settings import WORLD_W, WORLD_H

    # Create renderer
    biome = getattr(game, 'current_biome', 'lantern')
    game.renderer = GameRenderer(biome, enable_tileset=True)

    # Convert tile list to world array (if needed)
    if hasattr(game, 'tiles') and hasattr(game, 'world'):
        # Game already has world array - use it
        pass
    elif hasattr(game, 'tiles'):
        # Convert tiles to world array
        game.world = tiles_to_world(game.tiles, WORLD_W, WORLD_H, TILE_SIZE)

    print("[Integration] Tileset rendering enabled")
    print("[Integration] Use renderer.draw_tiles() in draw_world()")


# =========================================================
# USAGE EXAMPLE
# =========================================================
"""
# In core/game.py, in draw_world():

def draw_world(play_surf, tiles, phaseable_walls, exit_gate, coins, hazards,
               health_pickups, life_pickups, powerups, cam, debug, biome="lantern"):
    # ... existing background code ...

    # REPLACE tile drawing section with:
    if hasattr(game, 'renderer'):
        game.renderer.draw_tiles(
            play_surf,
            game.world,
            tiles,
            phaseable_walls,
            cam,
            game.seed,
            ground_color=(200, 180, 120),  # Biome-specific
            phaseable_color=(100, 100, 150),
            debug_grid=debug
        )
    else:
        # Original colored rect rendering
        for t in tiles:
            if cam.colliderect(t):
                color = COLOR_PHASEABLE_WALL if t in phaseable_walls else ground_color
                pygame.draw.rect(play_surf, color,
                               (t.x - cam.x, t.y - cam.y, t.w, t.h))

    # ... rest of draw_world() unchanged ...
"""
