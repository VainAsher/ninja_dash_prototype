"""
Menu Transition Effects - Animated transitions between game states
"""

import pygame
import math
from typing import Callable, Optional


class Transition:
    """Base class for state transitions."""

    def __init__(self, duration: float = 0.3):
        self.duration = duration
        self.progress = 0.0
        self.complete = False

    def update(self, dt: float) -> bool:
        """Update transition progress. Returns True when complete."""
        if self.complete:
            return True

        self.progress = min(1.0, self.progress + dt / self.duration)
        if self.progress >= 1.0:
            self.complete = True
        return self.complete

    def get_alpha(self) -> int:
        """Get current alpha value (0-255)."""
        return int(255 * self.progress)

    def reset(self):
        """Reset transition to beginning."""
        self.progress = 0.0
        self.complete = False


class FadeTransition(Transition):
    """Fade in/out transition."""

    def __init__(self, duration: float = 0.3, fade_in: bool = True):
        super().__init__(duration)
        self.fade_in = fade_in

    def get_alpha(self) -> int:
        """Get alpha for fade effect."""
        if self.fade_in:
            return int(255 * self.progress)
        else:
            return int(255 * (1.0 - self.progress))

    def apply(self, surface: pygame.Surface):
        """Apply fade effect to surface."""
        alpha = self.get_alpha()
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255 - alpha if self.fade_in else alpha))
        surface.blit(overlay, (0, 0))


class SlideTransition(Transition):
    """Slide transition from a direction."""

    DIRECTION_LEFT = "left"
    DIRECTION_RIGHT = "right"
    DIRECTION_UP = "up"
    DIRECTION_DOWN = "down"

    def __init__(self, duration: float = 0.3, direction: str = DIRECTION_LEFT):
        super().__init__(duration)
        self.direction = direction

    def get_offset(self, screen_width: int, screen_height: int) -> tuple:
        """Get current offset based on progress and direction."""
        # Easing function (ease-out cubic)
        t = self.progress
        eased = 1 - (1 - t) ** 3

        if self.direction == self.DIRECTION_LEFT:
            return (int(-screen_width * (1 - eased)), 0)
        elif self.direction == self.DIRECTION_RIGHT:
            return (int(screen_width * (1 - eased)), 0)
        elif self.direction == self.DIRECTION_UP:
            return (0, int(-screen_height * (1 - eased)))
        else:  # DOWN
            return (0, int(screen_height * (1 - eased)))

    def apply(self, surface: pygame.Surface, content_surface: pygame.Surface):
        """Apply slide effect."""
        offset = self.get_offset(surface.get_width(), surface.get_height())
        surface.fill((10, 10, 30))  # Background color
        surface.blit(content_surface, offset)


class ScaleTransition(Transition):
    """Scale/zoom transition."""

    def __init__(self, duration: float = 0.3, scale_in: bool = True):
        super().__init__(duration)
        self.scale_in = scale_in

    def get_scale(self) -> float:
        """Get current scale factor."""
        # Easing function (ease-out)
        t = self.progress
        eased = 1 - (1 - t) ** 2

        if self.scale_in:
            return 0.8 + (0.2 * eased)  # Scale from 80% to 100%
        else:
            return 1.0 + (0.2 * eased)  # Scale from 100% to 120%

    def apply(self, surface: pygame.Surface, content_surface: pygame.Surface):
        """Apply scale effect."""
        scale = self.get_scale()
        w, h = content_surface.get_size()
        new_w = int(w * scale)
        new_h = int(h * scale)

        if new_w > 0 and new_h > 0:
            scaled = pygame.transform.scale(content_surface, (new_w, new_h))

            # Center the scaled surface
            x = (w - new_w) // 2
            y = (h - new_h) // 2

            surface.fill((10, 10, 30))  # Background
            surface.blit(scaled, (x, y))

            # Add fade effect
            alpha = int(255 * self.progress if self.scale_in else 255 * (1 - self.progress))
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255 - alpha))
            surface.blit(overlay, (0, 0))


class TransitionManager:
    """Manages transitions between states."""

    def __init__(self):
        self.current_transition: Optional[Transition] = None
        self.transition_callback: Optional[Callable] = None

    def start_transition(self, transition: Transition, on_complete: Optional[Callable] = None):
        """Start a new transition."""
        self.current_transition = transition
        self.transition_callback = on_complete
        transition.reset()

    def update(self, dt: float):
        """Update current transition."""
        if self.current_transition:
            if self.current_transition.update(dt):
                # Transition complete
                if self.transition_callback:
                    self.transition_callback()
                self.current_transition = None
                self.transition_callback = None

    def is_transitioning(self) -> bool:
        """Check if a transition is in progress."""
        return self.current_transition is not None

    def get_current_transition(self) -> Optional[Transition]:
        """Get the current transition."""
        return self.current_transition


# Preset transitions for common use cases
def create_fade_in(duration: float = 0.3) -> FadeTransition:
    """Create a fade-in transition."""
    return FadeTransition(duration, fade_in=True)


def create_fade_out(duration: float = 0.3) -> FadeTransition:
    """Create a fade-out transition."""
    return FadeTransition(duration, fade_in=False)


def create_slide_left(duration: float = 0.3) -> SlideTransition:
    """Create a slide-from-left transition."""
    return SlideTransition(duration, SlideTransition.DIRECTION_LEFT)


def create_slide_right(duration: float = 0.3) -> SlideTransition:
    """Create a slide-from-right transition."""
    return SlideTransition(duration, SlideTransition.DIRECTION_RIGHT)


def create_scale_in(duration: float = 0.3) -> ScaleTransition:
    """Create a scale-in transition."""
    return ScaleTransition(duration, scale_in=True)


def create_scale_out(duration: float = 0.3) -> ScaleTransition:
    """Create a scale-out transition."""
    return ScaleTransition(duration, scale_in=False)
