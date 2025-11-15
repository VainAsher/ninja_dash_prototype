
# states/base.py - common base class for all game states

from __future__ import annotations

from typing import Any
import pygame


class GameState:
    """Base class for all game states."""

    def __init__(self, game: Any) -> None:
        self.game = game

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.EventType) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass
