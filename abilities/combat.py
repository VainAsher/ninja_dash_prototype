"""
Combat Abilities - Attack and defense abilities

This module contains combat-related abilities:
- SwordAttack: Melee attack with tap/hold mechanics (tap=attack, hold=block)
- GrappleHook: Pull levers/switches and maneuver enemies (not for player movement)

Future additions:
- Ranged attacks (projectile-based)
- Special combat moves
"""

import pygame
from abilities import Ability, CooldownAbility, AmmoAbility
from data.ability_config import get_ability_config


# ================= SWORD ATTACK SETTINGS =================
# TODO: Move these to settings.py after testing
SWORD_ATTACK_DAMAGE = 1
SWORD_ATTACK_RANGE = 40  # Pixels
SWORD_ATTACK_COOLDOWN = 0.3  # Between attacks
SWORD_ATTACK_DURATION = 0.2  # Attack animation duration
SWORD_BLOCK_HOLD_TIME = 0.15  # How long to hold before block activates

# Load ability configuration
_config = get_ability_config()


class SwordAttack(CooldownAbility):
    """
    Sword attack ability - melee combat with attack/block mechanics.

    Controls:
    - Tap input: Quick slash attack
    - Hold input: Defensive block stance

    Mechanics:
    - Attack: Short-range melee strike with knockback
    - Block: Reduces incoming damage, reflects projectiles
    - Cooldown between attacks (not block)

    State:
    - is_attacking: Whether attack is executing
    - is_blocking: Whether block is active
    - attack_timer: Time remaining in attack
    - hold_timer: Time input has been held
    """

    def __init__(self):
        cooldown = _config.get('combat', 'sword_attack', 'cooldown', SWORD_ATTACK_COOLDOWN)
        super().__init__("SWORD_ATTACK", cooldown)
        self.is_attacking = False
        self.is_blocking = False
        self.attack_timer = 0.0
        self.hold_timer = 0.0
        self.damage = _config.get('combat', 'sword_attack', 'damage', SWORD_ATTACK_DAMAGE)
        self.range = _config.get('combat', 'sword_attack', 'range', SWORD_ATTACK_RANGE)
        self.attack_duration = _config.get('combat', 'sword_attack', 'attack_duration', SWORD_ATTACK_DURATION)
        self.block_hold_time = _config.get('combat', 'sword_attack', 'block_hold_time', SWORD_BLOCK_HOLD_TIME)

    def can_use(self, player_state):
        """Can attack if not currently attacking and not on cooldown."""
        return not self.is_attacking and not self.is_on_cooldown()

    def use(self, player_state, input_state):
        """
        Begin sword action - start tracking hold time.

        Returns:
            dict: Initial state modifications
        """
        # Start tracking hold time
        self.hold_timer = 0.0

        return {}

    def on_input_pressed(self, player_state):
        """Called when sword input is first pressed."""
        self.hold_timer = 0.0

    def on_input_held(self, dt, player_state):
        """
        Called while sword input is held - tracks hold duration.

        Args:
            dt: Delta time since last frame
            player_state: Current player state

        Returns:
            dict: State modifications (block activation)
        """
        if self.is_attacking:
            return {}  # Can't block during attack

        self.hold_timer += dt

        # Activate block if held long enough
        if self.hold_timer >= self.block_hold_time:
            if not self.is_blocking:
                self.is_blocking = True
                return {
                    'is_blocking': True,
                    'block_damage_reduction': 0.5,  # 50% damage reduction
                    'can_reflect_projectiles': True
                }
            return {'is_blocking': True}

        return {}

    def on_input_released(self, player_state):
        """
        Called when sword input is released.

        Short press = attack
        Long press = block ends

        Returns:
            dict: State modifications (attack or block end)
        """
        # If was blocking, end block
        if self.is_blocking:
            self.is_blocking = False
            self.hold_timer = 0.0
            return {
                'is_blocking': False,
                'block_damage_reduction': 0.0,
                'can_reflect_projectiles': False
            }

        # If held briefly, execute attack (tap)
        if self.hold_timer < self.block_hold_time and self.can_use(player_state):
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.start_cooldown()

            facing = player_state.get('facing', 1)

            return {
                'is_attacking': True,
                'attack_direction': facing,
                'attack_range': self.range,
                'attack_damage': self.damage,
                'attack_knockback': 8.0  # Knockback force
            }

        self.hold_timer = 0.0
        return {}

    def update(self, dt, player_state):
        """Update attack timer and cooldown."""
        # Update cooldown
        self.update_cooldown(dt)

        # Update attack
        if self.is_attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
                return {'is_attacking': False}

            # Continue attack
            return {'is_attacking': True}

        return {}

    def reset(self):
        """Reset sword state."""
        super().reset()
        self.is_attacking = False
        self.is_blocking = False
        self.attack_timer = 0.0
        self.hold_timer = 0.0

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_attacking:
            info['status'] = f"attacking ({self.attack_timer:.2f}s)"
        elif self.is_blocking:
            info['status'] = "blocking"
        return info


class GrappleHook(CooldownAbility):
    """
    Grapple hook ability - interact with objects and enemies.

    Purpose:
    - Pull levers/switches for puzzles
    - Maneuver/pull enemies
    - NOT for player movement (per design requirements)

    Mechanics:
    - Fires grapple hook toward aim direction
    - Connects to grapple points, levers, or enemies
    - Pull action affects target, not player position

    State:
    - is_active: Whether grapple is deployed
    - grapple_timer: Time grapple is extended
    - target: What the grapple has connected to
    - max_range: Maximum grapple range
    """

    def __init__(self):
        cooldown = _config.get('combat', 'grapple_hook', 'cooldown', 1.0)
        super().__init__("GRAPPLE_HOOK", cooldown_duration=cooldown)
        self.is_active = False
        self.grapple_timer = 0.0
        self.target = None
        self.max_range = _config.get('combat', 'grapple_hook', 'range', 200)  # Pixels
        self.pull_force = _config.get('combat', 'grapple_hook', 'pull_speed', 10.0)
        self.duration = _config.get('combat', 'grapple_hook', 'duration', 1.5)  # Max grapple extension time

    def can_use(self, player_state):
        """Can use if not active and not on cooldown."""
        return not self.is_active and not self.is_on_cooldown()

    def use(self, player_state, input_state):
        """
        Fire grapple hook.

        Returns:
            dict: Grapple fire state
        """
        # Get aim direction (from mouse or directional input)
        aim_x = input_state.get('aim_x', player_state.get('facing', 1))
        aim_y = input_state.get('aim_y', 0)

        self.is_active = True
        self.grapple_timer = self.duration

        return {
            'is_grappling': True,
            'grapple_direction': (aim_x, aim_y),
            'grapple_range': self.max_range,
            'grapple_type': 'object_pull'  # Not player movement
        }

    def connect_to_target(self, target):
        """
        Called when grapple connects to a valid target.

        Args:
            target: The object grappled (lever, enemy, etc.)
        """
        self.target = target

    def update(self, dt, player_state):
        """Update grapple state and pull logic."""
        # Update cooldown
        self.update_cooldown(dt)

        if self.is_active:
            self.grapple_timer -= dt

            # End grapple if time expires
            if self.grapple_timer <= 0:
                self.is_active = False
                self.target = None
                self.start_cooldown()
                return {'is_grappling': False}

            # If connected to target, apply pull force
            if self.target is not None:
                return {
                    'is_grappling': True,
                    'pull_target': self.target,
                    'pull_force': self.pull_force
                }

            return {'is_grappling': True}

        return {}

    def release(self):
        """Manually release grapple."""
        self.is_active = False
        self.target = None
        self.grapple_timer = 0.0
        self.start_cooldown()

    def reset(self):
        """Reset grapple state."""
        super().reset()
        self.is_active = False
        self.grapple_timer = 0.0
        self.target = None

    def get_debug_info(self):
        info = super().get_debug_info()
        if self.is_active:
            status = "grappling"
            if self.target:
                status += f" (connected)"
            info['status'] = status
        return info


# Export combat abilities
__all__ = ['SwordAttack', 'GrappleHook']
