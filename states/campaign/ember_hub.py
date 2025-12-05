"""
Ember Monastery - Act 3 Rebuilding Hub

The warm monastery where you rebuild your skills and gear.
Forge, training grounds, and wise monks.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .base_hub import CampaignHub, NPC, MissionBoard, Shop

if TYPE_CHECKING:
    from core.game import Game


class EmberHub(CampaignHub):
    """
    Ember Monastery - Place of rebirth and crafting.

    Act 3: Rebuilding power and equipment
    NPCs: Smith Monk, Listening Elder
    Theme: Warm, hopeful, industrious
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.title = "Ember Monastery - Forge of Renewal"
        self.bg_color = (25, 15, 10)  # Dark reddish-brown

    def get_act_number(self) -> int:
        return 3

    def setup_npcs(self) -> None:
        """Setup Ember Hub NPCs and mission board."""
        # Mission board (center-right)
        self.mission_board = MissionBoard(
            name="Training Hall",
            x=900,
            y=450
        )

        # Smith Monk (equipment upgrades) - unlocked after Weightbound Ogre
        smith = NPC(
            name="Smith Monk",
            x=200,
            y=500,
            color=(255, 120, 40)  # Bright orange
        )
        smith.is_unlocked = self.game.campaign_state.npc_unlocked.get("smith_monk", True)  # Start unlocked for testing
        # Smith Monk is now a shop! (No dialogue needed, opens shop directly)
        self.npcs.append(smith)

        # Register Smith Monk as a shop
        self.shops["Smith Monk"] = Shop(smith)

        # Listening Elder (lore and guidance)
        elder = NPC(
            name="Listening Elder",
            x=450,
            y=500,
            color=(180, 140, 80)  # Golden brown
        )
        elder.is_unlocked = self.game.campaign_state.npc_unlocked.get("listening_elder", True)  # Start unlocked
        elder.dialogue = [
            "Listening Elder: Ah, another soul seeking answers.",
            "Listening Elder: You carry the mark of the Hollow...",
            "Listening Elder: Yet you resist its pull. Impressive.",
            "Listening Elder: The Veil Maiden was once human, like us.",
            "Listening Elder: Her story is a warning. Do not let vengeance consume you.",
            "Listening Elder: Find your Inner Lantern before the final trial.",
        ]
        self.npcs.append(elder)

        # Training Master (combat tips)
        trainer = NPC(
            name="Master Kenzo",
            x=700,
            y=500,
            color=(200, 80, 60)
        )
        trainer.dialogue = [
            "Master Kenzo: You're getting stronger. I can see it.",
            "Master Kenzo: But strength without technique is wasted.",
            "Master Kenzo: Remember: timing beats power.",
            "Master Kenzo: The scrolls you find will teach you new techniques.",
            "Master Kenzo: Master them before facing the summit.",
        ]
        self.npcs.append(trainer)

    def draw(self, surface):
        """Override draw to add warm glow effects."""
        super().draw(surface)

        # Add warm glow from forge
        import pygame
        glow = pygame.Surface((100, 100), pygame.SRCALPHA)
        for i in range(50, 0, -5):
            alpha = int((50 - i) * 2)
            color = (255, 150, 50, alpha)
            pygame.draw.circle(glow, color, (50, 50), i)

        # Place glow near smith
        surface.blit(glow, (150, 420), special_flags=pygame.BLEND_ALPHA_SDL2)
