
from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_BIG, FONT_SMALL, DIFFICULTY_CONFIG
from .base import GameState


class SettingsState(GameState):
    """Expanded settings screen with difficulty selection and notes."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self._difficulty_keys = list(DIFFICULTY_CONFIG.keys())

    def _cycle_difficulty(self, direction: int) -> None:
        if not self._difficulty_keys:
            return
        cur = self.game.difficulty
        if cur not in self._difficulty_keys:
            self.game.difficulty = self._difficulty_keys[0]
            return
        idx = self._difficulty_keys.index(cur)
        idx = (idx + direction) % len(self._difficulty_keys)
        self.game.difficulty = self._difficulty_keys[idx]

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("menu")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._cycle_difficulty(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._cycle_difficulty(+1)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((10, 15, 25))

        title = FONT_BIG.render("SETTINGS", True, (200, 230, 255))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 80))
        surface.blit(title, title_rect)

        diff = self.game.difficulty
        diff_cfg = DIFFICULTY_CONFIG.get(diff, {})
        label = FONT.render("Difficulty:", True, COLOR_TEXT)
        value = FONT.render(diff.upper(), True, (255, 220, 180))

        surface.blit(label, (120, 150))
        surface.blit(value, (320, 150))

        arrows = FONT_SMALL.render("<  LEFT / RIGHT  >", True, COLOR_TEXT)
        surface.blit(arrows, (120, 190))

        desc_lines = diff_cfg.get("description", [
            "Configure difficulty in DIFFICULTY_CONFIG inside settings.py.",
            "Each difficulty can change enemy density, coin ratio, and scoring.",
        ])
        y = 230
        for line in desc_lines:
            t = FONT_SMALL.render(line, True, COLOR_TEXT)
            surface.blit(t, (120, y))
            y += 22

        notes = [
            "Note: Changing difficulty here affects new runs.",
            "Existing runs keep their current difficulty.",
        ]
        y += 10
        for line in notes:
            t = FONT_SMALL.render(line, True, (180, 180, 210))
            surface.blit(t, (120, y))
            y += 20

        inst = FONT_SMALL.render("ESC: back to menu", True, COLOR_TEXT)
        inst_rect = inst.get_rect(
            bottomright=(LOGICAL_W - 16, LOGICAL_H - 12)
        )
        surface.blit(inst, inst_rect)
