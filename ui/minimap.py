"""
Minimap Rendering System

Displays a compact overview of the world's room layout, showing:
- Room types with color coding
- Connections between rooms
- Current room highlight
- Player position within current room
"""

from __future__ import annotations
from typing import Dict, Tuple
import pygame

from level_gen.zone_generator import (
    RoomNode, ROOM_START, ROOM_EXIT, ROOM_SHOP, ROOM_TREASURE,
    ROOM_BOSS, ROOM_PLATFORM, ROOM_COMBAT, ROOM_SAFE
)

# =========================================================
# MINIMAP COLORS
# =========================================================
MINIMAP_COLORS = {
    ROOM_START: (120, 220, 140),      # Green
    ROOM_EXIT: (240, 120, 120),       # Red
    ROOM_SHOP: (220, 200, 120),       # Gold
    ROOM_TREASURE: (120, 200, 220),   # Cyan
    ROOM_BOSS: (220, 120, 220),       # Magenta
    ROOM_PLATFORM: (160, 160, 220),   # Blue
    ROOM_COMBAT: (170, 170, 170),     # Gray
    ROOM_SAFE: (140, 200, 140),       # Light Green
}

# =========================================================
# MINIMAP RENDERER
# =========================================================
class Minimap:
    """
    Renders a minimap showing room layout and player position.
    """

    def __init__(self, cell_size: int = 10, padding: int = 8):
        """
        Initialize minimap renderer.

        Args:
            cell_size: Size of each room cell in pixels
            padding: Padding around the minimap
        """
        self.cell_size = cell_size
        self.padding = padding

    def draw(self, screen: pygame.Surface, rooms: Dict[Tuple[int, int], RoomNode],
             current_room: Tuple[int, int], player_rect: pygame.Rect,
             room_px_w: int, room_px_h: int, minx: int, miny: int) -> None:
        """
        Draw the minimap in the top-right corner.

        Args:
            screen: Target surface
            rooms: Dictionary of room nodes
            current_room: Current room coordinates
            player_rect: Player rectangle (world coordinates)
            room_px_w: Room width in pixels
            room_px_h: Room height in pixels
            minx, miny: Minimum room coordinates (for offset)
        """
        if not rooms:
            return

        coords = list(rooms.keys())
        maxx = max(x for x, _ in coords)
        maxy = max(y for _, y in coords)

        span_w = maxx - minx + 1
        span_h = maxy - miny + 1

        # Calculate minimap size
        cell = self.cell_size
        pad = self.padding
        width = span_w * cell + pad * 2
        height = span_h * cell + pad * 2

        # Create semi-transparent surface
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 140))

        def cell_xy(rc: Tuple[int, int]) -> Tuple[int, int]:
            """Convert room coords to minimap cell coords."""
            rx, ry = rc
            return pad + (rx - minx) * cell, pad + (ry - miny) * cell

        # Draw connections
        for rc, room in rooms.items():
            ax, ay = cell_xy(rc)
            acx, acy = ax + cell // 2, ay + cell // 2

            for nb in room.neighbors:
                if nb not in rooms or nb < rc:
                    continue

                bx, by = cell_xy(nb)
                bcx, bcy = bx + cell // 2, by + cell // 2

                pygame.draw.line(surf, (255, 255, 255, 60),
                               (acx, acy), (bcx, bcy), 2)

        # Draw room cells
        for rc, room in rooms.items():
            x, y = cell_xy(rc)
            color = MINIMAP_COLORS.get(room.type, (200, 200, 200))

            pygame.draw.rect(surf, (*color, 210),
                           (x, y, cell, cell), border_radius=3)

        # Highlight current room
        cx, cy = cell_xy(current_room)
        pygame.draw.rect(surf, (255, 255, 255, 240),
                        (cx - 2, cy - 2, cell + 4, cell + 4), 2, border_radius=4)

        # Draw player dot
        prx, pry = current_room
        room_ox = (prx - minx) * room_px_w
        room_oy = (pry - miny) * room_px_h

        rel_x = max(0, min(room_px_w - 1, player_rect.centerx - room_ox))
        rel_y = max(0, min(room_px_h - 1, player_rect.centery - room_oy))

        dot_x = cx + int((rel_x / room_px_w) * cell)
        dot_y = cy + int((rel_y / room_px_h) * cell)

        pygame.draw.circle(surf, (15, 15, 18, 230), (dot_x, dot_y), max(2, cell // 5))
        pygame.draw.circle(surf, (245, 245, 250, 230), (dot_x, dot_y), max(1, cell // 7))

        # Blit to screen (top-right corner)
        sw, _ = screen.get_size()
        screen.blit(surf, (sw - width - 10, 10))


# =========================================================
# WORLD DEBUG PRINTER
# =========================================================
def print_world(rooms: Dict[Tuple[int, int], RoomNode], start: Tuple[int, int],
                exitp: Tuple[int, int], grid: Tuple[int, int], style: str,
                title: str = "WORLD") -> None:
    """
    Print ASCII representation of the world to console.

    Args:
        rooms: Dictionary of room nodes
        start: Start room coordinates
        exitp: Exit room coordinates
        grid: Grid size (width, height)
        style: Generation style name
        title: Title for the printout
    """
    from level_gen.zone_generator import ROOM_SYMBOL

    if not rooms:
        print(f"\n[{title}] No rooms to display\n")
        return

    coords = list(rooms.keys())
    minx = min(x for x, _ in coords)
    miny = min(y for _, y in coords)
    maxx = max(x for x, _ in coords)
    maxy = max(y for _, y in coords)

    print("\n" + "=" * 78)
    print(title)
    print(f"style={style} rooms={len(rooms)} grid={grid} start={start} exit={exitp}")
    print("Legend: S=Start X=Exit $=Shop T=Treasure B=Boss P=Platform C=Combat .=Safe")
    print("-" * 78)

    # Column headers
    print("     " + " ".join(f"{x:2d}" for x in range(minx, maxx + 1)))

    # Rows
    for y in range(miny, maxy + 1):
        row = []
        for x in range(minx, maxx + 1):
            if (x, y) in rooms:
                symbol = ROOM_SYMBOL.get(rooms[(x, y)].type, "?")
                row.append(f" {symbol}")
            else:
                row.append(" .")

        print(f"y={y:2d} " + "".join(row))

    print("=" * 78 + "\n")
