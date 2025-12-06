"""
Lantern Hub - Act 0 Starting Hub (Enhanced)

The warm, welcoming starting area of the campaign.
Uses procedural level generation with fixed seed for consistent layout.
Features patrolling NPCs and mission exit points.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .base_hub import CampaignHub
from entities.hub_npc import HubNPC
from entities.hub_exit import HubExit, get_missions_for_act, ExitState

if TYPE_CHECKING:
    from core.game import Game


class LanternHub(CampaignHub):
    """
    Lantern Hub - The starting safe haven.

    Act 0: Tutorial and early missions
    Features:
    - Patrolling guide NPCs
    - Multiple mission exits
    - Shop for equipment
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.hub_name = "lantern_hub"
        self.title = "Lantern Heights - Safe Haven"
        self.bg_color = (15, 15, 30)
        self.biome = "lantern"

    def get_act_number(self) -> int:
        return 0

    def get_hub_config_name(self) -> str:
        return "lantern_hub"

    def setup_npcs(self) -> None:
        """Setup Lantern Hub NPCs and mission exits using new systems."""

        # ===== PATROLLING NPCs =====

        # Elder Guide - Main guide NPC
        guide = self.npc_manager.spawn_npc(
            x=0, y=0,  # Will be positioned by _place_hub_npcs
            name="Elder Guide",
            role="guide",
            dialogue=[
                "Elder Guide: Welcome to Lantern Heights, young ninja.",
                "Elder Guide: This is a safe place. Explore and prepare yourself.",
                "Elder Guide: When you're ready, find a mission portal to begin your trials.",
                "Elder Guide: Remember: collect coins to unlock the exit in each level.",
                "Elder Guide: You can use all your movement abilities here - practice!",
            ],
            patrol_range=150,
            speed=35.0
        )

        # Master Jin - Trainer NPC
        trainer = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Master Jin",
            role="trainer",
            dialogue=[
                "Master Jin: The path of the ninja requires mastery of movement.",
                "Master Jin: Use WASD or Arrow Keys to move and jump.",
                "Master Jin: Your dash ability (Shift) is essential for traversal.",
                "Master Jin: Wall jumps will save you when platforms fail.",
                "Master Jin: Practice here - there are no hazards in this haven.",
            ],
            patrol_range=120,
            speed=40.0
        )

        # Lorekeeper - Story NPC
        lorekeeper = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Lorekeeper",
            role="lore",
            dialogue=[
                "Lorekeeper: The Lantern Heights were once filled with light...",
                "Lorekeeper: But shadows grow stronger each day.",
                "Lorekeeper: We need skilled warriors to venture into the depths.",
                "Lorekeeper: Beyond the safe lands, you will face the Veil Maiden.",
                "Lorekeeper: Be careful out there, traveler.",
            ],
            patrol_range=100,
            speed=30.0
        )

        # Smith Apprentice - Shop NPC
        smith = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Smith Apprentice",
            role="shop",
            dialogue=[
                "Smith Apprentice: Welcome to the forge!",
                "Smith Apprentice: I can outfit you with basic equipment.",
                "Smith Apprentice: Fragments you collect can be traded for gear.",
            ],
            is_shop=True,
            patrol_range=80,
            speed=25.0
        )

        # Wandering Villager - Ambient NPC
        villager = self.npc_manager.spawn_npc(
            x=0, y=0,
            name="Villager",
            role="wanderer",
            dialogue=[
                "Villager: It's peaceful here... for now.",
                "Villager: Good luck on your missions!",
            ],
            patrol_range=200,
            speed=45.0
        )

        # Place NPCs on platforms
        self._place_hub_npcs()

        # ===== MISSION EXITS =====

        # Get missions for Act 0
        missions = get_missions_for_act(0)

        for mission in missions:
            exit_point = self.exit_manager.create_exit(
                x=0, y=0,  # Will be positioned by _place_hub_exits
                mission=mission
            )

        # Place exits and update availability
        self._place_hub_exits()
