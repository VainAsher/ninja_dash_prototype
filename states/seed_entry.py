
from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_SMALL, FONT_BIG, DEFAULT_SEED
from .base import GameState


class SeedEntryState(GameState):
    """State to enter a custom seed for procedural generation."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.seed_buffer: str = ""
        self.max_length: int = 20

    def enter(self) -> None:
        self.seed_buffer = ""

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("menu")
            elif event.key == pygame.K_BACKSPACE:
                self.seed_buffer = self.seed_buffer[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._apply_seed_and_start()
            else:
                if event.unicode and len(self.seed_buffer) < self.max_length:
                    if event.unicode.isprintable():
                        self.seed_buffer += event.unicode

    def _apply_seed_and_start(self) -> None:
        text = self.seed_buffer.strip()
        if not text:
            self.game.seed = DEFAULT_SEED
        else:
            self.game.seed = text
        self.game.start_new_run()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((5, 10, 25))

        title = FONT_BIG.render("CUSTOM SEED", True, (200, 230, 255))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 120))
        surface.blit(title, title_rect)

        subtitle = FONT.render("Enter a seed for your next run", True, COLOR_TEXT)
        subtitle_rect = subtitle.get_rect(center=(LOGICAL_W // 2, 170))
        surface.blit(subtitle, subtitle_rect)

        diff = self.game.difficulty
        diff_surf = FONT_SMALL.render(f"Difficulty: {diff}", True, COLOR_TEXT)
        diff_rect = diff_surf.get_rect(center=(LOGICAL_W // 2, 210))
        surface.blit(diff_surf, diff_rect)

        box_w, box_h = 420, 50
        box_rect = pygame.Rect(0, 0, box_w, box_h)
        box_rect.center = (LOGICAL_W // 2, 280)
        pygame.draw.rect(surface, (40, 40, 80), box_rect, border_radius=10)
        pygame.draw.rect(surface, (200, 200, 255), box_rect, 2, border_radius=10)

        display_seed = self.seed_buffer or "Leave empty for default seed"
        seed_color = COLOR_TEXT if self.seed_buffer else (140, 140, 180)
        seed_surf = FONT.render(display_seed, True, seed_color)
        seed_rect = seed_surf.get_rect(center=box_rect.center)
        surface.blit(seed_surf, seed_rect)

        inst_lines = [
            "Type any letters or numbers.",
            "ENTER: start run with this seed",
            "ESC: back to menu",
        ]
        y = 350
        for line in inst_lines:
            t = FONT_SMALL.render(line, True, COLOR_TEXT)
            r = t.get_rect(center=(LOGICAL_W // 2, y))
            surface.blit(t, r)
            y += 26
