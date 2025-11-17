"""
Tests for physics module - collision detection and player physics
"""

import unittest
import pygame

from physics.player_collider import PlayerCollider
from settings import WORLD_PX_W, WORLD_PX_H, TILE_SIZE


class TestPlayerCollider(unittest.TestCase):
    """Test PlayerCollider class."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.collider = PlayerCollider()
        self.player_rect = pygame.Rect(100, 100, 24, 48)

    def test_boundary_check_left(self):
        """Test left world boundary enforcement."""
        player_rect = pygame.Rect(-10, 100, 24, 48)
        vx, vy = -5.0, 0.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, []
        )

        # Player should be pushed back to left boundary
        self.assertEqual(player_rect.left, 0)
        # Leftward velocity should be stopped
        self.assertGreaterEqual(new_vx, 0)

    def test_boundary_check_right(self):
        """Test right world boundary enforcement."""
        player_rect = pygame.Rect(WORLD_PX_W - 10, 100, 24, 48)
        vx, vy = 20.0, 0.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, []
        )

        # Player should be constrained to right boundary
        self.assertEqual(player_rect.right, WORLD_PX_W)
        # Rightward velocity should be stopped
        self.assertLessEqual(new_vx, 0)

    def test_boundary_check_top(self):
        """Test top world boundary enforcement."""
        player_rect = pygame.Rect(100, -10, 24, 48)
        vx, vy = 0.0, -5.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, []
        )

        # Player should be pushed back to top boundary
        self.assertEqual(player_rect.top, 0)
        # Upward velocity should be stopped
        self.assertGreaterEqual(new_vy, 0)

    def test_boundary_check_bottom(self):
        """Test bottom world boundary enforcement."""
        player_rect = pygame.Rect(100, WORLD_PX_H - 10, 24, 48)
        vx, vy = 0.0, 20.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, []
        )

        # Player should be constrained to bottom boundary
        self.assertEqual(player_rect.bottom, WORLD_PX_H)
        # Downward velocity should be stopped
        self.assertLessEqual(new_vy, 0)

    def test_ground_collision_detection(self):
        """Test ground collision detection."""
        player_rect = pygame.Rect(100, 100, 24, 48)
        floor_tile = pygame.Rect(50, 150, TILE_SIZE, TILE_SIZE)
        vx, vy = 0.0, 10.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, [floor_tile]
        )

        # Player should be on ground
        self.assertTrue(on_ground)
        # Vertical velocity should be zeroed
        self.assertEqual(new_vy, 0.0)
        # Player should be positioned on top of tile
        self.assertEqual(player_rect.bottom, floor_tile.top)

    def test_ceiling_collision_detection(self):
        """Test ceiling collision detection."""
        player_rect = pygame.Rect(100, 100, 24, 48)
        ceiling_tile = pygame.Rect(50, 50, TILE_SIZE, TILE_SIZE)
        vx, vy = 0.0, -10.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, [ceiling_tile]
        )

        # Player should not be on ground
        self.assertFalse(on_ground)
        # Vertical velocity should be zeroed
        self.assertEqual(new_vy, 0.0)
        # Player should be positioned below ceiling
        self.assertEqual(player_rect.top, ceiling_tile.bottom)

    def test_wall_collision_detection_right(self):
        """Test right wall collision detection."""
        player_rect = pygame.Rect(100, 100, 24, 48)
        wall_tile = pygame.Rect(130, 90, TILE_SIZE, TILE_SIZE)
        vx, vy = 10.0, 0.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, [wall_tile]
        )

        # Player should be against wall
        self.assertTrue(on_wall)
        self.assertEqual(wall_dir, 1)
        # Horizontal velocity should be zeroed
        self.assertEqual(new_vx, 0.0)
        # Player should be positioned against wall
        self.assertEqual(player_rect.right, wall_tile.left)

    def test_wall_collision_detection_left(self):
        """Test left wall collision detection."""
        player_rect = pygame.Rect(100, 100, 24, 48)
        wall_tile = pygame.Rect(60, 90, TILE_SIZE, TILE_SIZE)
        vx, vy = -10.0, 0.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, [wall_tile]
        )

        # Player should be against wall
        self.assertTrue(on_wall)
        self.assertEqual(wall_dir, -1)
        # Horizontal velocity should be zeroed
        self.assertEqual(new_vx, 0.0)
        # Player should be positioned against wall
        self.assertEqual(player_rect.left, wall_tile.right)

    def test_no_collision_detection(self):
        """Test movement without collision."""
        player_rect = pygame.Rect(100, 100, 24, 48)
        distant_tile = pygame.Rect(500, 500, TILE_SIZE, TILE_SIZE)
        vx, vy = 5.0, 5.0

        initial_x = player_rect.x
        initial_y = player_rect.y

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, [distant_tile]
        )

        # Player should have moved
        self.assertEqual(player_rect.x, initial_x + int(round(vx)))
        self.assertEqual(player_rect.y, initial_y + int(round(vy)))
        # Velocities unchanged
        self.assertEqual(new_vx, vx)
        self.assertEqual(new_vy, vy)
        # No collision flags
        self.assertFalse(on_ground)
        self.assertFalse(on_wall)

    def test_velocity_calculation_on_collision(self):
        """Test velocity zeroing on collision."""
        player_rect = pygame.Rect(100, 100, 24, 48)
        floor_tile = pygame.Rect(50, 150, TILE_SIZE, TILE_SIZE)
        vx, vy = 3.0, 15.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, [floor_tile]
        )

        # Horizontal velocity should be unchanged
        self.assertEqual(new_vx, vx)
        # Vertical velocity should be zeroed on ground collision
        self.assertEqual(new_vy, 0.0)

    def test_phaseable_walls_smoke_stepping(self):
        """Test phasing through phaseable walls during smoke step."""
        player_rect = pygame.Rect(100, 100, 24, 48)
        phaseable_wall = pygame.Rect(130, 90, TILE_SIZE, TILE_SIZE)
        normal_wall = pygame.Rect(500, 90, TILE_SIZE, TILE_SIZE)
        vx, vy = 10.0, 0.0

        # Without smoke stepping - should collide
        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect.copy(), vx, vy,
            [phaseable_wall, normal_wall],
            phaseable_walls=[phaseable_wall],
            is_smoke_stepping=False
        )
        self.assertTrue(on_wall)  # Should collide

        # With smoke stepping - should phase through
        player_rect2 = pygame.Rect(100, 100, 24, 48)
        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect2, vx, vy,
            [phaseable_wall, normal_wall],
            phaseable_walls=[phaseable_wall],
            is_smoke_stepping=True
        )
        # Should not collide with phaseable wall during smoke step
        self.assertEqual(player_rect2.x, 100 + int(round(vx)))

    def test_can_uncrouch_check_clear(self):
        """Test uncrouch check when space is clear."""
        current_rect = pygame.Rect(100, 100, 24, 24)  # Crouched
        width = 24
        normal_height = 48
        tiles = [pygame.Rect(200, 200, TILE_SIZE, TILE_SIZE)]  # Distant tile

        can_uncrouch = self.collider.check_can_uncrouch(
            current_rect, width, normal_height, tiles
        )

        # Should be able to uncrouch
        self.assertTrue(can_uncrouch)

    def test_can_uncrouch_check_blocked(self):
        """Test uncrouch check when blocked by ceiling."""
        current_rect = pygame.Rect(100, 100, 24, 24)  # Crouched
        width = 24
        normal_height = 48
        # Ceiling tile directly above
        ceiling_tile = pygame.Rect(90, 70, TILE_SIZE, TILE_SIZE)
        tiles = [ceiling_tile]

        can_uncrouch = self.collider.check_can_uncrouch(
            current_rect, width, normal_height, tiles
        )

        # Should NOT be able to uncrouch
        self.assertFalse(can_uncrouch)

    def test_multiple_collision_resolution(self):
        """Test collision resolution with multiple tiles."""
        player_rect = pygame.Rect(100, 100, 24, 48)
        floor_tiles = [
            pygame.Rect(50, 150, TILE_SIZE, TILE_SIZE),
            pygame.Rect(50 + TILE_SIZE, 150, TILE_SIZE, TILE_SIZE),
        ]
        vx, vy = 5.0, 10.0

        new_vx, new_vy, on_ground, on_wall, wall_dir = self.collider.move_and_collide(
            player_rect, vx, vy, floor_tiles
        )

        # Player should be on ground despite multiple tiles
        self.assertTrue(on_ground)
        self.assertEqual(new_vy, 0.0)


if __name__ == '__main__':
    unittest.main()
