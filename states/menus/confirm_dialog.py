"""
Confirmation Dialog - Reusable confirmation dialog for destructive actions
"""

from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_BIG
from ui import Button
from ..base import GameState


class ConfirmDialog(GameState):
    """Modal confirmation dialog for destructive actions."""

    def __init__(self, game, message: str, on_confirm, on_cancel=None) -> None:
        super().__init__(game)
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel or (lambda: self.game.pop_state())
        self.buttons: list[Button] = []

    def enter(self) -> None:
        self.buttons.clear()

        # Create confirm and cancel buttons
        self.buttons.append(Button("Yes", self._handle_confirm))
        self.buttons.append(Button("No", self._handle_cancel))

    def _handle_confirm(self) -> None:
        """Execute confirmation action and close dialog."""
        self.game.pop_state()  # Close dialog first
        self.on_confirm()

    def _handle_cancel(self) -> None:
        """Execute cancel action and close dialog."""
        self.game.pop_state()  # Close dialog first
        self.on_cancel()

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._handle_cancel()
                return
            elif event.key == pygame.K_RETURN:
                self._handle_confirm()
                return

        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        # Draw dark overlay
        overlay = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Draw dialog box
        dialog_w = 500
        dialog_h = 200
        dialog_x = (LOGICAL_W - dialog_w) // 2
        dialog_y = (LOGICAL_H - dialog_h) // 2

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(surface, (30, 30, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(surface, (100, 120, 180), dialog_rect, 3, border_radius=12)

        # Draw message (with word wrapping)
        lines = self._wrap_text(self.message, dialog_w - 40)
        y_offset = dialog_y + 40
        for line in lines:
            text = FONT.render(line, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(LOGICAL_W // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 30

        # Draw buttons
        btn_w = 120
        btn_h = 40
        btn_spacing = 20
        total_btn_width = (btn_w * 2) + btn_spacing
        start_x = (LOGICAL_W - total_btn_width) // 2
        btn_y = dialog_y + dialog_h - 60

        for i, btn in enumerate(self.buttons):
            x = start_x + i * (btn_w + btn_spacing)
            btn.layout(x, btn_y, btn_w, btn_h)
            btn.draw(surface)

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        """Simple word wrapping for dialog text."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = FONT.render(test_line, True, COLOR_TEXT)

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines
