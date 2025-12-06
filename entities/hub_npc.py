"""
Hub NPC - Friendly NPCs for campaign hubs

Provides:
- Patrol behavior (walk back and forth like enemies)
- No attacking or chasing
- Interaction system for dialogue/shop
- Visual indicator for NPC type
"""

from __future__ import annotations

import pygame
import random
from typing import Any, Optional, Dict, List, Tuple

from settings import TILE_SIZE, FONT_SMALL


class HubNPC:
    """
    Friendly NPC that patrols around the hub world.

    Unlike enemies, HubNPCs:
    - Never attack or chase the player
    - Can be interacted with for dialogue or shopping
    - Have distinct visual appearances based on role
    """

    # NPC roles and their visual colors
    NPC_ROLES = {
        "guide": (100, 200, 150),      # Green - helpful guides
        "trainer": (255, 150, 50),      # Orange - combat trainers
        "lore": (200, 150, 255),        # Purple - lore keepers
        "shop": (255, 215, 0),          # Gold - merchants
        "story": (100, 150, 255),       # Blue - story NPCs
        "wanderer": (180, 180, 180),    # Gray - ambient NPCs
    }

    def __init__(
        self,
        x: float,
        y: float,
        name: str = "Villager",
        role: str = "wanderer",
        dialogue: Optional[List[str]] = None,
        is_shop: bool = False,
        patrol_range: int = 100,  # How far to patrol from spawn point
        speed: float = 40.0,
    ):
        """
        Initialize a hub NPC.

        Args:
            x: Initial x position
            y: Initial y position
            name: NPC's display name
            role: NPC role (guide, trainer, lore, shop, story, wanderer)
            dialogue: List of dialogue lines
            is_shop: Whether this NPC opens a shop on interaction
            patrol_range: Distance to patrol from spawn point
            speed: Movement speed in pixels/second
        """
        # Position and physics
        self.spawn_x = x
        self.spawn_y = y
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE * 1.5)
        self.vx = 0.0
        self.vy = 0.0

        # Identity
        self.name = name
        self.role = role
        self.color = self.NPC_ROLES.get(role, (180, 180, 180))
        self.dialogue = dialogue or [f"{name}: Hello, traveler."]
        self.is_shop = is_shop

        # Patrol behavior
        self.patrol_range = patrol_range
        self.patrol_speed = speed
        self.direction = 1  # 1 = right, -1 = left
        self.facing = 1

        # State
        self.state = "idle"  # idle, patrol, talking
        self.state_timer = 0.0
        self.idle_duration = random.uniform(1.0, 3.0)  # Random idle time
        self.on_ground = False

        # Interaction
        self.interaction_range = 80
        self.is_unlocked = True  # Can be gated by campaign progress

        # Gravity (for proper placement on platforms)
        self.gravity = 1200.0
        self.max_fall_speed = 600.0

    def can_interact(self, player_pos: Tuple[int, int]) -> bool:
        """Check if player is close enough to interact."""
        if not self.is_unlocked:
            return False
        px, py = player_pos
        dx = px - self.rect.centerx
        dy = py - self.rect.centery
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < self.interaction_range

    def update(self, dt: float, tiles: Any) -> None:
        """
        Update NPC state and movement.

        Args:
            dt: Delta time in seconds
            tiles: List of tile rectangles for collision
        """
        self.state_timer += dt

        if self.state == "idle":
            self._update_idle(dt)
        elif self.state == "patrol":
            self._update_patrol(dt, tiles)
        elif self.state == "talking":
            # Don't move while talking
            self.vx = 0

        # Apply physics
        self._apply_physics(dt, tiles)

    def _update_idle(self, dt: float) -> None:
        """Idle behavior - stand still for a while, then start patrolling."""
        self.vx = 0

        if self.state_timer >= self.idle_duration:
            # Start patrolling
            self.state = "patrol"
            self.state_timer = 0.0
            # Randomly choose direction
            self.direction = random.choice([-1, 1])
            self.facing = self.direction

    def _update_patrol(self, dt: float, tiles: Any) -> None:
        """Patrol behavior - walk back and forth within patrol range."""
        # Move in current direction
        self.vx = self.patrol_speed * self.direction
        self.facing = self.direction

        # Check if we've reached patrol limits
        if abs(self.rect.centerx - self.spawn_x) > self.patrol_range:
            # Turn around
            self.direction *= -1
            self.facing = self.direction
            self.vx = self.patrol_speed * self.direction

        # Check for walls ahead
        if self._check_wall_ahead(tiles):
            self._turn_around()

        # Check for platform edges
        if self.on_ground and self._check_edge_ahead(tiles):
            self._turn_around()

        # Random chance to stop and idle
        if random.random() < 0.003:  # ~0.3% chance per frame
            self.state = "idle"
            self.state_timer = 0.0
            self.idle_duration = random.uniform(1.5, 4.0)

    def _check_wall_ahead(self, tiles: Any) -> bool:
        """Check if there's a wall ahead in current direction."""
        if not tiles:
            return False

        # Create a small rect in front of the NPC
        check_rect = pygame.Rect(
            self.rect.centerx + (self.direction * (self.rect.width // 2 + 2)),
            self.rect.centery - 5,
            4, 10
        )

        for tile in tiles:
            if check_rect.colliderect(tile):
                return True
        return False

    def _check_edge_ahead(self, tiles: Any) -> bool:
        """Check if there's a platform edge ahead."""
        if not tiles:
            return False

        # Check if there's ground ahead at foot level
        check_rect = pygame.Rect(
            self.rect.centerx + (self.direction * (self.rect.width // 2 + TILE_SIZE // 2)),
            self.rect.bottom + 2,
            4, 4
        )

        for tile in tiles:
            if check_rect.colliderect(tile):
                return False  # Ground ahead, no edge
        return True  # No ground ahead, there's an edge

    def _turn_around(self) -> None:
        """Turn the NPC around."""
        self.direction *= -1
        self.facing = self.direction
        self.vx = self.patrol_speed * self.direction

    def _apply_physics(self, dt: float, tiles: Any) -> None:
        """Apply gravity and collision."""
        # Apply gravity
        self.vy += self.gravity * dt
        if self.vy > self.max_fall_speed:
            self.vy = self.max_fall_speed

        # Move horizontally
        self.rect.x += int(self.vx * dt)

        # Check horizontal collisions
        if tiles:
            self._resolve_horizontal_collision(tiles)

        # Move vertically
        self.rect.y += int(self.vy * dt)

        # Check vertical collisions
        if tiles:
            self._resolve_vertical_collision(tiles)

    def _resolve_horizontal_collision(self, tiles: Any) -> None:
        """Resolve horizontal collisions with tiles."""
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vx > 0:
                    self.rect.right = tile.left
                elif self.vx < 0:
                    self.rect.left = tile.right
                self.vx = 0

    def _resolve_vertical_collision(self, tiles: Any) -> None:
        """Resolve vertical collisions with tiles."""
        self.on_ground = False

        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                self.vy = 0

    def start_talking(self) -> None:
        """Enter talking state (stops movement)."""
        self.state = "talking"
        self.vx = 0
        self.state_timer = 0.0

    def stop_talking(self) -> None:
        """Exit talking state and return to idle."""
        self.state = "idle"
        self.state_timer = 0.0
        self.idle_duration = random.uniform(1.0, 2.0)

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0),
             show_prompt: bool = False) -> None:
        """
        Draw the NPC.

        Args:
            surface: Surface to draw on
            camera_offset: (cam_x, cam_y) for camera-relative drawing
            show_prompt: Whether to show interaction prompt
        """
        cam_x, cam_y = camera_offset
        screen_x = self.rect.x - cam_x
        screen_y = self.rect.y - cam_y

        # Draw NPC body with role color
        pygame.draw.rect(
            surface,
            self.color,
            (screen_x, screen_y, self.rect.width, self.rect.height),
            border_radius=4
        )

        # Draw outline
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (screen_x, screen_y, self.rect.width, self.rect.height),
            2,
            border_radius=4
        )

        # Draw eyes to show facing direction
        eye_color = (255, 255, 255)
        eye_size = 3
        eye_y = screen_y + 8

        if self.facing == 1:
            # Looking right
            left_eye_x = screen_x + self.rect.width // 3 + 2
            right_eye_x = screen_x + 2 * self.rect.width // 3 + 2
        else:
            # Looking left
            left_eye_x = screen_x + self.rect.width // 3 - 2
            right_eye_x = screen_x + 2 * self.rect.width // 3 - 2

        pygame.draw.circle(surface, eye_color, (int(left_eye_x), int(eye_y)), eye_size)
        pygame.draw.circle(surface, eye_color, (int(right_eye_x), int(eye_y)), eye_size)

        # Draw role indicator icon
        icon_y = screen_y - 12
        icon_x = screen_x + self.rect.width // 2

        if self.is_shop:
            # Shop icon (gold coin)
            pygame.draw.circle(surface, (255, 215, 0), (int(icon_x), int(icon_y)), 6)
            pygame.draw.circle(surface, (255, 255, 255), (int(icon_x), int(icon_y)), 6, 1)
        elif self.role == "story":
            # Story icon (exclamation mark)
            pygame.draw.rect(surface, (255, 200, 50),
                           (icon_x - 2, icon_y - 8, 4, 10))
            pygame.draw.circle(surface, (255, 200, 50), (int(icon_x), int(icon_y + 4)), 2)

        # Draw name label
        label = FONT_SMALL.render(self.name, True, (255, 255, 255))
        label_rect = label.get_rect(centerx=screen_x + self.rect.width // 2,
                                    bottom=screen_y - 15)
        surface.blit(label, label_rect)

        # Draw interaction prompt if close
        if show_prompt:
            if self.is_shop:
                prompt_text = "[E] Shop"
                prompt_color = (255, 215, 0)  # Gold
            else:
                prompt_text = "[E] Talk"
                prompt_color = (255, 255, 0)  # Yellow

            prompt = FONT_SMALL.render(prompt_text, True, prompt_color)
            prompt_rect = prompt.get_rect(
                centerx=screen_x + self.rect.width // 2,
                top=screen_y + self.rect.height + 5
            )
            surface.blit(prompt, prompt_rect)


class HubNPCManager:
    """Manages all NPCs in a hub world."""

    def __init__(self):
        self.npcs: List[HubNPC] = []

    def add_npc(self, npc: HubNPC) -> None:
        """Add an NPC to the manager."""
        self.npcs.append(npc)

    def clear(self) -> None:
        """Remove all NPCs."""
        self.npcs.clear()

    def spawn_npc(
        self,
        x: float,
        y: float,
        name: str = "Villager",
        role: str = "wanderer",
        dialogue: Optional[List[str]] = None,
        is_shop: bool = False,
        patrol_range: int = 100,
        speed: float = 40.0,
    ) -> HubNPC:
        """Create and add an NPC."""
        npc = HubNPC(
            x=x, y=y, name=name, role=role,
            dialogue=dialogue, is_shop=is_shop,
            patrol_range=patrol_range, speed=speed
        )
        self.npcs.append(npc)
        return npc

    def update(self, dt: float, tiles: Any) -> None:
        """Update all NPCs."""
        for npc in self.npcs:
            npc.update(dt, tiles)

    def get_interactable_npc(self, player_pos: Tuple[int, int]) -> Optional[HubNPC]:
        """Get the closest NPC that can be interacted with."""
        for npc in self.npcs:
            if npc.can_interact(player_pos):
                return npc
        return None

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int],
             player_pos: Tuple[int, int]) -> None:
        """Draw all NPCs."""
        for npc in self.npcs:
            can_interact = npc.can_interact(player_pos)
            npc.draw(surface, camera_offset, show_prompt=can_interact)
