"""
Loading Screen - Animated loading screen for level generation
"""

import pygame
import math
from settings import LOGICAL_W, LOGICAL_H, FONT_BIG, FONT, COLOR_TEXT


class LoadingScreen:
    """Animated loading screen shown during level generation."""

    def __init__(self, message="Loading..."):
        self.message = message
        self.spinner_angle = 0
        self.progress = 0.0  # 0.0 to 1.0
        self.show_progress = False
        self.elapsed_time = 0

    def set_message(self, message: str):
        """Update the loading message."""
        self.message = message

    def set_progress(self, progress: float):
        """Set progress (0.0 to 1.0) and enable progress bar."""
        self.progress = max(0.0, min(1.0, progress))
        self.show_progress = True

    def update(self, dt: float):
        """Update animation state."""
        self.elapsed_time += dt
        # Rotate spinner (360 degrees per second)
        self.spinner_angle = (self.spinner_angle + dt * 360) % 360

    def draw(self, surface: pygame.Surface):
        """Draw the loading screen."""
        # Fill background
        surface.fill((10, 10, 20))

        # Draw title
        title = FONT_BIG.render(self.message, True, (200, 200, 220))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, LOGICAL_H // 2 - 60))
        surface.blit(title, title_rect)

        # Draw animated spinner
        self._draw_spinner(surface, LOGICAL_W // 2, LOGICAL_H // 2)

        # Draw progress bar if enabled
        if self.show_progress:
            self._draw_progress_bar(surface)

        # Draw subtle hint text
        hint = FONT.render("Please wait...", True, (120, 120, 140))
        hint_rect = hint.get_rect(center=(LOGICAL_W // 2, LOGICAL_H // 2 + 80))
        surface.blit(hint, hint_rect)

    def _draw_spinner(self, surface: pygame.Surface, center_x: int, center_y: int):
        """Draw rotating spinner animation."""
        radius = 30
        thickness = 5
        arc_length = 270  # Degrees of arc to show

        # Convert angle to radians
        start_angle = math.radians(self.spinner_angle)
        end_angle = math.radians(self.spinner_angle + arc_length)

        # Draw arc as a circle segment
        # Create rect for arc
        rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Draw arc using pygame.draw.arc
        pygame.draw.arc(
            surface,
            (100, 200, 255),
            rect,
            start_angle,
            end_angle,
            thickness
        )

        # Draw dots around the spinner for more visual interest
        num_dots = 8
        for i in range(num_dots):
            dot_angle = math.radians(i * (360 / num_dots) + self.spinner_angle)
            dot_x = center_x + int(math.cos(dot_angle) * (radius + 15))
            dot_y = center_y + int(math.sin(dot_angle) * (radius + 15))

            # Fade dots based on position
            fade = (i + (self.spinner_angle / 45)) % num_dots / num_dots
            alpha = int(100 + 155 * fade)
            color = (alpha, alpha, min(255, alpha + 55))

            pygame.draw.circle(surface, color, (dot_x, dot_y), 3)

    def _draw_progress_bar(self, surface: pygame.Surface):
        """Draw progress bar."""
        bar_width = 400
        bar_height = 20
        bar_x = (LOGICAL_W - bar_width) // 2
        bar_y = LOGICAL_H // 2 + 40

        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=10)

        # Filled portion
        fill_width = int(bar_width * self.progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(surface, (100, 200, 255), fill_rect, border_radius=10)

        # Border
        pygame.draw.rect(surface, (100, 120, 180), bg_rect, 2, border_radius=10)

        # Percentage text
        percent_text = FONT.render(f"{int(self.progress * 100)}%", True, COLOR_TEXT)
        percent_rect = percent_text.get_rect(center=(LOGICAL_W // 2, bar_y + bar_height + 20))
        surface.blit(percent_text, percent_rect)


# Convenience function for showing loading screen
def show_loading_screen(surface: pygame.Surface, message: str = "Loading...", progress: float = None):
    """Quick function to show a loading screen frame."""
    loading = LoadingScreen(message)
    if progress is not None:
        loading.set_progress(progress)
    loading.update(0.016)  # ~60fps frame
    loading.draw(surface)
    pygame.display.flip()
