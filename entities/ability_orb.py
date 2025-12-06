"""
Ability Orb Entity - Rare collectible for unlocking abilities
Rainbow crystalline orb with visual effects
"""

from __future__ import annotations

import math
from typing import Any
import pygame


class AbilityOrb:
    """
    Rare collectible that grants ability unlock progress.
    Persists across playthroughs - not lost on death.
    """

    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.collected = False

        # Animation state
        self.animation_time = 0.0
        self.pulse_speed = 3.0
        self.rotation = 0.0
        self.rotation_speed = 120.0  # degrees per second
        self.bob_offset = 0.0
        self.bob_speed = 2.0
        self.bob_amount = 4.0

        # Visual effects
        self.particle_spawn_timer = 0.0
        self.particles = []  # Store particle data for rendering

        # Colors (rainbow cycle)
        self.colors = [
            (200, 100, 255),  # Purple
            (100, 150, 255),  # Blue
            (100, 255, 255),  # Cyan
            (100, 255, 150),  # Green-cyan
            (150, 100, 255),  # Purple-blue
        ]
        self.color_index = 0.0

    def update(self, dt: float) -> None:
        """Update animation state."""
        if self.collected:
            return

        # Update timers
        self.animation_time += dt
        self.rotation += self.rotation_speed * dt
        if self.rotation >= 360:
            self.rotation -= 360

        # Bob up and down
        self.bob_offset = math.sin(self.animation_time * self.bob_speed) * self.bob_amount

        # Color cycling
        self.color_index += dt * 2.0
        if self.color_index >= len(self.colors):
            self.color_index -= len(self.colors)

        # Particle generation
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer >= 0.1:  # 10 particles per second
            self.particle_spawn_timer = 0.0
            self._spawn_particle()

        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            particle['angle'] += particle['speed'] * dt
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def _spawn_particle(self) -> None:
        """Spawn a sparkle particle orbiting the orb."""
        import random

        particle = {
            'angle': random.uniform(0, 360),
            'radius': random.uniform(14, 18),
            'speed': random.uniform(60, 120),  # degrees per second
            'life': random.uniform(0.5, 1.0),
            'max_life': 1.0,
            'size': random.randint(2, 4),
            'color': random.choice(self.colors),
        }
        self.particles.append(particle)

    def get_current_color(self) -> tuple:
        """Get the current interpolated rainbow color."""
        # Ensure color_index is in valid range with modulo
        idx = int(self.color_index) % len(self.colors)
        next_idx = (idx + 1) % len(self.colors)
        t = (self.color_index % len(self.colors)) - idx

        c1 = self.colors[idx]
        c2 = self.colors[next_idx]

        # Linear interpolation
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)

        return (r, g, b)

    def get_display_rect(self) -> pygame.Rect:
        """Get the rect with bob offset applied."""
        display_rect = self.rect.copy()
        display_rect.y += int(self.bob_offset)
        return display_rect

    def try_collect(self, player_rect: pygame.Rect, game: Any) -> bool:
        """
        Attempt to collect the orb.

        In arcade mode: Adds to unlock manager progress
        In campaign mode: Adds scroll fragment for current act

        Returns:
            True if collected (triggers removal and effects)
        """
        if self.collected:
            return False

        # Check collision with bobbing position
        display_rect = self.get_display_rect()
        if not display_rect.colliderect(player_rect):
            return False

        # Mark as collected
        self.collected = True

        newly_unlocked = []

        # Handle collection based on game mode
        if hasattr(game, 'campaign_mode') and game.campaign_mode:
            # Campaign mode: Add scroll fragment
            newly_unlocked = self._handle_campaign_collection(game)
        else:
            # Arcade mode: Use unlock manager
            unlock_mgr = getattr(game, 'unlock_mgr', None)
            if unlock_mgr:
                newly_unlocked = unlock_mgr.add_ability_orb()

            # Immediately enable newly unlocked abilities in the player (mid-level unlock)
            player = getattr(game, 'player', None)
            if player and newly_unlocked:
                for ability_id in newly_unlocked:
                    player.unlock_ability(ability_id)

        # Trigger collection effects
        self._trigger_collection_effects(game, newly_unlocked)

        return True

    def _handle_campaign_collection(self, game: Any) -> list:
        """
        Handle ability orb collection in campaign mode.

        Adds a scroll fragment for the current act and checks if a scroll was completed.
        In early acts without scrolls, grants currency/fragments instead.

        Returns:
            List of newly unlocked ability names
        """
        from core.campaign import get_scroll_for_act, get_required_fragments_for_scroll

        campaign_state = game.campaign_state
        newly_unlocked = []

        # Get scrolls available in current act
        act_scrolls = get_scroll_for_act(campaign_state.act)

        if not act_scrolls:
            # No scrolls in this act (Acts 0 and 1) - give currency instead
            currency_reward = 75  # Bonus fragments
            campaign_state.add_currency(currency_reward)
            print(f"💎 Ability Orb collected! +{currency_reward} fragments")
            return newly_unlocked

        # For now, pick the first incomplete scroll in the act
        # In a full implementation, you might rotate or let the player choose
        for scroll_id, ability_name in act_scrolls.items():
            if scroll_id not in campaign_state.scrolls_completed:
                # Add fragment to this scroll
                required = get_required_fragments_for_scroll(scroll_id)
                scroll_completed = campaign_state.add_scroll_fragment(scroll_id, required)

                current, total = campaign_state.get_scroll_progress(scroll_id, required)
                print(f"📜 Scroll fragment collected: {scroll_id} ({current}/{total})")

                if scroll_completed:
                    # Scroll is complete! Unlock the ability
                    campaign_state.unlock_ability_from_scroll(scroll_id, ability_name)
                    newly_unlocked.append(ability_name)

                    # Immediately enable in player
                    player = getattr(game, 'player', None)
                    if player:
                        player.unlock_ability(ability_name)
                        print(f"✨ {ability_name} unlocked from scroll: {scroll_id}!")

                # Only collect one fragment per orb
                break

        return newly_unlocked

    def _trigger_collection_effects(self, game: Any, newly_unlocked: list) -> None:
        """Trigger visual/audio effects on collection."""
        # Store collection notification for UI to display
        if hasattr(game, 'ability_orb_collected'):
            game.ability_orb_collected = True

        # Store ability unlock notifications
        if newly_unlocked and hasattr(game, 'ability_unlocked'):
            # Store the first unlocked ability (most common case)
            # If multiple unlocks happen at once, just show the first one
            game.ability_unlocked = newly_unlocked[0]

        # Spawn particle burst on collection
        self._spawn_collection_burst()

        # TODO: Play collection sound (hook for audio system)
        # Sound hook: play "ability_orb_collect" sound effect

    def _spawn_collection_burst(self) -> None:
        """Spawn a burst of particles when collected."""
        import random

        # Create a large burst of particles
        num_particles = 20
        for _ in range(num_particles):
            particle = {
                'angle': random.uniform(0, 360),
                'radius': random.uniform(5, 15),
                'speed': random.uniform(180, 300),  # Faster particles
                'life': random.uniform(0.3, 0.8),
                'max_life': 0.8,
                'size': random.randint(3, 6),
                'color': random.choice(self.colors),
            }
            self.particles.append(particle)

    def draw(self, surface: pygame.Surface, camera_rect: pygame.Rect) -> None:
        """
        Draw the ability orb with all visual effects.

        Args:
            surface: Surface to draw on
            camera_rect: Camera rectangle for world-to-screen conversion
        """
        if self.collected:
            return

        display_rect = self.get_display_rect()

        # Check if on screen
        if not camera_rect.colliderect(display_rect):
            return

        # Convert to screen coordinates
        screen_x = display_rect.centerx - camera_rect.x
        screen_y = display_rect.centery - camera_rect.y

        # Draw glow (outer layer)
        glow_color = self.get_current_color()
        glow_alpha = int(128 + 64 * math.sin(self.animation_time * self.pulse_speed))
        glow_radius = int(display_rect.width * 0.8)

        # Draw multiple glow layers for depth
        for i in range(3, 0, -1):
            radius = glow_radius + i * 3
            alpha = glow_alpha // (i + 1)
            # Create glow surface
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (*glow_color, alpha),
                (radius, radius),
                radius
            )
            surface.blit(
                glow_surf,
                (screen_x - radius, screen_y - radius),
                special_flags=pygame.BLEND_ALPHA_SDL2
            )

        # Draw particles (sparkles orbiting)
        for particle in self.particles:
            angle_rad = math.radians(particle['angle'])
            px = screen_x + math.cos(angle_rad) * particle['radius']
            py = screen_y + math.sin(angle_rad) * particle['radius']

            # Fade based on lifetime
            life_ratio = particle['life'] / particle['max_life']
            particle_alpha = int(255 * life_ratio)

            pygame.draw.circle(
                surface,
                (*particle['color'], particle_alpha),
                (int(px), int(py)),
                particle['size']
            )

        # Draw main orb (core)
        core_color = self.get_current_color()
        pygame.draw.circle(
            surface,
            core_color,
            (screen_x, screen_y),
            display_rect.width // 2
        )

        # Draw highlight (makes it look 3D/crystalline)
        highlight_offset_x = int(display_rect.width * 0.2)
        highlight_offset_y = int(display_rect.width * 0.2)
        highlight_radius = display_rect.width // 4
        pygame.draw.circle(
            surface,
            (255, 255, 255, 200),
            (screen_x - highlight_offset_x, screen_y - highlight_offset_y),
            highlight_radius
        )

        # Draw rotating ring effect
        ring_color = (255, 255, 255, 128)
        ring_radius = display_rect.width // 2 + 2
        ring_width = 2

        # Calculate ring positions based on rotation
        num_segments = 8
        for i in range(num_segments):
            angle = self.rotation + (360 / num_segments) * i
            angle_rad = math.radians(angle)

            # Only draw segments on "visible" side
            if math.cos(angle_rad) > 0:
                x = screen_x + math.cos(angle_rad) * ring_radius
                y = screen_y + math.sin(angle_rad) * ring_radius * 0.3  # Ellipse

                pygame.draw.circle(
                    surface,
                    ring_color,
                    (int(x), int(y)),
                    ring_width
                )
