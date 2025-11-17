
from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_SMALL, FONT_BIG
from ..base import GameState
from highscores import add_highscore


class NameEntryState(GameState):
    """State for entering a custom name for a new highscore."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.name_buffer: str = ""
        self.max_length: int = 12

    def enter(self) -> None:
        self.name_buffer = ""

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._finish(skip_save=True)
            elif event.key == pygame.K_BACKSPACE:
                self.name_buffer = self.name_buffer[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._finish(skip_save=False)
            else:
                if event.unicode and len(self.name_buffer) < self.max_length:
                    if event.unicode.isprintable():
                        self.name_buffer += event.unicode

    def _finish(self, skip_save: bool) -> None:
        score = getattr(self.game, "pending_score", None)
        level = getattr(self.game, "pending_level", None)
        diff = getattr(self.game, "pending_difficulty", None)

        if not skip_save and score is not None and level is not None and diff is not None:
            name = self.name_buffer.strip() or "Player"
            add_highscore(name, score, level, diff)

        self.game.pending_score = None
        self.game.pending_level = None
        self.game.pending_difficulty = None

        self.game.change_state("gameover")

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((8, 8, 20))

        title = FONT_BIG.render("NEW HIGH SCORE!", True, (255, 215, 0))
        subtitle = FONT.render("Enter your name", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 120))
        subtitle_rect = subtitle.get_rect(center=(LOGICAL_W // 2, 170))
        surface.blit(title, title_rect)
        surface.blit(subtitle, subtitle_rect)

        score = getattr(self.game, "pending_score", 0)
        lvl = getattr(self.game, "pending_level", 1)
        diff = getattr(self.game, "pending_difficulty", "medium")
        info_text = FONT_SMALL.render(
            f"Score: {score}  Level: {lvl}  Difficulty: {diff}",
            True,
            COLOR_TEXT,
        )
        info_rect = info_text.get_rect(center=(LOGICAL_W // 2, 210))
        surface.blit(info_text, info_rect)

        box_w, box_h = 400, 50
        box_rect = pygame.Rect(0, 0, box_w, box_h)
        box_rect.center = (LOGICAL_W // 2, 280)
        pygame.draw.rect(surface, (40, 40, 80), box_rect, border_radius=10)
        pygame.draw.rect(surface, (200, 200, 255), box_rect, 2, border_radius=10)

        display_name = self.name_buffer or "Enter name..."
        name_color = COLOR_TEXT if self.name_buffer else (140, 140, 180)
        name_surf = FONT.render(display_name, True, name_color)
        name_rect = name_surf.get_rect(center=box_rect.center)
        surface.blit(name_surf, name_rect)

        inst_lines = [
            "Type to enter your name",
            "ENTER: confirm   ESC: skip",
            "BACKSPACE: delete",
        ]
        y = 350
        for line in inst_lines:
            t = FONT_SMALL.render(line, True, COLOR_TEXT)
            r = t.get_rect(center=(LOGICAL_W // 2, y))
            surface.blit(t, r)
            y += 26
