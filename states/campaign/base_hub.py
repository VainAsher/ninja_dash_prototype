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


class Shop:
    """Equipment shop for purchasing upgrades."""

    def __init__(self, npc: NPC):
        self.npc = npc
        self.is_shop = True  # Mark this NPC as a shop

    def get_available_equipment(self, game: Game) -> List[Tuple[str, any]]:
        """Get equipment available at current tier."""
        from core.equipment import ALL_EQUIPMENT

        max_tier = game.campaign_state.max_equipment_tier
        available = []

        for item_id, item in ALL_EQUIPMENT.items():
            if item.tier <= max_tier:
                available.append((item_id, item))

        # Sort by slot and tier
        available.sort(key=lambda x: (x[1].slot, x[1].tier))
        return available


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
        self.shops: Dict[str, Shop] = {}  # Map NPC name to Shop

        # Dialogue state
        self.showing_dialogue = False
        self.current_dialogue: List[str] = []
        self.dialogue_index = 0
        self.current_npc_name = ""

        # Shop state
        self.showing_shop = False
        self.shop_items: List[Tuple[str, any]] = []
        self.shop_selected_index = 0

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

    def open_shop(self, npc_name: str) -> None:
        """Open shop menu."""
        if npc_name not in self.shops:
            return

        shop = self.shops[npc_name]
        self.shop_items = shop.get_available_equipment(self.game)
        self.showing_shop = True
        self.shop_selected_index = 0
        self.current_npc_name = npc_name

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
                # Close shop/dialogue or return to menu
                if self.showing_shop:
                    self.showing_shop = False
                    return
                elif self.showing_dialogue:
                    self.showing_dialogue = False
                    return
                else:
                    # Return to main menu
                    self.game.campaign_mode = False
                    self.game.change_state("menu")
                    return

            if self.showing_shop:
                # Shop navigation
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.shop_selected_index = (self.shop_selected_index - 1) % max(1, len(self.shop_items))
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.shop_selected_index = (self.shop_selected_index + 1) % max(1, len(self.shop_items))
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Purchase selected item
                    if 0 <= self.shop_selected_index < len(self.shop_items):
                        item_id, item = self.shop_items[self.shop_selected_index]
                        if self.game.campaign_state.purchase_equipment(item_id):
                            # Refresh shop items after purchase
                            pass  # Items stay the same, just equipped status changes
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
                        # Check if this NPC is a shop
                        if npc.name in self.shops:
                            self.open_shop(npc.name)
                        else:
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

        if not self.showing_dialogue and not self.showing_shop:
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
            is_shop = npc.name in self.shops
            # Temporarily modify the draw call to show shop vs talk
            if can_interact and not self.showing_dialogue and not self.showing_shop:
                # Draw NPC body
                pygame.draw.rect(surface, npc.color, npc.rect, border_radius=4)
                # Draw name label
                label = FONT_SMALL.render(npc.name, True, (255, 255, 255))
                label_rect = label.get_rect(centerx=npc.rect.centerx, bottom=npc.rect.top - 5)
                surface.blit(label, label_rect)
                # Draw prompt
                prompt_text = "[E] Shop" if is_shop else "[E] Talk"
                prompt = FONT_SMALL.render(prompt_text, True, (255, 255, 0))
                prompt_rect = prompt.get_rect(centerx=npc.rect.centerx, top=npc.rect.bottom + 5)
                surface.blit(prompt, prompt_rect)
            else:
                npc.draw(surface, show_prompt=False)

        # Draw mission board
        if self.mission_board:
            can_interact = self.mission_board.can_interact((self.player_x, self.player_y))
            self.mission_board.draw(surface, show_prompt=can_interact and not self.showing_dialogue)

        # Draw player (simple rectangle)
        pygame.draw.rect(surface, (255, 80, 80), self.player_rect, border_radius=4)

        # Draw dialogue box if active
        if self.showing_dialogue:
            self.draw_dialogue_box(surface)

        # Draw shop if active
        if self.showing_shop:
            self.draw_shop(surface)

        # Draw instructions
        if not self.showing_dialogue and not self.showing_shop:
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

    def draw_shop(self, surface: pygame.Surface) -> None:
        """Draw equipment shop UI."""
        # Shop background overlay
        overlay = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Shop panel
        panel_width = 700
        panel_height = 500
        panel_x = (LOGICAL_W - panel_width) // 2
        panel_y = (LOGICAL_H - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        pygame.draw.rect(surface, (30, 25, 20), panel_rect)
        pygame.draw.rect(surface, (200, 150, 100), panel_rect, 3)

        # Shop title
        title = FONT_BIG.render(f"{self.current_npc_name}'s Forge", True, (255, 200, 100))
        title_rect = title.get_rect(centerx=panel_rect.centerx, top=panel_y + 20)
        surface.blit(title, title_rect)

        # Currency display
        currency = self.game.campaign_state.currency
        currency_text = FONT.render(f"Fragments: {currency}", True, (255, 255, 100))
        surface.blit(currency_text, (panel_x + 20, panel_y + 60))

        # Equipment list
        list_y = panel_y + 100
        item_height = 35
        visible_items = min(10, len(self.shop_items))

        for i in range(visible_items):
            if i >= len(self.shop_items):
                break

            item_id, item = self.shop_items[i]
            item_y = list_y + (i * item_height)

            # Highlight selected item
            if i == self.shop_selected_index:
                highlight_rect = pygame.Rect(panel_x + 15, item_y - 2, panel_width - 30, item_height - 2)
                pygame.draw.rect(surface, (80, 60, 40), highlight_rect, border_radius=3)

            # Item name and tier
            from core.equipment import TIER_NAMES, SLOT_WEAPON, SLOT_ARMOR, SLOT_BOOTS, SLOT_CHARM
            tier_name = TIER_NAMES.get(item.tier, "Unknown")
            slot_icons = {SLOT_WEAPON: "⚔️", SLOT_ARMOR: "🛡️", SLOT_BOOTS: "👢", SLOT_CHARM: "✨"}
            slot_icon = slot_icons.get(item.slot, "?")

            # Check if equipped
            is_equipped = self.game.campaign_state.equipped_items.get(item.slot) == item_id
            equipped_mark = " [EQUIPPED]" if is_equipped else ""

            item_text = f"{slot_icon} {item.name} ({tier_name}){equipped_mark}"
            color = (100, 255, 100) if is_equipped else (255, 255, 255)
            text = FONT_SMALL.render(item_text, True, color)
            surface.blit(text, (panel_x + 25, item_y + 5))

            # Cost
            can_afford = currency >= item.cost
            cost_color = (100, 255, 100) if can_afford else (255, 100, 100)
            cost_text = FONT_SMALL.render(f"{item.cost} frags", True, cost_color)
            surface.blit(cost_text, (panel_x + panel_width - 120, item_y + 5))

        # Selected item details
        if 0 <= self.shop_selected_index < len(self.shop_items):
            item_id, item = self.shop_items[self.shop_selected_index]
            details_y = list_y + (visible_items * item_height) + 20

            # Description
            desc_text = FONT_SMALL.render(item.description, True, (200, 200, 200))
            surface.blit(desc_text, (panel_x + 25, details_y))

            # Stats
            stats_y = details_y + 25
            stats = item.stats
            stats_str = f"HP:+{stats.hp} MP:+{stats.mp} STM:+{stats.stm} STG:+{stats.stg} DEF:+{stats.def_} SPD:+{stats.spd-1.0:.2f}x DEX:+{stats.dext}"
            stats_text = FONT_SMALL.render(stats_str, True, (150, 200, 255))
            surface.blit(stats_text, (panel_x + 25, stats_y))

        # Instructions
        instructions = "W/S: Navigate | ENTER/SPACE: Purchase | ESC: Close"
        inst_text = FONT_SMALL.render(instructions, True, (180, 180, 180))
        inst_rect = inst_text.get_rect(centerx=panel_rect.centerx, bottom=panel_rect.bottom - 15)
        surface.blit(inst_text, inst_rect)
