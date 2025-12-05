"""
Hollow Hub - Act 2 Recovery Hub

The dark, oppressive area after the Veil Maiden strips your power.
A place of recovery and rebuilding.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .base_hub import CampaignHub, NPC, MissionBoard

if TYPE_CHECKING:
    from core.game import Game


class HollowHub(CampaignHub):
    """
    Hollow Hub - The depths after losing your light.

    Act 2: Recovery and rebuilding
    NPCs: Shade Hermit, survivors
    Theme: Dark, oppressive, but not hopeless
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.title = "Hollow Depths - Refuge"
        self.bg_color = (8, 8, 18)  # Very dark purple-black

    def get_act_number(self) -> int:
        return 2

    def setup_npcs(self) -> None:
        """Setup Hollow Hub NPCs and mission board."""
        # Mission board (center-right) - appears more ominous
        self.mission_board = MissionBoard(
            name="Descent Map",
            x=850,
            y=450
        )

        # Shade Hermit (mysterious guide) - unlocked after first Hollow mission
        hermit = NPC(
            name="Shade Hermit",
            x=250,
            y=500,
            color=(80, 40, 120)  # Dark purple
        )
        hermit.is_unlocked = self.game.campaign_state.npc_unlocked.get("shade_hermit", False)
        hermit.dialogue = [
            "Shade Hermit: ...So you fell here too.",
            "Shade Hermit: The Veil Maiden takes from all who face her.",
            "Shade Hermit: But you're not hollow. Not yet.",
            "Shade Hermit: These depths hold fragments of forgotten scrolls...",
            "Shade Hermit: Collect them. Piece together what was lost.",
            "Shade Hermit: Or remain empty forever.",
        ]
        self.npcs.append(hermit)

        # Survivor NPC (center) - always available
        survivor = NPC(
            name="Lost Warrior",
            x=500,
            y=500,
            color=(60, 60, 90)
        )
        survivor.dialogue = [
            "Lost Warrior: I... I can't remember who I was.",
            "Lost Warrior: The darkness took everything.",
            "Lost Warrior: Are you here to save us? Or join us?",
            "Lost Warrior: Be careful. The deeper you go, the less returns.",
        ]
        self.npcs.append(survivor)

        # Warning NPC (right side)
        watcher = NPC(
            name="Hollow Watcher",
            x=650,
            y=500,
            color=(100, 40, 40)
        )
        watcher.dialogue = [
            "Hollow Watcher: Turn back while you still can.",
            "Hollow Watcher: Every step deeper steals more of you.",
            "Hollow Watcher: But if you must go on... hunt for the scrolls.",
            "Hollow Watcher: They're the only way to regain what was taken.",
        ]
        self.npcs.append(watcher)

    def draw(self, surface):
        """Override draw to add atmospheric effects."""
        super().draw(surface)

        # Add darkness vignette effect
        import pygame
        # Create dark overlay at edges
        vignette = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        # Draw dark circles at edges
        for i in range(200, 0, -20):
            alpha = int((200 - i) * 0.3)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (0, 0), i)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (surface.get_width(), 0), i)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (0, surface.get_height()), i)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (surface.get_width(), surface.get_height()), i)

        surface.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
