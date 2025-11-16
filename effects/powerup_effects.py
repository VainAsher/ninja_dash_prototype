"""
Powerup Visual Effects Manager

Handles visual feedback for active powerups including:
- Speed boost visual effects (speed lines, aura)
- Triple jump particle effects
- Magnet visualization (coin highlighting)
- HUD indicators for active powerups
"""

import pygame
import math
from typing import List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class Particle:
    """A simple particle for effects."""
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    max_lifetime: float
    color: Tuple[int, int, int]
    size: float

    def update(self, dt: float) -> bool:
        """
        Update particle position and lifetime.

        Returns:
            True if particle is still alive
        """
        self.x += self.vx * dt * 60  # Normalize to 60 FPS
        self.y += self.vy * dt * 60
        self.lifetime -= dt
        return self.lifetime > 0

    def get_alpha(self) -> int:
        """Get alpha value based on lifetime."""
        return int(255 * (self.lifetime / self.max_lifetime))


class PowerupEffectManager:
    """
    Manages visual effects for active powerups.

    Provides visual feedback to the player about which powerups are active
    and creates particle effects for various powerup actions.
    """

    def __init__(self):
        """Initialize the powerup effect manager."""
        self.particles: List[Particle] = []
        self.speed_lines: List[Tuple[float, float, float, float]] = []
        self.aura_pulse = 0.0

        # Effect settings
        self.speed_line_count = 15
        self.speed_line_length = 30
        self.speed_line_speed = 200

        # Colors
        self.speed_boost_color = (255, 200, 50)
        self.triple_jump_color = (100, 255, 200)
        self.extra_jump_color = (150, 255, 150)
        self.magnet_color = (255, 215, 0)

    def update(self, dt: float, player: Any):
        """
        Update all visual effects.

        Args:
            dt: Delta time
            player: Player instance
        """
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Update aura pulse
        self.aura_pulse += dt * 3.0
        if self.aura_pulse > math.pi * 2:
            self.aura_pulse -= math.pi * 2

        # Generate speed lines if speed boost is active
        if player.speed_boost_timer > 0 and abs(player.vx) > 3:
            self._generate_speed_lines(player, dt)

        # Update speed lines
        self._update_speed_lines(dt)

    def _generate_speed_lines(self, player: Any, dt: float):
        """Generate speed lines for speed boost effect."""
        # Limit generation rate
        if len(self.speed_lines) < self.speed_line_count:
            import random

            # Create speed line behind player
            direction = -1 if player.vx > 0 else 1
            line_x = player.rect.centerx + direction * random.randint(20, 40)
            line_y = player.rect.centery + random.randint(-20, 20)

            # Line velocity (moves opposite to player movement)
            line_vx = direction * self.speed_line_speed

            self.speed_lines.append((line_x, line_y, line_vx, 1.0))  # x, y, vx, alpha

    def _update_speed_lines(self, dt: float):
        """Update speed line positions and fade."""
        updated_lines = []
        for x, y, vx, alpha in self.speed_lines:
            # Move line
            x += vx * dt
            # Fade out
            alpha -= dt * 2
            if alpha > 0:
                updated_lines.append((x, y, vx, alpha))

        self.speed_lines = updated_lines

    def create_jump_particles(self, x: float, y: float, is_triple_jump: bool = False):
        """
        Create particles for jump effect.

        Args:
            x: X position
            y: Y position
            is_triple_jump: Whether this is a triple jump (extra particles)
        """
        import random

        particle_count = 20 if is_triple_jump else 10
        color = self.triple_jump_color if is_triple_jump else (200, 200, 255)

        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 100  # Bias upward

            self.particles.append(Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                lifetime=random.uniform(0.3, 0.6),
                max_lifetime=0.6,
                color=color,
                size=random.uniform(2, 4)
            ))

    def create_extra_jump_particles(self, x: float, y: float):
        """Create particles for extra jump powerup usage."""
        import random

        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(40, 120)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            self.particles.append(Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                lifetime=random.uniform(0.4, 0.7),
                max_lifetime=0.7,
                color=self.extra_jump_color,
                size=random.uniform(2, 5)
            ))

    def create_magnet_particles(self, x: float, y: float):
        """Create particles for magnet activation."""
        import random

        for _ in range(25):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 180)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            self.particles.append(Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                lifetime=random.uniform(0.5, 1.0),
                max_lifetime=1.0,
                color=self.magnet_color,
                size=random.uniform(2, 4)
            ))

    def render(self, surface: pygame.Surface, player: Any, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Render all powerup visual effects.

        Args:
            surface: Surface to render on
            player: Player instance
            camera_offset: Camera offset for world coordinates
        """
        # Render auras
        self._render_auras(surface, player, camera_offset)

        # Render speed lines
        self._render_speed_lines(surface, camera_offset)

        # Render particles
        self._render_particles(surface, camera_offset)

        # Render magnet visualization
        if player.magnet_timer > 0:
            self._render_magnet_radius(surface, player, camera_offset)

    def _render_auras(self, surface: pygame.Surface, player: Any, camera_offset: Tuple[int, int]):
        """Render powerup auras around player."""
        screen_x = player.rect.centerx - camera_offset[0]
        screen_y = player.rect.centery - camera_offset[1]

        # Speed boost aura
        if player.speed_boost_timer > 0:
            pulse = abs(math.sin(self.aura_pulse))
            radius = int(player.rect.width * 0.8 + pulse * 10)
            alpha = int(80 + pulse * 60)

            aura_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                aura_surface,
                (*self.speed_boost_color, alpha),
                (radius, radius),
                radius
            )
            surface.blit(aura_surface, (screen_x - radius, screen_y - radius))

        # Triple jump aura
        if player.triple_jump_timer > 0:
            pulse = abs(math.sin(self.aura_pulse * 1.5))
            radius = int(player.rect.width * 0.7 + pulse * 8)
            alpha = int(60 + pulse * 50)

            aura_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                aura_surface,
                (*self.triple_jump_color, alpha),
                (radius, radius),
                radius
            )
            surface.blit(aura_surface, (screen_x - radius, screen_y - radius))

    def _render_speed_lines(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Render speed lines for speed boost."""
        for line_x, line_y, vx, alpha in self.speed_lines:
            screen_x = int(line_x - camera_offset[0])
            screen_y = int(line_y - camera_offset[1])

            line_alpha = int(alpha * 200)
            color = (*self.speed_boost_color, line_alpha)

            # Draw line
            end_x = screen_x + int(self.speed_line_length * (1 if vx > 0 else -1))
            pygame.draw.line(surface, color[:3], (screen_x, screen_y), (end_x, screen_y), 2)

    def _render_particles(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Render all particles."""
        for particle in self.particles:
            screen_x = int(particle.x - camera_offset[0])
            screen_y = int(particle.y - camera_offset[1])

            alpha = particle.get_alpha()
            color = (*particle.color, alpha)

            # Draw particle as circle
            size = int(particle.size)
            if size > 0:
                particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    particle_surface,
                    color,
                    (size, size),
                    size
                )
                surface.blit(particle_surface, (screen_x - size, screen_y - size))

    def _render_magnet_radius(self, surface: pygame.Surface, player: Any, camera_offset: Tuple[int, int]):
        """Render magnet radius visualization."""
        screen_x = player.rect.centerx - camera_offset[0]
        screen_y = player.rect.centery - camera_offset[1]
        radius = int(player.magnet_radius)

        # Pulsing circle
        pulse = abs(math.sin(self.aura_pulse * 2))
        alpha = int(30 + pulse * 40)

        # Draw outer circle
        circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            circle_surface,
            (*self.magnet_color, alpha),
            (radius, radius),
            radius,
            2
        )
        surface.blit(circle_surface, (screen_x - radius, screen_y - radius))

    def highlight_coins_in_range(self, surface: pygame.Surface, player: Any,
                                 coins: List[Any], camera_offset: Tuple[int, int] = (0, 0)):
        """
        Highlight coins within magnet range.

        Args:
            surface: Surface to render on
            player: Player instance
            coins: List of coin entities
            camera_offset: Camera offset
        """
        if player.magnet_timer <= 0:
            return

        magnet_radius = player.magnet_radius
        player_center = player.rect.center

        for coin in coins:
            # Calculate distance
            coin_center = coin.rect.center if hasattr(coin, 'rect') else (coin.x, coin.y)
            dx = coin_center[0] - player_center[0]
            dy = coin_center[1] - player_center[1]
            distance = math.sqrt(dx * dx + dy * dy)

            # If in range, highlight
            if distance <= magnet_radius:
                screen_x = coin_center[0] - camera_offset[0]
                screen_y = coin_center[1] - camera_offset[1]

                # Draw highlight ring
                pulse = abs(math.sin(self.aura_pulse * 3))
                radius = int(12 + pulse * 4)
                alpha = int(150 + pulse * 100)

                highlight_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    highlight_surface,
                    (*self.magnet_color, alpha),
                    (radius, radius),
                    radius,
                    2
                )
                surface.blit(highlight_surface, (screen_x - radius, screen_y - radius))

    def render_hud_indicators(self, surface: pygame.Surface, player: Any, x: int, y: int):
        """
        Render HUD indicators for active powerups.

        Args:
            surface: Surface to render on
            player: Player instance
            x: HUD X position
            y: HUD Y position
        """
        font = pygame.font.SysFont("consolas", 14)
        indicator_height = 20
        current_y = y

        # Speed Boost
        if player.speed_boost_timer > 0:
            self._render_powerup_indicator(
                surface,
                font,
                "SPEED",
                player.speed_boost_timer,
                self.speed_boost_color,
                x,
                current_y
            )
            current_y += indicator_height

        # Triple Jump
        if player.triple_jump_timer > 0:
            self._render_powerup_indicator(
                surface,
                font,
                "TRIPLE",
                player.triple_jump_timer,
                self.triple_jump_color,
                x,
                current_y
            )
            current_y += indicator_height

        # Extra Jump
        if player.extra_jump_uses > 0:
            text = f"EXTRA JUMPS: {player.extra_jump_uses}"
            text_surface = font.render(text, True, self.extra_jump_color)
            surface.blit(text_surface, (x, current_y))
            current_y += indicator_height

        # Magnet
        if player.magnet_timer > 0:
            self._render_powerup_indicator(
                surface,
                font,
                "MAGNET",
                player.magnet_timer,
                self.magnet_color,
                x,
                current_y
            )
            current_y += indicator_height

    def _render_powerup_indicator(self, surface: pygame.Surface, font: pygame.font.Font,
                                  label: str, time_left: float, color: Tuple[int, int, int],
                                  x: int, y: int):
        """Render a single powerup indicator."""
        text = f"{label}: {time_left:.1f}s"
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def clear(self):
        """Clear all visual effects."""
        self.particles.clear()
        self.speed_lines.clear()
        self.aura_pulse = 0.0
