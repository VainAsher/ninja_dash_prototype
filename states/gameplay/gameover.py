
# states/gameover.py - game over screen

from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_BIG, FONT_SMALL
from ..base import GameState


class GameOverState(GameState):
    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.game.change_state("menu")

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((10, 0, 20))

        title = FONT_BIG.render("GAME OVER", True, (255, 120, 120))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 160))
        surface.blit(title, title_rect)

        score_txt = FONT.render(f"Final Score: {self.game.total_score}", True, COLOR_TEXT)
        level_txt = FONT.render(f"Level Reached: {self.game.level_index}", True, COLOR_TEXT)
        inst_txt = FONT_SMALL.render("Press ENTER to return to menu", True, COLOR_TEXT)

        surface.blit(score_txt, (LOGICAL_W // 2 - score_txt.get_width() // 2, 240))
        surface.blit(level_txt, (LOGICAL_W // 2 - level_txt.get_width() // 2, 280))
        surface.blit(inst_txt, (LOGICAL_W // 2 - inst_txt.get_width() // 2, 340))
