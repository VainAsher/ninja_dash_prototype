"""
Enhanced Shop System for Campaign Mode

Provides:
- Improved shop UI with categories
- Item preview and comparison
- Currency/inventory management
- Consumable items (health potions, buffs, etc.)
"""

from __future__ import annotations

import pygame
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Dict, Tuple, Optional, Any
from enum import Enum

from settings import LOGICAL_W, LOGICAL_H, FONT, FONT_BIG, FONT_SMALL
from core.equipment import (
    ALL_EQUIPMENT, EquipmentPiece, Stats,
    SLOT_WEAPON, SLOT_ARMOR, SLOT_BOOTS, SLOT_CHARM,
    TIER_NAMES, ALL_SLOTS
)

if TYPE_CHECKING:
    from core.game import Game


class ShopCategory(Enum):
    """Categories for shop items."""
    WEAPONS = "weapons"
    ARMOR = "armor"
    BOOTS = "boots"
    CHARMS = "charms"
    CONSUMABLES = "consumables"


@dataclass
class ConsumableItem:
    """A consumable item that can be purchased and used."""
    item_id: str
    name: str
    description: str
    cost: int
    effect_type: str  # "heal", "buff_damage", "buff_speed", etc.
    effect_value: int
    max_stack: int = 10

    def apply(self, player: Any, campaign_state: Any) -> bool:
        """
        Apply the consumable effect.

        Returns:
            True if successfully applied
        """
        if self.effect_type == "heal":
            # Heal player
            from settings import PLAYER_MAX_HEALTH
            if player.health < PLAYER_MAX_HEALTH:
                player.health = min(player.health + self.effect_value, PLAYER_MAX_HEALTH)
                return True
            return False  # Already full health

        elif self.effect_type == "full_heal":
            from settings import PLAYER_MAX_HEALTH
            if player.health < PLAYER_MAX_HEALTH:
                player.health = PLAYER_MAX_HEALTH
                return True
            return False

        elif self.effect_type == "extra_life":
            # Add extra life
            return True  # Handled externally

        return False


# Pre-defined consumable items
CONSUMABLES: Dict[str, ConsumableItem] = {
    "health_potion": ConsumableItem(
        item_id="health_potion",
        name="Health Potion",
        description="Restores 25 HP",
        cost=25,
        effect_type="heal",
        effect_value=25,
        max_stack=10
    ),
    "large_health_potion": ConsumableItem(
        item_id="large_health_potion",
        name="Large Health Potion",
        description="Restores 50 HP",
        cost=50,
        effect_type="heal",
        effect_value=50,
        max_stack=5
    ),
    "full_restore": ConsumableItem(
        item_id="full_restore",
        name="Full Restore",
        description="Fully restores HP",
        cost=100,
        effect_type="full_heal",
        effect_value=0,
        max_stack=3
    ),
    "extra_life": ConsumableItem(
        item_id="extra_life",
        name="Extra Life",
        description="Grants an additional life",
        cost=200,
        effect_type="extra_life",
        effect_value=1,
        max_stack=2
    ),
}


@dataclass
class PlayerInventory:
    """Tracks player's consumable inventory."""
    items: Dict[str, int] = field(default_factory=dict)  # item_id -> quantity

    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add items to inventory, respecting max stack."""
        if item_id not in CONSUMABLES:
            return False

        item = CONSUMABLES[item_id]
        current = self.items.get(item_id, 0)
        new_amount = min(current + quantity, item.max_stack)

        if new_amount > current:
            self.items[item_id] = new_amount
            return True
        return False  # Already at max

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove items from inventory."""
        current = self.items.get(item_id, 0)
        if current >= quantity:
            self.items[item_id] = current - quantity
            if self.items[item_id] == 0:
                del self.items[item_id]
            return True
        return False

    def get_quantity(self, item_id: str) -> int:
        """Get quantity of an item."""
        return self.items.get(item_id, 0)

    def use_item(self, item_id: str, player: Any, campaign_state: Any) -> bool:
        """Use an item from inventory."""
        if item_id not in self.items or self.items[item_id] <= 0:
            return False

        item = CONSUMABLES.get(item_id)
        if item and item.apply(player, campaign_state):
            self.remove_item(item_id)
            return True
        return False


class ShopUI:
    """
    Enhanced shop UI with categories and better item display.
    """

    def __init__(self, game: Game):
        self.game = game
        self.visible = False

        # UI state
        self.category = ShopCategory.WEAPONS
        self.selected_index = 0
        self.scroll_offset = 0

        # Available items (filtered by tier)
        self.available_items: List[Tuple[str, Any]] = []

        # Animation
        self.animation_time = 0.0
        self.selected_item_preview: Optional[Any] = None

    def open(self, npc_name: str = "Merchant") -> None:
        """Open the shop UI."""
        self.visible = True
        self.npc_name = npc_name
        self.category = ShopCategory.WEAPONS
        self.selected_index = 0
        self.scroll_offset = 0
        self._refresh_items()

    def close(self) -> None:
        """Close the shop UI."""
        self.visible = False

    def _refresh_items(self) -> None:
        """Refresh available items based on category and tier."""
        max_tier = self.game.campaign_state.max_equipment_tier

        if self.category == ShopCategory.CONSUMABLES:
            # Show consumables
            self.available_items = [
                (item_id, item)
                for item_id, item in CONSUMABLES.items()
            ]
        else:
            # Map category to slot
            slot_map = {
                ShopCategory.WEAPONS: SLOT_WEAPON,
                ShopCategory.ARMOR: SLOT_ARMOR,
                ShopCategory.BOOTS: SLOT_BOOTS,
                ShopCategory.CHARMS: SLOT_CHARM,
            }
            slot = slot_map.get(self.category, SLOT_WEAPON)

            # Filter equipment by slot and tier
            self.available_items = [
                (item_id, item)
                for item_id, item in ALL_EQUIPMENT.items()
                if item.slot == slot and item.tier <= max_tier
            ]
            # Sort by tier
            self.available_items.sort(key=lambda x: x[1].tier)

        # Reset selection if needed
        if self.selected_index >= len(self.available_items):
            self.selected_index = max(0, len(self.available_items) - 1)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Returns:
            True if event was consumed
        """
        if not self.visible:
            return False

        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_ESCAPE:
            self.close()
            return True

        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            # Previous category
            categories = list(ShopCategory)
            idx = categories.index(self.category)
            self.category = categories[(idx - 1) % len(categories)]
            self._refresh_items()
            return True

        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            # Next category
            categories = list(ShopCategory)
            idx = categories.index(self.category)
            self.category = categories[(idx + 1) % len(categories)]
            self._refresh_items()
            return True

        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            # Previous item
            if len(self.available_items) > 0:
                self.selected_index = (self.selected_index - 1) % len(self.available_items)
            return True

        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            # Next item
            if len(self.available_items) > 0:
                self.selected_index = (self.selected_index + 1) % len(self.available_items)
            return True

        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Purchase item
            self._purchase_selected()
            return True

        return False

    def _purchase_selected(self) -> None:
        """Attempt to purchase the selected item."""
        if self.selected_index >= len(self.available_items):
            return

        item_id, item = self.available_items[self.selected_index]
        currency = self.game.campaign_state.currency

        if currency < item.cost:
            # Can't afford
            return

        if self.category == ShopCategory.CONSUMABLES:
            # Purchase consumable
            consumable = CONSUMABLES.get(item_id)
            if consumable:
                # Check if we can add to inventory
                inventory = getattr(self.game.campaign_state, 'inventory', None)
                if inventory is None:
                    inventory = PlayerInventory()
                    self.game.campaign_state.inventory = inventory

                if inventory.add_item(item_id):
                    self.game.campaign_state.currency -= item.cost
                    print(f"Purchased {item.name}")
        else:
            # Purchase equipment
            if self.game.campaign_state.purchase_equipment(item_id):
                print(f"Purchased and equipped {item.name}")

    def update(self, dt: float) -> None:
        """Update animation state."""
        if self.visible:
            self.animation_time += dt

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the shop UI."""
        if not self.visible:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Main panel
        panel_width = 800
        panel_height = 550
        panel_x = (LOGICAL_W - panel_width) // 2
        panel_y = (LOGICAL_H - panel_height) // 2

        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, (30, 25, 35), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (100, 80, 60), panel_rect, 3, border_radius=8)

        # Title
        title = FONT_BIG.render(f"{getattr(self, 'npc_name', 'Shop')}", True, (255, 220, 150))
        title_rect = title.get_rect(centerx=panel_rect.centerx, top=panel_y + 15)
        surface.blit(title, title_rect)

        # Currency display
        currency = self.game.campaign_state.currency
        currency_text = FONT.render(f"Fragments: {currency}", True, (255, 215, 0))
        surface.blit(currency_text, (panel_x + 20, panel_y + 20))

        # Category tabs
        tab_y = panel_y + 60
        tab_width = (panel_width - 40) // len(ShopCategory)
        for i, cat in enumerate(ShopCategory):
            tab_x = panel_x + 20 + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width - 5, 30)

            # Highlight selected
            if cat == self.category:
                pygame.draw.rect(surface, (80, 60, 100), tab_rect, border_radius=4)
            else:
                pygame.draw.rect(surface, (40, 35, 50), tab_rect, border_radius=4)
            pygame.draw.rect(surface, (100, 80, 120), tab_rect, 1, border_radius=4)

            tab_text = FONT_SMALL.render(cat.value.title(), True, (255, 255, 255))
            text_rect = tab_text.get_rect(center=tab_rect.center)
            surface.blit(tab_text, text_rect)

        # Item list area
        list_y = tab_y + 45
        list_height = panel_height - 180
        items_visible = list_height // 35

        for i, (item_id, item) in enumerate(self.available_items[:items_visible]):
            item_y = list_y + i * 35
            item_rect = pygame.Rect(panel_x + 20, item_y, panel_width // 2 - 30, 32)

            # Highlight selected
            if i == self.selected_index:
                pygame.draw.rect(surface, (60, 50, 80), item_rect, border_radius=4)
                pygame.draw.rect(surface, (150, 130, 100), item_rect, 2, border_radius=4)
            else:
                pygame.draw.rect(surface, (35, 30, 45), item_rect, border_radius=4)

            # Item info
            if self.category == ShopCategory.CONSUMABLES:
                name_text = item.name
                cost = item.cost
                tier_text = ""
            else:
                tier_name = TIER_NAMES.get(item.tier, "?")
                name_text = f"{item.name}"
                tier_text = f"[{tier_name}]"
                cost = item.cost

            # Check if equipped
            is_equipped = False
            if self.category != ShopCategory.CONSUMABLES:
                equipped_id = self.game.campaign_state.equipped_items.get(item.slot)
                is_equipped = equipped_id == item_id

            # Name color
            name_color = (100, 255, 100) if is_equipped else (255, 255, 255)
            name = FONT_SMALL.render(name_text, True, name_color)
            surface.blit(name, (item_rect.x + 10, item_rect.y + 8))

            # Tier (if equipment)
            if tier_text:
                tier = FONT_SMALL.render(tier_text, True, (180, 180, 200))
                surface.blit(tier, (item_rect.x + 150, item_rect.y + 8))

            # Cost
            can_afford = currency >= cost
            cost_color = (100, 255, 100) if can_afford else (255, 100, 100)
            cost_text = FONT_SMALL.render(f"{cost}", True, cost_color)
            surface.blit(cost_text, (item_rect.right - 60, item_rect.y + 8))

            # Equipped marker
            if is_equipped:
                equipped_marker = FONT_SMALL.render("[E]", True, (100, 255, 100))
                surface.blit(equipped_marker, (item_rect.right - 100, item_rect.y + 8))

        # Selected item details (right side)
        details_x = panel_x + panel_width // 2 + 10
        details_width = panel_width // 2 - 30
        details_rect = pygame.Rect(details_x, list_y, details_width, list_height)
        pygame.draw.rect(surface, (25, 22, 30), details_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 60, 80), details_rect, 1, border_radius=6)

        if 0 <= self.selected_index < len(self.available_items):
            item_id, item = self.available_items[self.selected_index]

            # Item name
            detail_name = FONT.render(item.name, True, (255, 220, 150))
            surface.blit(detail_name, (details_x + 15, list_y + 10))

            # Description
            desc = FONT_SMALL.render(item.description, True, (200, 200, 200))
            surface.blit(desc, (details_x + 15, list_y + 40))

            # Stats (if equipment)
            if self.category != ShopCategory.CONSUMABLES and hasattr(item, 'stats'):
                stats_y = list_y + 70
                stats = item.stats

                stat_lines = [
                    f"HP: +{stats.hp}" if stats.hp else None,
                    f"MP: +{stats.mp}" if stats.mp else None,
                    f"STM: +{stats.stm}" if stats.stm else None,
                    f"STG: +{stats.stg}" if stats.stg else None,
                    f"DEF: +{stats.def_}" if stats.def_ else None,
                    f"SPD: {stats.spd:.2f}x" if stats.spd != 1.0 else None,
                    f"DEX: +{stats.dext}" if stats.dext else None,
                ]

                for stat_line in stat_lines:
                    if stat_line:
                        stat_text = FONT_SMALL.render(stat_line, True, (150, 200, 255))
                        surface.blit(stat_text, (details_x + 15, stats_y))
                        stats_y += 18

        # Instructions
        instructions = "A/D: Category | W/S: Select | SPACE: Buy | ESC: Close"
        inst_text = FONT_SMALL.render(instructions, True, (150, 150, 170))
        inst_rect = inst_text.get_rect(centerx=panel_rect.centerx, bottom=panel_rect.bottom - 15)
        surface.blit(inst_text, inst_rect)
