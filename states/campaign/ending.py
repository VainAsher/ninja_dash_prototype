"""
Campaign Ending - Beacon Restoration

Final cutscene after defeating the Hollow Reflection and restoring the Inner Lantern.
Shows the Beacon being relit and the world recovering from the Hollow.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from settings import LOGICAL_W, LOGICAL_H, FONT, FONT_BIG
from states.base import GameState

if TYPE_CHECKING:
    from core.game import Game


class CampaignEnding(GameState):
    """
    Ending cutscene for Hollowed Ninja campaign.

    Shows the restoration of the Beacon and the end of the Hollow's spread.
    """

    def __init__(self, game: Game):
        super().__init__(game)
        self.timer = 0.0
        self.scene_index = 0
        self.scenes = [
            {
                "text": [
                    "The Hollow Reflection shatters into a thousand fragments of darkness.",
                    "From its core, a brilliant light emerges...",
                    "Your Inner Lantern.",
                ],
                "duration": 5.0,
                "bg_color": (10, 5, 15),  # Dark purple
            },
            {
                "text": [
                    "The light spreads, pushing back the Hollow.",
                    "The Beacon above awakens, responding to your Inner Lantern.",
                    "One by one, the lanterns of the Heights rekindle.",
                ],
                "duration": 5.0,
                "bg_color": (20, 15, 30),  # Lighter purple
            },
            {
                "text": [
                    "The world breathes again.",
                    "The Hollow recedes, not destroyed, but held at bay.",
                    "As long as the Inner Lantern burns, the darkness cannot return.",
                ],
                "duration": 5.0,
                "bg_color": (30, 25, 40),  # Even lighter
            },
            {
                "text": [
                    "You stand at the summit, lantern in hand.",
                    "The Veil Maiden's curse is broken.",
                    "You are whole once more.",
                ],
                "duration": 5.0,
                "bg_color": (40, 35, 50),  # Brightening
            },
            {
                "text": [
                    "--- Hollowed Ninja: Complete ---",
                    "",
                    "Thank you for playing!",
                ],
                "duration": 10.0,
                "bg_color": (50, 45, 70),  # Final bright purple
            },
        ]

    def enter(self) -> None:
        """Called when entering the ending."""
        self.timer = 0.0
        self.scene_index = 0
        print("🎬 Campaign Ending: Beacon Restored")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input - allow skipping scenes."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Skip to next scene
                self.scene_index += 1
                self.timer = 0.0

                if self.scene_index >= len(self.scenes):
                    # Ending complete, return to menu
                    self.game.campaign_mode = False
                    self.game.change_state("menu")
            elif event.key == pygame.K_ESCAPE:
                # Skip to menu immediately
                self.game.campaign_mode = False
                self.game.change_state("menu")

    def update(self, dt: float) -> None:
        """Update ending timer and advance scenes."""
        self.timer += dt

        if self.scene_index < len(self.scenes):
            scene = self.scenes[self.scene_index]
            if self.timer >= scene["duration"]:
                # Advance to next scene
                self.scene_index += 1
                self.timer = 0.0

        # If all scenes complete, return to menu
        if self.scene_index >= len(self.scenes):
            self.game.campaign_mode = False
            self.game.change_state("menu")

    def draw(self, surface: pygame.Surface) -> None:
        """Draw ending cutscene."""
        if self.scene_index >= len(self.scenes):
            return

        scene = self.scenes[self.scene_index]

        # Background color (brightens over time)
        bg_color = scene["bg_color"]
        surface.fill(bg_color)

        # Draw lantern glow in center (gets brighter with each scene)
        glow_strength = (self.scene_index + 1) * 50
        glow = pygame.Surface((200, 200), pygame.SRCALPHA)
        for i in range(100, 0, -10):
            alpha = int(glow_strength * (100 - i) / 100)
            alpha = min(alpha, 255)
            color = (255, 220, 150, alpha)
            pygame.draw.circle(glow, color, (100, 100), i)

        glow_x = (LOGICAL_W - 200) // 2
        glow_y = (LOGICAL_H - 200) // 2
        surface.blit(glow, (glow_x, glow_y), special_flags=pygame.BLEND_ALPHA_SDL2)

        # Draw text lines
        text_y = LOGICAL_H // 2 + 150
        line_spacing = 40

        for i, line in enumerate(scene["text"]):
            if line == "--- Hollowed Ninja: Complete ---":
                # Title line - larger and centered
                text = FONT_BIG.render(line, True, (255, 220, 150))
                text_rect = text.get_rect(centerx=LOGICAL_W // 2, centery=LOGICAL_H // 2 - 50)
            else:
                # Regular lines
                text = FONT.render(line, True, (255, 255, 255))
                text_rect = text.get_rect(centerx=LOGICAL_W // 2, top=text_y + (i * line_spacing))

            # Fade in effect
            fade_time = 1.0
            alpha = min(255, int((self.timer / fade_time) * 255))
            text.set_alpha(alpha)

            surface.blit(text, text_rect)

        # Draw progress indicator
        progress_text = f"Scene {self.scene_index + 1}/{len(self.scenes)}"
        progress = FONT.render(progress_text, True, (150, 150, 150))
        progress_rect = progress.get_rect(right=LOGICAL_W - 20, bottom=LOGICAL_H - 20)
        surface.blit(progress, progress_rect)

        # Draw skip prompt
        prompt = FONT.render("SPACE: Next | ESC: Skip to Menu", True, (180, 180, 180))
        prompt_rect = prompt.get_rect(centerx=LOGICAL_W // 2, bottom=LOGICAL_H - 20)
        surface.blit(prompt, prompt_rect)
