"""
Base Campaign Hub State

Abstract base class for all campaign hub locations.
Hubs are safe zones between missions where players can:
- Talk to NPCs
- Upgrade equipment
- View progression
- Start missions
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Tuple, Optional

import pygame

from settings import LOGICAL_W, LOGICAL_H, FONT, FONT_BIG, FONT_SMALL
from states.base import GameState

if TYPE_CHECKING:
    from core.game import Game


class NPC:
    """Simple NPC with interaction zone."""

    def __init__(self, name: str, x: int, y: int, width: int = 40, height: int = 60, color: Tuple[int, int, int] = (100, 150, 255)):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.interaction_range = 80
        self.dialogue: List[str] = []
        self.is_unlocked = True  # Can be gated by campaign progress

    def can_interact(self, player_pos: Tuple[int, int]) -> bool:
        """Check if player is close enough to interact."""
        px, py = player_pos
        dx = px - self.rect.centerx
        dy = py - self.rect.centery
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < self.interaction_range and self.is_unlocked

    def draw(self, surface: pygame.Surface, show_prompt: bool = False):
        """Draw NPC sprite (placeholder rectangle)."""
        # Draw NPC body
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)

        # Draw name label
        label = FONT_SMALL.render(self.name, True, (255, 255, 255))
        label_rect = label.get_rect(centerx=self.rect.centerx, bottom=self.rect.top - 5)
        surface.blit(label, label_rect)

        # Draw interaction prompt if close
        if show_prompt:
            prompt = FONT_SMALL.render("[E] Talk", True, (255, 255, 0))
            prompt_rect = prompt.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 5)
            surface.blit(prompt, prompt_rect)


class MissionBoard:
    """Mission start trigger."""

    def __init__(self, name: str, x: int, y: int, width: int = 80, height: int = 100):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.interaction_range = 100

    def can_interact(self, player_pos: Tuple[int, int]) -> bool:
        """Check if player is close enough to interact."""
        px, py = player_pos
        dx = px - self.rect.centerx
        dy = py - self.rect.centery
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < self.interaction_range

    def draw(self, surface: pygame.Surface, show_prompt: bool = False):
        """Draw mission board (placeholder)."""
        # Draw board
        pygame.draw.rect(surface, (80, 60, 40), self.rect)  # Brown wood
        pygame.draw.rect(surface, (200, 180, 140), self.rect, 3)  # Border

        # Draw label
        label = FONT_SMALL.render(self.name, True, (255, 255, 255))
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

        # Draw interaction prompt
        if show_prompt:
            prompt = FONT_SMALL.render("[SPACE] Start Mission", True, (255, 255, 0))
            prompt_rect = prompt.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 10)
            surface.blit(prompt, prompt_rect)


class CampaignHub(GameState, ABC):
    """
    Abstract base class for campaign hub states.

    Each hub has:
    - Background/environment
    - NPCs for interaction
    - Mission board to start missions
    - Dialogue system (simple text display)
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.player_x: int = LOGICAL_W // 2
        self.player_y: int = LOGICAL_H - 200
        self.player_rect = pygame.Rect(self.player_x - 16, self.player_y - 24, 32, 48)

        self.npcs: List[NPC] = []
        self.mission_board: Optional[MissionBoard] = None

        # Dialogue state
        self.showing_dialogue = False
        self.current_dialogue: List[str] = []
        self.dialogue_index = 0
        self.current_npc_name = ""

        # UI
        self.title = "Hub"  # Override in subclasses
        self.bg_color = (20, 20, 30)  # Override in subclasses

    @abstractmethod
    def setup_npcs(self) -> None:
        """Setup NPCs and mission board. Override in subclasses."""
        pass

    @abstractmethod
    def get_act_number(self) -> int:
        """Return the act number this hub corresponds to."""
        pass

    def enter(self) -> None:
        """Called when entering this hub."""
        self.setup_npcs()
        self.showing_dialogue = False
        self.current_dialogue = []
        self.dialogue_index = 0

        # Update campaign state to this hub's act
        self.game.campaign_state.act = self.get_act_number()
        self.game.campaign_state.mission_index = 0

    def start_mission(self) -> None:
        """Start a mission from this hub."""
        # Build level for current act/mission
        self.game.seed = None  # Random seed
        self.game.build_level()
        self.game.change_state("play")

    def open_dialogue(self, npc: NPC) -> None:
        """Open dialogue with an NPC."""
        if not npc.dialogue:
            npc.dialogue = [f"{npc.name}: Hello, traveler."]

        self.showing_dialogue = True
        self.current_dialogue = npc.dialogue
        self.dialogue_index = 0
        self.current_npc_name = npc.name

    def advance_dialogue(self) -> None:
        """Advance to next dialogue line or close."""
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.current_dialogue):
            self.showing_dialogue = False
            self.dialogue_index = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to main menu
                self.game.campaign_mode = False
                self.game.change_state("menu")
                return

            if self.showing_dialogue:
                # Advance dialogue on any key
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                    self.advance_dialogue()
                return

            # Check NPC interactions
            if event.key == pygame.K_e:
                for npc in self.npcs:
                    if npc.can_interact((self.player_x, self.player_y)):
                        self.open_dialogue(npc)
                        return

            # Check mission board interaction
            if event.key == pygame.K_SPACE:
                if self.mission_board and self.mission_board.can_interact((self.player_x, self.player_y)):
                    self.start_mission()
                    return

    def update(self, dt: float) -> None:
        """Update hub state."""
        # Simple player movement for hub navigation
        keys = pygame.key.get_pressed()

        if not self.showing_dialogue:
            move_speed = 200 * dt
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player_x -= move_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player_x += move_speed

            # Clamp to screen bounds
            self.player_x = max(50, min(LOGICAL_W - 50, self.player_x))

            # Update player rect
            self.player_rect.centerx = int(self.player_x)
            self.player_rect.centery = int(self.player_y)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw hub."""
        # Background
        surface.fill(self.bg_color)

        # Draw ground
        ground_y = LOGICAL_H - 150
        pygame.draw.rect(surface, (60, 50, 40), (0, ground_y, LOGICAL_W, 150))

        # Draw title
        title_text = FONT_BIG.render(self.title, True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=LOGICAL_W // 2, top=40)
        surface.blit(title_text, title_rect)

        # Draw NPCs
        for npc in self.npcs:
            can_interact = npc.can_interact((self.player_x, self.player_y))
            npc.draw(surface, show_prompt=can_interact and not self.showing_dialogue)

        # Draw mission board
        if self.mission_board:
            can_interact = self.mission_board.can_interact((self.player_x, self.player_y))
            self.mission_board.draw(surface, show_prompt=can_interact and not self.showing_dialogue)

        # Draw player (simple rectangle)
        pygame.draw.rect(surface, (255, 80, 80), self.player_rect, border_radius=4)

        # Draw dialogue box if active
        if self.showing_dialogue:
            self.draw_dialogue_box(surface)

        # Draw instructions
        if not self.showing_dialogue:
            help_text = FONT_SMALL.render("ESC: Menu | A/D: Move | E: Talk | SPACE: Start Mission", True, (180, 180, 200))
            help_rect = help_text.get_rect(centerx=LOGICAL_W // 2, bottom=LOGICAL_H - 20)
            surface.blit(help_text, help_rect)

    def draw_dialogue_box(self, surface: pygame.Surface) -> None:
        """Draw dialogue box at bottom of screen."""
        box_height = 150
        box_y = LOGICAL_H - box_height - 20
        box_rect = pygame.Rect(40, box_y, LOGICAL_W - 80, box_height)

        # Draw box background
        pygame.draw.rect(surface, (20, 20, 30), box_rect)
        pygame.draw.rect(surface, (100, 150, 255), box_rect, 3)

        # Draw NPC name
        name_text = FONT.render(self.current_npc_name, True, (255, 255, 100))
        surface.blit(name_text, (box_rect.x + 20, box_rect.y + 15))

        # Draw current dialogue line
        if self.dialogue_index < len(self.current_dialogue):
            line = self.current_dialogue[self.dialogue_index]
            dialogue_text = FONT_SMALL.render(line, True, (255, 255, 255))
            surface.blit(dialogue_text, (box_rect.x + 20, box_rect.y + 55))

        # Draw continue prompt
        progress_text = f"[{self.dialogue_index + 1}/{len(self.current_dialogue)}]"
        prompt_text = FONT_SMALL.render(f"{progress_text} Press SPACE to continue", True, (150, 150, 150))
        prompt_rect = prompt_text.get_rect(right=box_rect.right - 20, bottom=box_rect.bottom - 15)
        surface.blit(prompt_text, prompt_rect)
