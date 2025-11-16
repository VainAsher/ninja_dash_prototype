"""
Player Collision Detection Module

Handles all collision detection and resolution for the player character,
including tile collisions, wall detection, and world boundary enforcement.
"""

import pygame
from settings import WORLD_PX_W, WORLD_PX_H, MAX_RUN_SPEED


class PlayerCollider:
    """
    Handles collision detection and resolution for the player.

    This class is responsible for:
    - Detecting collisions with tiles
    - Resolving collision responses (position correction, velocity zeroing)
    - Tracking wall/ground contact states
    - Enforcing world boundaries
    """

    def __init__(self):
        """Initialize the collider."""
        pass

    def move_and_collide(self, player_rect, vx, vy, tiles,
                        phaseable_walls=None, is_smoke_stepping=False,
                        is_sliding=False):
        """
        Move player and resolve collisions with tiles.

        Args:
            player_rect: Player's pygame.Rect
            vx: Horizontal velocity
            vy: Vertical velocity
            tiles: List of tile rectangles for collision
            phaseable_walls: Optional list of walls that can be phased through
            is_smoke_stepping: Whether player is currently smoke stepping
            is_sliding: Whether player is currently sliding

        Returns:
            tuple: (new_vx, new_vy, on_ground, on_wall, wall_dir)
        """
        if phaseable_walls is None:
            phaseable_walls = []

        # During smoke step, ignore phaseable walls (doors only)
        collision_tiles = tiles
        if is_smoke_stepping:
            # Can phase through phaseable walls (doors/walls, not floors)
            collision_tiles = [t for t in tiles if t not in phaseable_walls]

        # Cap slide speed to prevent glitching through collisions
        if is_sliding:
            max_slide_speed = MAX_RUN_SPEED * 1.5
            if abs(vx) > max_slide_speed:
                vx = max_slide_speed * (1 if vx > 0 else -1)

        # Horizontal movement and collision
        player_rect.x += int(round(vx))
        on_wall = False
        wall_dir = 0

        for t in collision_tiles:
            if player_rect.colliderect(t):
                if vx > 0:
                    player_rect.right = t.left
                    on_wall = True
                    wall_dir = 1
                elif vx < 0:
                    player_rect.left = t.right
                    on_wall = True
                    wall_dir = -1
                vx = 0.0

        # Vertical movement and collision
        player_rect.y += int(round(vy))
        on_ground = False

        for t in collision_tiles:
            if player_rect.colliderect(t):
                if vy > 0:
                    player_rect.bottom = t.top
                    vy = 0.0
                    on_ground = True
                elif vy < 0:
                    player_rect.top = t.bottom
                    vy = 0.0

        # World border checks - push player back into viewable area
        if player_rect.left < 0:
            player_rect.left = 0
            vx = max(0, vx)  # Stop leftward movement
        elif player_rect.right > WORLD_PX_W:
            player_rect.right = WORLD_PX_W
            vx = min(0, vx)  # Stop rightward movement

        if player_rect.top < 0:
            player_rect.top = 0
            vy = max(0, vy)  # Stop upward movement
        elif player_rect.bottom > WORLD_PX_H:
            player_rect.bottom = WORLD_PX_H
            vy = min(0, vy)  # Stop downward movement

        return vx, vy, on_ground, on_wall, wall_dir

    def check_can_uncrouch(self, current_rect, width, normal_height, tiles):
        """
        Check if player can exit crouch without hitting ceiling.

        Args:
            current_rect: Current player rect (crouched)
            width: Player width
            normal_height: Player's normal standing height
            tiles: List of tile rectangles

        Returns:
            bool: True if player can safely uncrouch
        """
        crouch_height = current_rect.height
        diff = normal_height - crouch_height
        test_rect = pygame.Rect(
            current_rect.x,
            current_rect.y - diff,
            width,
            normal_height
        )

        return not any(test_rect.colliderect(t) for t in tiles)
