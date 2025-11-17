
from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT_BIG, FONT_SMALL
from ui import Button
from ..base import GameState


class HelpState(GameState):
    """More detailed help page covering controls, goals, abilities, and meta."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.buttons: list[Button] = []

    def enter(self) -> None:
        self.buttons.clear()
        self.buttons.append(Button("🎮 View Controls", lambda: self.game.change_state("controls")))

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("menu")
            return
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((5, 10, 20))

        title = FONT_BIG.render("HELP & INFO", True, (200, 240, 255))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 80))
        surface.blit(title, title_rect)

        sections = [
            ("Controls",
             [
                 "Move:  Left / Right Arrow Keys",
                 "Jump:  Up Arrow / Space",
                 "Crouch: Down Arrow",
                 "Dash:  Left Shift (when unlocked)",
                 "Pause: ESC",
             ]),
            ("Goal",
             [
                 "Reach the exit to clear each level.",
                 "Collect coins to unlock the exit gate.",
                 "Avoid hazards or you'll lose health and lives.",
             ]),
            ("Abilities",
             [
                 "Double Jump   – unlocks extra mid-air jump.",
                 "Dash          – quick burst of speed, can pass through hazards.",
                 "Wall Jump     – jump off walls to climb.",
                 "Shadow Step   – brief invulnerability window during dash.",
                 "Coin Magnet   – pulls nearby coins toward you.",
             ]),
            ("Meta Progression",
             [
                 "Clearing levels awards points and unlocks abilities over time.",
                 "Higher difficulties increase rewards and challenge.",
                 "High scores are saved per difficulty.",
             ]),
        ]

        y = 130
        for header, lines in sections:
            header_surf = FONT_SMALL.render(header, True, (220, 230, 255))
            surface.blit(header_surf, (80, y))
            y += 24
            for line in lines:
                text_surf = FONT_SMALL.render("• " + line, True, COLOR_TEXT)
                surface.blit(text_surf, (100, y))
                y += 22
            y += 10

        # Draw Controls button
        btn_w = 240
        btn_h = 40
        btn_x = (LOGICAL_W - btn_w) // 2
        btn_y = LOGICAL_H - 100
        if self.buttons:
            self.buttons[0].layout(btn_x, btn_y, btn_w, btn_h)
            self.buttons[0].draw(surface)

        inst = FONT_SMALL.render("ESC: back to menu", True, COLOR_TEXT)
        inst_rect = inst.get_rect(
            bottomright=(LOGICAL_W - 16, LOGICAL_H - 12)
        )
        surface.blit(inst, inst_rect)
