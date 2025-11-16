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
from data.ability_config import get_ability_config
from settings import (
    SHADOW_STEP_CHARGES, SHADOW_STEP_DURATION, SHADOW_STEP_INVULN_TIME,
    SHADOW_STEP_SPEED, SHADOW_STEP_COOLDOWN, SHADOW_STEP_PHASE_DOORS_ONLY,
    WALL_CLING_SLIDE_SPEED, WALL_CLING_STAMINA, WALL_CLING_STAMINA_REGEN,
    AIR_DODGE_SPEED, AIR_DODGE_DURATION, AIR_DODGE_HANG_TIME, AIR_DODGE_HANG_GRAVITY_MULT,
    AIR_DODGE_INVULN_TIME, AIR_DODGE_COOLDOWN, AIR_DODGE_MAX_USES,
    GLIDE_FALL_SPEED, GLIDE_HORIZONTAL_MULT, GLIDE_MAX_DURATION, GLIDE_HORIZONTAL_ACCEL,
)

# Load ability configuration
_config = get_ability_config()


class ShadowStep(ResourceAbility):
    """
    Shadow Step (Smoke Bomb) - defensive evasion ability.

    Reworked as a defensive tool rather than offensive dash:
    - Creates smoke cloud for evasion and escape
    - Full invulnerability during smoke (damage evasion)
    - Can phase/dash through doors (phaseable walls)
    - Slower movement than offensive dash (tactical repositioning)

    Mechanics:
    - Consumes 1 charge per use
    - Grants invulnerability for full duration (defensive)
    - Allows phasing through specially marked doors/walls
    - Charges regenerate per level

    State:
    - charges: Number of charges remaining
    - is_active: Whether smoke bomb is active
    - smoke_timer: Time remaining in smoke cloud
    - direction: Movement direction during smoke
    """

    def __init__(self):
        # Load from config with fallback to settings.py
        super().__init__(
            "SHADOW_STEP",
            _config.get('advanced', 'shadow_step', 'charges', SHADOW_STEP_CHARGES),
            "charges"
        )
        self.is_active = False
        self.smoke_timer = 0.0
        self.direction = 1
        self.duration = _config.get('advanced', 'shadow_step', 'duration', SHADOW_STEP_DURATION)
        self.speed = _config.get('advanced', 'shadow_step', 'speed', SHADOW_STEP_SPEED)
        self.cooldown_timer = 0.0
        self.cooldown_duration = _config.get('advanced', 'shadow_step', 'cooldown', SHADOW_STEP_COOLDOWN)
        self.phase_doors_only = _config.get('advanced', 'shadow_step', 'phase_doors_only', SHADOW_STEP_PHASE_DOORS_ONLY)
        self.invuln_time = _config.get('advanced', 'shadow_step', 'invuln_time', SHADOW_STEP_INVULN_TIME)

    def can_use(self, player_state):
        """Can use if we have charges and not on cooldown."""
        return (self.resource > 0 and
                not self.is_active and
                self.cooldown_timer <= 0)

    def use(self, player_state, input_state):
        """
        Activate smoke bomb for evasion and phasing.

        Returns:
            dict: Movement modifications, invulnerability, and phasing state
        """
        self.direction = player_state.get('facing', 1)
        if self.direction == 0:
            self.direction = 1

        self.consume_resource(1)
        self.is_active = True
        self.smoke_timer = self.duration

        return {
            'vx': self.direction * self.speed,
            'is_smoke_stepping': True,  # Renamed for clarity (smoke bomb)
            'is_dashing': False,  # Cancel regular dash
            'invulnerable': True,  # Full invuln for defensive use
            'can_phase_doors': True,  # Can phase through doors/walls
            'smoke_effect': True  # Visual indicator for smoke cloud
        }

    def update(self, dt, player_state):
        """Update smoke timer, cooldown, and invulnerability."""
        # Update cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

        # Update smoke bomb
        if self.is_active:
            self.smoke_timer -= dt
            if self.smoke_timer <= 0:
                self.is_active = False
                self.cooldown_timer = self.cooldown_duration
                return {
                    'is_smoke_stepping': False,
                    'invulnerable': False,
                    'can_phase_doors': False,
                    'smoke_effect': False
                }

            # Continue smoke movement with full defensive benefits
            return {
                'vx': self.direction * self.speed,
                'is_smoke_stepping': True,
                'invulnerable': True,  # Invuln during entire duration
                'can_phase_doors': True,
                'smoke_effect': True
            }

        return {}

    def is_invulnerable(self):
        """Check if player is currently invulnerable from smoke bomb."""
        return self.is_active

    def can_phase_through_doors(self):
        """Check if player can currently phase through doors."""
        return self.is_active

    def reset(self):
        """Reset charges and timers."""
        super().reset()
        self.is_active = False
        self.smoke_timer = 0.0
        self.cooldown_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_active:
            info['status'] = f"smoke active ({self.smoke_timer:.2f}s)"
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
        stamina_max = _config.get('advanced', 'wall_cling', 'stamina_max', WALL_CLING_STAMINA)
        super().__init__("WALL_CLING", stamina_max, "stamina")
        self.is_active = False
        self.slide_speed = _config.get('advanced', 'wall_cling', 'slide_speed', WALL_CLING_SLIDE_SPEED)
        self.regen_rate = _config.get('advanced', 'wall_cling', 'stamina_regen', WALL_CLING_STAMINA_REGEN)

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
    Air dodge ability - directional dodge with hang time and invulnerability.

    Mechanics:
    - Activation triggers brief "hang time" with reduced gravity
    - Player can input direction during hang time
    - After hang time, executes dodge in chosen direction
    - Invulnerability frames during and after dodge

    State:
    - is_hanging: Whether in hang time (directional input phase)
    - is_dodging: Whether dodge is executing
    - hang_timer: Time remaining in hang phase
    - dodge_timer: Time remaining in dodge phase
    - uses_left: Number of air dodges remaining (resets on ground)
    - direction: Dodge direction vector (x, y)
    - invuln_timer: Invulnerability time remaining
    """

    def __init__(self):
        cooldown = _config.get('advanced', 'air_dodge', 'cooldown', AIR_DODGE_COOLDOWN)
        super().__init__("AIR_DODGE", cooldown)
        self.is_hanging = False
        self.is_dodging = False
        self.hang_timer = 0.0
        self.dodge_timer = 0.0
        self.invuln_timer = 0.0
        self.max_uses = _config.get('advanced', 'air_dodge', 'max_uses', AIR_DODGE_MAX_USES)
        self.uses_left = self.max_uses
        self.direction = (1, 0)
        self.hang_duration = _config.get('advanced', 'air_dodge', 'hang_time', AIR_DODGE_HANG_TIME)
        self.dodge_duration = _config.get('advanced', 'air_dodge', 'duration', AIR_DODGE_DURATION)
        self.speed = _config.get('advanced', 'air_dodge', 'speed', AIR_DODGE_SPEED)
        self.hang_gravity_mult = _config.get('advanced', 'air_dodge', 'hang_gravity_mult', AIR_DODGE_HANG_GRAVITY_MULT)
        self.invuln_time = _config.get('advanced', 'air_dodge', 'invuln_time', AIR_DODGE_INVULN_TIME)

    @property
    def is_active(self):
        """Dodge is active if hanging or dodging."""
        return self.is_hanging or self.is_dodging

    def can_use(self, player_state):
        """Can dodge if in air, have uses, and not on cooldown."""
        on_ground = player_state.get('on_ground', False)
        return (not on_ground and
                self.uses_left > 0 and
                not self.is_active and
                not self.is_on_cooldown())

    def use(self, player_state, input_state):
        """
        Activate air dodge - begins with hang time for directional input.

        Returns:
            dict: Movement modifications for hang time
        """
        # Start hang time phase
        self.is_hanging = True
        self.hang_timer = self.hang_duration
        self.uses_left -= 1

        # Store default direction (will be updated during hang time)
        facing = player_state.get('facing', 1)
        self.direction = (facing, 0)

        return {
            'is_air_dodge_hanging': True,
            'gravity_mult': self.hang_gravity_mult,  # Reduced gravity
            'vx_mult': 0.5,  # Slow horizontal movement during hang
        }

    def update_direction(self, input_state, player_state):
        """
        Update dodge direction during hang time based on input.

        Args:
            input_state: Current input state with dodge direction
            player_state: Current player state
        """
        if not self.is_hanging:
            return

        # Get dodge direction from input
        dodge_x = input_state.get('dodge_x', 0)
        dodge_y = input_state.get('dodge_y', 0)
        facing = player_state.get('facing', 1)

        # Update direction if input provided
        if dodge_x != 0 or dodge_y != 0:
            # Normalize direction
            length = math.sqrt(dodge_x * dodge_x + dodge_y * dodge_y)
            if length > 0:
                self.direction = (dodge_x / length, dodge_y / length)
        else:
            # Default to facing direction
            self.direction = (facing, 0)

    def update(self, dt, player_state):
        """Update hang time, dodge timer, cooldown, and invulnerability."""
        on_ground = player_state.get('on_ground', False)

        # Reset uses on ground
        if on_ground:
            self.uses_left = self.max_uses

        # Update cooldown
        self.update_cooldown(dt)

        # Update hang time
        if self.is_hanging:
            self.hang_timer -= dt
            if self.hang_timer <= 0:
                # Hang time over - execute dodge
                self.is_hanging = False
                self.is_dodging = True
                self.dodge_timer = self.dodge_duration
                self.invuln_timer = self.invuln_time

                # Begin dodge movement
                return {
                    'vx': self.direction[0] * self.speed,
                    'vy': self.direction[1] * self.speed,
                    'is_air_dodge_hanging': False,
                    'is_air_dodging': True,
                    'invulnerable': True,
                    'gravity_mult': 1.0  # Restore normal gravity
                }

            # Continue hang time
            return {
                'is_air_dodge_hanging': True,
                'gravity_mult': self.hang_gravity_mult,
                'vx_mult': 0.5
            }

        # Update dodge
        if self.is_dodging:
            self.dodge_timer -= dt
            if self.dodge_timer <= 0:
                self.is_dodging = False
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
        self.is_hanging = False
        self.is_dodging = False
        self.hang_timer = 0.0
        self.dodge_timer = 0.0
        self.invuln_timer = 0.0
        self.uses_left = self.max_uses
        self.cooldown_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        info['uses'] = f"{self.uses_left}/{self.max_uses}"
        if self.is_hanging:
            info['status'] = f"hang time ({self.hang_timer:.2f}s)"
        elif self.is_dodging:
            info['status'] = f"dodging ({self.dodge_timer:.2f}s)"
        return info


class Glide(Ability):
    """
    Glide ability - control descent with enhanced horizontal movement.

    Mechanics:
    - ONLY affects descent (vertical) movement - slows falling
    - ENHANCES horizontal movement and air control
    - Future: may interact with environmental up/down drafts

    State:
    - is_active: Whether currently gliding
    - glide_timer: Time spent gliding (can limit duration)
    """

    def __init__(self):
        super().__init__("GLIDE")
        self.is_active = False
        self.glide_timer = 0.0
        self.fall_speed = _config.get('advanced', 'glide', 'fall_speed', GLIDE_FALL_SPEED)
        self.horizontal_mult = _config.get('advanced', 'glide', 'horizontal_mult', GLIDE_HORIZONTAL_MULT)  # Now > 1.0 for enhancement
        self.horizontal_accel = _config.get('advanced', 'glide', 'horizontal_accel', GLIDE_HORIZONTAL_ACCEL)
        self.max_duration = _config.get('advanced', 'glide', 'max_duration', GLIDE_MAX_DURATION)

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

            modifications = {'is_gliding': True}

            # ONLY modify descent - cap fall speed for controlled descent
            if vy > self.fall_speed:
                modifications['vy'] = self.fall_speed

            # ENHANCE horizontal movement (multiplier > 1.0)
            # Also boost air control
            modifications['horizontal_mult'] = self.horizontal_mult
            modifications['air_accel_mult'] = self.horizontal_accel

            # Note: horizontal velocity is NOT reduced, it's enhanced
            # The player.py should apply horizontal_mult to max speed
            # and air_accel_mult to acceleration

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
