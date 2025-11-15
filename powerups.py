"""
Powerup System - Temporary power-up effects for player

This module contains powerup classes that apply temporary effects:
- SpeedBoost: Increase movement speed
- TripleJump: Add extra jumps
- CoinMagnet: Attract coins from distance
"""

import math
from settings import (
    POWERUP_SPEED_DURATION, POWERUP_SPEED_FACTOR,
    POWERUP_TRIPLE_DURATION, POWERUP_TRIPLE_EXTRA_JUMPS,
    POWERUP_EXTRA_JUMP_USES, POWERUP_EXTRA_JUMP_DAMAGE_LIMIT,
    POWERUP_MAGNET_DURATION, POWERUP_MAGNET_RADIUS,
    MAX_JUMPS,
)


class Powerup:
    """
    Base class for temporary powerup effects.

    Powerups have a duration and apply effects while active.
    """

    def __init__(self, name, duration):
        """
        Initialize powerup.

        Args:
            name: Powerup identifier
            duration: How long the powerup lasts in seconds
        """
        self.name = name
        self.duration = duration
        self.timer = 0.0
        self.active = False

    def activate(self, duration=None):
        """
        Activate the powerup.

        Args:
            duration: Optional override for powerup duration
        """
        self.duration = duration if duration is not None else self.duration
        self.timer = self.duration
        self.active = True

    def update(self, dt):
        """
        Update powerup timer.

        Args:
            dt: Delta time since last frame

        Returns:
            bool: True if still active, False if expired
        """
        if self.active:
            self.timer = max(0.0, self.timer - dt)
            if self.timer <= 0:
                self.active = False
                self.on_expire()
                return False
        return self.active

    def on_expire(self):
        """Called when powerup expires. Override to clean up effects."""
        pass

    def is_active(self):
        """Check if powerup is currently active."""
        return self.active

    def get_time_remaining(self):
        """Get time remaining in seconds."""
        return self.timer if self.active else 0.0

    def deactivate(self):
        """Immediately deactivate the powerup."""
        self.active = False
        self.timer = 0.0
        self.on_expire()

    def get_debug_info(self):
        """Get debug information."""
        return {
            'name': self.name,
            'active': self.active,
            'time_remaining': f"{self.timer:.1f}s" if self.active else "inactive"
        }


class SpeedBoost(Powerup):
    """
    Speed boost powerup - increases player movement speed.

    Attributes:
        speed_factor: Multiplier for max speed (e.g., 1.5 = 150% speed)
    """

    def __init__(self, duration=None, factor=None):
        """
        Initialize speed boost.

        Args:
            duration: How long the boost lasts (default from settings)
            factor: Speed multiplier (default from settings)
        """
        super().__init__("SPEED_BOOST", duration or POWERUP_SPEED_DURATION)
        self.speed_factor = factor or POWERUP_SPEED_FACTOR

    def activate(self, duration=None, factor=None):
        """
        Activate speed boost.

        Args:
            duration: Optional duration override
            factor: Optional speed factor override
        """
        super().activate(duration)
        if factor is not None:
            self.speed_factor = factor

    def get_speed_multiplier(self):
        """Get the current speed multiplier."""
        return self.speed_factor if self.active else 1.0

    def on_expire(self):
        """Reset speed factor to normal."""
        pass  # Speed factor only matters while active

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.active:
            info['speed_factor'] = f"{self.speed_factor}x"
        return info


class TripleJump(Powerup):
    """
    Triple jump powerup - adds extra jumps to player.

    Attributes:
        extra_jumps: Number of additional jumps granted
    """

    def __init__(self, duration=None, extra_jumps=None):
        """
        Initialize triple jump powerup.

        Args:
            duration: How long the powerup lasts (default from settings)
            extra_jumps: Number of extra jumps to grant (default from settings)
        """
        super().__init__("TRIPLE_JUMP", duration or POWERUP_TRIPLE_DURATION)
        self.extra_jumps = extra_jumps or POWERUP_TRIPLE_EXTRA_JUMPS
        self.base_max_jumps = MAX_JUMPS

    def activate(self, duration=None, extra_jumps=None):
        """
        Activate triple jump.

        Args:
            duration: Optional duration override
            extra_jumps: Optional extra jumps override
        """
        super().activate(duration)
        if extra_jumps is not None:
            self.extra_jumps = extra_jumps

    def get_max_jumps(self):
        """Get the maximum jumps (base + extra if active)."""
        return self.base_max_jumps + (self.extra_jumps if self.active else 0)

    def get_extra_jumps(self):
        """Get the number of extra jumps granted."""
        return self.extra_jumps if self.active else 0

    def on_expire(self):
        """Called when triple jump expires."""
        pass  # Jump count handled by ability system

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.active:
            info['extra_jumps'] = f"+{self.extra_jumps}"
        return info


class ExtraJump(Powerup):
    """
    Extra jump powerup - grants a consumable extra jump.

    Unlike TripleJump (duration-based), this powerup:
    - Gives X uses of an extra jump
    - OR expires after taking Y damage
    - Works with 1 jump (becomes double) or 2 jumps (becomes triple)

    Attributes:
        uses_remaining: Number of extra jumps left
        damage_limit: Maximum damage before expiration
        damage_taken: Accumulated damage while active
    """

    def __init__(self, uses=None, damage_limit=None):
        """
        Initialize extra jump powerup.

        Args:
            uses: Number of extra jump uses (default from settings)
            damage_limit: Damage threshold for expiration (default from settings)
        """
        super().__init__("EXTRA_JUMP", duration=999999)  # No time limit
        self.max_uses = uses or POWERUP_EXTRA_JUMP_USES
        self.uses_remaining = self.max_uses
        self.damage_limit = damage_limit or POWERUP_EXTRA_JUMP_DAMAGE_LIMIT
        self.damage_taken = 0.0

    def activate(self, uses=None, damage_limit=None):
        """
        Activate extra jump powerup.

        Args:
            uses: Optional number of uses override
            damage_limit: Optional damage limit override
        """
        super().activate()
        if uses is not None:
            self.max_uses = uses
        self.uses_remaining = self.max_uses
        self.damage_taken = 0.0
        if damage_limit is not None:
            self.damage_limit = damage_limit

    def consume_use(self):
        """
        Consume one use of the extra jump.

        Returns:
            bool: True if use was consumed, False if no uses remaining
        """
        if not self.active or self.uses_remaining <= 0:
            return False

        self.uses_remaining -= 1

        # Deactivate if out of uses
        if self.uses_remaining <= 0:
            self.deactivate()

        return True

    def take_damage(self, damage_amount):
        """
        Register damage taken while powerup is active.

        Args:
            damage_amount: Amount of damage taken (usually 1)

        Returns:
            bool: True if powerup is still active, False if expired
        """
        if not self.active:
            return False

        self.damage_taken += damage_amount

        # Deactivate if damage limit reached
        if self.damage_taken >= self.damage_limit:
            self.deactivate()
            return False

        return True

    def has_uses(self):
        """Check if extra jump has uses remaining."""
        return self.active and self.uses_remaining > 0

    def get_extra_jumps(self):
        """
        Get the number of extra jumps granted (1 if active and has uses).

        Returns:
            int: 1 if active with uses, 0 otherwise
        """
        return 1 if self.has_uses() else 0

    def on_expire(self):
        """Called when extra jump expires."""
        self.uses_remaining = 0

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.active:
            info['uses'] = f"{self.uses_remaining}/{self.max_uses}"
            info['damage'] = f"{self.damage_taken:.0f}/{self.damage_limit}"
        return info


class CoinMagnet(Powerup):
    """
    Coin magnet powerup - pulls coins toward player.

    Attributes:
        radius: Distance at which coins are attracted
    """

    def __init__(self, duration=None, radius=None):
        """
        Initialize coin magnet.

        Args:
            duration: How long the magnet lasts (default from settings)
            radius: Attraction radius in pixels (default from settings)
        """
        super().__init__("COIN_MAGNET", duration or POWERUP_MAGNET_DURATION)
        self.radius = radius or POWERUP_MAGNET_RADIUS

    def activate(self, duration=None, radius=None):
        """
        Activate coin magnet.

        Args:
            duration: Optional duration override
            radius: Optional radius override
        """
        super().activate(duration)
        if radius is not None:
            self.radius = radius

    def get_radius(self):
        """Get the current magnet radius."""
        return self.radius if self.active else 0.0

    def apply_to_coins(self, player_center, coins, dt):
        """
        Pull coins toward player if magnet is active.

        Args:
            player_center: Tuple (x, y) of player center position
            coins: List of coin rectangles to attract
            dt: Delta time (unused, kept for consistency)
        """
        if not self.active:
            return

        for coin in coins:
            coin_center = coin.center
            dx = player_center[0] - coin_center[0]
            dy = player_center[1] - coin_center[1]
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < self.radius and dist > 1:
                # Lerp coin toward player
                speed = 8.0
                move_x = (dx / dist) * speed
                move_y = (dy / dist) * speed
                coin.x += int(move_x)
                coin.y += int(move_y)

    def on_expire(self):
        """Called when magnet expires."""
        pass

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.active:
            info['radius'] = f"{self.radius}px"
        return info


class PowerupManager:
    """
    Manager class for handling multiple active powerups.

    Tracks all powerups and provides convenient access to their effects.
    """

    def __init__(self):
        """Initialize powerup manager."""
        self.powerups = {
            'speed_boost': SpeedBoost(),
            'triple_jump': TripleJump(),
            'extra_jump': ExtraJump(),
            'coin_magnet': CoinMagnet(),
        }

    def activate_speed_boost(self, duration=None, factor=None):
        """Activate speed boost powerup."""
        self.powerups['speed_boost'].activate(duration, factor)

    def activate_triple_jump(self, duration=None, extra_jumps=None):
        """Activate triple jump powerup."""
        self.powerups['triple_jump'].activate(duration, extra_jumps)

    def activate_extra_jump(self, uses=None, damage_limit=None):
        """Activate extra jump powerup (use-based or damage-based)."""
        self.powerups['extra_jump'].activate(uses, damage_limit)

    def activate_coin_magnet(self, duration=None, radius=None):
        """Activate coin magnet powerup."""
        self.powerups['coin_magnet'].activate(duration, radius)

    def update(self, dt):
        """
        Update all powerups.

        Args:
            dt: Delta time since last frame
        """
        for powerup in self.powerups.values():
            powerup.update(dt)

    def get_speed_multiplier(self):
        """Get current speed multiplier from speed boost."""
        return self.powerups['speed_boost'].get_speed_multiplier()

    def get_extra_jumps(self):
        """Get current extra jumps from all jump powerups."""
        triple_jumps = self.powerups['triple_jump'].get_extra_jumps()
        extra_jump = self.powerups['extra_jump'].get_extra_jumps()
        return triple_jumps + extra_jump

    def consume_extra_jump_use(self):
        """Consume one use of the extra jump powerup."""
        return self.powerups['extra_jump'].consume_use()

    def register_damage(self, damage_amount):
        """Register damage for powerups that track damage (extra_jump)."""
        self.powerups['extra_jump'].take_damage(damage_amount)

    def get_magnet_radius(self):
        """Get current magnet radius."""
        return self.powerups['coin_magnet'].get_radius()

    def apply_magnet_to_coins(self, player_center, coins, dt):
        """Apply coin magnet effect."""
        self.powerups['coin_magnet'].apply_to_coins(player_center, coins, dt)

    def get_active_powerups(self):
        """Get list of currently active powerup names."""
        return [name for name, powerup in self.powerups.items() if powerup.is_active()]

    def deactivate_all(self):
        """Deactivate all powerups."""
        for powerup in self.powerups.values():
            powerup.deactivate()

    def get_debug_info(self):
        """Get debug info for all powerups."""
        return {name: powerup.get_debug_info()
                for name, powerup in self.powerups.items()
                if powerup.is_active()}


# Export powerup classes
__all__ = ['Powerup', 'SpeedBoost', 'TripleJump', 'ExtraJump', 'CoinMagnet', 'PowerupManager']
