
from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT_BIG, FONT_SMALL
from .base import GameState


class HelpState(GameState):
    """More detailed help page covering controls, goals, abilities, and meta."""

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("menu")

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

        # Add note about controls viewer
        controls_note = FONT_SMALL.render("Press F1 or check Pause menu for full controls viewer", True, (150, 200, 255))
        controls_note_rect = controls_note.get_rect(center=(LOGICAL_W // 2, LOGICAL_H - 60))
        surface.blit(controls_note, controls_note_rect)

        inst = FONT_SMALL.render("ESC: back to menu", True, COLOR_TEXT)
        inst_rect = inst.get_rect(
            bottomright=(LOGICAL_W - 16, LOGICAL_H - 12)
        )
        surface.blit(inst, inst_rect)
