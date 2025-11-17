
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
                 "Move:        Arrow Keys (Left/Right)",
                 "Jump:        Up Arrow or Space",
                 "Crouch:      Down Arrow (hold)",
                 "Dash:        Left Shift (hold)",
                 "Slide:       V (while moving)",
                 "Shadow Step: Q (teleport with invincibility)",
                 "Air Dodge:   C (quick dodge in air)",
                 "Pause:       ESC",
             ]),
            ("Goal",
             [
                 "Reach the exit to clear each level.",
                 "Collect coins to unlock the exit gate.",
                 "Avoid hazards or you'll lose health and lives.",
                 "Collect ability orbs to unlock new abilities!",
             ]),
            ("Core Abilities",
             [
                 "Double Jump  – Jump again in mid-air (default)",
                 "Dash         – Quick burst of speed (uses stamina)",
                 "Wall Jump    – Jump off walls to climb higher",
                 "Slide        – Slide under obstacles at high speed",
                 "Sword Attack – Attack enemies with your sword (default)",
             ]),
            ("Advanced Abilities",
             [
                 "Wall Cling   – Hold onto walls to rest",
                 "Shadow Step  – Phase through hazards and enemies",
                 "Air Dodge    – Quick dodge with invincibility frames",
                 "Glide        – Hold jump while falling to glide",
                 "Grapple Hook – Swing or pull yourself to platforms",
             ]),
            ("Progression",
             [
                 "Collect Ability Orbs to unlock new abilities.",
                 "Progress is saved automatically on level completion.",
                 "Death deletes your save - play carefully!",
                 "View unlocked abilities in the Unlocks menu.",
             ]),
        ]

        # Use two columns for better space utilization
        left_sections = sections[:3]
        right_sections = sections[3:]

        # Left column
        y = 120
        for header, lines in left_sections:
            header_surf = FONT_SMALL.render(header, True, (220, 230, 255))
            surface.blit(header_surf, (40, y))
            y += 22
            for line in lines:
                text_surf = FONT_SMALL.render("• " + line, True, COLOR_TEXT)
                surface.blit(text_surf, (55, y))
                y += 20
            y += 8

        # Right column
        y = 120
        for header, lines in right_sections:
            header_surf = FONT_SMALL.render(header, True, (220, 230, 255))
            surface.blit(header_surf, (660, y))
            y += 22
            for line in lines:
                text_surf = FONT_SMALL.render("• " + line, True, COLOR_TEXT)
                surface.blit(text_surf, (675, y))
                y += 20
            y += 8

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
