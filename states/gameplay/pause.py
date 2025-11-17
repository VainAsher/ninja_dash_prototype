
# states/pause.py - pause overlay

from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_BIG
from ui import Button
from ..base import GameState


class PauseState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.buttons: list[Button] = []

    def _quit_to_menu(self) -> None:
        """Save game and return to menu."""
        # Save current progress before quitting to menu
        if self.game.lives > 0:
            self.game.unlock_mgr.save_game_state(
                self.game.level_index,
                self.game.lives,
                self.game.total_score,
                self.game.game_time
            )
        self.game.change_state("menu")

    def enter(self) -> None:
        self.buttons.clear()

        def add(label: str, cb):
            self.buttons.append(Button(label, cb))

        add("▶ Resume", lambda: self.game.change_state("play"))
        add("⚙ Options", lambda: self.game.change_state("options"))
        add("🎮 Controls", lambda: self.game.change_state("controls"))
        add("🔧 Debug", lambda: self.game.change_state("debug"))
        add("↩ Quit to Menu", self._quit_to_menu)

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("play")
            return
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self.game.draw_world_and_player()

        overlay = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        title = FONT_BIG.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 180))
        surface.blit(title, title_rect)

        btn_w = 320
        btn_h = 40
        total_h = len(self.buttons) * (btn_h + 12)
        start_y = 260
        for i, btn in enumerate(self.buttons):
            x = (LOGICAL_W - btn_w) // 2
            y = start_y + i * (btn_h + 12)
            btn.layout(x, y, btn_w, btn_h)
            btn.draw(surface)
