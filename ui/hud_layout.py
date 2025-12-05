"""
Responsive HUD Layout System - Grid-based layout that adapts to screen sizes
"""

import pygame
from typing import Tuple


class HUDLayout:
    """Responsive HUD layout manager using a 12-column grid system."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hud_height = 100
        self.padding = 8

        # 12-column grid (like Bootstrap)
        self.columns = 12
        self.col_width = screen_width / self.columns

        # Responsive breakpoints
        self.is_ultrawide = screen_width >= 2560
        self.is_wide = 1920 <= screen_width < 2560
        self.is_standard = 1280 <= screen_width < 1920
        self.is_small = screen_width < 1280

    def get_section_rect(self, col_start: int, col_span: int, row: int = 0) -> pygame.Rect:
        """
        Get rectangle for a HUD section using grid coordinates.

        Args:
            col_start: Starting column (0-11)
            col_span: Number of columns to span
            row: Row number (0 = top HUD bar, 1+ = below)

        Returns:
            pygame.Rect for the section
        """
        x = int(col_start * self.col_width) + self.padding
        width = int(col_span * self.col_width) - (self.padding * 2)
        y = row * self.hud_height if row > 0 else self.padding
        height = self.hud_height - (self.padding * 2)

        return pygame.Rect(x, y, width, height)

    def get_adaptive_layout(self) -> dict:
        """
        Get adaptive layout configuration based on screen size.

        Returns:
            Dictionary mapping section names to (col_start, col_span, row) tuples
        """
        if self.is_ultrawide:
            # Ultrawide: Spread out sections with more spacing
            return {
                'score': (0, 2, 0),
                'vitals': (2, 3, 0),
                'level': (5, 2, 0),
                'time_abilities': (7, 3, 0),
                'ability_progress': (10, 2, 0)
            }
        elif self.is_wide:
            # Wide (1080p+): Standard layout
            return {
                'score': (0, 2, 0),
                'vitals': (2, 3, 0),
                'level': (5, 2, 0),
                'time_abilities': (7, 3, 0),
                'ability_progress': (10, 2, 0)
            }
        elif self.is_standard:
            # Standard (720p-1080p): Slightly compressed
            return {
                'score': (0, 2, 0),
                'vitals': (2, 3, 0),
                'level': (5, 2, 0),
                'time_abilities': (7, 3, 0),
                'ability_progress': (10, 2, 0)
            }
        else:
            # Small screens: Stack some elements
            return {
                'score': (0, 3, 0),
                'vitals': (3, 4, 0),
                'level': (7, 2, 0),
                'time_abilities': (9, 3, 0),
                'ability_progress': (0, 12, 1)  # Full width, second row
            }

    def get_overlay_position(self, anchor: str, width: int, height: int,
                           offset_x: int = 0, offset_y: int = 0) -> Tuple[int, int]:
        """
        Get position for overlay elements (powerups, ability resources, etc.)

        Args:
            anchor: Anchor point (top_left, top_right, bottom_left, bottom_right, center)
            width: Width of the element
            height: Height of the element
            offset_x: X offset from anchor
            offset_y: Y offset from anchor

        Returns:
            (x, y) tuple for positioning
        """
        margin = 20

        if anchor == "top_left":
            return (margin + offset_x, self.hud_height + margin + offset_y)
        elif anchor == "top_right":
            return (self.screen_width - width - margin + offset_x,
                   self.hud_height + margin + offset_y)
        elif anchor == "bottom_left":
            return (margin + offset_x,
                   self.screen_height - height - margin + offset_y)
        elif anchor == "bottom_right":
            return (self.screen_width - width - margin + offset_x,
                   self.screen_height - height - margin + offset_y)
        elif anchor == "center":
            return (self.screen_width // 2 - width // 2 + offset_x,
                   self.screen_height // 2 - height // 2 + offset_y)
        elif anchor == "top_center":
            return (self.screen_width // 2 - width // 2 + offset_x,
                   self.hud_height + margin + offset_y)
        elif anchor == "bottom_center":
            return (self.screen_width // 2 - width // 2 + offset_x,
                   self.screen_height - height - margin + offset_y)
        else:
            # Default to top-left
            return (margin + offset_x, self.hud_height + margin + offset_y)

    def scale_for_aspect_ratio(self, base_size: int, dimension: str = "width") -> int:
        """
        Scale a size value based on screen aspect ratio.

        Args:
            base_size: Base size at 16:9 aspect ratio
            dimension: "width" or "height"

        Returns:
            Scaled size
        """
        aspect_ratio = self.screen_width / self.screen_height
        standard_aspect = 16 / 9

        if dimension == "width":
            scale_factor = aspect_ratio / standard_aspect
        else:
            scale_factor = standard_aspect / aspect_ratio

        return int(base_size * scale_factor)

    def is_element_visible(self, rect: pygame.Rect) -> bool:
        """Check if an element would be visible on screen."""
        screen_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        return screen_rect.colliderect(rect)

    def clamp_to_screen(self, rect: pygame.Rect, margin: int = 10) -> pygame.Rect:
        """Clamp a rectangle to stay within screen bounds with margin."""
        x = max(margin, min(rect.x, self.screen_width - rect.width - margin))
        y = max(margin, min(rect.y, self.screen_height - rect.height - margin))
        return pygame.Rect(x, y, rect.width, rect.height)
