"""
Options/Settings State

Comprehensive options menu with tabbed categories:
- Gameplay Assists (God Mode, Infinite Resources, etc.)
- Ability Toggles (Enable/Disable individual abilities)
- Visual Options (Debug Overlay, Hitboxes, Grid, FPS)
- Level Options (Reload, Hazards, etc.)

All settings are saved to user preferences and persist between sessions.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any
from ..base import GameState
from gameplay_modifiers import get_modifiers


class OptionsState(GameState):
    """Comprehensive options menu with multiple tabs."""

    # Tab identifiers
    TAB_GAMEPLAY = "gameplay"
    TAB_ABILITIES = "abilities"
    TAB_VISUAL = "visual"
    TAB_LEVEL = "level"

    def __init__(self, game):
        super().__init__(game)
        self.modifiers = get_modifiers()

        # Tab management
        self.tabs = [
            (self.TAB_GAMEPLAY, "Gameplay Assists"),
            (self.TAB_ABILITIES, "Ability Toggles"),
            (self.TAB_VISUAL, "Visual Options"),
            (self.TAB_LEVEL, "Level Options"),
        ]
        self.current_tab = self.TAB_GAMEPLAY

        # UI layout
        self.tab_height = 50
        self.content_y = 120
        self.item_height = 45
        self.checkbox_size = 24
        self.slider_width = 200

        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.SysFont("consolas", 36)
        self.tab_font = pygame.font.SysFont("consolas", 20)
        self.item_font = pygame.font.SysFont("consolas", 18)
        self.desc_font = pygame.font.SysFont("consolas", 14)

        # Colors
        self.bg_color = (15, 15, 25)
        self.tab_bg = (30, 30, 45)
        self.tab_active = (50, 50, 80)
        self.tab_hover = (40, 40, 65)
        self.item_bg = (25, 25, 40)
        self.item_hover = (35, 35, 55)
        self.text_color = (230, 230, 255)
        self.text_dim = (150, 150, 170)
        self.checkbox_bg = (40, 40, 60)
        self.checkbox_checked = (100, 200, 100)
        self.checkbox_unchecked = (200, 100, 100)
        self.slider_bg = (40, 40, 60)
        self.slider_fill = (100, 150, 255)
        self.button_bg = (50, 100, 150)
        self.button_hover = (70, 120, 180)
        self.button_text = (255, 255, 255)

        # Mouse state
        self.mouse_pos = (0, 0)
        self.hovered_item = None

        # Build option items for each tab
        self.option_items = self._build_option_items()

    def _build_option_items(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build the UI items for each tab."""
        return {
            self.TAB_GAMEPLAY: [
                {
                    'type': 'checkbox',
                    'label': 'God Mode',
                    'description': 'Invincibility - take no damage from hazards or enemies',
                    'key': 'god_mode',
                    'getter': lambda: self.modifiers.god_mode,
                    'setter': lambda v: setattr(self.modifiers, 'god_mode', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Infinite Stamina',
                    'description': 'Abilities that use stamina never deplete (Dash, Wall Cling)',
                    'key': 'infinite_stamina',
                    'getter': lambda: self.modifiers.infinite_stamina,
                    'setter': lambda v: setattr(self.modifiers, 'infinite_stamina', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Infinite Charges',
                    'description': 'Abilities that use charges never deplete (Shadow Step, Grapple)',
                    'key': 'infinite_charges',
                    'getter': lambda: self.modifiers.infinite_charges,
                    'setter': lambda v: setattr(self.modifiers, 'infinite_charges', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Flight Mode',
                    'description': 'Disable gravity - fly freely through the level',
                    'key': 'flight_mode',
                    'getter': lambda: self.modifiers.flight_mode,
                    'setter': lambda v: setattr(self.modifiers, 'flight_mode', v),
                },
                {
                    'type': 'slider',
                    'label': 'Time Scale',
                    'description': 'Slow down or speed up game time (0.1x - 2.0x)',
                    'key': 'time_scale',
                    'getter': lambda: self.modifiers.time_scale,
                    'setter': lambda v: self.modifiers.set_time_scale(v),
                    'min': 0.1,
                    'max': 2.0,
                    'step': 0.1,
                },
                {
                    'type': 'button',
                    'label': 'Reset Gameplay Assists',
                    'description': 'Reset all gameplay assists to default values',
                    'action': self._reset_gameplay_assists,
                },
            ],
            self.TAB_ABILITIES: [
                {
                    'type': 'checkbox',
                    'label': 'Double Jump',
                    'description': 'Jump again while in the air',
                    'key': 'double_jump',
                    'getter': lambda: self.modifiers.ability_states.get('double_jump', True),
                    'setter': lambda v: self.modifiers.set_ability_state('double_jump', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Dash',
                    'description': 'Hold Shift for a speed boost',
                    'key': 'dash',
                    'getter': lambda: self.modifiers.ability_states.get('dash', True),
                    'setter': lambda v: self.modifiers.set_ability_state('dash', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Slide',
                    'description': 'Press V to slide along the ground',
                    'key': 'slide',
                    'getter': lambda: self.modifiers.ability_states.get('slide', True),
                    'setter': lambda v: self.modifiers.set_ability_state('slide', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Shadow Step (Smoke Bomb)',
                    'description': 'Press Q to teleport with invincibility',
                    'key': 'shadow_step',
                    'getter': lambda: self.modifiers.ability_states.get('shadow_step', True),
                    'setter': lambda v: self.modifiers.set_ability_state('shadow_step', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Wall Cling',
                    'description': 'Hold toward a wall to cling to it',
                    'key': 'wall_cling',
                    'getter': lambda: self.modifiers.ability_states.get('wall_cling', True),
                    'setter': lambda v: self.modifiers.set_ability_state('wall_cling', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Air Dodge',
                    'description': 'Press C to dodge in any direction while airborne',
                    'key': 'air_dodge',
                    'getter': lambda: self.modifiers.ability_states.get('air_dodge', True),
                    'setter': lambda v: self.modifiers.set_ability_state('air_dodge', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Glide',
                    'description': 'Hold Jump while falling to glide',
                    'key': 'glide',
                    'getter': lambda: self.modifiers.ability_states.get('glide', True),
                    'setter': lambda v: self.modifiers.set_ability_state('glide', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Sword Attack',
                    'description': 'Combat ability (when unlocked)',
                    'key': 'sword_attack',
                    'getter': lambda: self.modifiers.ability_states.get('sword_attack', True),
                    'setter': lambda v: self.modifiers.set_ability_state('sword_attack', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Grapple Hook',
                    'description': 'Advanced movement ability (when unlocked)',
                    'key': 'grapple_hook',
                    'getter': lambda: self.modifiers.ability_states.get('grapple_hook', True),
                    'setter': lambda v: self.modifiers.set_ability_state('grapple_hook', v),
                },
                {
                    'type': 'button',
                    'label': 'Enable All Abilities',
                    'description': 'Turn on all ability toggles',
                    'action': lambda: self.modifiers.reset_all_abilities(),
                },
            ],
            self.TAB_VISUAL: [
                {
                    'type': 'checkbox',
                    'label': 'Debug Overlay (F3)',
                    'description': 'Show real-time ability states, resources, and combos',
                    'key': 'show_debug_overlay',
                    'getter': lambda: self.modifiers.show_debug_overlay,
                    'setter': lambda v: setattr(self.modifiers, 'show_debug_overlay', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Show Hitboxes (F4)',
                    'description': 'Display collision boxes for player, enemies, and objects',
                    'key': 'show_hitboxes',
                    'getter': lambda: self.modifiers.show_hitboxes,
                    'setter': lambda v: setattr(self.modifiers, 'show_hitboxes', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Show Grid',
                    'description': 'Display the level tile grid',
                    'key': 'show_grid',
                    'getter': lambda: self.modifiers.show_grid,
                    'setter': lambda v: setattr(self.modifiers, 'show_grid', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Show FPS Counter',
                    'description': 'Display frames per second in the corner',
                    'key': 'show_fps',
                    'getter': lambda: self.modifiers.show_fps,
                    'setter': lambda v: setattr(self.modifiers, 'show_fps', v),
                },
            ],
            self.TAB_LEVEL: [
                {
                    'type': 'checkbox',
                    'label': 'Disable Hazards',
                    'description': 'Hazards (spikes, pits) no longer damage the player',
                    'key': 'disable_hazards',
                    'getter': lambda: self.modifiers.disable_hazards,
                    'setter': lambda v: setattr(self.modifiers, 'disable_hazards', v),
                },
                {
                    'type': 'button',
                    'label': 'Reload Current Level (F5)',
                    'description': 'Restart the current level from the beginning',
                    'action': self._reload_level,
                },
            ],
        }

    def _reset_gameplay_assists(self):
        """Reset gameplay assists to defaults."""
        self.modifiers.god_mode = False
        self.modifiers.infinite_stamina = False
        self.modifiers.infinite_charges = False
        self.modifiers.flight_mode = False
        self.modifiers.time_scale = 1.0
        self.modifiers.save_preferences()

    def _reload_level(self):
        """Reload the current level."""
        if hasattr(self.game, 'restart_level'):
            self.game.restart_level()
            self.game.change_state("play")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Save and return to previous state
                self.modifiers.save_preferences()
                # Return to wherever we came from (menu, pause, etc.)
                return_state = self.game.previous_state_name or "menu"
                self.game.change_state(return_state)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                # Navigate tabs with arrow keys
                self._navigate_tabs(1 if event.key == pygame.K_RIGHT else -1)

    def _navigate_tabs(self, direction: int):
        """Navigate between tabs."""
        current_index = next((i for i, (tab_id, _) in enumerate(self.tabs) if tab_id == self.current_tab), 0)
        new_index = (current_index + direction) % len(self.tabs)
        self.current_tab = self.tabs[new_index][0]

    def _handle_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks."""
        # Check tab clicks
        tab_y = 60
        tab_width = 1280 // len(self.tabs)
        for i, (tab_id, tab_name) in enumerate(self.tabs):
            tab_rect = pygame.Rect(i * tab_width, tab_y, tab_width, self.tab_height)
            if tab_rect.collidepoint(pos):
                self.current_tab = tab_id
                return

        # Check option item clicks
        items = self.option_items.get(self.current_tab, [])
        for i, item in enumerate(items):
            item_y = self.content_y + i * self.item_height
            item_rect = pygame.Rect(100, item_y, 1080, self.item_height - 5)

            if item_rect.collidepoint(pos):
                if item['type'] == 'checkbox':
                    # Toggle checkbox
                    current = item['getter']()
                    item['setter'](not current)
                    self.modifiers.save_preferences()
                    # Apply to player abilities if in-game
                    self._apply_ability_states()

                elif item['type'] == 'button':
                    # Execute button action
                    item['action']()

                elif item['type'] == 'slider':
                    # Handle slider interaction (drag to adjust)
                    pass  # Will be handled in update for dragging

    def _apply_ability_states(self):
        """Apply ability toggle states to the player."""
        if hasattr(self.game, 'player') and self.game.player:
            player = self.game.player
            for ability_name, enabled in self.modifiers.ability_states.items():
                if ability_name in player.abilities:
                    player.abilities[ability_name].enabled = enabled

    def update(self, dt: float) -> None:
        """Update options menu state."""
        # Handle slider dragging
        if pygame.mouse.get_pressed()[0]:  # Left mouse button held
            self._handle_slider_drag(self.mouse_pos)

    def _handle_slider_drag(self, pos: Tuple[int, int]):
        """Handle slider dragging."""
        items = self.option_items.get(self.current_tab, [])
        for i, item in enumerate(items):
            if item['type'] != 'slider':
                continue

            item_y = self.content_y + i * self.item_height
            slider_x = 500
            slider_rect = pygame.Rect(slider_x, item_y + 10, self.slider_width, 20)

            if slider_rect.collidepoint(pos):
                # Calculate new value based on mouse position
                relative_x = pos[0] - slider_x
                percent = max(0, min(1, relative_x / self.slider_width))
                value_range = item['max'] - item['min']
                new_value = item['min'] + percent * value_range
                # Round to step
                step = item.get('step', 0.1)
                new_value = round(new_value / step) * step
                new_value = max(item['min'], min(item['max'], new_value))

                item['setter'](new_value)
                self.modifiers.save_preferences()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the options menu."""
        # Background
        surface.fill(self.bg_color)

        # Title
        title = self.title_font.render("GAME OPTIONS", True, self.text_color)
        title_rect = title.get_rect(center=(640, 30))
        surface.blit(title, title_rect)

        # Draw tabs
        self._draw_tabs(surface)

        # Draw current tab content
        self._draw_tab_content(surface)

        # Draw back button
        self._draw_back_button(surface)

    def _draw_tabs(self, surface: pygame.Surface):
        """Draw tab navigation."""
        tab_y = 60
        tab_width = 1280 // len(self.tabs)

        for i, (tab_id, tab_name) in enumerate(self.tabs):
            tab_x = i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, self.tab_height)

            # Determine tab color
            if tab_id == self.current_tab:
                color = self.tab_active
            elif tab_rect.collidepoint(self.mouse_pos):
                color = self.tab_hover
            else:
                color = self.tab_bg

            # Draw tab background
            pygame.draw.rect(surface, color, tab_rect)
            pygame.draw.rect(surface, self.text_dim, tab_rect, 2)

            # Draw tab label
            label = self.tab_font.render(tab_name, True, self.text_color)
            label_rect = label.get_rect(center=tab_rect.center)
            surface.blit(label, label_rect)

    def _draw_tab_content(self, surface: pygame.Surface):
        """Draw the content of the current tab."""
        items = self.option_items.get(self.current_tab, [])

        for i, item in enumerate(items):
            item_y = self.content_y + i * self.item_height
            self._draw_option_item(surface, item, item_y)

    def _draw_option_item(self, surface: pygame.Surface, item: Dict[str, Any], y: int):
        """Draw a single option item."""
        item_rect = pygame.Rect(100, y, 1080, self.item_height - 5)

        # Background
        if item_rect.collidepoint(self.mouse_pos):
            pygame.draw.rect(surface, self.item_hover, item_rect, border_radius=5)
        else:
            pygame.draw.rect(surface, self.item_bg, item_rect, border_radius=5)

        # Draw based on type
        if item['type'] == 'checkbox':
            self._draw_checkbox(surface, item, item_rect)
        elif item['type'] == 'slider':
            self._draw_slider(surface, item, item_rect)
        elif item['type'] == 'button':
            self._draw_button(surface, item, item_rect)

    def _draw_checkbox(self, surface: pygame.Surface, item: Dict[str, Any], rect: pygame.Rect):
        """Draw a checkbox option."""
        # Checkbox
        checkbox_rect = pygame.Rect(rect.x + 20, rect.y + 10, self.checkbox_size, self.checkbox_size)
        checked = item['getter']()

        pygame.draw.rect(surface, self.checkbox_bg, checkbox_rect)
        if checked:
            # Draw checkmark
            pygame.draw.rect(surface, self.checkbox_checked, checkbox_rect.inflate(-6, -6))
        pygame.draw.rect(surface, self.text_color, checkbox_rect, 2)

        # Label
        label = self.item_font.render(item['label'], True, self.text_color)
        surface.blit(label, (rect.x + 60, rect.y + 8))

        # Description
        if 'description' in item:
            desc = self.desc_font.render(item['description'], True, self.text_dim)
            surface.blit(desc, (rect.x + 60, rect.y + 28))

    def _draw_slider(self, surface: pygame.Surface, item: Dict[str, Any], rect: pygame.Rect):
        """Draw a slider option."""
        # Label
        current_value = item['getter']()
        label_text = f"{item['label']}: {current_value:.1f}x"
        label = self.item_font.render(label_text, True, self.text_color)
        surface.blit(label, (rect.x + 20, rect.y + 8))

        # Description
        if 'description' in item:
            desc = self.desc_font.render(item['description'], True, self.text_dim)
            surface.blit(desc, (rect.x + 20, rect.y + 28))

        # Slider
        slider_x = 500
        slider_y = rect.y + 10
        slider_rect = pygame.Rect(slider_x, slider_y, self.slider_width, 20)

        # Background
        pygame.draw.rect(surface, self.slider_bg, slider_rect, border_radius=3)

        # Fill (based on value)
        value_percent = (current_value - item['min']) / (item['max'] - item['min'])
        fill_width = int(self.slider_width * value_percent)
        fill_rect = pygame.Rect(slider_x, slider_y, fill_width, 20)
        pygame.draw.rect(surface, self.slider_fill, fill_rect, border_radius=3)

        # Border
        pygame.draw.rect(surface, self.text_color, slider_rect, 2, border_radius=3)

        # Value markers
        for val in [item['min'], (item['min'] + item['max']) / 2, item['max']]:
            marker_x = slider_x + int((val - item['min']) / (item['max'] - item['min']) * self.slider_width)
            marker_text = self.desc_font.render(f"{val:.1f}", True, self.text_dim)
            marker_rect = marker_text.get_rect(center=(marker_x, slider_y + 35))
            surface.blit(marker_text, marker_rect)

    def _draw_button(self, surface: pygame.Surface, item: Dict[str, Any], rect: pygame.Rect):
        """Draw a button option."""
        button_rect = pygame.Rect(rect.x + 20, rect.y + 5, 300, 30)

        # Background
        if button_rect.collidepoint(self.mouse_pos):
            color = self.button_hover
        else:
            color = self.button_bg

        pygame.draw.rect(surface, color, button_rect, border_radius=5)
        pygame.draw.rect(surface, self.text_color, button_rect, 2, border_radius=5)

        # Label
        label = self.item_font.render(item['label'], True, self.button_text)
        label_rect = label.get_rect(center=button_rect.center)
        surface.blit(label, label_rect)

        # Description
        if 'description' in item:
            desc = self.desc_font.render(item['description'], True, self.text_dim)
            surface.blit(desc, (rect.x + 340, rect.y + 12))

    def _draw_back_button(self, surface: pygame.Surface):
        """Draw back/exit button."""
        back_rect = pygame.Rect(50, 650, 200, 50)

        # Background
        if back_rect.collidepoint(self.mouse_pos):
            color = self.button_hover
        else:
            color = self.button_bg

        pygame.draw.rect(surface, color, back_rect, border_radius=5)
        pygame.draw.rect(surface, self.text_color, back_rect, 2, border_radius=5)

        # Label
        label = self.tab_font.render("Back (ESC)", True, self.button_text)
        label_rect = label.get_rect(center=back_rect.center)
        surface.blit(label, label_rect)
