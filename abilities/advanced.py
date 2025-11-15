"""
Advanced Abilities - Complex movement abilities

This module contains advanced movement abilities:
- WallCling: Stick to walls using stamina
- ShadowStep: Invulnerable teleport dash
- AirDodge: Directional dodge with i-frames
- Glide: Slow descent while airborne
"""

import math
import pygame
from abilities import Ability, ResourceAbility, CooldownAbility
from settings import (
    SHADOW_STEP_CHARGES, SHADOW_STEP_DURATION, SHADOW_STEP_INVULN_TIME,
    SHADOW_STEP_SPEED, SHADOW_STEP_COOLDOWN,
    WALL_CLING_SLIDE_SPEED, WALL_CLING_STAMINA, WALL_CLING_STAMINA_REGEN,
    AIR_DODGE_SPEED, AIR_DODGE_DURATION, AIR_DODGE_INVULN_TIME,
    AIR_DODGE_COOLDOWN, AIR_DODGE_MAX_USES,
    GLIDE_FALL_SPEED, GLIDE_HORIZONTAL_MULT, GLIDE_MAX_DURATION,
)


class ShadowStep(ResourceAbility):
    """
    Shadow step ability - invulnerable dash with charges.

    State:
    - charges: Number of charges remaining
    - is_active: Whether shadow step is executing
    - shadow_step_timer: Time remaining in shadow step
    - invuln_timer: Invulnerability time remaining
    - direction: Shadow step direction
    """

    def __init__(self):
        super().__init__("SHADOW_STEP", SHADOW_STEP_CHARGES, "charges")
        self.is_active = False
        self.shadow_step_timer = 0.0
        self.invuln_timer = 0.0
        self.direction = 1
        self.duration = SHADOW_STEP_DURATION
        self.speed = SHADOW_STEP_SPEED
        self.cooldown_timer = 0.0
        self.cooldown_duration = SHADOW_STEP_COOLDOWN

    def can_use(self, player_state):
        """Can use if we have charges and not on cooldown."""
        return (self.resource > 0 and
                not self.is_active and
                self.cooldown_timer <= 0)

    def use(self, player_state, input_state):
        """
        Activate shadow step.

        Returns:
            dict: Movement modifications and invulnerability state
        """
        self.direction = player_state.get('facing', 1)
        if self.direction == 0:
            self.direction = 1

        self.consume_resource(1)
        self.is_active = True
        self.shadow_step_timer = self.duration
        self.invuln_timer = SHADOW_STEP_INVULN_TIME

        return {
            'vx': self.direction * self.speed,
            'is_shadow_stepping': True,
            'is_dashing': False,  # Cancel regular dash
            'invulnerable': True
        }

    def update(self, dt, player_state):
        """Update shadow step timer, cooldown, and invulnerability."""
        # Update cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

        # Update shadow step
        if self.is_active:
            self.shadow_step_timer -= dt
            if self.shadow_step_timer <= 0:
                self.is_active = False
                self.cooldown_timer = self.cooldown_duration
                # Invulnerability persists briefly after
                self.invuln_timer = SHADOW_STEP_INVULN_TIME
                return {'is_shadow_stepping': False}

            # Continue shadow step movement
            return {
                'vx': self.direction * self.speed,
                'is_shadow_stepping': True,
                'invulnerable': True
            }

        # Update lingering invulnerability
        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)
            return {'invulnerable': self.invuln_timer > 0}

        return {}

    def is_invulnerable(self):
        """Check if player is currently invulnerable from shadow step."""
        return self.is_active or self.invuln_timer > 0

    def reset(self):
        """Reset charges and timers."""
        super().reset()
        self.is_active = False
        self.shadow_step_timer = 0.0
        self.invuln_timer = 0.0
        self.cooldown_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_active:
            info['status'] = f"active ({self.shadow_step_timer:.2f}s)"
        elif self.invuln_timer > 0:
            info['invuln'] = f"{self.invuln_timer:.2f}s"
        if self.cooldown_timer > 0:
            info['cooldown'] = f"{self.cooldown_timer:.2f}s"
        return info


class WallCling(ResourceAbility):
    """
    Wall cling ability - stick to walls using stamina.

    State:
    - is_active: Whether currently clinging
    - stamina: Stamina remaining
    """

    def __init__(self):
        super().__init__("WALL_CLING", WALL_CLING_STAMINA, "stamina")
        self.is_active = False
        self.slide_speed = WALL_CLING_SLIDE_SPEED
        self.regen_rate = WALL_CLING_STAMINA_REGEN

    def can_use(self, player_state):
        """Can cling if on wall, not on ground, and have stamina."""
        on_wall = player_state.get('on_wall', False)
        on_ground = player_state.get('on_ground', False)
        return on_wall and not on_ground and self.resource > 0

    def use(self, player_state, input_state):
        """
        Activate wall cling.

        Returns:
            dict: State modifications for wall cling
        """
        wall_dir = player_state.get('wall_dir', 0)
        left = input_state.get('left', False)
        right = input_state.get('right', False)

        # Check if holding toward wall
        holding_toward_wall = (
            (left and wall_dir == -1) or
            (right and wall_dir == 1)
        )

        if holding_toward_wall and self.resource > 0:
            self.is_active = True
            return {'is_wall_clinging': True}
        else:
            self.is_active = False
            return {'is_wall_clinging': False}

    def update(self, dt, player_state):
        """Update stamina drain and regeneration."""
        on_wall = player_state.get('on_wall', False)
        on_ground = player_state.get('on_ground', False)

        if self.is_active:
            # Drain stamina
            self.resource -= dt
            if self.resource <= 0:
                self.resource = 0
                self.is_active = False
                return {'is_wall_clinging': False}

            # Apply slow slide
            vy = player_state.get('vy', 0)
            if vy > self.slide_speed:
                return {
                    'vy': self.slide_speed,
                    'is_wall_clinging': True
                }
            return {'is_wall_clinging': True}
        else:
            # Regenerate stamina when not clinging
            if self.resource < self.max_resource:
                self.restore_resource(self.regen_rate * dt)

        return {}

    def deactivate(self):
        """Stop clinging."""
        self.is_active = False

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_active:
            info['status'] = "clinging"
        return info


class AirDodge(CooldownAbility):
    """
    Air dodge ability - directional dodge with invulnerability frames.

    State:
    - is_active: Whether dodge is executing
    - uses_left: Number of air dodges remaining (resets on ground)
    - direction: Dodge direction vector (x, y)
    - invuln_timer: Invulnerability time remaining
    """

    def __init__(self):
        super().__init__("AIR_DODGE", AIR_DODGE_COOLDOWN)
        self.is_active = False
        self.dodge_timer = 0.0
        self.invuln_timer = 0.0
        self.uses_left = AIR_DODGE_MAX_USES
        self.max_uses = AIR_DODGE_MAX_USES
        self.direction = (1, 0)
        self.duration = AIR_DODGE_DURATION
        self.speed = AIR_DODGE_SPEED

    def can_use(self, player_state):
        """Can dodge if in air, have uses, and not on cooldown."""
        on_ground = player_state.get('on_ground', False)
        return (not on_ground and
                self.uses_left > 0 and
                not self.is_active and
                not self.is_on_cooldown())

    def use(self, player_state, input_state):
        """
        Activate air dodge in specified direction.

        Returns:
            dict: Movement modifications and invulnerability
        """
        # Get dodge direction from input
        dodge_x = input_state.get('dodge_x', 0)
        dodge_y = input_state.get('dodge_y', 0)
        facing = player_state.get('facing', 1)

        # Normalize direction
        if dodge_x == 0 and dodge_y == 0:
            dodge_x = facing  # Default to facing direction

        length = math.sqrt(dodge_x * dodge_x + dodge_y * dodge_y)
        if length > 0:
            self.direction = (dodge_x / length, dodge_y / length)
        else:
            self.direction = (facing, 0)

        self.is_active = True
        self.dodge_timer = self.duration
        self.invuln_timer = AIR_DODGE_INVULN_TIME
        self.uses_left -= 1

        return {
            'vx': self.direction[0] * self.speed,
            'vy': self.direction[1] * self.speed,
            'is_air_dodging': True,
            'invulnerable': True
        }

    def update(self, dt, player_state):
        """Update dodge timer, cooldown, and invulnerability."""
        on_ground = player_state.get('on_ground', False)

        # Reset uses on ground
        if on_ground:
            self.uses_left = self.max_uses

        # Update cooldown
        self.update_cooldown(dt)

        # Update dodge
        if self.is_active:
            self.dodge_timer -= dt
            if self.dodge_timer <= 0:
                self.is_active = False
                self.start_cooldown()
                return {'is_air_dodging': False}

            # Continue dodge movement
            return {
                'vx': self.direction[0] * self.speed,
                'vy': self.direction[1] * self.speed,
                'is_air_dodging': True,
                'invulnerable': True
            }

        # Update invulnerability
        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)
            return {'invulnerable': self.invuln_timer > 0}

        return {}

    def is_invulnerable(self):
        """Check if player is invulnerable from dodge."""
        return self.is_active or self.invuln_timer > 0

    def reset(self):
        """Reset dodge state."""
        self.is_active = False
        self.dodge_timer = 0.0
        self.invuln_timer = 0.0
        self.uses_left = self.max_uses
        self.cooldown_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        info['uses'] = f"{self.uses_left}/{self.max_uses}"
        if self.is_active:
            info['status'] = f"dodging ({self.dodge_timer:.2f}s)"
        return info


class Glide(Ability):
    """
    Glide ability - slow descent while holding jump.

    State:
    - is_active: Whether currently gliding
    - glide_timer: Time spent gliding (can limit duration)
    """

    def __init__(self):
        super().__init__("GLIDE")
        self.is_active = False
        self.glide_timer = 0.0
        self.fall_speed = GLIDE_FALL_SPEED
        self.horizontal_mult = GLIDE_HORIZONTAL_MULT
        self.max_duration = GLIDE_MAX_DURATION

    def can_use(self, player_state):
        """Can glide if in air and falling."""
        on_ground = player_state.get('on_ground', False)
        vy = player_state.get('vy', 0)
        return not on_ground and vy > 0

    def use(self, player_state, input_state):
        """
        Activate glide.

        Returns:
            dict: Movement modifications for glide
        """
        jump_held = input_state.get('jump_held', False)

        if jump_held and self.can_use(player_state):
            if not self.is_active:
                self.is_active = True
                self.glide_timer = 0.0

            return {
                'is_gliding': True
            }
        else:
            self.is_active = False
            self.glide_timer = 0.0
            return {'is_gliding': False}

    def update(self, dt, player_state):
        """Update glide state and apply movement modifications."""
        on_ground = player_state.get('on_ground', False)

        if on_ground:
            self.is_active = False
            self.glide_timer = 0.0
            return {}

        if self.is_active:
            self.glide_timer += dt

            # Optional: limit glide duration
            if self.glide_timer >= self.max_duration:
                self.is_active = False
                return {'is_gliding': False}

            # Apply glide physics
            vy = player_state.get('vy', 0)
            vx = player_state.get('vx', 0)

            modifications = {'is_gliding': True}

            # Cap fall speed
            if vy > self.fall_speed:
                modifications['vy'] = self.fall_speed

            # Reduce horizontal speed
            modifications['vx'] = vx * self.horizontal_mult

            return modifications

        return {}

    def deactivate(self):
        """Stop gliding."""
        self.is_active = False
        self.glide_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_active:
            info['status'] = f"gliding ({self.glide_timer:.1f}s)"
        return info


# Export advanced abilities
__all__ = ['ShadowStep', 'WallCling', 'AirDodge', 'Glide']
