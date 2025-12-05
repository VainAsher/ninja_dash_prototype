"""
Options State

Player-focused options menu with tabbed categories:
- Gameplay (Difficulty selection and gameplay settings)
- Abilities (Enable/Disable individual abilities for accessibility)

All settings are saved to user preferences and persist between sessions.
Debug/testing options have been moved to the Debug Menu.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any
from ..base import GameState
from gameplay_modifiers import get_modifiers
from settings import DIFFICULTY_CONFIG
from utils import transform_mouse_to_logical


class OptionsState(GameState):
    """Player-focused options menu with gameplay and ability settings."""

    # Tab identifiers
    TAB_AUDIO = "audio"
    TAB_VIDEO = "video"
    TAB_GAMEPLAY = "gameplay"
    TAB_ABILITIES = "abilities"
    TAB_CONTROLS = "controls"

    def __init__(self, game):
        super().__init__(game)
        self.modifiers = get_modifiers()

        # Tab management (expanded with Audio, Video, Controls)
        self.tabs = [
            (self.TAB_AUDIO, "Audio"),
            (self.TAB_VIDEO, "Video"),
            (self.TAB_GAMEPLAY, "Gameplay"),
            (self.TAB_ABILITIES, "Abilities"),
            (self.TAB_CONTROLS, "Controls"),
        ]
        self.current_tab = self.TAB_GAMEPLAY

        # Difficulty management
        self._difficulty_keys = list(DIFFICULTY_CONFIG.keys())

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

    def _cycle_difficulty(self, direction: int) -> None:
        """Cycle through difficulty options."""
        if not self._difficulty_keys:
            return
        cur = self.game.difficulty
        if cur not in self._difficulty_keys:
            self.game.difficulty = self._difficulty_keys[0]
            return
        idx = self._difficulty_keys.index(cur)
        idx = (idx + direction) % len(self._difficulty_keys)
        self.game.difficulty = self._difficulty_keys[idx]

    def _build_option_items(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build the UI items for each tab."""
        return {
            self.TAB_GAMEPLAY: [
                {
                    'type': 'difficulty',
                    'label': 'Difficulty',
                    'description': 'Select game difficulty (affects new runs only)',
                    'getter': lambda: self.game.difficulty,
                    'cycle_left': lambda: self._cycle_difficulty(-1),
                    'cycle_right': lambda: self._cycle_difficulty(1),
                },
                # Level Structure
                {
                    'type': 'slider',
                    'label': 'Level Verticality',
                    'description': 'Horizontal (left) to Vertical (right) level bias',
                    'getter': lambda: self.modifiers.level_verticality,
                    'setter': lambda v: self.modifiers.set_level_verticality(v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                {
                    'type': 'slider',
                    'label': 'Level Branchiness',
                    'description': 'Linear (left) to Branchy/Open (right) level structure',
                    'getter': lambda: self.modifiers.level_branchiness,
                    'setter': lambda v: self.modifiers.set_level_branchiness(v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                {
                    'type': 'slider',
                    'label': 'Platform Density',
                    'description': 'Sparse (left) to Dense (right) platforming',
                    'getter': lambda: self.modifiers.level_platform_density,
                    'setter': lambda v: self.modifiers.set_level_platform_density(v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                # Combat/Challenge
                {
                    'type': 'slider',
                    'label': 'Hazard Density',
                    'description': 'Minimal (left) to Maximum (right) spike hazards',
                    'getter': lambda: self.modifiers.hazard_density,
                    'setter': lambda v: self.modifiers.set_hazard_density(v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                {
                    'type': 'slider',
                    'label': 'Enemy Density',
                    'description': 'Minimal (left) to Maximum (right) enemy spawns',
                    'getter': lambda: self.modifiers.enemy_density,
                    'setter': lambda v: self.modifiers.set_enemy_density(v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                # Level Features
                {
                    'type': 'slider',
                    'label': 'Pillar Frequency',
                    'description': 'None (left) to Many (right) vertical pillars/obstacles',
                    'getter': lambda: self.modifiers.pillar_frequency,
                    'setter': lambda v: self.modifiers.set_pillar_frequency(v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                {
                    'type': 'slider',
                    'label': 'Hole/Gap Frequency',
                    'description': 'None (left) to Many (right) gaps in floors',
                    'getter': lambda: self.modifiers.hole_frequency,
                    'setter': lambda v: self.modifiers.set_hole_frequency(v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                {
                    'type': 'slider',
                    'label': 'Phaseable Walls',
                    'description': 'None (left) to Many (right) walls you can phase through',
                    'getter': lambda: self.modifiers.phaseable_walls,
                    'setter': lambda v: self.modifiers.set_phaseable_walls(v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
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
            self.TAB_AUDIO: [
                {
                    'type': 'slider',
                    'label': 'Master Volume',
                    'description': 'Overall volume for all game sounds',
                    'getter': lambda: getattr(self.game, 'master_volume', 0.8),
                    'setter': lambda v: setattr(self.game, 'master_volume', v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                {
                    'type': 'slider',
                    'label': 'Music Volume',
                    'description': 'Background music volume',
                    'getter': lambda: getattr(self.game, 'music_volume', 0.6),
                    'setter': lambda v: setattr(self.game, 'music_volume', v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                {
                    'type': 'slider',
                    'label': 'SFX Volume',
                    'description': 'Sound effects volume',
                    'getter': lambda: getattr(self.game, 'sfx_volume', 0.8),
                    'setter': lambda v: setattr(self.game, 'sfx_volume', v),
                    'min': 0.0,
                    'max': 1.0,
                    'step': 0.05,
                },
                {
                    'type': 'checkbox',
                    'label': 'Mute All',
                    'description': 'Mute all game audio',
                    'key': 'mute_all',
                    'getter': lambda: getattr(self.game, 'audio_muted', False),
                    'setter': lambda v: setattr(self.game, 'audio_muted', v),
                },
            ],
            self.TAB_VIDEO: [
                {
                    'type': 'checkbox',
                    'label': 'Fullscreen',
                    'description': 'Toggle fullscreen mode (restart may be required)',
                    'key': 'fullscreen',
                    'getter': lambda: getattr(self.game, 'fullscreen', False),
                    'setter': lambda v: setattr(self.game, 'fullscreen', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'VSync',
                    'description': 'Vertical sync to reduce screen tearing',
                    'key': 'vsync',
                    'getter': lambda: getattr(self.game, 'vsync', True),
                    'setter': lambda v: setattr(self.game, 'vsync', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Show FPS',
                    'description': 'Display frames per second counter',
                    'key': 'show_fps',
                    'getter': lambda: getattr(self.game, 'show_fps', False),
                    'setter': lambda v: setattr(self.game, 'show_fps', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Particle Effects',
                    'description': 'Enable/disable particle visual effects',
                    'key': 'particles',
                    'getter': lambda: getattr(self.game, 'particles_enabled', True),
                    'setter': lambda v: setattr(self.game, 'particles_enabled', v),
                },
                {
                    'type': 'checkbox',
                    'label': 'Screen Shake',
                    'description': 'Camera shake on impacts and actions',
                    'key': 'screen_shake',
                    'getter': lambda: getattr(self.game, 'screen_shake_enabled', True),
                    'setter': lambda v: setattr(self.game, 'screen_shake_enabled', v),
                },
                {
                    'type': 'info',
                    'label': 'Colorblind Mode',
                    'description': 'Accessible color schemes (coming soon)',
                },
            ],
            self.TAB_CONTROLS: [
                {
                    'type': 'button',
                    'label': 'Configure Controls',
                    'description': 'Customize key bindings and input settings',
                    'action': lambda: self.game.change_state("controls"),
                },
                {
                    'type': 'button',
                    'label': 'Reset to Defaults',
                    'description': 'Restore default control scheme',
                    'action': lambda: self._reset_controls(),
                },
                {
                    'type': 'info',
                    'label': 'Movement',
                    'description': 'Arrow Keys or WASD',
                },
                {
                    'type': 'info',
                    'label': 'Jump',
                    'description': 'Space, W, or Up Arrow',
                },
                {
                    'type': 'info',
                    'label': 'Abilities',
                    'description': 'Q, E, C, V, Shift - See Controls menu for full list',
                },
            ],
        }

    def _reset_controls(self):
        """Reset controls to default bindings."""
        from controls import get_controls_manager
        controls = get_controls_manager()
        controls.reset_to_defaults()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = transform_mouse_to_logical(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(transform_mouse_to_logical(event.pos))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Save and return to previous state
                self.modifiers.save_preferences()
                # Return to wherever we came from (menu, pause, etc.)
                return_state = self.game.previous_state_name or "menu"
                self.game.change_state(return_state)
            elif event.key == pygame.K_LEFT:
                # Navigate tabs or difficulty depending on current tab
                if self.current_tab == self.TAB_GAMEPLAY:
                    self._cycle_difficulty(-1)
                else:
                    self._navigate_tabs(-1)
            elif event.key == pygame.K_RIGHT:
                # Navigate tabs or difficulty depending on current tab
                if self.current_tab == self.TAB_GAMEPLAY:
                    self._cycle_difficulty(1)
                else:
                    self._navigate_tabs(1)

    def _navigate_tabs(self, direction: int):
        """Navigate between tabs."""
        current_index = next((i for i, (tab_id, _) in enumerate(self.tabs) if tab_id == self.current_tab), 0)
        new_index = (current_index + direction) % len(self.tabs)
        self.current_tab = self.tabs[new_index][0]

    def _handle_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks."""
        # Check back button click
        back_rect = pygame.Rect(50, 650, 200, 50)
        if back_rect.collidepoint(pos):
            self.modifiers.save_preferences()
            return_state = self.game.previous_state_name or "menu"
            self.game.change_state(return_state)
            return

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

                elif item['type'] == 'difficulty':
                    # Check if clicking on left/right arrows
                    # Need to calculate arrow positions same as _draw_difficulty()
                    current_diff = item['getter']()
                    value_text = current_diff.upper()
                    value_surface = self.item_font.render(value_text, True, (255, 220, 180))

                    # Center the value
                    center_x = item_rect.x + item_rect.width // 2
                    value_width = value_surface.get_width()
                    value_left = center_x - value_width // 2
                    value_right = center_x + value_width // 2

                    # Click areas match the hover backgrounds in _draw_difficulty
                    left_arrow_rect = pygame.Rect(value_left - 70, item_rect.y + 3, 60, 24)
                    right_arrow_rect = pygame.Rect(value_right + 10, item_rect.y + 3, 60, 24)

                    if left_arrow_rect.collidepoint(pos):
                        item['cycle_left']()
                        self.modifiers.save_preferences()
                    elif right_arrow_rect.collidepoint(pos):
                        item['cycle_right']()
                        self.modifiers.save_preferences()

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
        title = self.title_font.render("OPTIONS", True, self.text_color)
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
        elif item['type'] == 'difficulty':
            self._draw_difficulty(surface, item, item_rect)

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

    def _draw_difficulty(self, surface: pygame.Surface, item: Dict[str, Any], rect: pygame.Rect):
        """Draw difficulty selector with clickable arrow tiles."""
        # Label
        label = self.item_font.render(item['label'] + ":", True, self.text_color)
        surface.blit(label, (rect.x + 20, rect.y + 8))

        # Current difficulty value
        current_diff = item['getter']()
        diff_config = DIFFICULTY_CONFIG.get(current_diff, {})
        value_text = current_diff.upper()
        value = self.item_font.render(value_text, True, (255, 220, 180))

        # Center the value with arrows
        center_x = rect.x + rect.width // 2
        value_rect = value.get_rect(center=(center_x, rect.y + 15))
        surface.blit(value, value_rect)

        # Calculate clickable zones matching the click handler
        left_arrow_bg_rect = pygame.Rect(value_rect.left - 70, rect.y + 3, 60, 24)
        right_arrow_bg_rect = pygame.Rect(value_rect.right + 10, rect.y + 3, 60, 24)

        # Left arrow tile with hover effect
        left_hover = left_arrow_bg_rect.collidepoint(self.mouse_pos)
        if left_hover:
            pygame.draw.rect(surface, (70, 100, 150), left_arrow_bg_rect, border_radius=8)

        left_arrow = self.item_font.render("◄", True, (255, 255, 255) if left_hover else self.text_color)
        left_arrow_rect = left_arrow.get_rect(midright=(value_rect.left - 30, rect.y + 15))
        surface.blit(left_arrow, left_arrow_rect)

        # Right arrow tile with hover effect
        right_hover = right_arrow_bg_rect.collidepoint(self.mouse_pos)
        if right_hover:
            pygame.draw.rect(surface, (70, 100, 150), right_arrow_bg_rect, border_radius=8)

        right_arrow = self.item_font.render("►", True, (255, 255, 255) if right_hover else self.text_color)
        right_arrow_rect = right_arrow.get_rect(midleft=(value_rect.right + 30, rect.y + 15))
        surface.blit(right_arrow, right_arrow_rect)

        # Description
        if 'description' in item:
            desc = self.desc_font.render(item['description'], True, self.text_dim)
            desc_rect = desc.get_rect(center=(rect.x + rect.width // 2, rect.y + 32))
            surface.blit(desc, desc_rect)

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
