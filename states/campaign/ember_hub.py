"""
Ember Monastery - Act 3 Hub (Enhanced)

The warm monastery where you rebuild your skills and gear.
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


class EmberHub(CampaignHub):
    """
    Ember Monastery - Place of rebirth and crafting.

    Act 3: Rebuilding power and equipment
    Features:
    - Smith Monk shop
    - Training masters
    - Mission exits for monastery trials
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.hub_name = "ember_hub"
        self.title = "Ember Monastery - Forge of Renewal"
        self.bg_color = (25, 15, 10)
        self.biome = "ember"

    def get_act_number(self) -> int:
        return 3

    def get_hub_config_name(self) -> str:
        return "ember_hub"

    def setup_npcs(self) -> None:
        """Setup Ember Hub NPCs and mission exits."""

        # ===== PATROLLING NPCs =====

        # Smith Monk - Equipment upgrades
        smith = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Smith Monk",
            role="shop",
            dialogue=[
                "Smith Monk: The forge burns eternal here.",
                "Smith Monk: I can craft equipment worthy of your journey.",
                "Smith Monk: Bring me fragments, and I'll arm you for battle.",
            ],
            is_shop=True,
            patrol_range=60,
            speed=20.0
        )
        smith.is_unlocked = self.game.campaign_state.npc_unlocked.get("smith_monk", True)

        # Listening Elder - Lore and guidance
        elder = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Listening Elder",
            role="lore",
            dialogue=[
                "Listening Elder: Ah, another soul seeking answers.",
                "Listening Elder: You carry the mark of the Hollow...",
                "Listening Elder: Yet you resist its pull. Impressive.",
                "Listening Elder: The Veil Maiden was once human, like us.",
                "Listening Elder: Her story is a warning. Do not let vengeance consume you.",
                "Listening Elder: Find your Inner Lantern before the final trial.",
            ],
            patrol_range=100,
            speed=25.0
        )
        elder.is_unlocked = self.game.campaign_state.npc_unlocked.get("listening_elder", True)

        # Master Kenzo - Training
        trainer = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Master Kenzo",
            role="trainer",
            dialogue=[
                "Master Kenzo: You're getting stronger. I can see it.",
                "Master Kenzo: But strength without technique is wasted.",
                "Master Kenzo: Remember: timing beats power.",
                "Master Kenzo: The scrolls you find will teach you new techniques.",
                "Master Kenzo: Master them before facing the summit.",
            ],
            patrol_range=150,
            speed=35.0
        )

        # Forge Apprentice - Ambient
        apprentice = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Forge Apprentice",
            role="wanderer",
            dialogue=[
                "Forge Apprentice: The flames here never die...",
                "Forge Apprentice: They say they've burned since the first age.",
                "Forge Apprentice: I hope to be a master smith one day!",
            ],
            patrol_range=80,
            speed=40.0
        )

        # Place NPCs on platforms
        self._place_hub_npcs()

        # ===== MISSION EXITS =====

        missions = get_missions_for_act(3)

        for mission in missions:
            self.exit_manager.create_exit(
                x=0, y=0,
                mission=mission
            )

        self._place_hub_exits()

    def draw(self, surface: pygame.Surface) -> None:
        """Override draw to add warm glow effects."""
        super().draw(surface)

        # Add warm glow from forge
        glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(60, 0, -5):
            alpha = int((60 - i) * 2)
            color = (255, 150, 50, alpha)
            pygame.draw.circle(glow, color, (60, 60), i)

        # Place multiple glows around the monastery
        glow_positions = [(100, 300), (400, 200), (700, 350)]
        for pos in glow_positions:
            surface.blit(glow, pos, special_flags=pygame.BLEND_ADD)
