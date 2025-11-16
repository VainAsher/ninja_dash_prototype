"""
Shared data structures for level generation.
Contains unified room and cell definitions used across generation modules.
"""

from dataclasses import dataclass


@dataclass
class Room:
    """
    Represents a room in the level generation system.

    A room has four directional connections (up, down, left, right) that indicate
    which adjacent rooms are accessible. Optionally stores room coordinates.

    Attributes:
        rx: Room x-coordinate in the grid (defaults to 0)
        ry: Room y-coordinate in the grid (defaults to 0)
        open_up: Whether this room connects to the room above
        open_down: Whether this room connects to the room below
        open_left: Whether this room connects to the room to the left
        open_right: Whether this room connects to the room to the right
    """
    rx: int = 0
    ry: int = 0
    open_up: bool = False
    open_down: bool = False
    open_left: bool = False
    open_right: bool = False
