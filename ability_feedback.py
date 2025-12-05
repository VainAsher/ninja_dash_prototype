"""
Ability Activation Feedback - Visual feedback for ability usage
Shows brief popups when abilities are activated, on cooldown, fail, etc.
"""

import pygame
from settings import FONT, FONT_SMALL


class AbilityFeedback:
    """Shows brief popup messages when abilities are used."""

    def __init__(self):
        self.messages = []  # List of {text, timer, color, y_offset}
        self.max_messages = 3  # Show at most 3 messages at once

    def show(self, ability_name: str, status: str):
        """
        Show feedback for an ability activation.

        Args:
            ability_name: Name of the ability (e.g., "Dash", "Shadow Step")
            status: One of "activated", "cooldown", "no_charges", "failed"
        """
        # Define colors for different statuses
        colors = {
            "activated": (100, 255, 140),  # Green
            "cooldown": (255, 200, 80),    # Orange/yellow
            "no_charges": (255, 100, 100), # Red
            "failed": (200, 100, 100)       # Dark red
        }

        # Define messages for different statuses
        messages = {
            "activated": f"{ability_name}!",
            "cooldown": f"{ability_name} on cooldown",
            "no_charges": f"No {ability_name} charges",
            "failed": f"{ability_name} failed"
        }

        # Remove oldest message if at max capacity
        if len(self.messages) >= self.max_messages:
            self.messages.pop(0)

        # Add new message
        self.messages.append({
            'text': messages.get(status, ability_name),
            'timer': 1.5,  # Display for 1.5 seconds
            'color': colors.get(status, (200, 200, 200)),
            'alpha': 255
        })

    def update(self, dt: float):
        """Update message timers and remove expired messages."""
        for msg in self.messages[:]:
            msg['timer'] -= dt
            if msg['timer'] <= 0:
                self.messages.remove(msg)
            else:
                # Fade out in last 0.5 seconds
                if msg['timer'] < 0.5:
                    msg['alpha'] = int(255 * (msg['timer'] / 0.5))
                else:
                    msg['alpha'] = 255

    def draw(self, surf: pygame.Surface, x: int, y: int):
        """
        Draw feedback messages.

        Args:
            surf: Surface to draw on
            x: X position (typically player.x or center of screen)
            y: Y position (typically above player)
        """
        y_offset = 0
        spacing = 25

        for msg in self.messages:
            # Create text with color
            text = FONT_SMALL.render(msg['text'], True, msg['color'])

            # Apply alpha for fade effect
            text.set_alpha(msg['alpha'])

            # Center text horizontally
            text_rect = text.get_rect(center=(x, y + y_offset))

            # Draw semi-transparent background
            bg_rect = text_rect.inflate(16, 8)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_alpha = min(180, msg['alpha'])
            bg_surf.fill((0, 0, 0, bg_alpha))
            surf.blit(bg_surf, bg_rect.topleft)

            # Draw text
            surf.blit(text, text_rect)

            y_offset += spacing

    def clear(self):
        """Clear all messages."""
        self.messages.clear()

    def has_messages(self) -> bool:
        """Check if there are active messages."""
        return len(self.messages) > 0
