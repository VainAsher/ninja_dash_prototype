"""
Combat System - Handles damage dealing, knockback, and combat interactions

This module provides:
- Damage calculation and application
- Knockback physics
- Combat hit detection
- Damage number visualization
"""

import pygame
import math
from typing import Optional, List, Tuple


class DamageNumber:
    """
    Visual representation of damage dealt.

    Displays a floating number that rises and fades out.
    """

    def __init__(self, x, y, damage, color=(255, 50, 50)):
        """
        Initialize damage number.

        Args:
            x: X position (center of hit)
            y: Y position (center of hit)
            damage: Damage amount to display
            color: RGB color tuple (default: red)
        """
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.lifetime = 1.0  # Seconds to display
        self.timer = 0.0
        self.vy = -50  # Float upward speed (pixels/second)

    def update(self, dt):
        """
        Update damage number animation.

        Args:
            dt: Delta time since last frame

        Returns:
            bool: True if still alive, False if expired
        """
        self.timer += dt
        self.y += self.vy * dt

        # Slow down as it rises
        self.vy += 100 * dt  # Decelerate

        return self.timer < self.lifetime

    def draw(self, screen, camera_offset=(0, 0), font=None):
        """
        Draw damage number to screen.

        Args:
            screen: Pygame surface to draw on
            camera_offset: (x, y) camera offset for world space
            font: Pygame font object (None = use default)
        """
        # Calculate fade based on lifetime
        alpha_factor = 1.0 - (self.timer / self.lifetime)
        alpha = int(255 * alpha_factor)

        # Create faded color
        faded_color = (
            min(255, self.color[0]),
            min(255, self.color[1]),
            min(255, self.color[2]),
            alpha
        )

        # Use default font if none provided
        if font is None:
            font = pygame.font.Font(None, 24)

        # Render text
        damage_text = str(int(self.damage))
        text_surface = font.render(damage_text, True, self.color)

        # Apply alpha
        text_surface.set_alpha(alpha)

        # Calculate screen position
        screen_x = self.x - camera_offset[0] - text_surface.get_width() // 2
        screen_y = self.y - camera_offset[1]

        screen.blit(text_surface, (screen_x, screen_y))


class DamageNumberManager:
    """Manages all active damage numbers."""

    def __init__(self):
        self.damage_numbers = []
        self.font = None  # Will be initialized on first use

    def add_damage_number(self, x, y, damage, color=(255, 50, 50)):
        """
        Add a new damage number to display.

        Args:
            x: X position
            y: Y position
            damage: Damage amount
            color: RGB color tuple
        """
        self.damage_numbers.append(DamageNumber(x, y, damage, color))

    def update(self, dt):
        """Update all damage numbers and remove expired ones."""
        self.damage_numbers = [
            dn for dn in self.damage_numbers
            if dn.update(dt)
        ]

    def draw(self, screen, camera_offset=(0, 0)):
        """Draw all damage numbers."""
        # Initialize font on first draw
        if self.font is None:
            self.font = pygame.font.Font(None, 28)

        for dn in self.damage_numbers:
            dn.draw(screen, camera_offset, self.font)

    def clear(self):
        """Clear all damage numbers."""
        self.damage_numbers.clear()


def calculate_knockback(
    attacker_pos: Tuple[float, float],
    target_pos: Tuple[float, float],
    knockback_force: float
) -> Tuple[float, float]:
    """
    Calculate knockback velocity from an attack.

    Creates a gentle, graceful arc away from the damage source with
    primarily horizontal knockback and a slight upward component.

    Args:
        attacker_pos: (x, y) position of attacker
        target_pos: (x, y) position of target
        knockback_force: Base knockback force

    Returns:
        (vx, vy): Knockback velocity components
    """
    # Calculate direction from attacker to target
    dx = target_pos[0] - attacker_pos[0]
    dy = target_pos[1] - attacker_pos[1]

    # Avoid division by zero
    distance = math.sqrt(dx * dx + dy * dy)
    if distance < 1:
        # Default to horizontal knockback if overlapping
        return (knockback_force * 0.6 if dx >= 0 else -knockback_force * 0.6, -knockback_force * 0.3)

    # Normalize direction
    nx = dx / distance
    ny = dy / distance

    # Apply knockback force with gentle arc
    # Focus on horizontal knockback, with controlled vertical component
    vx = nx * knockback_force * 0.7  # Reduced horizontal force for gentler feel

    # Vertical component: bias toward slight upward arc, but cap extremes
    # If target is above attacker (ny < 0), limit upward force
    # If target is below attacker (ny > 0), convert to slight upward
    if ny < 0:  # Target above attacker
        # Already going up, limit the upward force to prevent extreme launches
        vy = max(ny * knockback_force * 0.3, -300)  # Cap upward velocity at -300
    else:  # Target at same level or below attacker
        # Convert downward into gentle upward arc
        vy = -knockback_force * 0.2  # Small upward arc

    return (vx, vy)


def deal_damage(
    attacker,
    target,
    damage_amount: float,
    knockback_force: float = 0.0,
    damage_numbers: Optional[DamageNumberManager] = None
) -> bool:
    """
    Deal damage from one entity to another.

    Args:
        attacker: The attacking entity (must have .rect for position)
        target: The target entity (must have .take_damage() method)
        damage_amount: Amount of damage to deal
        knockback_force: Knockback force to apply (default: 0)
        damage_numbers: Optional damage number manager to add visual feedback

    Returns:
        bool: True if damage was dealt, False if blocked/invulnerable
    """
    # Apply damage to target
    damage_dealt = target.take_damage(damage_amount)

    if not damage_dealt:
        return False

    # Apply knockback if force is specified
    if knockback_force > 0 and hasattr(target, 'vx') and hasattr(target, 'vy'):
        attacker_center = (
            attacker.rect.centerx,
            attacker.rect.centery
        )
        target_center = (
            target.rect.centerx,
            target.rect.centery
        )

        kb_vx, kb_vy = calculate_knockback(
            attacker_center,
            target_center,
            knockback_force
        )

        # Apply knockback to target velocity
        target.vx = kb_vx
        target.vy = kb_vy

    # Add damage number if manager provided
    if damage_numbers is not None:
        damage_numbers.add_damage_number(
            target.rect.centerx,
            target.rect.centery - target.rect.height // 2,
            damage_amount
        )

    return True


def check_attack_hit(
    attack_hitbox: pygame.Rect,
    targets: List,
    already_hit: set = None
) -> List:
    """
    Check if an attack hitbox collides with any targets.

    Args:
        attack_hitbox: Rectangle representing the attack area
        targets: List of potential targets (must have .rect attribute)
        already_hit: Set of entity IDs already hit (to prevent multi-hit)

    Returns:
        List of targets that were hit
    """
    if already_hit is None:
        already_hit = set()

    hit_targets = []

    for target in targets:
        # Skip if already hit
        target_id = id(target)
        if target_id in already_hit:
            continue

        # Check collision
        if hasattr(target, 'rect') and attack_hitbox.colliderect(target.rect):
            hit_targets.append(target)
            already_hit.add(target_id)

    return hit_targets


# Global damage number manager instance
_damage_number_manager = None


def get_damage_number_manager() -> DamageNumberManager:
    """Get the global damage number manager instance."""
    global _damage_number_manager
    if _damage_number_manager is None:
        _damage_number_manager = DamageNumberManager()
    return _damage_number_manager


def reset_damage_number_manager():
    """Reset the global damage number manager."""
    global _damage_number_manager
    _damage_number_manager = None
