"""
Mouse utility functions for coordinate transformations.
"""

from typing import Tuple
import pygame
from settings import LOGICAL_W, LOGICAL_H


def transform_mouse_to_logical(window_pos: Tuple[int, int]) -> Tuple[int, int]:
    """Transform window coordinates to logical surface coordinates.

    This is needed because the game uses letterboxing to scale the logical
    surface (1280x720) to fit the actual window size. Mouse coordinates from
    pygame events are in window coordinates, so we need to transform them to
    match the scaled/offset logical surface.

    Args:
        window_pos: Mouse position in window coordinates

    Returns:
        Mouse position in logical surface coordinates
    """
    window = pygame.display.get_surface()
    ww, wh = window.get_size()
    lw, lh = LOGICAL_W, LOGICAL_H

    scale = min(ww / lw, wh / lh)
    tw, th = int(lw * scale), int(lh * scale)
    offset_x = (ww - tw) // 2
    offset_y = (wh - th) // 2

    # Transform mouse position
    mx, my = window_pos
    logical_x = (mx - offset_x) / scale
    logical_y = (my - offset_y) / scale

    return (int(logical_x), int(logical_y))
