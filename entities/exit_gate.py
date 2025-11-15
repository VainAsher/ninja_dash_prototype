
# entities/exit_gate.py - ExitGate entity

from __future__ import annotations

from typing import Optional
import pygame


class ExitGate:
    """Represents the level exit, optionally gated by coins collected."""

    def __init__(self, rect: Optional[pygame.Rect], coin_total: int, required_coins: int) -> None:
        self.rect: Optional[pygame.Rect] = rect
        self.coin_total: int = coin_total
        self.required_coins: int = max(0, required_coins)
        self.coins_collected: int = 0
        self.unlocked: bool = (self.required_coins == 0)

    def on_coin_collected(self) -> None:
        """Notify the gate that one coin was collected; may unlock it."""
        if self.unlocked:
            return
        self.coins_collected += 1
        if self.coins_collected >= self.required_coins:
            self.unlocked = True

    def can_finish(self, player_rect: pygame.Rect) -> bool:
        """Return True if the player can use this gate to finish the level."""
        return (
            self.unlocked
            and self.rect is not None
            and self.rect.colliderect(player_rect)
        )
