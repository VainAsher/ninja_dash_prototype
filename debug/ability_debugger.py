"""
Enhanced Debug Visualization for Abilities

Provides visual overlays and real-time state information for debugging
and development of the ability system.
"""

import pygame
from typing import Dict, Any, Optional, List, Tuple


class AbilityDebugger:
    """
    Visual debugger for ability system.

    Displays real-time information about:
    - Active abilities and their states
    - Cooldowns and timers
    - Resource levels (stamina, charges)
    - Combo system status
    - Powerup effects
    """

    def __init__(self, font: Optional[pygame.font.Font] = None,
                 small_font: Optional[pygame.font.Font] = None):
        """
        Initialize the ability debugger.

        Args:
            font: Main font for text (optional)
            small_font: Small font for details (optional)
        """
        pygame.font.init()
        self.font = font or pygame.font.SysFont("consolas", 16)
        self.small_font = small_font or pygame.font.SysFont("consolas", 12)

        # Visual settings
        self.enabled = False
        self.panel_width = 300
        self.panel_x = 10
        self.panel_y = 100
        self.line_height = 20
        self.small_line_height = 16

        # Colors
        self.bg_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)
        self.active_color = (100, 255, 100)
        self.cooldown_color = (255, 100, 100)
        self.resource_color = (100, 200, 255)
        self.combo_color = (255, 200, 50)
        self.bar_bg_color = (50, 50, 50)
        self.bar_fill_color = (100, 200, 255)

    def toggle(self):
        """Toggle debug display on/off."""
        self.enabled = not self.enabled

    def render(self, surface: pygame.Surface, player: Any):
        """
        Render debug overlay on the screen.

        Args:
            surface: Pygame surface to draw on
            player: Player instance to debug
        """
        if not self.enabled:
            return

        y_offset = self.panel_y

        # Draw semi-transparent background panel
        panel_height = 500
        bg_surface = pygame.Surface((self.panel_width, panel_height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        surface.blit(bg_surface, (self.panel_x, y_offset))

        # Title
        y_offset += 10
        self._draw_text(surface, "=== ABILITY DEBUG ===", self.panel_x + 10, y_offset, self.text_color)
        y_offset += self.line_height + 5

        # Player state
        y_offset = self._draw_player_state(surface, player, y_offset)
        y_offset += 5

        # Active abilities
        y_offset = self._draw_active_abilities(surface, player, y_offset)
        y_offset += 5

        # Ability details
        y_offset = self._draw_ability_details(surface, player, y_offset)
        y_offset += 5

        # Combo status
        if hasattr(player, 'combo_tracker'):
            y_offset = self._draw_combo_status(surface, player, y_offset)
            y_offset += 5

        # Powerup status
        y_offset = self._draw_powerup_status(surface, player, y_offset)

    def _draw_player_state(self, surface: pygame.Surface, player: Any, y: int) -> int:
        """Draw basic player state information."""
        self._draw_text(surface, "Player State:", self.panel_x + 10, y, self.text_color)
        y += self.line_height

        state_info = [
            f"  Ground: {player.on_ground}",
            f"  Wall: {player.on_wall} (dir: {player.wall_dir})",
            f"  Velocity: ({player.vx:.1f}, {player.vy:.1f})",
            f"  Facing: {player.facing}",
        ]

        for info in state_info:
            self._draw_text(surface, info, self.panel_x + 10, y, self.resource_color, self.small_font)
            y += self.small_line_height

        return y

    def _draw_active_abilities(self, surface: pygame.Surface, player: Any, y: int) -> int:
        """Draw currently active abilities."""
        self._draw_text(surface, "Active Abilities:", self.panel_x + 10, y, self.text_color)
        y += self.line_height

        active_states = {
            'Dashing': player.is_dashing,
            'Smoke Step': player.is_smoke_stepping,
            'Sliding': player.is_sliding,
            'Air Dodge': player.is_air_dodging,
            'Gliding': player.is_gliding,
            'Wall Cling': player.is_wall_clinging,
            'Attacking': player.is_attacking,
            'Blocking': player.is_blocking,
        }

        has_active = False
        for name, is_active in active_states.items():
            if is_active:
                self._draw_text(surface, f"  • {name}", self.panel_x + 10, y, self.active_color, self.small_font)
                y += self.small_line_height
                has_active = True

        if not has_active:
            self._draw_text(surface, "  (none)", self.panel_x + 10, y, self.cooldown_color, self.small_font)
            y += self.small_line_height

        return y

    def _draw_ability_details(self, surface: pygame.Surface, player: Any, y: int) -> int:
        """Draw detailed ability information with bars."""
        self._draw_text(surface, "Ability Resources:", self.panel_x + 10, y, self.text_color)
        y += self.line_height

        # Dash stamina
        dash = player.abilities.get('dash')
        if dash:
            stamina_pct = dash.resource / dash.max_resource
            y = self._draw_resource_bar(
                surface,
                "Dash Stamina",
                stamina_pct,
                self.panel_x + 10,
                y,
                dash.is_active
            )

        # Shadow Step charges
        shadow_step = player.abilities.get('shadow_step')
        if shadow_step:
            charges_pct = shadow_step.resource / shadow_step.max_resource
            y = self._draw_resource_bar(
                surface,
                f"Shadow Step ({int(shadow_step.resource)}/{int(shadow_step.max_resource)})",
                charges_pct,
                self.panel_x + 10,
                y,
                shadow_step.is_active
            )
            if shadow_step.cooldown_timer > 0:
                self._draw_text(
                    surface,
                    f"    Cooldown: {shadow_step.cooldown_timer:.1f}s",
                    self.panel_x + 15,
                    y,
                    self.cooldown_color,
                    self.small_font
                )
                y += self.small_line_height

        # Wall Cling stamina
        wall_cling = player.abilities.get('wall_cling')
        if wall_cling:
            stamina_pct = wall_cling.resource / wall_cling.max_resource
            y = self._draw_resource_bar(
                surface,
                "Wall Cling",
                stamina_pct,
                self.panel_x + 10,
                y,
                wall_cling.is_active
            )

        # Air Dodge uses
        air_dodge = player.abilities.get('air_dodge')
        if air_dodge:
            uses_pct = air_dodge.uses_left / air_dodge.max_uses
            y = self._draw_resource_bar(
                surface,
                f"Air Dodge ({air_dodge.uses_left}/{air_dodge.max_uses})",
                uses_pct,
                self.panel_x + 10,
                y,
                air_dodge.is_dodging if hasattr(air_dodge, 'is_dodging') else False
            )

        # Double Jump
        double_jump = player.abilities.get('double_jump')
        if double_jump:
            jumps_pct = double_jump.jumps_left / double_jump.max_jumps
            y = self._draw_resource_bar(
                surface,
                f"Jumps ({double_jump.jumps_left}/{double_jump.max_jumps})",
                jumps_pct,
                self.panel_x + 10,
                y,
                False
            )

        return y

    def _draw_combo_status(self, surface: pygame.Surface, player: Any, y: int) -> int:
        """Draw combo system status."""
        self._draw_text(surface, "Combo Status:", self.panel_x + 10, y, self.text_color)
        y += self.line_height

        combo_tracker = player.combo_tracker
        if combo_tracker.is_combo_active():
            combo_name = combo_tracker.get_combo_name()
            effects = combo_tracker.get_active_effects()
            time_left = effects.get('time_remaining', 0)

            self._draw_text(
                surface,
                f"  {combo_name}",
                self.panel_x + 10,
                y,
                self.combo_color
            )
            y += self.line_height

            # Combo timer bar
            timer_pct = time_left / effects.get('duration', 1.0)
            y = self._draw_resource_bar(
                surface,
                f"Time: {time_left:.1f}s",
                timer_pct,
                self.panel_x + 15,
                y,
                True,
                self.combo_color
            )
        else:
            self._draw_text(
                surface,
                "  (no active combo)",
                self.panel_x + 10,
                y,
                self.cooldown_color,
                self.small_font
            )
            y += self.small_line_height

        # Show last combo
        if combo_tracker.last_combo_name:
            self._draw_text(
                surface,
                f"  Last: {combo_tracker.last_combo_name}",
                self.panel_x + 10,
                y,
                (150, 150, 150),
                self.small_font
            )
            y += self.small_line_height

        return y

    def _draw_powerup_status(self, surface: pygame.Surface, player: Any, y: int) -> int:
        """Draw active powerup status."""
        self._draw_text(surface, "Powerups:", self.panel_x + 10, y, self.text_color)
        y += self.line_height

        has_powerup = False

        # Speed Boost
        if player.speed_boost_timer > 0:
            y = self._draw_powerup_bar(
                surface,
                "Speed Boost",
                player.speed_boost_timer,
                8.0,  # Default duration
                self.panel_x + 10,
                y,
                (255, 200, 50)
            )
            has_powerup = True

        # Triple Jump
        if player.triple_jump_timer > 0:
            y = self._draw_powerup_bar(
                surface,
                "Triple Jump",
                player.triple_jump_timer,
                10.0,
                self.panel_x + 10,
                y,
                (100, 255, 200)
            )
            has_powerup = True

        # Extra Jump
        if player.extra_jump_uses > 0:
            self._draw_text(
                surface,
                f"  Extra Jumps: {player.extra_jump_uses}",
                self.panel_x + 10,
                y,
                (150, 255, 150),
                self.small_font
            )
            y += self.small_line_height
            has_powerup = True

        # Coin Magnet
        if player.magnet_timer > 0:
            y = self._draw_powerup_bar(
                surface,
                f"Magnet (r:{player.magnet_radius:.0f})",
                player.magnet_timer,
                12.0,
                self.panel_x + 10,
                y,
                (255, 215, 0)
            )
            has_powerup = True

        if not has_powerup:
            self._draw_text(
                surface,
                "  (none active)",
                self.panel_x + 10,
                y,
                self.cooldown_color,
                self.small_font
            )
            y += self.small_line_height

        return y

    def _draw_resource_bar(self, surface: pygame.Surface, label: str, percent: float,
                          x: int, y: int, is_active: bool,
                          custom_color: Optional[Tuple[int, int, int]] = None) -> int:
        """Draw a resource bar with label."""
        # Label
        color = self.active_color if is_active else self.text_color
        self._draw_text(surface, f"  {label}", x, y, color, self.small_font)
        y += self.small_line_height

        # Bar
        bar_width = self.panel_width - 40
        bar_height = 8
        bar_x = x + 5

        # Background
        pygame.draw.rect(surface, self.bar_bg_color, (bar_x, y, bar_width, bar_height))

        # Fill
        fill_width = int(bar_width * max(0, min(1, percent)))
        fill_color = custom_color or self.bar_fill_color
        if fill_width > 0:
            pygame.draw.rect(surface, fill_color, (bar_x, y, fill_width, bar_height))

        # Border
        pygame.draw.rect(surface, self.text_color, (bar_x, y, bar_width, bar_height), 1)

        y += bar_height + 3
        return y

    def _draw_powerup_bar(self, surface: pygame.Surface, label: str,
                         time_left: float, max_time: float,
                         x: int, y: int, color: Tuple[int, int, int]) -> int:
        """Draw a powerup timer bar."""
        percent = time_left / max_time
        self._draw_text(surface, f"  {label}: {time_left:.1f}s", x, y, color, self.small_font)
        y += self.small_line_height

        bar_width = self.panel_width - 40
        bar_height = 6
        bar_x = x + 5

        pygame.draw.rect(surface, self.bar_bg_color, (bar_x, y, bar_width, bar_height))
        fill_width = int(bar_width * max(0, min(1, percent)))
        if fill_width > 0:
            pygame.draw.rect(surface, color, (bar_x, y, fill_width, bar_height))
        pygame.draw.rect(surface, self.text_color, (bar_x, y, bar_width, bar_height), 1)

        y += bar_height + 3
        return y

    def _draw_text(self, surface: pygame.Surface, text: str, x: int, y: int,
                  color: Tuple[int, int, int], font: Optional[pygame.font.Font] = None):
        """Helper to draw text."""
        font = font or self.font
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def render_minimal_hud(self, surface: pygame.Surface, player: Any, x: int, y: int):
        """
        Render a minimal HUD showing just active combos and critical info.

        Args:
            surface: Surface to draw on
            player: Player instance
            x: X position
            y: Y position
        """
        if hasattr(player, 'combo_tracker') and player.combo_tracker.is_combo_active():
            combo_name = player.combo_tracker.get_combo_name()
            effects = player.combo_tracker.get_active_effects()

            # Draw combo notification
            combo_text = f"COMBO: {combo_name}"
            text_surface = self.font.render(combo_text, True, self.combo_color)

            # Add background
            padding = 8
            bg_rect = text_surface.get_rect()
            bg_rect.inflate_ip(padding * 2, padding * 2)
            bg_rect.topleft = (x - padding, y - padding)

            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))
            surface.blit(bg_surface, bg_rect.topleft)

            # Draw text
            surface.blit(text_surface, (x, y))
