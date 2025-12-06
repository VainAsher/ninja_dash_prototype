"""
Base Campaign Hub State - Enhanced with Level Generation

Abstract base class for all campaign hub locations.
Hubs are safe zones between missions where players can:
- Explore procedurally generated levels (same generator, fixed seed)
- Talk to patrolling NPCs
- Use full movement abilities
- Access shop and upgrade equipment
- Select missions via exit points
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Tuple, Optional, Any

import pygame

from settings import (
    LOGICAL_W, LOGICAL_H, HUD_HEIGHT,
    FONT, FONT_BIG, FONT_SMALL,
    COLOR_BG, COLOR_TILE, COLOR_PLAYER,
    TILE_SIZE
)
from states.base import GameState
from level_gen import generate_level
from level_gen.config import HUB_CONFIGS, get_hub_seed
from player import Player
from camera import get_camera_rect

from entities.hub_npc import HubNPC, HubNPCManager
from entities.hub_exit import (
    HubExit, HubExitManager, Mission, ExitState,
    get_missions_for_act
)
from core.shop_system import ShopUI

if TYPE_CHECKING:
    from core.game import Game


# Legacy NPC class for backward compatibility
class NPC:
    """Simple NPC with interaction zone (legacy, use HubNPC for new code)."""

    def __init__(self, name: str, x: int, y: int, width: int = 40, height: int = 60,
                 color: Tuple[int, int, int] = (100, 150, 255)):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.interaction_range = 80
        self.dialogue: List[str] = []
        self.is_unlocked = True

    def can_interact(self, player_pos: Tuple[int, int]) -> bool:
        px, py = player_pos
        dx = px - self.rect.centerx
        dy = py - self.rect.centery
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < self.interaction_range and self.is_unlocked

    def draw(self, surface: pygame.Surface, show_prompt: bool = False):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        label = FONT_SMALL.render(self.name, True, (255, 255, 255))
        label_rect = label.get_rect(centerx=self.rect.centerx, bottom=self.rect.top - 5)
        surface.blit(label, label_rect)
        if show_prompt:
            prompt = FONT_SMALL.render("[E] Talk", True, (255, 255, 0))
            prompt_rect = prompt.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 5)
            surface.blit(prompt, prompt_rect)


class MissionBoard:
    """Legacy mission start trigger."""

    def __init__(self, name: str, x: int, y: int, width: int = 80, height: int = 100):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.interaction_range = 100

    def can_interact(self, player_pos: Tuple[int, int]) -> bool:
        px, py = player_pos
        dx = px - self.rect.centerx
        dy = py - self.rect.centery
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < self.interaction_range

    def draw(self, surface: pygame.Surface, show_prompt: bool = False):
        pygame.draw.rect(surface, (80, 60, 40), self.rect)
        pygame.draw.rect(surface, (200, 180, 140), self.rect, 3)
        label = FONT_SMALL.render(self.name, True, (255, 255, 255))
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)
        if show_prompt:
            prompt = FONT_SMALL.render("[SPACE] Start Mission", True, (255, 255, 0))
            prompt_rect = prompt.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 10)
            surface.blit(prompt, prompt_rect)


class Shop:
    """Equipment shop wrapper (legacy)."""

    def __init__(self, npc: NPC):
        self.npc = npc
        self.is_shop = True

    def get_available_equipment(self, game: Game) -> List[Tuple[str, Any]]:
        from core.equipment import ALL_EQUIPMENT
        max_tier = game.campaign_state.max_equipment_tier
        available = [
            (item_id, item)
            for item_id, item in ALL_EQUIPMENT.items()
            if item.tier <= max_tier
        ]
        available.sort(key=lambda x: (x[1].slot, x[1].tier))
        return available


class CampaignHub(GameState, ABC):
    """
    Abstract base class for campaign hub states.

    Enhanced to use procedural level generation with fixed seeds,
    creating explorable hub worlds with patrolling NPCs and
    mission exit points.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        # Hub identification
        self.hub_name: str = "base_hub"
        self.title: str = "Hub"
        self.bg_color: Tuple[int, int, int] = (20, 20, 30)
        self.biome: str = "lantern"

        # Level data
        self.world: List[List[int]] = []
        self.tiles: List[pygame.Rect] = []
        self.phaseable_walls: List[pygame.Rect] = []
        self.spawn: Tuple[int, int] = (100, 100)

        # Player
        self.player: Optional[Player] = None

        # NPCs (new system)
        self.npc_manager = HubNPCManager()

        # Exit points (new system)
        self.exit_manager = HubExitManager()

        # Legacy compatibility
        self.npcs: List[NPC] = []
        self.mission_board: Optional[MissionBoard] = None
        self.shops: Dict[str, Shop] = {}

        # UI State
        self.showing_dialogue = False
        self.current_dialogue: List[str] = []
        self.dialogue_index = 0
        self.current_npc_name = ""

        # Shop UI (enhanced)
        self.shop_ui = ShopUI(game)

        # Legacy shop state
        self.showing_shop = False
        self.shop_items: List[Tuple[str, Any]] = []
        self.shop_selected_index = 0

        # Rendering surfaces
        self.play_area = pygame.Surface((LOGICAL_W, LOGICAL_H - HUD_HEIGHT))
        self.hud_area = pygame.Surface((LOGICAL_W, HUD_HEIGHT))

    @abstractmethod
    def setup_npcs(self) -> None:
        """Setup NPCs and mission exits. Override in subclasses."""
        pass

    @abstractmethod
    def get_act_number(self) -> int:
        """Return the act number this hub corresponds to."""
        pass

    def get_hub_config_name(self) -> str:
        """Get the hub config name for level generation."""
        return self.hub_name

    def enter(self) -> None:
        """Called when entering this hub."""
        # Generate hub level
        self._generate_hub_level()

        # Setup NPCs and exits
        self.setup_npcs()

        # Reset UI state
        self.showing_dialogue = False
        self.current_dialogue = []
        self.dialogue_index = 0
        self.shop_ui.close()

        # Update campaign state
        self.game.campaign_state.act = self.get_act_number()
        self.game.campaign_state.mission_index = 0

        print(f"Entered hub: {self.title}")

    def _generate_hub_level(self) -> None:
        """Generate the hub level using the level generator."""
        config_name = self.get_hub_config_name()
        config = HUB_CONFIGS.get(config_name)

        if not config:
            # Fallback to lantern hub config
            config = HUB_CONFIGS["lantern_hub"]

        # Get deterministic seed for this hub
        seed = get_hub_seed(config_name)

        # Get player abilities (all abilities available in hub)
        from core.campaign import get_base_abilities_for_act
        abilities = list(get_base_abilities_for_act(self.game.campaign_state))
        abilities.extend(list(self.game.campaign_state.abilities_unlocked))

        # Generate level
        (
            world,
            tiles,
            exit_rect,
            spawn,
            coins,          # Will be empty for hubs
            hazards,        # Will be empty for hubs
            healths,        # Will be empty for hubs
            lives,          # Will be empty for hubs
            powerups,       # Will be empty for hubs
            phaseable_walls,
            ability_orbs,   # Will be empty for hubs
            enemy_positions # Will be empty for hubs
        ) = generate_level(
            seed=seed,
            config=config,
            abilities=abilities
        )

        # Store level data
        self.world = world
        self.tiles = tiles
        self.phaseable_walls = phaseable_walls
        self.spawn = spawn
        self.biome = config.biome

        # Create player at spawn point
        sx, sy = spawn
        self.player = Player(sx, sy)

        # Clear NPC and exit managers
        self.npc_manager.clear()
        self.exit_manager.clear()

    def _place_hub_npcs(self) -> None:
        """
        Place NPCs at platform locations in the generated level.
        Called by subclasses after setting up NPC definitions.
        """
        # Find valid spawn positions (on platforms)
        valid_positions = self._find_platform_positions()

        # Place each NPC at a valid position
        for i, npc in enumerate(self.npc_manager.npcs):
            if i < len(valid_positions):
                x, y = valid_positions[i]
                npc.spawn_x = x
                npc.spawn_y = y
                npc.rect.x = x
                npc.rect.y = y - npc.rect.height

    def _place_hub_exits(self) -> None:
        """
        Place mission exits at platform locations in the generated level.
        """
        valid_positions = self._find_platform_positions()

        # Skip positions used by NPCs
        npc_count = len(self.npc_manager.npcs)
        exit_positions = valid_positions[npc_count:]

        # Update exit availability based on campaign progress
        completed = self.game.campaign_state.mission_index
        self.exit_manager.update_availability(completed)

        # Place each exit
        for i, exit_point in enumerate(self.exit_manager.exits):
            if i < len(exit_positions):
                x, y = exit_positions[i]
                exit_point.rect.x = x - exit_point.rect.width // 2
                exit_point.rect.y = y - exit_point.rect.height

    def _find_platform_positions(self) -> List[Tuple[int, int]]:
        """
        Find valid positions on platforms for placing NPCs/exits.

        Returns:
            List of (x, y) pixel positions on top of platforms
        """
        positions = []

        # Scan for floor tiles with empty space above
        for ty in range(1, len(self.world) - 1):
            for tx in range(1, len(self.world[0]) - 1):
                # Check if this is a floor tile with space above
                if (self.world[ty][tx] == 1 and
                    self.world[ty - 1][tx] == 0 and
                    self.world[ty - 2][tx] == 0):

                    # Convert to pixel coordinates
                    x = tx * TILE_SIZE + TILE_SIZE // 2
                    y = ty * TILE_SIZE

                    # Check minimum distance from player spawn
                    spawn_dist = abs(x - self.spawn[0])
                    if spawn_dist > TILE_SIZE * 5:
                        positions.append((x, y))

        # Sort by distance from spawn (spread NPCs out)
        positions.sort(key=lambda p: abs(p[0] - self.spawn[0]) + abs(p[1] - self.spawn[1]))

        # Spread positions out - take every Nth position
        spread_positions = []
        for i in range(0, len(positions), 5):
            if i < len(positions):
                spread_positions.append(positions[i])

        return spread_positions

    def start_mission(self, mission: Optional[Mission] = None) -> None:
        """Start a mission from this hub."""
        if mission:
            # Set campaign state for specific mission
            self.game.campaign_state.act = mission.act
            self.game.campaign_state.mission_index = mission.mission_index
        else:
            # Use current mission index
            pass

        # Build level for current act/mission
        self.game.seed = None  # Random seed for missions
        self.game.build_level()
        self.game.change_state("play")

    def open_dialogue(self, npc: Any) -> None:
        """Open dialogue with an NPC."""
        if hasattr(npc, 'dialogue') and npc.dialogue:
            self.showing_dialogue = True
            self.current_dialogue = npc.dialogue
            self.dialogue_index = 0
            self.current_npc_name = npc.name

            # Stop NPC movement while talking
            if hasattr(npc, 'start_talking'):
                npc.start_talking()

    def close_dialogue(self, npc: Any = None) -> None:
        """Close the current dialogue."""
        self.showing_dialogue = False
        self.dialogue_index = 0

        # Resume NPC movement
        if npc and hasattr(npc, 'stop_talking'):
            npc.stop_talking()

    def advance_dialogue(self) -> None:
        """Advance to next dialogue line or close."""
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.current_dialogue):
            self.showing_dialogue = False
            self.dialogue_index = 0

    def open_shop(self, npc_name: str) -> None:
        """Open enhanced shop menu."""
        self.shop_ui.open(npc_name)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN:
            return

        # Shop UI takes priority
        if self.shop_ui.visible:
            if self.shop_ui.handle_event(event):
                return

        if event.key == pygame.K_ESCAPE:
            # Close any open UI or return to menu
            if self.shop_ui.visible:
                self.shop_ui.close()
            elif self.showing_dialogue:
                self.showing_dialogue = False
            else:
                self.game.campaign_mode = False
                self.game.change_state("menu")
            return

        if self.showing_dialogue:
            # Advance dialogue
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                self.advance_dialogue()
            return

        # Player at position
        player_pos = (self.player.rect.centerx, self.player.rect.centery)

        # Interact with NPCs
        if event.key == pygame.K_e:
            # Check new NPC system
            npc = self.npc_manager.get_interactable_npc(player_pos)
            if npc:
                if npc.is_shop:
                    self.open_shop(npc.name)
                else:
                    self.open_dialogue(npc)
                return

            # Check legacy NPCs
            for legacy_npc in self.npcs:
                if legacy_npc.can_interact(player_pos):
                    if legacy_npc.name in self.shops:
                        self.open_shop(legacy_npc.name)
                    else:
                        self.open_dialogue(legacy_npc)
                    return

        # Interact with mission exits or board
        if event.key == pygame.K_SPACE:
            # Check new exit system
            hub_exit = self.exit_manager.get_interactable_exit(player_pos)
            if hub_exit and hub_exit.state == ExitState.AVAILABLE:
                self.start_mission(hub_exit.mission)
                return

            # Check legacy mission board
            if self.mission_board and self.mission_board.can_interact(player_pos):
                self.start_mission()
                return

    def update(self, dt: float) -> None:
        """Update hub state."""
        # Update shop UI
        if self.shop_ui.visible:
            self.shop_ui.update(dt)

        # Don't update player/world when in dialogue or shop
        if self.showing_dialogue or self.shop_ui.visible:
            return

        # Update player
        if self.player:
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.tiles, dt, self.phaseable_walls)

        # Update NPCs
        self.npc_manager.update(dt, self.world)

        # Update exit animations
        self.exit_manager.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw hub."""
        # Draw world to play area
        self._draw_world()

        # Draw HUD
        self._draw_hub_hud()

        # Composite to main surface
        surface.blit(self.hud_area, (0, 0))
        surface.blit(self.play_area, (0, HUD_HEIGHT))

        # Draw dialogue overlay
        if self.showing_dialogue:
            self.draw_dialogue_box(surface)

        # Draw shop overlay
        if self.shop_ui.visible:
            self.shop_ui.draw(surface)

    def _draw_world(self) -> None:
        """Draw the hub world with camera."""
        if not self.player:
            self.play_area.fill(self.bg_color)
            return

        # Get camera
        cam = get_camera_rect(self.player.rect)

        # Biome-specific colors
        bg_colors = {
            "lantern": (10, 10, 20),
            "hollow": (5, 5, 15),
            "ember": (20, 10, 5),
            "sky": (15, 25, 40),
        }
        tile_colors = {
            "lantern": (200, 180, 120),
            "hollow": (40, 40, 70),
            "ember": (150, 80, 40),
            "sky": (180, 220, 255),
        }

        self.play_area.fill(bg_colors.get(self.biome, COLOR_BG))
        ground_color = tile_colors.get(self.biome, COLOR_TILE)

        # Draw tiles
        for t in self.tiles:
            if cam.colliderect(t):
                color = (120, 80, 160) if t in self.phaseable_walls else ground_color
                pygame.draw.rect(
                    self.play_area,
                    color,
                    (t.x - cam.x, t.y - cam.y, t.w, t.h)
                )

        # Draw NPCs
        player_pos = (self.player.rect.centerx, self.player.rect.centery)
        self.npc_manager.draw(self.play_area, (cam.x, cam.y), player_pos)

        # Draw legacy NPCs
        for npc in self.npcs:
            npc_screen_rect = npc.rect.move(-cam.x, -cam.y)
            if self.play_area.get_rect().colliderect(npc_screen_rect):
                can_interact = npc.can_interact(player_pos)
                is_shop = npc.name in self.shops

                pygame.draw.rect(self.play_area, npc.color, npc_screen_rect, border_radius=4)
                label = FONT_SMALL.render(npc.name, True, (255, 255, 255))
                label_rect = label.get_rect(centerx=npc_screen_rect.centerx,
                                           bottom=npc_screen_rect.top - 5)
                self.play_area.blit(label, label_rect)

                if can_interact and not self.showing_dialogue:
                    prompt_text = "[E] Shop" if is_shop else "[E] Talk"
                    prompt = FONT_SMALL.render(prompt_text, True, (255, 255, 0))
                    prompt_rect = prompt.get_rect(centerx=npc_screen_rect.centerx,
                                                  top=npc_screen_rect.bottom + 5)
                    self.play_area.blit(prompt, prompt_rect)

        # Draw legacy mission board
        if self.mission_board:
            board_screen_rect = self.mission_board.rect.move(-cam.x, -cam.y)
            if self.play_area.get_rect().colliderect(board_screen_rect):
                pygame.draw.rect(self.play_area, (80, 60, 40), board_screen_rect)
                pygame.draw.rect(self.play_area, (200, 180, 140), board_screen_rect, 3)

                label = FONT_SMALL.render(self.mission_board.name, True, (255, 255, 255))
                label_rect = label.get_rect(center=board_screen_rect.center)
                self.play_area.blit(label, label_rect)

                if self.mission_board.can_interact(player_pos):
                    prompt = FONT_SMALL.render("[SPACE] Start Mission", True, (255, 255, 0))
                    prompt_rect = prompt.get_rect(centerx=board_screen_rect.centerx,
                                                  top=board_screen_rect.bottom + 10)
                    self.play_area.blit(prompt, prompt_rect)

        # Draw exit points
        self.exit_manager.draw(self.play_area, (cam.x, cam.y), player_pos)

        # Draw player
        player_screen_rect = self.player.rect.move(-cam.x, -cam.y)
        pygame.draw.rect(self.play_area, COLOR_PLAYER, player_screen_rect, border_radius=4)

        # Draw player facing indicator
        if self.player.facing == 1:
            points = [
                (player_screen_rect.right - 5, player_screen_rect.top + 5),
                (player_screen_rect.right - 5, player_screen_rect.top + 15),
                (player_screen_rect.right - 2, player_screen_rect.top + 10)
            ]
        else:
            points = [
                (player_screen_rect.left + 5, player_screen_rect.top + 5),
                (player_screen_rect.left + 5, player_screen_rect.top + 15),
                (player_screen_rect.left + 2, player_screen_rect.top + 10)
            ]
        pygame.draw.polygon(self.play_area, (255, 255, 255), points)

    def _draw_hub_hud(self) -> None:
        """Draw simplified hub HUD."""
        self.hud_area.fill((20, 20, 30))

        # Title
        title = FONT_BIG.render(self.title, True, (255, 255, 255))
        title_rect = title.get_rect(centerx=LOGICAL_W // 2, centery=HUD_HEIGHT // 2)
        self.hud_area.blit(title, title_rect)

        # Currency
        currency = self.game.campaign_state.currency
        currency_text = FONT.render(f"Fragments: {currency}", True, (255, 215, 0))
        self.hud_area.blit(currency_text, (20, HUD_HEIGHT // 2 - 10))

        # Act info
        act = self.game.campaign_state.act
        act_text = FONT_SMALL.render(f"Act {act}", True, (200, 200, 200))
        self.hud_area.blit(act_text, (LOGICAL_W - 100, HUD_HEIGHT // 2 - 8))

    def draw_dialogue_box(self, surface: pygame.Surface) -> None:
        """Draw dialogue box at bottom of screen."""
        box_height = 150
        box_y = LOGICAL_H - box_height - 20
        box_rect = pygame.Rect(40, box_y, LOGICAL_W - 80, box_height)

        pygame.draw.rect(surface, (20, 20, 30), box_rect)
        pygame.draw.rect(surface, (100, 150, 255), box_rect, 3)

        name_text = FONT.render(self.current_npc_name, True, (255, 255, 100))
        surface.blit(name_text, (box_rect.x + 20, box_rect.y + 15))

        if self.dialogue_index < len(self.current_dialogue):
            line = self.current_dialogue[self.dialogue_index]
            dialogue_text = FONT_SMALL.render(line, True, (255, 255, 255))
            surface.blit(dialogue_text, (box_rect.x + 20, box_rect.y + 55))

        progress_text = f"[{self.dialogue_index + 1}/{len(self.current_dialogue)}]"
        prompt_text = FONT_SMALL.render(f"{progress_text} Press SPACE to continue",
                                        True, (150, 150, 150))
        prompt_rect = prompt_text.get_rect(right=box_rect.right - 20,
                                           bottom=box_rect.bottom - 15)
        surface.blit(prompt_text, prompt_rect)

    # Legacy method for backward compatibility
    def draw_shop(self, surface: pygame.Surface) -> None:
        """Draw equipment shop UI (legacy - use shop_ui instead)."""
        pass  # Handled by ShopUI now
