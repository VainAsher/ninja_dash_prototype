
# states/menu.py - main menu

from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_BIG
from ui import Button
from ..base import GameState


class MenuState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.buttons: list[Button] = []

    def enter(self) -> None:
        self.buttons.clear()

        def add(label: str, cb):
            self.buttons.append(Button(label, cb))

        # Show Continue button if save exists
        if self.game.unlock_mgr.has_save():
            add("▶ Continue", self.game.continue_game)

        add("📖 Campaign", self.game.start_campaign)
        add("🆕 New Game", self.game.start_new_game)
        add("🎲 Custom Seed Run", lambda: self.game.change_state("seed_entry"))
        add("🏆 High Scores", lambda: self.game.change_state("highscores"))
        add("⭐ Unlocks", lambda: self.game.change_state("unlocks"))
        add("⚙ Options", lambda: self.game.change_state("options"))
        add("❓ Help", lambda: self.game.change_state("help"))
        add("✕ Quit", self.game.quit)

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()
            return
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 30))
        title = FONT_BIG.render("NINJA DASH", True, (100, 200, 255))
        subtitle = FONT.render("Refactored Prototype", True, (180, 180, 220))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 120))
        sub_rect = subtitle.get_rect(center=(LOGICAL_W // 2, 170))
        surface.blit(title, title_rect)
        surface.blit(subtitle, sub_rect)

        btn_w = 360
        btn_h = 40
        total_h = len(self.buttons) * (btn_h + 12)
        start_y = (LOGICAL_H - total_h) // 2

        for i, btn in enumerate(self.buttons):
            x = (LOGICAL_W - btn_w) // 2
            y = start_y + i * (btn_h + 12)
            btn.layout(x, y, btn_w, btn_h)
            btn.draw(surface)
