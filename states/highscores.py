
# states/highscores.py - highscores screen

from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_BIG, FONT_SMALL
from highscores import get_highscores
from .base import GameState


class HighscoresState(GameState):
    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("menu")

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 30))
        title = FONT_BIG.render("HIGH SCORES", True, (255, 215, 0))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 80))
        surface.blit(title, title_rect)

        scores = get_highscores()
        y = 150
        for i, entry in enumerate(scores[:10], start=1):
            name = entry.get("name", "???")
            score = entry.get("score", 0)
            lvl = entry.get("level", 1)
            diff = entry.get("difficulty", "medium")
            line = f"{i:2d}. {name:10s}  {score:6d} pts  L{lvl} [{diff}]"
            txt = FONT.render(line, True, COLOR_TEXT)
            surface.blit(txt, (120, y))
            y += 36

        inst_txt = FONT_SMALL.render("ESC: back to menu", True, COLOR_TEXT)
        surface.blit(
            inst_txt,
            (LOGICAL_W - inst_txt.get_width() - 16, LOGICAL_H - 40),
        )
