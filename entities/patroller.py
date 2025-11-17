"""
Patroller Enemy - Basic walking enemy with edge and wall detection

Provides:
- Basic patrol behavior (walk back and forth)
- Edge detection (turn at platform edges)
- Wall detection (turn at walls)
- Configurable loot drops
"""

from __future__ import annotations

import pygame
from typing import Any, Optional, Dict
from settings import TILE_SIZE

from .enemy import Enemy


class Patroller(Enemy):
    """
    Basic patrolling enemy that walks back and forth.

    Turns around when hitting walls or platform edges.
    """

    # Default loot table for Patrollers
    DEFAULT_LOOT = {
        "coins": (1, 5),        # Drop 1-5 coins
        "health": 0.2,          # 20% chance to drop health
        "powerup": 0.05,        # 5% chance to drop powerup
        "ability_orb": 0.02,    # 2% chance to drop ability orb
    }

    def __init__(
        self,
        x: float,
        y: float,
        hp: int = 3,
        damage: int = 1,
        speed: float = 60.0,  # Pixels per second
        points: int = 100,
        loot_table: Optional[Dict] = None
    ):
        """
        Initialize patroller enemy.

        Args:
            x: Initial x position
            y: Initial y position
            hp: Health points (default: 3)
            damage: Contact damage (default: 1)
            speed: Movement speed in pixels/second (default: 60)
            points: Points awarded on death (default: 100)
            loot_table: Custom loot configuration (default: DEFAULT_LOOT)
        """
        # Use default loot table if none provided
        if loot_table is None:
            loot_table = self.DEFAULT_LOOT.copy()

        super().__init__(x, y, hp, damage, speed, points, loot_table)

        # Patroller-specific state
        self.direction = 1  # 1 = right, -1 = left
        self.facing = 1
        self.patrol_speed = speed

        # Edge detection parameters
        # Check from the edge of the enemy rect, not center
        # Enemy is TILE_SIZE wide, so check at least TILE_SIZE ahead to detect edges
        # before the enemy's leading edge reaches them
        self.edge_check_distance = TILE_SIZE
        self.wall_check_distance = 4

        # Start in patrol state
        self.change_state("patrol")

    def _update_idle(self, dt: float, world: Any, player: Any) -> None:
        """
        Patroller doesn't idle - immediately transitions to patrol.

        Args:
            dt: Delta time
            world: Level data
            player: Player entity
        """
        self.change_state("patrol")

    def _update_patrol(self, dt: float, world: Any, player: Any) -> None:
        """
        Update patrol behavior with edge and wall detection.

        Args:
            dt: Delta time
            world: Level data
            player: Player entity
        """
        # Move in current direction
        self.vx = self.patrol_speed * self.direction
        self.facing = self.direction

        # Check for walls ahead
        if self._check_wall_ahead(world):
            self._turn_around()

        # Check for platform edge ahead
        # Always check for edges, not just when on_ground
        # This prevents walking off edges even if on_ground state is unreliable
        if self._check_edge_ahead(world):
            self._turn_around()

        # Optional: Chase player if nearby
        if player and self._should_chase_player(player):
            self.change_state("chase")

    def _update_chase(self, dt: float, world: Any, player: Any) -> None:
        """
        Chase player with increased speed.

        Args:
            dt: Delta time
            world: Level data
            player: Player entity
        """
        if not player:
            self.change_state("patrol")
            return

        # Check if player is still in chase range
        if not self._should_chase_player(player):
            self.change_state("patrol")
            return

        # Move towards player (faster than patrol)
        if player.rect.centerx > self.rect.centerx:
            self.vx = self.patrol_speed * 1.5
            self.direction = 1
            self.facing = 1
        else:
            self.vx = -self.patrol_speed * 1.5
            self.direction = -1
            self.facing = -1

        # Still respect walls and edges during chase
        if self._check_wall_ahead(world):
            self.vx = 0

        # Always check for edges during chase, not just when on_ground
        if self._check_edge_ahead(world):
            self.vx = 0

    def _check_wall_ahead(self, world: Any) -> bool:
        """
        Check if there's a wall ahead in the current direction.

        Args:
            world: Level tile data

        Returns:
            bool: True if wall detected ahead
        """
        if not world:
            return False

        # Check position ahead based on direction
        check_x = self.rect.centerx + (self.direction * (self.rect.width // 2 + self.wall_check_distance))
        check_y = self.rect.centery

        # Convert to tile coordinates
        tile_x = int(check_x // TILE_SIZE)
        tile_y = int(check_y // TILE_SIZE)

        # Bounds check
        if tile_y < 0 or tile_y >= len(world):
            return True  # Treat out of bounds as wall
        if tile_x < 0 or tile_x >= len(world[0]):
            return True

        # Check if tile is solid
        return world[tile_y][tile_x] == 1

    def _check_edge_ahead(self, world: Any) -> bool:
        """
        Check if there's a platform edge ahead (no ground below).

        Args:
            world: Level tile data

        Returns:
            bool: True if edge detected ahead
        """
        if not world:
            return False

        # Check position ahead and below based on direction
        check_x = self.rect.centerx + (self.direction * self.edge_check_distance)
        check_y = self.rect.bottom + 4  # Check slightly below current position

        # Convert to tile coordinates
        tile_x = int(check_x // TILE_SIZE)
        tile_y = int(check_y // TILE_SIZE)

        # Bounds check
        if tile_y < 0 or tile_y >= len(world):
            return True  # Treat out of bounds as edge
        if tile_x < 0 or tile_x >= len(world[0]):
            return True

        # Check if there's no ground below (empty tile)
        # An edge is detected if the tile below is empty (0)
        return world[tile_y][tile_x] == 0

    def _should_chase_player(self, player: Any) -> bool:
        """
        Determine if player is close enough to chase.

        Args:
            player: Player entity

        Returns:
            bool: True if should chase player
        """
        if not player or not hasattr(player, 'rect'):
            return False

        # Calculate distance to player
        dx = abs(player.rect.centerx - self.rect.centerx)
        dy = abs(player.rect.centery - self.rect.centery)

        # Chase if player is within range (horizontally and not too far vertically)
        chase_range_x = TILE_SIZE * 5  # 5 tiles horizontal range
        chase_range_y = TILE_SIZE * 3  # 3 tiles vertical range

        # Reduce detection range when player is crouched (stealth benefit)
        if hasattr(player, 'crouching') and player.crouching:
            chase_range_x *= 0.5  # 50% reduced horizontal detection
            chase_range_y *= 0.5  # 50% reduced vertical detection

        return dx < chase_range_x and dy < chase_range_y

    def _turn_around(self) -> None:
        """
        Turn the patroller around to face the opposite direction.
        """
        self.direction *= -1
        self.facing = self.direction
        self.vx = self.patrol_speed * self.direction

    def draw(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)) -> None:
        """
        Draw patroller with distinctive appearance.

        Args:
            screen: Pygame surface
            camera_offset: (x, y) camera offset
        """
        # Call parent draw for basic rendering
        super().draw(screen, camera_offset)

        # Add patrol-specific visual elements
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]

        # Draw eyes to show it's looking in the direction it's moving
        if not self.is_dead:
            eye_color = (255, 255, 255)
            eye_size = 3

            # Left eye
            left_eye_x = screen_x + self.rect.width // 3
            left_eye_y = screen_y + self.rect.height // 3

            # Right eye
            right_eye_x = screen_x + 2 * self.rect.width // 3
            right_eye_y = screen_y + self.rect.height // 3

            # Offset eyes based on facing direction
            eye_offset = 2 if self.facing == 1 else -2

            pygame.draw.circle(
                screen,
                eye_color,
                (int(left_eye_x + eye_offset), int(left_eye_y)),
                eye_size
            )
            pygame.draw.circle(
                screen,
                eye_color,
                (int(right_eye_x + eye_offset), int(right_eye_y)),
                eye_size
            )
