"""
Tile-Based Asset Loading System with Auto-Tiling

Supports folder-based tile organization by biome and category,
with automatic 3x3 tile pattern selection for walls and platforms.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
import pygame

# =========================================================
# AUTO-TILING PATTERNS (3x3)
# =========================================================
SHAPES_3X3 = [
    "top_left", "top_mid", "top_right",
    "mid_left", "mid_mid", "mid_right",
    "bottom_left", "bottom_mid", "bottom_right",
]

# Required sprite keys for basic rendering
REQUIRED_KEYS = [
    "world/void",
    "door/door",
    "feature/marker",
] + [f"wall/{s}" for s in SHAPES_3X3] + [f"platform/{s}" for s in SHAPES_3X3]

# =========================================================
# PIXEL ART SCALING
# =========================================================
def scale_pixel_art(src: pygame.Surface, dst_size: int) -> pygame.Surface:
    """
    Scale pixel art with nearest-neighbor filtering.

    Args:
        src: Source surface
        dst_size: Target size (square)

    Returns:
        Scaled surface
    """
    src = src.convert_alpha()
    if src.get_width() == dst_size and src.get_height() == dst_size:
        return src
    return pygame.transform.scale(src, (dst_size, dst_size))

def load_tile_png(path: Path, tile_size: int, expected_src: int = 8) -> pygame.Surface:
    """
    Load a tile PNG and scale it to the target tile size.

    Args:
        path: Path to PNG file
        tile_size: Target tile size in pixels
        expected_src: Expected source size (default 8x8)

    Returns:
        Scaled pygame Surface
    """
    if not path.exists():
        # Return magenta placeholder
        surf = pygame.Surface((tile_size, tile_size))
        surf.fill((255, 0, 255))
        return surf

    img = pygame.image.load(str(path)).convert_alpha()

    if img.get_width() != expected_src or img.get_height() != expected_src:
        print(f"[Tiles] Warning: {path.name} is {img.get_width()}x{img.get_height()} "
              f"(expected {expected_src}x{expected_src}). Scaling anyway.")

    return scale_pixel_art(img, tile_size)

# =========================================================
# TILESET CLASS
# =========================================================
class TileSet:
    """
    Manages tile sprites organized by biome and category.

    Folder structure:
        assets/tiles/{biome}/{category}/{sprite}_0.png, {sprite}_1.png, ...

    Examples:
        assets/tiles/grassland/wall/top_left_0.png
        assets/tiles/grassland/platform/mid_mid_0.png
        assets/tiles/hollow/world/void_0.png
    """

    def __init__(self, biome: str, tile_size: int, root: Path):
        """
        Initialize tileset for a specific biome.

        Args:
            biome: Biome name (e.g., "grassland", "hollow", "ember")
            tile_size: Tile size in pixels (e.g., 32)
            root: Root path to tiles folder
        """
        self.biome = biome
        self.tile_size = tile_size
        self.root = Path(root) / biome
        self.sprites: Dict[str, List[pygame.Surface]] = {}
        self._load()

    @staticmethod
    def _base(stem: str) -> str:
        """
        Extract base name from numbered sprite file.

        Examples:
            top_left_0 -> top_left
            mid_mid_1 -> mid_mid
            door -> door
        """
        parts = stem.split("_")
        return "_".join(parts[:-1]) if parts and parts[-1].isdigit() else stem

    def _load(self) -> None:
        """Load all tile sprites from the biome folder."""
        if not self.root.exists():
            print(f"[Tiles] Warning: Biome folder not found: {self.root}")
            print(f"[Tiles] Creating placeholder tiles...")
            self._create_placeholders()
            return

        # Scan categories
        for cat in self.root.iterdir():
            if not cat.is_dir():
                continue

            # Load all PNGs in category
            for p in sorted(cat.glob("*.png")):
                key = f"{cat.name}/{self._base(p.stem)}"
                surf = load_tile_png(p, self.tile_size, expected_src=8)
                self.sprites.setdefault(key, []).append(surf)

        print(f"[Tiles] Loaded {len(self.sprites)} sprite keys for biome '{self.biome}'")

    def _create_placeholders(self) -> None:
        """Create placeholder tiles when assets are missing."""
        colors = {
            "world/void": (20, 20, 30),
            "wall/": (100, 100, 120),
            "platform/": (140, 100, 70),
            "door/door": (200, 200, 50),
            "feature/marker": (255, 0, 255),
        }

        for key in REQUIRED_KEYS:
            color = colors.get(key, (100, 100, 100))
            for prefix, col in colors.items():
                if key.startswith(prefix):
                    color = col
                    break

            surf = pygame.Surface((self.tile_size, self.tile_size))
            surf.fill(color)
            self.sprites[key] = [surf]

    def get(self, key: str, hash_value: int) -> Optional[pygame.Surface]:
        """
        Get a sprite by key with deterministic variant selection.

        Args:
            key: Sprite key (e.g., "wall/top_left", "door/door")
            hash_value: Hash for deterministic variant selection

        Returns:
            pygame Surface or None if not found
        """
        vs = self.sprites.get(key)
        if not vs:
            return None
        return vs[0] if len(vs) == 1 else vs[hash_value % len(vs)]

# =========================================================
# AUTO-TILING LOGIC
# =========================================================
def autotile_key(tilemap: List[List[int]], x: int, y: int, tid: int) -> str:
    """
    Determine which 3x3 tile pattern to use based on neighbors.

    Args:
        tilemap: 2D tile array
        x, y: Tile coordinates
        tid: Tile ID to match against

    Returns:
        Pattern name (e.g., "top_left", "mid_mid")
    """
    h = len(tilemap)
    w = len(tilemap[0])

    def at(xx: int, yy: int) -> int:
        if xx < 0 or yy < 0 or xx >= w or yy >= h:
            return -9999
        return tilemap[yy][xx]

    up = at(x, y - 1)
    dn = at(x, y + 1)
    lf = at(x - 1, y)
    rt = at(x + 1, y)

    # Determine row
    if up != tid:
        row = "top"
    elif dn != tid:
        row = "bottom"
    else:
        row = "mid"

    # Determine column
    if lf != tid:
        col = "left"
    elif rt != tid:
        col = "right"
    else:
        col = "mid"

    return f"{row}_{col}"

# =========================================================
# TILE RENDERING
# =========================================================
def draw_tiles(screen: pygame.Surface, tilemap: List[List[int]], cam: pygame.Vector2,
               ts: TileSet, seed: int, debug_grid: bool = False) -> None:
    """
    Draw tiles with auto-tiling and camera culling.

    Args:
        screen: Target surface
        tilemap: 2D tile array
        cam: Camera position (world coordinates)
        ts: TileSet instance
        seed: Seed for deterministic variant selection
        debug_grid: Whether to draw debug grid lines
    """
    from level_gen.zone_generator import AIR, WALL, PLATFORM, DOOR, EXIT

    sw, sh = screen.get_size()
    h = len(tilemap)
    w = len(tilemap[0])

    # Calculate visible tile range
    x0 = max(0, int(cam.x) // ts.tile_size - 1)
    y0 = max(0, int(cam.y) // ts.tile_size - 1)
    x1 = min(w - 1, (int(cam.x) + sw) // ts.tile_size + 1)
    y1 = min(h - 1, (int(cam.y) + sh) // ts.tile_size + 1)

    for y in range(y0, y1 + 1):
        row = tilemap[y]
        for x in range(x0, x1 + 1):
            tid = row[x]

            if tid == AIR:
                continue

            # Determine sprite key
            if tid == WALL:
                key = f"world/void"  # Use as wall background
            elif tid == EXIT:
                key = "door/door"
            elif tid == DOOR:
                key = "door/door"
            elif tid == PLATFORM:
                key = f"platform/{autotile_key(tilemap, x, y, PLATFORM)}"
            else:
                key = "world/void"

            # Get sprite with deterministic hash
            hsh = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791) ^ (tid * 2654435761)
            img = ts.get(key, hsh)

            # Calculate screen position
            sx = x * ts.tile_size - cam.x
            sy = y * ts.tile_size - cam.y

            # Draw
            if img:
                screen.blit(img, (sx, sy))
            else:
                # Magenta placeholder for missing tiles
                pygame.draw.rect(screen, (255, 0, 255),
                               (sx, sy, ts.tile_size, ts.tile_size))

            if debug_grid:
                pygame.draw.rect(screen, (55, 55, 65),
                               (sx, sy, ts.tile_size, ts.tile_size), 1)

# =========================================================
# VALIDATION
# =========================================================
def validate_tiles(ts: TileSet) -> None:
    """
    Check if all required sprite keys are present.

    Prints warnings for missing keys that will render as magenta.
    """
    missing = [k for k in REQUIRED_KEYS if k not in ts.sprites]
    if missing:
        print(f"[Tiles] Missing sprite keys (will render as magenta):")
        for k in missing:
            print(f"  - {k}")
        print()
