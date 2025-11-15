
# entities/collectibles.py - Coin, HealthPickup, LifePickup, Powerup entities

from __future__ import annotations

from typing import Any
import pygame


class Coin:
    def __init__(self, rect: pygame.Rect, value: int) -> None:
        self.rect = rect
        self.value = value

    def try_collect(self, player_rect: pygame.Rect, game: Any) -> bool:
        """Return True if collected; applies score and notifies exit gate."""
        if not self.rect.colliderect(player_rect):
            return False

        # Add score
        game.total_score += self.value

        # Inform exit gate, if present
        gate = getattr(game, "exit_gate", None)
        if gate is not None:
            gate.on_coin_collected()

        return True


class HealthPickup:
    def __init__(self, rect: pygame.Rect, amount: int = 1) -> None:
        self.rect = rect
        self.amount = amount

    def try_collect(self, player: Any, game: Any) -> bool:
        if not self.rect.colliderect(player.rect):
            return False
        player.heal(self.amount)
        return True


class LifePickup:
    def __init__(self, rect: pygame.Rect, amount: int = 1) -> None:
        self.rect = rect
        self.amount = amount

    def try_collect(self, player: Any, game: Any) -> bool:
        if not self.rect.colliderect(player.rect):
            return False
        game.lives += self.amount
        return True


class Powerup:
    def __init__(self, rect: pygame.Rect, ptype: str) -> None:
        self.rect = rect
        self.ptype = ptype

    def try_collect(self, player: Any, game: Any) -> bool:
        if not self.rect.colliderect(player.rect):
            return False

        if self.ptype == "speed":
            player.apply_speed_boost()
        elif self.ptype == "triple":
            player.apply_triple_jump()
        elif self.ptype == "magnet":
            player.activate_magnet()

        return True
