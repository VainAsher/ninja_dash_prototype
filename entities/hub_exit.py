"""
Hub Exit Points - Mission entry gates for campaign hubs

Provides:
- Multiple exit points per hub for different missions
- Active/inactive/completed states
- Visual indicators for mission availability
- Mission objectives and rewards
"""

from __future__ import annotations

import pygame
from dataclasses import dataclass, field
from typing import Any, Optional, List, Tuple, Dict
from enum import Enum

from settings import TILE_SIZE, FONT_SMALL, FONT


class ExitState(Enum):
    """State of a hub exit point."""
    LOCKED = "locked"        # Not yet available (future mission)
    AVAILABLE = "available"  # Can be entered
    ACTIVE = "active"        # Currently selected mission
    COMPLETED = "completed"  # Mission completed, exit closed


@dataclass
class MissionObjective:
    """A single objective within a mission."""
    objective_type: str  # "coins", "kills", "collectibles", "survive"
    target_amount: int
    current_amount: int = 0
    description: str = ""

    @property
    def is_complete(self) -> bool:
        return self.current_amount >= self.target_amount

    @property
    def progress_text(self) -> str:
        return f"{self.current_amount}/{self.target_amount}"


@dataclass
class MissionReward:
    """Rewards for completing a mission."""
    currency: int = 0           # Fragments for shop
    xp: int = 0                 # Experience points
    ability_orbs: int = 0       # Rare ability orbs
    scroll_fragments: int = 0   # For unlocking abilities


@dataclass
class Mission:
    """A mission that can be started from a hub exit."""
    mission_id: str
    name: str
    description: str
    objectives: List[MissionObjective] = field(default_factory=list)
    rewards: MissionReward = field(default_factory=MissionReward)
    difficulty: str = "normal"  # easy, normal, hard, boss
    act: int = 0
    mission_index: int = 0

    @property
    def is_complete(self) -> bool:
        return all(obj.is_complete for obj in self.objectives)

    def reset_progress(self) -> None:
        """Reset all objective progress."""
        for obj in self.objectives:
            obj.current_amount = 0

    def update_objective(self, objective_type: str, amount: int = 1) -> None:
        """Update progress on an objective type."""
        for obj in self.objectives:
            if obj.objective_type == objective_type:
                obj.current_amount = min(obj.current_amount + amount, obj.target_amount)


class HubExit:
    """
    An exit point in a hub world that leads to a mission.

    Exit points can be:
    - Locked: Future mission, not yet available
    - Available: Can be entered to start the mission
    - Completed: Mission done, exit closed (grayed out)
    """

    # Visual colors for different states
    STATE_COLORS = {
        ExitState.LOCKED: (60, 60, 80),       # Dark gray
        ExitState.AVAILABLE: (100, 200, 255), # Cyan
        ExitState.ACTIVE: (255, 220, 100),    # Gold
        ExitState.COMPLETED: (80, 150, 80),   # Green (dimmed)
    }

    GLOW_COLORS = {
        ExitState.LOCKED: (40, 40, 60),
        ExitState.AVAILABLE: (50, 100, 150),
        ExitState.ACTIVE: (150, 130, 50),
        ExitState.COMPLETED: (40, 80, 40),
    }

    def __init__(
        self,
        x: float,
        y: float,
        mission: Mission,
        width: int = TILE_SIZE * 2,
        height: int = TILE_SIZE * 3,
    ):
        """
        Initialize a hub exit.

        Args:
            x: X position
            y: Y position
            mission: The mission this exit leads to
            width: Exit gate width
            height: Exit gate height
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.mission = mission
        self.state = ExitState.LOCKED
        self.interaction_range = 100

        # Animation
        self.pulse_time = 0.0
        self.pulse_speed = 2.0

    def set_state(self, state: ExitState) -> None:
        """Change the exit's state."""
        self.state = state

    def can_interact(self, player_pos: Tuple[int, int]) -> bool:
        """Check if player is close enough to interact."""
        if self.state not in (ExitState.AVAILABLE, ExitState.ACTIVE):
            return False
        px, py = player_pos
        dx = px - self.rect.centerx
        dy = py - self.rect.centery
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < self.interaction_range

    def update(self, dt: float) -> None:
        """Update animation state."""
        if self.state == ExitState.AVAILABLE or self.state == ExitState.ACTIVE:
            self.pulse_time += dt * self.pulse_speed

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0),
             show_prompt: bool = False) -> None:
        """Draw the exit gate."""
        # Don't draw locked or completed exits
        if self.state == ExitState.LOCKED or self.state == ExitState.COMPLETED:
            return

        cam_x, cam_y = camera_offset
        screen_x = self.rect.x - cam_x
        screen_y = self.rect.y - cam_y

        # Get colors for current state
        base_color = self.STATE_COLORS[self.state]
        glow_color = self.GLOW_COLORS[self.state]

        # Pulsing effect for available exits
        if self.state == ExitState.AVAILABLE or self.state == ExitState.ACTIVE:
            import math
            pulse = (math.sin(self.pulse_time * 3) + 1) / 2  # 0 to 1
            # Interpolate color brightness
            r = int(base_color[0] + (255 - base_color[0]) * pulse * 0.3)
            g = int(base_color[1] + (255 - base_color[1]) * pulse * 0.3)
            b = int(base_color[2] + (255 - base_color[2]) * pulse * 0.3)
            draw_color = (r, g, b)
        else:
            draw_color = base_color

        # Draw glow behind
        glow_rect = pygame.Rect(
            screen_x - 4, screen_y - 4,
            self.rect.width + 8, self.rect.height + 8
        )
        pygame.draw.rect(surface, glow_color, glow_rect, border_radius=8)

        # Draw main gate
        pygame.draw.rect(
            surface,
            draw_color,
            (screen_x, screen_y, self.rect.width, self.rect.height),
            border_radius=6
        )

        # Draw portal effect (inner gradient)
        if self.state == ExitState.AVAILABLE or self.state == ExitState.ACTIVE:
            inner_rect = pygame.Rect(
                screen_x + 4, screen_y + 4,
                self.rect.width - 8, self.rect.height - 8
            )
            # Darker center
            pygame.draw.rect(surface, (20, 40, 60), inner_rect, border_radius=4)

        # Draw border
        border_color = (255, 255, 255) if self.state != ExitState.LOCKED else (100, 100, 100)
        pygame.draw.rect(
            surface,
            border_color,
            (screen_x, screen_y, self.rect.width, self.rect.height),
            2,
            border_radius=6
        )

        # Draw mission name
        name_text = FONT_SMALL.render(self.mission.name, True, (255, 255, 255))
        name_rect = name_text.get_rect(
            centerx=screen_x + self.rect.width // 2,
            bottom=screen_y - 5
        )
        surface.blit(name_text, name_rect)

        # Draw state indicator
        if self.state == ExitState.LOCKED:
            # Lock icon (simple rectangle with keyhole)
            lock_x = screen_x + self.rect.width // 2 - 8
            lock_y = screen_y + self.rect.height // 2 - 8
            pygame.draw.rect(surface, (100, 100, 100), (lock_x, lock_y, 16, 12))
            pygame.draw.circle(surface, (60, 60, 60), (lock_x + 8, lock_y + 6), 3)
        elif self.state == ExitState.COMPLETED:
            # Checkmark
            check_x = screen_x + self.rect.width // 2
            check_y = screen_y + self.rect.height // 2
            pygame.draw.lines(
                surface, (100, 200, 100), False,
                [(check_x - 8, check_y), (check_x - 2, check_y + 6), (check_x + 8, check_y - 8)],
                3
            )

        # Draw interaction prompt
        if show_prompt and self.state == ExitState.AVAILABLE:
            prompt = FONT_SMALL.render("[SPACE] Enter Mission", True, (255, 255, 0))
            prompt_rect = prompt.get_rect(
                centerx=screen_x + self.rect.width // 2,
                top=screen_y + self.rect.height + 10
            )
            surface.blit(prompt, prompt_rect)

            # Show mission objectives preview
            obj_y = prompt_rect.bottom + 5
            for obj in self.mission.objectives[:2]:  # Show first 2 objectives
                obj_text = FONT_SMALL.render(
                    f"- {obj.description or obj.objective_type}: {obj.target_amount}",
                    True, (200, 200, 200)
                )
                surface.blit(obj_text, (prompt_rect.left, obj_y))
                obj_y += 16


class HubExitManager:
    """Manages all exit points in a hub world."""

    def __init__(self):
        self.exits: List[HubExit] = []
        self.current_mission_index: int = 0  # Which mission is currently available

    def add_exit(self, hub_exit: HubExit) -> None:
        """Add an exit to the manager."""
        self.exits.append(hub_exit)

    def clear(self) -> None:
        """Remove all exits."""
        self.exits.clear()

    def create_exit(
        self,
        x: float,
        y: float,
        mission: Mission,
    ) -> HubExit:
        """Create and add a hub exit."""
        exit_point = HubExit(x=x, y=y, mission=mission)
        self.exits.append(exit_point)
        return exit_point

    def update_availability(self, completed_missions: int) -> None:
        """
        Update exit states based on campaign progress.

        Args:
            completed_missions: Number of missions completed in this act
        """
        for i, exit_point in enumerate(self.exits):
            if i < completed_missions:
                exit_point.set_state(ExitState.COMPLETED)
            elif i == completed_missions:
                exit_point.set_state(ExitState.AVAILABLE)
            else:
                exit_point.set_state(ExitState.LOCKED)
        self.current_mission_index = completed_missions

    def update(self, dt: float) -> None:
        """Update all exits."""
        for exit_point in self.exits:
            exit_point.update(dt)

    def get_interactable_exit(self, player_pos: Tuple[int, int]) -> Optional[HubExit]:
        """Get the exit that can be interacted with."""
        for exit_point in self.exits:
            if exit_point.can_interact(player_pos):
                return exit_point
        return None

    def get_current_mission(self) -> Optional[Mission]:
        """Get the currently available mission."""
        if 0 <= self.current_mission_index < len(self.exits):
            return self.exits[self.current_mission_index].mission
        return None

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int],
             player_pos: Tuple[int, int]) -> None:
        """Draw all exits."""
        for exit_point in self.exits:
            can_interact = exit_point.can_interact(player_pos)
            exit_point.draw(surface, camera_offset, show_prompt=can_interact)


# ============================================================================
# MISSION FACTORY
# ============================================================================

def create_fetch_mission(
    mission_id: str,
    name: str,
    act: int,
    mission_index: int,
    coin_target: int = 0,
    kill_target: int = 0,
    collectible_target: int = 0,
    currency_reward: int = 50,
    xp_reward: int = 100,
    ability_orb_reward: int = 0,
) -> Mission:
    """
    Factory function to create a fetch-style mission.

    Args:
        mission_id: Unique identifier
        name: Display name
        act: Act number
        mission_index: Mission index within act
        coin_target: Coins to collect
        kill_target: Enemies to defeat
        collectible_target: Items to collect
        currency_reward: Fragments reward
        xp_reward: XP reward
        ability_orb_reward: Ability orbs reward

    Returns:
        Configured Mission object
    """
    objectives = []

    if coin_target > 0:
        objectives.append(MissionObjective(
            objective_type="coins",
            target_amount=coin_target,
            description=f"Collect {coin_target} coins"
        ))

    if kill_target > 0:
        objectives.append(MissionObjective(
            objective_type="kills",
            target_amount=kill_target,
            description=f"Defeat {kill_target} enemies"
        ))

    if collectible_target > 0:
        objectives.append(MissionObjective(
            objective_type="collectibles",
            target_amount=collectible_target,
            description=f"Find {collectible_target} items"
        ))

    rewards = MissionReward(
        currency=currency_reward,
        xp=xp_reward,
        ability_orbs=ability_orb_reward,
    )

    return Mission(
        mission_id=mission_id,
        name=name,
        description=f"Act {act} - Mission {mission_index + 1}",
        objectives=objectives,
        rewards=rewards,
        act=act,
        mission_index=mission_index,
    )


# Pre-defined missions for each act
ACT_MISSIONS: Dict[int, List[Mission]] = {
    0: [
        create_fetch_mission("lantern_1", "First Steps", 0, 0,
                           coin_target=10, currency_reward=50, xp_reward=100),
        create_fetch_mission("lantern_2", "Coin Hunter", 0, 1,
                           coin_target=15, kill_target=3, currency_reward=75, xp_reward=150),
        create_fetch_mission("lantern_3", "Trial Run", 0, 2,
                           coin_target=20, kill_target=5, currency_reward=100, xp_reward=200),
    ],
    1: [
        create_fetch_mission("veil_1", "Veil Approach", 1, 0,
                           coin_target=15, kill_target=5, currency_reward=100, xp_reward=200),
    ],
    2: [
        create_fetch_mission("hollow_1", "Descent", 2, 0,
                           coin_target=12, kill_target=4, currency_reward=75, xp_reward=175),
        create_fetch_mission("hollow_2", "Hollow Hunt", 2, 1,
                           coin_target=16, kill_target=6, currency_reward=100, xp_reward=225),
        create_fetch_mission("hollow_3", "Deep Exploration", 2, 2,
                           coin_target=20, kill_target=8, currency_reward=125, xp_reward=275,
                           ability_orb_reward=1),
    ],
    3: [
        create_fetch_mission("ember_1", "Monastery Grounds", 3, 0,
                           coin_target=18, kill_target=6, currency_reward=100, xp_reward=250),
        create_fetch_mission("ember_2", "Inner Sanctum", 3, 1,
                           coin_target=22, kill_target=8, currency_reward=125, xp_reward=300),
        create_fetch_mission("ember_3", "Forge Trial", 3, 2,
                           coin_target=25, kill_target=10, currency_reward=150, xp_reward=350,
                           ability_orb_reward=1),
    ],
    4: [
        create_fetch_mission("sky_1", "Ascent Begins", 4, 0,
                           coin_target=20, kill_target=8, currency_reward=125, xp_reward=300),
        create_fetch_mission("sky_2", "Cloud Walk", 4, 1,
                           coin_target=25, kill_target=10, currency_reward=150, xp_reward=350),
        create_fetch_mission("sky_3", "Summit Push", 4, 2,
                           coin_target=30, kill_target=12, currency_reward=200, xp_reward=400,
                           ability_orb_reward=2),
    ],
}


def get_missions_for_act(act: int) -> List[Mission]:
    """Get all missions for an act."""
    return ACT_MISSIONS.get(act, [])
