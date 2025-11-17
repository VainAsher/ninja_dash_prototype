# states/unlocks.py - unlock viewer

from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_BIG, FONT_SMALL
from unlocks import ABILITY_ORDER, ABILITY_INFO
from .base import GameState


class UnlocksState(GameState):
    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("menu")

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((15, 10, 25))
        title = FONT_BIG.render("UNLOCKS", True, (180, 220, 255))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 80))
        surface.blit(title, title_rect)

        # Instead of using .unlocked_ids, query via is_unlocked()
        unlock_mgr = self.game.unlock_mgr

        y = 150
        for aid in ABILITY_ORDER:
            info = ABILITY_INFO.get(aid, {"name": aid, "description": ""})
            name = info.get("name", aid)
            desc = info.get("description", "")

            enabled = unlock_mgr.is_unlocked(aid)
            color = (180, 255, 180) if enabled else (120, 120, 120)

            label = FONT.render(name, True, color)
            surface.blit(label, (120, y))

            if desc:
                desc_txt = FONT_SMALL.render(desc, True, COLOR_TEXT)
                surface.blit(desc_txt, (140, y + 32))

            y += 64

        inst_txt = FONT_SMALL.render("ESC: back to menu", True, COLOR_TEXT)
        surface.blit(
            inst_txt,
            (LOGICAL_W - inst_txt.get_width() - 16, LOGICAL_H - 40),
        )
