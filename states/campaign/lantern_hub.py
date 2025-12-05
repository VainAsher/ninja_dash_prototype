"""
Lantern Hub - Act 0 Starting Hub

The warm, welcoming starting area of the campaign.
Safe haven with basic NPCs and mission access.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .base_hub import CampaignHub, NPC, MissionBoard

if TYPE_CHECKING:
    from core.game import Game


class LanternHub(CampaignHub):
    """
    Lantern Hub - The starting safe haven.

    Act 0: Tutorial and early missions
    NPCs: Guides, trainers, and friendly faces
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.title = "Lantern Heights - Safe Haven"
        self.bg_color = (15, 15, 30)  # Dark blue-black

    def get_act_number(self) -> int:
        return 0

    def setup_npcs(self) -> None:
        """Setup Lantern Hub NPCs and mission board."""
        # Mission board (center-right)
        self.mission_board = MissionBoard(
            name="Mission Board",
            x=900,
            y=450
        )

        # Guide NPC (left side)
        guide = NPC(
            name="Elder Guide",
            x=200,
            y=500,
            color=(100, 200, 150)
        )
        guide.dialogue = [
            "Elder Guide: Welcome to Lantern Heights, young ninja.",
            "Elder Guide: This is a safe place. Take your time to prepare.",
            "Elder Guide: When you're ready, check the Mission Board to begin your trials.",
            "Elder Guide: Remember: collect coins to unlock the exit in each level.",
        ]
        self.npcs.append(guide)

        # Trainer NPC (center-left)
        trainer = NPC(
            name="Master Jin",
            x=400,
            y=500,
            color=(255, 150, 50)
        )
        trainer.dialogue = [
            "Master Jin: The path of the ninja requires mastery of movement.",
            "Master Jin: Use WASD or Arrow Keys to move and jump.",
            "Master Jin: Your dash ability (Shift) is essential for traversal.",
            "Master Jin: Wall jumps will save you when platforms fail.",
        ]
        self.npcs.append(trainer)

        # Lore NPC (right side)
        lorekeeper = NPC(
            name="Lorekeeper",
            x=700,
            y=500,
            color=(200, 150, 255)
        )
        lorekeeper.dialogue = [
            "Lorekeeper: The Lantern Heights were once filled with light...",
            "Lorekeeper: But shadows grow stronger each day.",
            "Lorekeeper: We need skilled warriors to venture into the depths.",
            "Lorekeeper: Be careful out there, traveler.",
        ]
        self.npcs.append(lorekeeper)
