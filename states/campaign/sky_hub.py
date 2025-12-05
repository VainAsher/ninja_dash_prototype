"""
Skyroad Hub - Act 4 Summit Approach

The final preparation area before ascending to face the Hollow Reflection.
Cold, windswept, at the edge of the world.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .base_hub import CampaignHub, NPC, MissionBoard

if TYPE_CHECKING:
    from core.game import Game


class SkyHub(CampaignHub):
    """
    Skyroad Hub - The summit approach.

    Act 4: Final preparation before the ultimate trial
    NPCs: Advocate, Peak Guardians
    Theme: Airy, bright but cold, anticipatory
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.title = "Skyroad - Summit Approach"
        self.bg_color = (18, 28, 45)  # Dark blue-gray

    def get_act_number(self) -> int:
        return 4

    def setup_npcs(self) -> None:
        """Setup Sky Hub NPCs and mission board."""
        # Mission board (center-right) - final trials
        self.mission_board = MissionBoard(
            name="Summit Path",
            x=880,
            y=450
        )

        # The Advocate (final upgrades and preparation)
        advocate = NPC(
            name="The Advocate",
            x=300,
            y=500,
            color=(200, 230, 255)  # Bright sky blue
        )
        advocate.is_unlocked = self.game.campaign_state.npc_unlocked.get("advocate", True)  # Start unlocked
        advocate.dialogue = [
            "Advocate: You've made it this far. Remarkable.",
            "Advocate: The summit holds your greatest challenge...",
            "Advocate: Your own reflection, twisted by the Hollow.",
            "Advocate: It knows all your moves. All your weaknesses.",
            "Advocate: Only by accepting what you've lost can you win.",
            "Advocate: When you're ready, take the path to the summit.",
        ]
        self.npcs.append(advocate)

        # Peak Guardian (warnings)
        guardian = NPC(
            name="Peak Guardian",
            x=550,
            y=500,
            color=(140, 180, 220)
        )
        guardian.dialogue = [
            "Peak Guardian: Few reach this height.",
            "Peak Guardian: Fewer still survive what comes next.",
            "Peak Guardian: The Hollow Reflection awaits at the world's peak.",
            "Peak Guardian: It is you... but it is not you.",
            "Peak Guardian: Defeat it, and you'll find your Inner Lantern.",
        ]
        self.npcs.append(guardian)

        # Weathered Monk (final wisdom)
        monk = NPC(
            name="Weathered Monk",
            x=700,
            y=500,
            color=(100, 120, 140)
        )
        monk.dialogue = [
            "Weathered Monk: The wind here never stops...",
            "Weathered Monk: It carries away all that is unnecessary.",
            "Weathered Monk: By the time you reach the summit...",
            "Weathered Monk: Only your true self will remain.",
            "Weathered Monk: Are you ready to face it?",
        ]
        self.npcs.append(monk)

    def draw(self, surface):
        """Override draw to add wind/cloud effects."""
        super().draw(surface)

        # Add cloud effects (simple horizontal lines)
        import pygame
        cloud_color = (60, 80, 110, 100)

        # Draw moving clouds (use game time for animation if available)
        for i in range(5):
            y = 100 + i * 80
            x_offset = (i * 30) % 200
            cloud_surface = pygame.Surface((200, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surface, cloud_color, (0, 0, 200, 30))
            surface.blit(cloud_surface, (x_offset, y), special_flags=pygame.BLEND_ALPHA_SDL2)
            surface.blit(cloud_surface, (x_offset + 400, y), special_flags=pygame.BLEND_ALPHA_SDL2)
            surface.blit(cloud_surface, (x_offset + 800, y), special_flags=pygame.BLEND_ALPHA_SDL2)
