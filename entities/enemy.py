"""
Enemy Base Class - AI-driven enemy entities

Provides:
- Base enemy class with health, damage, and movement
- AI state machine (idle, patrol, chase, attack, dead)
- Collision detection with player
- Damage dealing to player on contact
- Integration with combat system
"""

from __future__ import annotations

import pygame
import math
from typing import Any, Optional, Tuple, Dict
from settings import TILE_SIZE, GRAVITY


class Enemy:
    """
    Base enemy class with AI state machine.

    All enemies should extend this class and implement their specific behaviors.
    """

    def __init__(
        self,
        x: float,
        y: float,
        hp: int,
        damage: int,
        speed: float,
        points: int = 10,
        loot_table: Optional[Dict] = None
    ):
        """
        Initialize enemy.

        Args:
            x: Initial x position
            y: Initial y position
            hp: Maximum health points
            damage: Damage dealt to player on contact
            speed: Movement speed (pixels/second)
            points: Points awarded on death
            loot_table: Loot drop configuration (optional)
        """
        # Physical properties
        self.rect = pygame.Rect(int(x), int(y), TILE_SIZE, TILE_SIZE)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        # Combat stats
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.points = points
        self.loot_table = loot_table or {}

        # Movement
        self.speed = speed
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1  # 1 = right, -1 = left

        # Physics state
        self.on_ground = False
        self.gravity = GRAVITY

        # AI state machine
        self.state = "idle"  # idle, patrol, chase, attack, dead
        self.state_timer = 0.0

        # Invincibility (for damage cooldown)
        self.inv_timer = 0.0
        self.inv_duration = 0.5  # Half second between damage

        # Death state
        self.is_dead = False
        self.death_timer = 0.0
        self.death_duration = 0.5  # How long death animation lasts

        # Contact damage cooldown (per player)
        self.contact_damage_cooldown = {}
        self.contact_damage_interval = 1.0  # 1 second between contact damage

    def update(self, dt: float, world: Any, player: Any, game: Any = None) -> None:
        """
        Update enemy AI and physics.

        Args:
            dt: Delta time since last frame
            world: Level tile data (2D list)
            player: Player entity
            game: Game instance (for damage numbers, etc.)
        """
        # Update invincibility timer
        if self.inv_timer > 0:
            self.inv_timer -= dt

        # Handle death state
        if self.is_dead:
            self.death_timer += dt
            if self.death_timer >= self.death_duration:
                # Enemy can be removed by manager
                pass
            return

        # Update state timer
        self.state_timer += dt

        # AI state machine
        if self.state == "idle":
            self._update_idle(dt, world, player)
        elif self.state == "patrol":
            self._update_patrol(dt, world, player)
        elif self.state == "chase":
            self._update_chase(dt, world, player)
        elif self.state == "attack":
            self._update_attack(dt, world, player)

        # Apply physics
        self._apply_physics(dt, world)

        # Check collision with player (contact damage)
        if player and not self.is_dead:
            self._check_player_collision(player, game)

    def _update_idle(self, dt: float, world: Any, player: Any) -> None:
        """
        Update idle state - override in subclasses.

        Args:
            dt: Delta time
            world: Level data
            player: Player entity
        """
        # Default: transition to patrol after 1 second
        if self.state_timer > 1.0:
            self.change_state("patrol")

    def _update_patrol(self, dt: float, world: Any, player: Any) -> None:
        """
        Update patrol state - override in subclasses.

        Args:
            dt: Delta time
            world: Level data
            player: Player entity
        """
        # Default: basic left-right movement
        self.vx = self.speed * self.facing

    def _update_chase(self, dt: float, world: Any, player: Any) -> None:
        """
        Update chase state - override in subclasses.

        Args:
            dt: Delta time
            world: Level data
            player: Player entity
        """
        # Default: move towards player horizontally
        if player:
            if player.rect.centerx > self.rect.centerx:
                self.vx = self.speed * 1.5  # Chase faster than patrol
                self.facing = 1
            else:
                self.vx = -self.speed * 1.5
                self.facing = -1

    def _update_attack(self, dt: float, world: Any, player: Any) -> None:
        """
        Update attack state - override in subclasses.

        Args:
            dt: Delta time
            world: Level data
            player: Player entity
        """
        # Default: stay in place for attack animation
        self.vx = 0

        # Return to chase after 0.5 seconds
        if self.state_timer > 0.5:
            self.change_state("chase")

    def _apply_physics(self, dt: float, world: Any) -> None:
        """
        Apply gravity and collision detection.

        Args:
            dt: Delta time
            world: Level tile data
        """
        # Apply gravity
        if not self.on_ground:
            self.vy += self.gravity * dt

        # Cap fall speed
        max_fall = 600
        if self.vy > max_fall:
            self.vy = max_fall

        # Apply velocity
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)

        # Basic collision detection with world
        if world:
            self._collide_with_world(world)

    def _collide_with_world(self, world: Any) -> None:
        """
        Basic tile collision detection.

        Args:
            world: Level tile data (2D list)
        """
        # Reset ground state - will be set True if we find ground below
        self.on_ground = False

        # Get tiles near enemy
        tile_x = self.rect.x // TILE_SIZE
        tile_y = self.rect.y // TILE_SIZE

        # Check surrounding tiles
        for dy in range(-1, 3):
            for dx in range(-1, 3):
                check_x = tile_x + dx
                check_y = tile_y + dy

                # Bounds check
                if check_y < 0 or check_y >= len(world):
                    continue
                if check_x < 0 or check_x >= len(world[0]):
                    continue

                # Check if solid tile
                tile = world[check_y][check_x]
                if tile == 1:  # Solid tile
                    tile_rect = pygame.Rect(
                        check_x * TILE_SIZE,
                        check_y * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )

                    if self.rect.colliderect(tile_rect):
                        # Resolve collision
                        self._resolve_tile_collision(tile_rect)

        # After collision resolution, check if there's solid ground immediately below
        # This provides a more reliable on_ground state
        self._check_ground_below(world)

    def _check_ground_below(self, world: Any) -> None:
        """
        Check if there's solid ground immediately below the enemy.
        Provides a more reliable on_ground state than relying solely on collision resolution.

        Args:
            world: Level tile data (2D list)
        """
        if not world:
            return

        # Check a few pixels below the bottom of the enemy rect
        check_y = self.rect.bottom + 2  # Check 2 pixels below feet

        # Check at left edge, center, and right edge of enemy
        check_points = [
            self.rect.left + 4,      # Left edge (with small margin)
            self.rect.centerx,        # Center
            self.rect.right - 4       # Right edge (with small margin)
        ]

        for check_x in check_points:
            tile_x = int(check_x // TILE_SIZE)
            tile_y = int(check_y // TILE_SIZE)

            # Bounds check
            if tile_y < 0 or tile_y >= len(world):
                continue
            if tile_x < 0 or tile_x >= len(world[0]):
                continue

            # If any check point has solid ground below, enemy is on ground
            if world[tile_y][tile_x] == 1:
                self.on_ground = True
                return

    def _resolve_tile_collision(self, tile_rect: pygame.Rect) -> None:
        """
        Resolve collision with a tile.

        Args:
            tile_rect: Rectangle of the colliding tile
        """
        # Calculate overlap
        overlap_left = self.rect.right - tile_rect.left
        overlap_right = tile_rect.right - self.rect.left
        overlap_top = self.rect.bottom - tile_rect.top
        overlap_bottom = tile_rect.bottom - self.rect.top

        # Find minimum overlap
        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        # Resolve based on minimum overlap
        if min_overlap == overlap_top and self.vy > 0:
            # Collision from above
            self.rect.bottom = tile_rect.top
            self.vy = 0
            # on_ground will be set by _check_ground_below()
        elif min_overlap == overlap_bottom and self.vy < 0:
            # Collision from below
            self.rect.top = tile_rect.bottom
            self.vy = 0
        elif min_overlap == overlap_left and self.vx > 0:
            # Collision from left
            self.rect.right = tile_rect.left
            self.vx = 0
        elif min_overlap == overlap_right and self.vx < 0:
            # Collision from right
            self.rect.left = tile_rect.right
            self.vx = 0

    def _check_player_collision(self, player: Any, game: Any = None) -> None:
        """
        Check collision with player and deal contact damage with knockback.

        Args:
            player: Player entity
            game: Game instance (for damage numbers)
        """
        if not player or not hasattr(player, 'rect'):
            return

        # Check collision
        if self.rect.colliderect(player.rect):
            # Check contact damage cooldown
            player_id = id(player)
            current_time = pygame.time.get_ticks() / 1000.0

            if player_id not in self.contact_damage_cooldown:
                self.contact_damage_cooldown[player_id] = 0

            if current_time - self.contact_damage_cooldown[player_id] >= self.contact_damage_interval:
                # Deal contact damage with knockback using combat system
                if hasattr(player, 'take_damage'):
                    # Import combat system for knockback
                    from core.combat_system import deal_damage

                    # Get damage numbers manager if available
                    damage_numbers = getattr(game, 'damage_numbers', None)

                    # Deal damage with knockback (200 force for enemy contact)
                    damage_dealt = deal_damage(
                        self,
                        player,
                        self.damage,
                        knockback_force=200,
                        damage_numbers=damage_numbers
                    )

                    if damage_dealt:
                        # Update cooldown
                        self.contact_damage_cooldown[player_id] = current_time

    def take_damage(self, amount: int) -> bool:
        """
        Take damage from an attack.

        Args:
            amount: Damage amount

        Returns:
            bool: True if damage was dealt, False if invulnerable
        """
        # Check invincibility
        if self.inv_timer > 0 or self.is_dead:
            return False

        # Apply damage
        self.hp -= amount
        self.inv_timer = self.inv_duration

        # Check death
        if self.hp <= 0:
            self.hp = 0
            self.die()

        return True

    def die(self) -> None:
        """
        Handle enemy death.

        Marks enemy as dead and prepares for loot spawning.
        Override to customize death behavior.
        """
        if self.is_dead:
            return

        self.is_dead = True
        self.state = "dead"
        self.death_timer = 0.0

        # Loot spawning will be handled by enemy manager

    def change_state(self, new_state: str) -> None:
        """
        Change AI state.

        Args:
            new_state: New state name
        """
        if self.state != new_state:
            self.state = new_state
            self.state_timer = 0.0

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        Draw enemy to screen.

        Args:
            screen: Pygame surface
            camera_offset: (x, y) camera offset
        """
        # Calculate screen position
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]

        # Choose color based on state
        if self.is_dead:
            color = (50, 50, 50)  # Gray for dead
        elif self.inv_timer > 0:
            color = (255, 200, 200)  # Light red when hit
        elif self.state == "chase":
            color = (255, 100, 100)  # Red when chasing
        elif self.state == "attack":
            color = (200, 0, 0)  # Dark red when attacking
        else:
            color = (150, 50, 50)  # Default red-brown

        # Draw enemy rectangle
        pygame.draw.rect(
            screen,
            color,
            (screen_x, screen_y, self.rect.width, self.rect.height)
        )

        # Draw health bar
        if not self.is_dead and self.hp < self.max_hp:
            self._draw_health_bar(screen, (screen_x, screen_y))

        # Draw facing direction indicator
        if not self.is_dead:
            # Draw a small triangle to show facing
            if self.facing == 1:
                # Right facing
                points = [
                    (screen_x + self.rect.width - 5, screen_y + 5),
                    (screen_x + self.rect.width - 5, screen_y + 15),
                    (screen_x + self.rect.width - 2, screen_y + 10)
                ]
            else:
                # Left facing
                points = [
                    (screen_x + 5, screen_y + 5),
                    (screen_x + 5, screen_y + 15),
                    (screen_x + 2, screen_y + 10)
                ]
            pygame.draw.polygon(screen, (255, 255, 255), points)

    def _draw_health_bar(self, screen: pygame.Surface, pos: Tuple[int, int]) -> None:
        """
        Draw health bar above enemy.

        Args:
            screen: Pygame surface
            pos: (x, y) screen position
        """
        bar_width = self.rect.width
        bar_height = 4
        bar_x = pos[0]
        bar_y = pos[1] - 8

        # Background (red)
        pygame.draw.rect(
            screen,
            (100, 0, 0),
            (bar_x, bar_y, bar_width, bar_height)
        )

        # Health (green)
        health_width = int(bar_width * (self.hp / self.max_hp))
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (bar_x, bar_y, health_width, bar_height)
        )

        # Border
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (bar_x, bar_y, bar_width, bar_height),
            1
        )

    def can_be_removed(self) -> bool:
        """
        Check if enemy can be removed from game.

        Returns:
            bool: True if enemy should be removed
        """
        return self.is_dead and self.death_timer >= self.death_duration
