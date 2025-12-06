"""
Skyroad Hub - Act 4 Summit Approach (Enhanced)

The final preparation area before ascending to face the Hollow Reflection.
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


class SkyHub(CampaignHub):
    """
    Skyroad Hub - The summit approach.

    Act 4: Final preparation before the ultimate trial
    Features:
    - The Advocate for final guidance
    - Peak Guardians
    - Summit path exits
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.hub_name = "sky_hub"
        self.title = "Skyroad - Summit Approach"
        self.bg_color = (18, 28, 45)
        self.biome = "sky"

        # Animation time for clouds
        self.cloud_time = 0.0

    def get_act_number(self) -> int:
        return 4

    def get_hub_config_name(self) -> str:
        return "sky_hub"

    def setup_npcs(self) -> None:
        """Setup Sky Hub NPCs and mission exits."""

        # ===== PATROLLING NPCs =====

        # The Advocate - Final guide
        advocate = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="The Advocate",
            role="story",
            dialogue=[
                "Advocate: You've made it this far. Remarkable.",
                "Advocate: The summit holds your greatest challenge...",
                "Advocate: Your own reflection, twisted by the Hollow.",
                "Advocate: It knows all your moves. All your weaknesses.",
                "Advocate: Only by accepting what you've lost can you win.",
                "Advocate: When you're ready, take the path to the summit.",
            ],
            patrol_range=120,
            speed=30.0
        )
        advocate.is_unlocked = self.game.campaign_state.npc_unlocked.get("advocate", True)

        # Peak Guardian - Warnings
        guardian = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Peak Guardian",
            role="guide",
            dialogue=[
                "Peak Guardian: Few reach this height.",
                "Peak Guardian: Fewer still survive what comes next.",
                "Peak Guardian: The Hollow Reflection awaits at the world's peak.",
                "Peak Guardian: It is you... but it is not you.",
                "Peak Guardian: Defeat it, and you'll find your Inner Lantern.",
            ],
            patrol_range=100,
            speed=35.0
        )

        # Weathered Monk - Wisdom
        monk = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Weathered Monk",
            role="lore",
            dialogue=[
                "Weathered Monk: The wind here never stops...",
                "Weathered Monk: It carries away all that is unnecessary.",
                "Weathered Monk: By the time you reach the summit...",
                "Weathered Monk: Only your true self will remain.",
                "Weathered Monk: Are you ready to face it?",
            ],
            patrol_range=80,
            speed=25.0
        )

        # Sky Wanderer - Ambient
        wanderer = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Sky Wanderer",
            role="wanderer",
            dialogue=[
                "Sky Wanderer: The view from here... breathtaking.",
                "Sky Wanderer: I've climbed so far, yet the summit still beckons.",
                "Sky Wanderer: Good luck up there, friend.",
            ],
            patrol_range=150,
            speed=40.0
        )

        # Summit Shopkeeper - Final equipment
        shopkeeper = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Summit Merchant",
            role="shop",
            dialogue=[
                "Summit Merchant: The finest gear for the final ascent.",
                "Summit Merchant: You'll need every advantage against what awaits.",
            ],
            is_shop=True,
            patrol_range=70,
            speed=20.0
        )

        # Place NPCs on platforms
        self._place_hub_npcs()

        # ===== MISSION EXITS =====

        missions = get_missions_for_act(4)

        for mission in missions:
            self.exit_manager.create_exit(
                x=0, y=0,
                mission=mission
            )

        self._place_hub_exits()

    def update(self, dt: float) -> None:
        """Update with cloud animation."""
        super().update(dt)
        self.cloud_time += dt * 20  # Slow cloud movement

    def draw(self, surface: pygame.Surface) -> None:
        """Override draw to add wind/cloud effects."""
        super().draw(surface)

        # Add cloud effects
        cloud_color = (100, 130, 170, 60)

        for i in range(5):
            y = 80 + i * 100
            # Moving clouds based on time
            x_offset = int((self.cloud_time + i * 50) % (surface.get_width() + 250)) - 200

            cloud_surface = pygame.Surface((200, 40), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surface, cloud_color, (0, 5, 200, 30))
            pygame.draw.ellipse(cloud_surface, cloud_color, (30, 0, 140, 40))

            surface.blit(cloud_surface, (x_offset, y), special_flags=pygame.BLEND_ADD)

            # Second layer of clouds
            x_offset2 = int((self.cloud_time * 0.7 + i * 80) % (surface.get_width() + 300)) - 250
            surface.blit(cloud_surface, (x_offset2, y + 30), special_flags=pygame.BLEND_ADD)
