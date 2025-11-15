
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pygame
from player import Player


@dataclass
class PlayerController:
    """Thin wrapper around Player to centralise per-frame behaviour."""

    player: Player

    def update(self, dt: float, game: Any) -> None:
        """Update the underlying Player using current input and world info."""
        keys = pygame.key.get_pressed()

        # Core movement / abilities update
        self.player.update(
            keys,
            game.tiles,
            dt,
            game.phaseable_walls,
            game.abilities,
        )

        # Coin magnet still expects a list of rects, so convert entities -> rects
        coin_rects = [c.rect for c in getattr(game, "coins", [])]
        self.player.apply_magnet_to_coins(coin_rects, dt)
