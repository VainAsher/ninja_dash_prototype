"""
Ability Chip Component - Hoverable ability indicators with tooltips
"""

import pygame
from settings import FONT_SMALL
from unlocks import ABILITY_INFO


class AbilityChip:
    """Hoverable ability chip with tooltip support."""

    def __init__(self, ability_id: str, x: int, y: int, width: int = 40, height: int = 24):
        self.ability_id = ability_id
        self.rect = pygame.Rect(x, y, width, height)
        self.hover = False
        self.hover_timer = 0.0

        # Get ability info
        info = ABILITY_INFO.get(ability_id, {})
        self.short_name = info.get("short", "??")
        self.full_name = info.get("name", ability_id)
        self.description = info.get("description", "")
        self.color = info.get("color", (150, 150, 150))

    def update(self, dt: float, mouse_pos: tuple):
        """Update hover state and timer."""
        self.hover = self.rect.collidepoint(mouse_pos)

        if self.hover:
            self.hover_timer += dt
        else:
            self.hover_timer = 0.0

    def draw(self, surf: pygame.Surface):
        """Draw the ability chip."""
        # Highlight on hover
        if self.hover:
            # Draw glow effect
            glow_rect = self.rect.inflate(4, 4)
            glow_color = tuple(min(255, c + 40) for c in self.color)
            pygame.draw.rect(surf, glow_color, glow_rect, border_radius=5)

        # Draw chip background
        pygame.draw.rect(surf, self.color, self.rect, border_radius=4)
        pygame.draw.rect(surf, (255, 255, 255), self.rect, 2, border_radius=4)

        # Draw short name
        text = FONT_SMALL.render(self.short_name, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surf.blit(text, text_rect)

        # Draw tooltip after 0.5s hover
        if self.hover and self.hover_timer > 0.5:
            self._draw_tooltip(surf)

    def _draw_tooltip(self, surf: pygame.Surface):
        """Draw tooltip with ability name and description."""
        padding = 10
        line_spacing = 18

        # Prepare tooltip text
        lines = [self.full_name]

        # Wrap description
        if self.description:
            lines.append("")  # Empty line for spacing
            words = self.description.split(' ')
            current_line = []
            max_width = 250

            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surf = FONT_SMALL.render(test_line, True, (255, 255, 255))

                if test_surf.get_width() <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))

        # Calculate tooltip size
        max_text_width = max(FONT_SMALL.render(line, True, (255, 255, 255)).get_width()
                           for line in lines if line)
        tooltip_width = max_text_width + padding * 2
        tooltip_height = len(lines) * line_spacing + padding * 2

        # Position tooltip below chip (or above if not enough space)
        tooltip_x = self.rect.centerx - tooltip_width // 2
        tooltip_y = self.rect.bottom + 8

        # Clamp to screen bounds
        screen_w = surf.get_width()
        screen_h = surf.get_height()
        tooltip_x = max(4, min(tooltip_x, screen_w - tooltip_width - 4))

        # If goes off bottom, show above
        if tooltip_y + tooltip_height > screen_h - 4:
            tooltip_y = self.rect.top - tooltip_height - 8

        # Create tooltip surface
        tooltip_surf = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)

        # Background
        pygame.draw.rect(tooltip_surf, (20, 20, 30, 240), tooltip_surf.get_rect(), border_radius=6)
        pygame.draw.rect(tooltip_surf, (100, 120, 180, 255), tooltip_surf.get_rect(), 2, border_radius=6)

        # Draw text lines
        y_offset = padding
        for i, line in enumerate(lines):
            if not line:  # Skip empty lines
                y_offset += line_spacing // 2
                continue

            # First line (ability name) is brighter
            color = (255, 230, 120) if i == 0 else (220, 220, 240)
            text = FONT_SMALL.render(line, True, color)
            tooltip_surf.blit(text, (padding, y_offset))
            y_offset += line_spacing

        # Blit to main surface
        surf.blit(tooltip_surf, (tooltip_x, tooltip_y))


class AbilityChipGroup:
    """Group of ability chips with layout management."""

    def __init__(self, x: int, y: int, chip_width: int = 36, chip_height: int = 24, gap: int = 4):
        self.x = x
        self.y = y
        self.chip_width = chip_width
        self.chip_height = chip_height
        self.gap = gap
        self.chips = []

    def set_abilities(self, ability_ids: list):
        """Set the abilities to display."""
        self.chips.clear()

        for i, ability_id in enumerate(ability_ids[:6]):  # Max 6 chips
            chip_x = self.x + i * (self.chip_width + self.gap)
            chip = AbilityChip(ability_id, chip_x, self.y, self.chip_width, self.chip_height)
            self.chips.append(chip)

    def update(self, dt: float, mouse_pos: tuple):
        """Update all chips."""
        for chip in self.chips:
            chip.update(dt, mouse_pos)

    def draw(self, surf: pygame.Surface):
        """Draw all chips."""
        for chip in self.chips:
            chip.draw(surf)

    def get_total_width(self) -> int:
        """Get total width of the chip group."""
        if not self.chips:
            return 0
        return len(self.chips) * (self.chip_width + self.gap) - self.gap
