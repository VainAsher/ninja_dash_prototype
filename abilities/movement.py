"""
Movement Abilities - Core movement abilities for player

This module contains the fundamental movement abilities:
- DoubleJump: Multi-jump in air
- Dash: Quick horizontal burst
- WallJump: Jump off walls
- Slide: Fast ground slide
"""

import pygame
from abilities import Ability, CooldownAbility
from settings import (
    JUMP_POWER, MAX_JUMPS,
    DASH_SPEED, DASH_DURATION, DASH_COOLDOWN,
    WALL_JUMP_POWER_X, WALL_JUMP_POWER_Y, WALL_JUMP_INPUT_LOCK,
    SLIDE_SPEED_MULT, SLIDE_DURATION, SLIDE_MIN_SPEED, SLIDE_COOLDOWN,
    COYOTE_TIME, JUMP_BUFFER_TIME,
    CROUCH_JUMP_MULT,
)


class DoubleJump(Ability):
    """
    Multi-jump ability allowing jumps in air.

    State:
    - jumps_left: Number of jumps remaining
    - max_jumps: Maximum jumps allowed (can be modified by powerups)
    """

    def __init__(self):
        super().__init__("DOUBLE_JUMP")
        self.max_jumps = MAX_JUMPS
        self.jumps_left = self.max_jumps
        self.jump_buffer_timer = 0.0
        self.coyote_timer = 0.0

    def can_use(self, player_state):
        """Can use if we have jumps remaining or in coyote time."""
        on_ground = player_state.get('on_ground', False)

        # Ground/coyote jump always available
        if on_ground or self.coyote_timer > 0:
            return True

        # Air jumps only if we have jumps left
        return self.jumps_left > 0

    def use(self, player_state, input_state):
        """
        Execute a jump.

        Returns:
            dict: Movement modifications including vertical velocity
        """
        on_ground = player_state.get('on_ground', False)
        crouching = player_state.get('crouching', False)
        jump_power = player_state.get('jump_power', JUMP_POWER)

        # Ground or coyote jump
        if on_ground or self.coyote_timer > 0:
            power = jump_power * (CROUCH_JUMP_MULT if crouching else 1.0)
            self.jumps_left = self.max_jumps - 1
            self.coyote_timer = 0.0
            self.jump_buffer_timer = 0.0
            return {
                'vy': -power,
                'on_ground': False
            }

        # Air jump (double/triple jump)
        elif self.jumps_left > 0:
            self.jumps_left -= 1
            self.jump_buffer_timer = 0.0
            return {
                'vy': -jump_power
            }

        return None

    def update(self, dt, player_state):
        """Update coyote time and jump buffer."""
        on_ground = player_state.get('on_ground', False)

        # Update coyote timer
        if on_ground:
            self.coyote_timer = COYOTE_TIME
            self.jumps_left = self.max_jumps  # Reset jumps on ground
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        # Update jump buffer
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)

        return {}

    def request_jump(self):
        """Called when jump input is pressed to buffer the jump."""
        self.jump_buffer_timer = JUMP_BUFFER_TIME

    def has_buffered_jump(self):
        """Check if a jump is buffered."""
        return self.jump_buffer_timer > 0

    def set_max_jumps(self, max_jumps):
        """Modify max jumps (used by powerups)."""
        old_max = self.max_jumps
        self.max_jumps = max_jumps
        # Add extra jumps if increased
        if max_jumps > old_max:
            self.jumps_left += (max_jumps - old_max)

    def reset(self):
        """Reset jumps to maximum."""
        self.max_jumps = MAX_JUMPS
        self.jumps_left = self.max_jumps
        self.jump_buffer_timer = 0.0
        self.coyote_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        info['jumps'] = f"{self.jumps_left}/{self.max_jumps}"
        info['coyote'] = f"{self.coyote_timer:.2f}s" if self.coyote_timer > 0 else "0"
        return info


class Dash(CooldownAbility):
    """
    Quick horizontal dash ability.

    State:
    - is_active: Whether dash is currently executing
    - dash_timer: Time remaining in dash
    - direction: Dash direction (1 or -1)
    """

    def __init__(self):
        super().__init__("DASH", DASH_COOLDOWN)
        self.is_active = False
        self.dash_timer = 0.0
        self.direction = 1
        self.duration = DASH_DURATION
        self.speed = DASH_SPEED

    def can_use(self, player_state):
        """Can dash if not already dashing and not on cooldown."""
        return not self.is_active and not self.is_on_cooldown()

    def use(self, player_state, input_state):
        """
        Activate dash.

        Returns:
            dict: Movement modifications for dash
        """
        self.direction = player_state.get('facing', 1)
        if self.direction == 0:
            self.direction = 1

        self.is_active = True
        self.dash_timer = self.duration

        return {
            'vx': self.direction * self.speed,
            'is_dashing': True
        }

    def update(self, dt, player_state):
        """Update dash timer and cooldown."""
        # Update cooldown
        self.update_cooldown(dt)

        # Update dash timer
        if self.is_active:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_active = False
                self.start_cooldown()
                return {'is_dashing': False}

            # Continue dash movement
            return {
                'vx': self.direction * self.speed,
                'is_dashing': True
            }

        return {}

    def is_active_dash(self):
        """Check if dash is currently active."""
        return self.is_active

    def reset(self):
        """Reset dash state."""
        self.is_active = False
        self.dash_timer = 0.0
        self.cooldown_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_active:
            info['status'] = f"active ({self.dash_timer:.2f}s)"
        return info


class WallJump(Ability):
    """
    Wall jump ability - jump off walls with directional boost.

    State:
    - input_lock_timer: Time remaining where horizontal input is locked
    """

    def __init__(self):
        super().__init__("WALL_JUMP")
        self.input_lock_timer = 0.0

    def can_use(self, player_state):
        """Can wall jump if on a wall and not on ground."""
        on_wall = player_state.get('on_wall', False)
        on_ground = player_state.get('on_ground', False)
        return on_wall and not on_ground

    def use(self, player_state, input_state):
        """
        Execute wall jump.

        Returns:
            dict: Movement modifications including velocity and facing direction
        """
        wall_dir = player_state.get('wall_dir', 0)
        jump_power = player_state.get('jump_power', JUMP_POWER)

        # Calculate jump velocities
        vy = -WALL_JUMP_POWER_Y * (jump_power / JUMP_POWER)
        vx = -wall_dir * WALL_JUMP_POWER_X
        new_facing = -wall_dir

        # Set input lock
        self.input_lock_timer = WALL_JUMP_INPUT_LOCK

        return {
            'vy': vy,
            'vx': vx,
            'facing': new_facing,
            'is_dashing': False,  # Cancel dash
        }

    def update(self, dt, player_state):
        """Update input lock timer."""
        if self.input_lock_timer > 0:
            self.input_lock_timer = max(0.0, self.input_lock_timer - dt)
        return {}

    def is_input_locked(self):
        """Check if horizontal input is currently locked."""
        return self.input_lock_timer > 0

    def reset(self):
        """Reset wall jump state."""
        self.input_lock_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_input_locked():
            info['input_lock'] = f"{self.input_lock_timer:.2f}s"
        return info


class Slide(CooldownAbility):
    """
    Ground slide ability - fast horizontal movement while crouched.

    State:
    - is_active: Whether slide is currently executing
    - slide_timer: Time remaining in slide
    - direction: Slide direction (1 or -1)
    """

    def __init__(self):
        super().__init__("SLIDE", SLIDE_COOLDOWN)
        self.is_active = False
        self.slide_timer = 0.0
        self.direction = 1
        self.duration = SLIDE_DURATION
        self.speed_mult = SLIDE_SPEED_MULT
        self.min_speed = SLIDE_MIN_SPEED

    def can_use(self, player_state):
        """Can slide if on ground, moving fast enough, and not on cooldown."""
        on_ground = player_state.get('on_ground', False)
        vx = abs(player_state.get('vx', 0))
        return (on_ground and
                vx >= self.min_speed and
                not self.is_active and
                not self.is_on_cooldown())

    def use(self, player_state, input_state):
        """
        Activate slide.

        Returns:
            dict: Movement modifications for slide
        """
        vx = player_state.get('vx', 0)
        self.direction = 1 if vx > 0 else -1

        self.is_active = True
        self.slide_timer = self.duration

        return {
            'is_sliding': True,
            'crouching': True  # Force crouch during slide
        }

    def update(self, dt, player_state):
        """Update slide timer and cooldown."""
        # Update cooldown
        self.update_cooldown(dt)

        # Update slide timer
        if self.is_active:
            self.slide_timer -= dt
            vx = abs(player_state.get('vx', 0))

            # End slide if time expires or too slow
            if self.slide_timer <= 0 or vx < self.min_speed:
                self.is_active = False
                self.start_cooldown()
                return {'is_sliding': False}

            # Continue slide movement
            return {
                'vx': self.direction * vx * self.speed_mult,
                'is_sliding': True
            }

        return {}

    def is_active_slide(self):
        """Check if slide is currently active."""
        return self.is_active

    def reset(self):
        """Reset slide state."""
        self.is_active = False
        self.slide_timer = 0.0
        self.cooldown_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_active:
            info['status'] = f"active ({self.slide_timer:.2f}s)"
        return info


# Export movement abilities
__all__ = ['DoubleJump', 'Dash', 'WallJump', 'Slide']
