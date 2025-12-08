"""
Minimap HUD Component

Displays the minimap in the top-right corner during gameplay.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
import pygame

from ui.minimap import Minimap
from settings import ROOM_W, ROOM_H, TILE_SIZE

if TYPE_CHECKING:
    from core.game import Game


class MinimapHUD:
    """
    HUD component that renders the minimap.
    """

    def __init__(self, cell_size: int = 8, padding: int = 6):
        """
        Initialize minimap HUD.

        Args:
            cell_size: Size of each room cell in minimap
            padding: Padding around minimap
        """
        self.minimap = Minimap(cell_size, padding)
        self.enabled = True  # Can be toggled with key

    def toggle(self) -> bool:
        """Toggle minimap visibility."""
        self.enabled = not self.enabled
        return self.enabled

    def draw(self, surface: pygame.Surface, game: Game) -> None:
        """
        Draw minimap on the surface.

        Args:
            surface: Target surface (play area or screen)
            game: Game instance
        """
        if not self.enabled:
            return

        # Check if we have room data
        if not hasattr(game, 'room_nodes') or not game.room_nodes:
            return

        # Calculate current room from player position
        if game.player:
            room_px_w = ROOM_W * TILE_SIZE
            room_px_h = ROOM_H * TILE_SIZE

            # Get room offset (minimum room coordinates)
            coords = list(game.room_nodes.keys())
            minx = min(x for x, _ in coords)
            miny = min(y for _, y in coords)

            # Calculate current room
            gx = game.player.rect.centerx // room_px_w
            gy = game.player.rect.centery // room_px_h

            # Adjust for offset
            current_room = (gx, gy)
            if current_room not in game.room_nodes:
                # Default to start room if player is out of bounds
                current_room = coords[0] if coords else (0, 0)

            # Draw minimap
            self.minimap.draw(
                surface,
                game.room_nodes,
                current_room,
                game.player.rect,
                room_px_w,
                room_px_h,
                minx,
                miny
            )
