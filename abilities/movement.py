"""
Movement Abilities - Core movement abilities for player

This module contains the fundamental movement abilities:
- DoubleJump: Multi-jump in air
- Dash: Quick horizontal burst
- WallJump: Jump off walls
- Slide: Fast ground slide
"""

import pygame
from abilities import Ability, CooldownAbility, StaminaAbility
from settings import (
    JUMP_POWER, JUMP_POWER_SECOND, JUMP_HORIZONTAL_BOOST_SECOND, MAX_JUMPS,
    DASH_STAMINA_MAX, DASH_STAMINA_DRAIN, DASH_STAMINA_REGEN, DASH_SPEED_MULT,
    WALL_JUMP_POWER_X, WALL_JUMP_POWER_Y, WALL_JUMP_INPUT_LOCK,
    SLIDE_SPEED_MULT, SLIDE_DURATION, SLIDE_MIN_SPEED, SLIDE_COOLDOWN,
    COYOTE_TIME, JUMP_BUFFER_TIME,
    CROUCH_JUMP_MULT,
    MAX_RUN_SPEED,
)


class DoubleJump(Ability):
    """
    Multi-jump ability with differentiated jump mechanics.

    State:
    - jumps_left: Number of jumps remaining
    - max_jumps: Maximum jumps allowed (can be modified by powerups)
    - jumps_used: Counter tracking which jump we're on

    Jump Mechanics:
    - First jump (ground/coyote): Balanced vertical + trajectory-based
    - Second jump (air): More horizontal, less vertical
    - Extra jumps (powerups): Similar to second jump mechanics
    """

    def __init__(self):
        super().__init__("DOUBLE_JUMP")
        self.max_jumps = MAX_JUMPS
        self.jumps_left = self.max_jumps
        self.jump_buffer_timer = 0.0
        self.coyote_timer = 0.0
        self.jumps_used = 0  # Track which jump we're on

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
        Execute a jump with mechanics based on which jump this is.

        First jump: Balanced vertical power, respects current momentum
        Second+ jump: Reduced vertical, boosted horizontal for aerial control

        Returns:
            dict: Movement modifications including vertical velocity
        """
        on_ground = player_state.get('on_ground', False)
        on_wall = player_state.get('on_wall', False)
        crouching = player_state.get('crouching', False)
        jump_power = player_state.get('jump_power', JUMP_POWER)
        vx = player_state.get('vx', 0)

        # Ground or coyote jump (first jump)
        if on_ground or self.coyote_timer > 0:
            power = jump_power * (CROUCH_JUMP_MULT if crouching else 1.0)
            self.jumps_left = self.max_jumps - 1
            self.jumps_used = 1
            self.coyote_timer = 0.0
            self.jump_buffer_timer = 0.0

            # First jump: Balanced, maintains current momentum
            return {
                'vy': -power,
                'on_ground': False
            }

        # Air jump (second jump or extra jumps from powerups)
        elif self.jumps_left > 0:
            self.jumps_left -= 1
            self.jumps_used += 1
            self.jump_buffer_timer = 0.0

            # Second+ jump: More horizontal-focused
            # Reduced vertical power, boost horizontal velocity
            vertical_power = JUMP_POWER_SECOND

            # If jumping from wall, give some upward boost (wall surface exception)
            if on_wall:
                vertical_power = JUMP_POWER * 0.85  # Slightly less than full jump

            result = {
                'vy': -vertical_power
            }

            # Boost horizontal velocity for aerial maneuverability
            if vx != 0:
                # Boost existing horizontal movement
                result['vx'] = vx * JUMP_HORIZONTAL_BOOST_SECOND
            else:
                # If not moving horizontally, give small boost in facing direction
                facing = player_state.get('facing', 1)
                result['vx'] = facing * MAX_RUN_SPEED * 0.5

            return result

        return None

    def update(self, dt, player_state):
        """Update coyote time and jump buffer."""
        on_ground = player_state.get('on_ground', False)

        # Update coyote timer
        if on_ground:
            self.coyote_timer = COYOTE_TIME
            self.jumps_left = self.max_jumps  # Reset jumps on ground
            self.jumps_used = 0  # Reset jump counter
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
        self.jumps_used = 0

    def get_debug_info(self):
        info = super().get_debug_info()
        info['jumps'] = f"{self.jumps_left}/{self.max_jumps}"
        info['coyote'] = f"{self.coyote_timer:.2f}s" if self.coyote_timer > 0 else "0"
        return info


class Dash(StaminaAbility):
    """
    Stamina-based run speed modifier.

    State:
    - is_active: Whether dash is currently active
    - resource (stamina): Remaining stamina

    Mechanics:
    - Hold to activate and increase run speed
    - Drains stamina while active
    - Regenerates stamina when not active
    - Auto-deactivates when stamina depleted
    """

    def __init__(self):
        super().__init__(
            "DASH",
            max_stamina=DASH_STAMINA_MAX,
            regen_rate=DASH_STAMINA_REGEN,
            drain_rate=DASH_STAMINA_DRAIN
        )
        self.is_active = False
        self.speed_multiplier = DASH_SPEED_MULT

    def can_use(self, player_state):
        """Can activate dash if we have stamina available."""
        return self.resource > 0

    def use(self, player_state, input_state):
        """
        Activate/toggle dash mode.

        Returns:
            dict: Movement modifications for dash
        """
        if not self.is_active and self.resource > 0:
            self.is_active = True

        return {
            'is_dashing': self.is_active,
            'dash_speed_mult': self.speed_multiplier if self.is_active else 1.0
        }

    def deactivate_dash(self):
        """Manually deactivate dash (when player releases key)."""
        self.is_active = False

    def update(self, dt, player_state):
        """Update stamina drain/regen based on dash state."""
        if self.is_active:
            # Drain stamina while dashing
            if not self.drain_stamina(dt):
                # Out of stamina - auto-deactivate
                self.is_active = False
                return {
                    'is_dashing': False,
                    'dash_speed_mult': 1.0
                }

            return {
                'is_dashing': True,
                'dash_speed_mult': self.speed_multiplier
            }
        else:
            # Regenerate stamina when not dashing
            self.regenerate_stamina(dt)

        return {}

    def is_active_dash(self):
        """Check if dash is currently active."""
        return self.is_active

    def get_stamina_percent(self):
        """Get stamina as percentage (0.0 to 1.0)."""
        return self.resource / self.max_resource

    def reset(self):
        """Reset dash state and restore stamina."""
        super().reset()
        self.is_active = False

    def get_debug_info(self):
        info = super().get_debug_info()
        info['status'] = "ACTIVE" if self.is_active else "ready"
        info['stamina_pct'] = f"{self.get_stamina_percent()*100:.0f}%"
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

    Note: Collision handling must be managed by player.py to prevent
    glitching through terrain. The ability only provides velocity
    modifications and state flags.
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
            'crouching': True,  # Force crouch during slide
            'check_collisions': True  # Flag to ensure collision checking is active
        }

    def update(self, dt, player_state):
        """Update slide timer and cooldown."""
        # Update cooldown
        self.update_cooldown(dt)

        # Update slide timer
        if self.is_active:
            self.slide_timer -= dt
            vx = player_state.get('vx', 0)  # Keep original vx sign
            speed = abs(vx)

            # End slide if time expires or too slow
            if self.slide_timer <= 0 or speed < self.min_speed:
                self.is_active = False
                self.start_cooldown()
                return {'is_sliding': False}

            # Continue slide movement with speed boost
            # Note: Apply multiplier to current speed, preserve direction
            return {
                'vx_mult': self.speed_mult,  # Multiplier instead of direct set
                'is_sliding': True,
                'check_collisions': True
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
