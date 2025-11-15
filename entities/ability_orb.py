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
        idx = int(self.color_index)
        next_idx = (idx + 1) % len(self.colors)
        t = self.color_index - idx

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

        # Notify unlock manager
        unlock_mgr = getattr(game, 'unlock_mgr', None)
        if unlock_mgr:
            unlock_mgr.add_ability_orb()

        # Trigger collection effects
        self._trigger_collection_effects(game)

        return True

    def _trigger_collection_effects(self, game: Any) -> None:
        """Trigger visual/audio effects on collection."""
        # Store collection notification for UI to display
        if hasattr(game, 'ability_orb_collected'):
            game.ability_orb_collected = True

        # TODO: Play collection sound
        # TODO: Trigger screen flash
        # TODO: Spawn particle burst

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
