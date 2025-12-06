"""
Hollow Hub - Act 2 Hub (Enhanced)

The dark, cramped depths after being hollowed.
Uses procedural level generation with fixed seed for consistent layout.
Features patrolling NPCs and mission exit points.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from .base_hub import CampaignHub
from entities.hub_npc import HubNPC
from entities.hub_exit import HubExit, get_missions_for_act, ExitState

if TYPE_CHECKING:
    from core.game import Game


class HollowHub(CampaignHub):
    """
    Hollow Hub - The depths after being hollowed.

    Act 2: Survival in the darkness
    Features:
    - Mysterious patrolling NPCs
    - Challenging mission exits
    - Limited shop access
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.hub_name = "hollow_hub"
        self.title = "Hollow Depths - Refuge"
        self.bg_color = (5, 5, 15)
        self.biome = "hollow"

    def get_act_number(self) -> int:
        return 2

    def get_hub_config_name(self) -> str:
        return "hollow_hub"

    def setup_npcs(self) -> None:
        """Setup Hollow Hub NPCs and mission exits."""

        # ===== PATROLLING NPCs =====

        # Shade Hermit - Mysterious guide
        hermit = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Shade Hermit",
            role="lore",
            dialogue=[
                "Shade Hermit: So... you've been hollowed too.",
                "Shade Hermit: I've lived here for ages... or has it been moments?",
                "Shade Hermit: Time moves strangely in the depths.",
                "Shade Hermit: Your abilities... they're fading, aren't they?",
                "Shade Hermit: The only way forward is through.",
                "Shade Hermit: Collect the scroll fragments. They hold forgotten power.",
            ],
            patrol_range=80,
            speed=25.0
        )
        # Check if unlocked
        hermit.is_unlocked = self.game.campaign_state.npc_unlocked.get("shade_hermit", True)

        # Lost Warrior - Fellow hollowed
        warrior = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Lost Warrior",
            role="trainer",
            dialogue=[
                "Lost Warrior: I was a warrior once... like you.",
                "Lost Warrior: The Veil Maiden took everything from me.",
                "Lost Warrior: But I'm learning... adapting...",
                "Lost Warrior: Even hollowed, we can still fight.",
                "Lost Warrior: Find the Ember Monastery. There is hope there.",
            ],
            patrol_range=120,
            speed=30.0
        )

        # Hollow Watcher - Silent observer
        watcher = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Hollow Watcher",
            role="wanderer",
            dialogue=[
                "Hollow Watcher: ...",
                "Hollow Watcher: *The figure stares silently*",
                "Hollow Watcher: ...deeper...",
            ],
            patrol_range=60,
            speed=15.0
        )

        # Scavenger - Shop NPC (limited)
        scavenger = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Scavenger",
            role="shop",
            dialogue=[
                "Scavenger: Found some things... might be useful.",
                "Scavenger: Not much to trade down here...",
                "Scavenger: Take what you need. We're all just surviving.",
            ],
            is_shop=True,
            patrol_range=100,
            speed=20.0
        )

        # Place NPCs on platforms
        self._place_hub_npcs()

        # ===== MISSION EXITS =====

        missions = get_missions_for_act(2)

        for mission in missions:
            self.exit_manager.create_exit(
                x=0, y=0,
                mission=mission
            )

        self._place_hub_exits()

    def draw(self, surface: pygame.Surface) -> None:
        """Override draw to add atmospheric effects."""
        super().draw(surface)

        # Add darkness vignette effect
        vignette = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)

        # Draw dark gradient at edges
        for i in range(150, 0, -15):
            alpha = int((150 - i) * 0.5)
            # Corners
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (0, 0), i)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (surface.get_width(), 0), i)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (0, surface.get_height()), i)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (surface.get_width(), surface.get_height()), i)

        surface.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
