
# states/menu.py - main menu

from __future__ import annotations

import pygame

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, FONT, FONT_BIG
from ui import Button
from ..base import GameState
from .confirm_dialog import ConfirmDialog


class MenuState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.buttons: list[Button] = []
        self.selected_index = 0  # For keyboard navigation

    def _confirm_quit(self) -> None:
        """Show confirmation before quitting the game."""
        confirm = ConfirmDialog(
            self.game,
            "Quit Ninja Dash?",
            on_confirm=self.game.quit
        )
        self.game.push_state(confirm)

    def enter(self) -> None:
        self.buttons.clear()

        def add(label: str, cb, tooltip=None):
            self.buttons.append(Button(label, cb, tooltip))

        # Reorganized in logical order for RPG-style menu
        # Top row: Primary gameplay options
        if self.game.unlock_mgr.has_save():
            add("Continue", self.game.continue_game,
                "Resume your saved progress from the last checkpoint")
        else:
            add("New Game", self.game.start_new_game,
                "Start a fresh playthrough")

        add("Campaign", self.game.start_campaign,
            "Play through story mode with progressive difficulty")

        # Second row: Alternative game modes
        add("Custom Seed Run", lambda: self.game.change_state("seed_entry"),
            "Enter a custom seed for procedurally generated levels")
        add("High Scores", lambda: self.game.change_state("highscores"),
            "View your best scores and completion times")

        # Third row: Progression and management
        if self.game.unlock_mgr.has_save():
            add("New Game", self.game.start_new_game,
                "Start a fresh playthrough (will overwrite current save)")
        add("Unlocks", lambda: self.game.change_state("unlocks"),
            "View and manage unlocked abilities and progression")

        # Bottom rows: Settings and info
        add("Options", lambda: self.game.change_state("options"),
            "Configure game settings, controls, graphics, and audio")
        add("Help", lambda: self.game.change_state("help"),
            "View game instructions, controls, and tutorials")

        add("Quit", self._confirm_quit,
            "Exit Ninja Dash")

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._confirm_quit()
                return
            elif event.key == pygame.K_UP:
                # Navigate up (move up 2 rows in grid)
                self.selected_index = (self.selected_index - 2) % len(self.buttons)
                return
            elif event.key == pygame.K_DOWN:
                # Navigate down (move down 2 rows in grid)
                self.selected_index = (self.selected_index + 2) % len(self.buttons)
                return
            elif event.key == pygame.K_LEFT:
                # Navigate left in grid
                if self.selected_index % 2 == 1:  # If in right column
                    self.selected_index -= 1
                return
            elif event.key == pygame.K_RIGHT:
                # Navigate right in grid
                if self.selected_index % 2 == 0 and self.selected_index + 1 < len(self.buttons):
                    self.selected_index += 1
                return
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Activate selected button
                if 0 <= self.selected_index < len(self.buttons):
                    self.buttons[self.selected_index].on_click()
                return

        # Still support mouse
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt: float) -> None:
        # Update buttons for tooltip timing
        for btn in self.buttons:
            btn.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 30))

        # Title area - moved higher and more prominent
        title = FONT_BIG.render("NINJA DASH", True, (100, 200, 255))
        subtitle = FONT.render("Refactored Prototype", True, (180, 180, 220))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 50))
        sub_rect = subtitle.get_rect(center=(LOGICAL_W // 2, 90))

        # Draw title background for prominence
        title_bg = pygame.Rect(0, 0, LOGICAL_W, 130)
        pygame.draw.rect(surface, (15, 15, 40), title_bg)
        pygame.draw.line(surface, (60, 80, 120), (0, 129), (LOGICAL_W, 129), 2)

        surface.blit(title, title_rect)
        surface.blit(subtitle, sub_rect)

        # Two-column grid layout
        btn_w = 280
        btn_h = 40
        col_gap = 20
        row_gap = 12

        # Calculate grid dimensions
        cols = 2
        total_grid_w = cols * btn_w + (cols - 1) * col_gap
        start_x = (LOGICAL_W - total_grid_w) // 2
        start_y = 160  # Start below title area

        for i, btn in enumerate(self.buttons):
            col = i % cols
            row = i // cols

            x = start_x + col * (btn_w + col_gap)
            y = start_y + row * (btn_h + row_gap)
            btn.layout(x, y, btn_w, btn_h)

            # Draw selection indicator for keyboard navigation
            if i == self.selected_index:
                # Draw glow/border around selected button
                glow_rect = pygame.Rect(x - 4, y - 4, btn_w + 8, btn_h + 8)
                pygame.draw.rect(surface, (255, 255, 100), glow_rect, 3, border_radius=10)

            btn.draw(surface)
