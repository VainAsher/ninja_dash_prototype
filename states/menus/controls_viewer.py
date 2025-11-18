"""
Controls Viewer State - Display keybindings and allow rebinding
"""

from __future__ import annotations

import pygame
from typing import Optional, Tuple

from settings import LOGICAL_W, LOGICAL_H, COLOR_TEXT, COLOR_BG, FONT, FONT_SMALL, FONT_BIG
from controls import get_controls_manager
from core.game import transform_mouse_to_logical
from ..base import GameState


class ControlsViewerState(GameState):
    """
    State for viewing and optionally rebinding controls.
    """

    def __init__(self, game):
        super().__init__(game)
        self.controls = get_controls_manager()

        # UI state
        self.scroll_offset = 0
        self.max_scroll = 0
        self.category_index = 0
        self.categories = []
        self.mouse_pos = (0, 0)

        # Rebinding state
        self.rebinding_action: Optional[str] = None
        self.waiting_for_key = False

        # Visual
        self.bg_color = (15, 15, 25)
        self.panel_color = (25, 25, 40)
        self.highlight_color = (50, 100, 200)
        self.category_color = (80, 150, 255)
        self.key_bg_color = (40, 40, 60)
        self.key_text_color = (200, 220, 255)

    def enter(self) -> None:
        """Initialize the controls viewer."""
        self.scroll_offset = 0
        self.category_index = 0
        self.categories = self.controls.get_all_categories()
        self.rebinding_action = None
        self.waiting_for_key = False

    def exit(self) -> None:
        """Clean up when leaving the controls viewer."""
        # Save any changes
        self.controls.save_user_bindings()

    def handle_event(self, event: pygame.event.EventType) -> None:
        """Handle input events."""
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = transform_mouse_to_logical(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(transform_mouse_to_logical(event.pos))

        elif event.type == pygame.KEYDOWN:
            # If waiting for rebind key
            if self.waiting_for_key and self.rebinding_action:
                self._handle_rebind_key(event.key)
                return

            # Navigation
            if event.key == pygame.K_ESCAPE:
                # Return to wherever we came from (help, menu, pause, etc.)
                return_state = self.game.previous_state_name or "menu"
                self.game.change_state(return_state)
                return

            if event.key == pygame.K_LEFT:
                self.category_index = max(0, self.category_index - 1)
                self.scroll_offset = 0

            elif event.key == pygame.K_RIGHT:
                self.category_index = min(len(self.categories) - 1,
                                        self.category_index + 1)
                self.scroll_offset = 0

            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)

            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll,
                                        self.scroll_offset + 1)

            # Reset to defaults
            elif event.key == pygame.K_r:
                self.controls.reset_to_defaults()

        # Mouse wheel scrolling
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll,
                                           self.scroll_offset - event.y))

    def _handle_rebind_key(self, pygame_key: int) -> None:
        """Handle key press during rebinding."""
        # Cancel rebinding on Escape
        if pygame_key == pygame.K_ESCAPE:
            self.waiting_for_key = False
            self.rebinding_action = None
            return

        # Convert pygame key back to string (simplified)
        # This is a basic implementation; full implementation would
        # reverse the mapping in ControlAction
        key_name = pygame.key.name(pygame_key)

        # Try to rebind
        if self.rebinding_action:
            # For now, replace all keys with single new key
            # TODO: Allow multi-key bindings
            success = self.controls.rebind_action(
                self.rebinding_action,
                [key_name],
                allow_conflicts=False
            )

            if success:
                self.waiting_for_key = False
                self.rebinding_action = None
            # If failed (conflict), could show message

    def _handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse clicks."""
        # Check back button click (bottom left corner)
        back_rect = pygame.Rect(50, LOGICAL_H - 70, 200, 50)
        if back_rect.collidepoint(pos):
            self.controls.save_user_bindings()
            return_state = self.game.previous_state_name or "menu"
            self.game.change_state(return_state)
            return

        # Check category tab clicks
        tab_y = 100
        tab_height = 40
        tab_spacing = 10
        start_x = 50

        for i, category in enumerate(self.categories):
            # Calculate tab dimensions (same as _draw_category_tabs)
            category_display = category.replace("_", " ").title()
            text = FONT.render(category_display, True, COLOR_TEXT)
            tab_width = text.get_width() + 30

            tab_rect = pygame.Rect(
                start_x + i * (tab_width + tab_spacing),
                tab_y,
                tab_width,
                tab_height
            )

            if tab_rect.collidepoint(pos):
                self.category_index = i
                self.scroll_offset = 0
                return

    def update(self, dt: float) -> None:
        """Update the controls viewer."""
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Render the controls viewer."""
        surface.fill(self.bg_color)

        # Title
        title = FONT_BIG.render("CONTROLS", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(LOGICAL_W // 2, 50))
        surface.blit(title, title_rect)

        # Instructions
        if self.waiting_for_key:
            instr = FONT_SMALL.render(
                "Press a key to rebind (Esc to cancel)",
                True, (255, 255, 100)
            )
        else:
            instr = FONT_SMALL.render(
                "Arrow Keys: Navigate | R: Reset to Defaults | Esc: Back",
                True, (180, 180, 220)
            )
        instr_rect = instr.get_rect(center=(LOGICAL_W // 2, LOGICAL_H - 30))
        surface.blit(instr, instr_rect)

        # Category tabs
        self._draw_category_tabs(surface)

        # Controls panel
        self._draw_controls_panel(surface)

        # Back button
        self._draw_back_button(surface)

    def _draw_category_tabs(self, surface: pygame.Surface) -> None:
        """Draw category selection tabs."""
        tab_y = 100
        tab_height = 40
        tab_spacing = 10
        start_x = 50

        for i, category in enumerate(self.categories):
            # Calculate tab dimensions
            category_display = category.replace("_", " ").title()
            text = FONT.render(category_display, True, COLOR_TEXT)
            tab_width = text.get_width() + 30

            tab_rect = pygame.Rect(
                start_x + i * (tab_width + tab_spacing),
                tab_y,
                tab_width,
                tab_height
            )

            # Draw tab background
            color = self.highlight_color if i == self.category_index else self.panel_color
            pygame.draw.rect(surface, color, tab_rect, border_radius=8)

            # Draw tab text
            text_rect = text.get_rect(center=tab_rect.center)
            surface.blit(text, text_rect)

    def _draw_controls_panel(self, surface: pygame.Surface) -> None:
        """Draw the controls list for the selected category."""
        panel_rect = pygame.Rect(50, 160, LOGICAL_W - 100, LOGICAL_H - 220)
        pygame.draw.rect(surface, self.panel_color, panel_rect, border_radius=12)

        # Get actions for current category
        if not self.categories:
            return

        category = self.categories[self.category_index]
        action_ids = self.controls.get_category_actions(category)

        # Draw each action
        y_offset = panel_rect.top + 20
        line_height = 36
        visible_actions = (panel_rect.height - 40) // line_height

        # Calculate max scroll
        self.max_scroll = max(0, len(action_ids) - visible_actions)

        for i, action_id in enumerate(action_ids):
            # Skip if scrolled past
            if i < self.scroll_offset:
                continue
            if i >= self.scroll_offset + visible_actions:
                break

            # Action name
            action_name = self.controls.get_action_display_name(action_id)
            name_text = FONT.render(action_name, True, COLOR_TEXT)

            # Key bindings
            keys_display = self.controls.get_action_keys_display(action_id)
            keys_text = FONT_SMALL.render(keys_display, True, self.key_text_color)

            # Draw action name
            name_x = panel_rect.left + 30
            name_y = y_offset + (i - self.scroll_offset) * line_height
            surface.blit(name_text, (name_x, name_y))

            # Draw key binding box
            key_box_rect = pygame.Rect(
                panel_rect.right - 250,
                name_y - 4,
                220,
                28
            )

            # Highlight if rebinding this action
            box_color = self.highlight_color if action_id == self.rebinding_action else self.key_bg_color
            pygame.draw.rect(surface, box_color, key_box_rect, border_radius=6)

            # Draw keys text
            keys_rect = keys_text.get_rect(center=key_box_rect.center)
            surface.blit(keys_text, keys_rect)

        # Draw scrollbar if needed
        if self.max_scroll > 0:
            self._draw_scrollbar(surface, panel_rect)

    def _draw_scrollbar(self, surface: pygame.Surface, panel_rect: pygame.Rect) -> None:
        """Draw scrollbar for long lists."""
        scrollbar_x = panel_rect.right - 15
        scrollbar_y = panel_rect.top + 10
        scrollbar_height = panel_rect.height - 20
        scrollbar_width = 8

        # Background
        bg_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(surface, (40, 40, 50), bg_rect, border_radius=4)

        # Thumb
        thumb_height = max(20, scrollbar_height * (1.0 / (self.max_scroll + 1)))
        thumb_y = scrollbar_y + (scrollbar_height - thumb_height) * (
            self.scroll_offset / max(1, self.max_scroll)
        )
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(surface, (100, 100, 150), thumb_rect, border_radius=4)

    def _draw_back_button(self, surface: pygame.Surface) -> None:
        """Draw back/exit button."""
        back_rect = pygame.Rect(50, LOGICAL_H - 70, 200, 50)

        # Background with hover effect
        if back_rect.collidepoint(self.mouse_pos):
            color = self.highlight_color
        else:
            color = self.panel_color

        pygame.draw.rect(surface, color, back_rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_TEXT, back_rect, 2, border_radius=5)

        # Label
        label = FONT.render("Back (ESC)", True, COLOR_TEXT)
        label_rect = label.get_rect(center=back_rect.center)
        surface.blit(label, label_rect)
