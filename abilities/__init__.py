"""
Ability System - Base classes for player abilities

This module provides the base Ability class that all player abilities inherit from.
Abilities are self-contained systems with their own state, update logic, and activation conditions.
"""

from abc import ABC, abstractmethod
from typing import Optional

# Lazy import to avoid circular dependencies
def _get_modifier_manager():
    """Lazy import of modifier manager to avoid circular dependencies."""
    try:
        from abilities.modifiers import get_modifier_manager
        return get_modifier_manager()
    except ImportError:
        return None


class Ability(ABC):
    """
    Base class for all player abilities.

    Abilities encapsulate their own state (cooldowns, charges, timers) and logic
    (can_use, use, update). This separation allows for cleaner player code and
    easier testing of individual abilities.
    """

    def __init__(self, name):
        """
        Initialize the ability with a name.

        Args:
            name: String identifier for this ability (e.g., "DASH", "DOUBLE_JUMP")
        """
        self.name = name
        self.enabled = False  # Set to True when ability is unlocked

    @abstractmethod
    def can_use(self, player_state):
        """
        Check if the ability can be activated given current player state.

        Args:
            player_state: Dictionary containing relevant player state information
                         (on_ground, on_wall, velocity, etc.)

        Returns:
            bool: True if the ability can be activated, False otherwise
        """
        pass

    @abstractmethod
    def use(self, player_state, input_state):
        """
        Activate the ability and return movement modifications.

        Args:
            player_state: Dictionary containing current player state
            input_state: Dictionary containing current input (keys, direction)

        Returns:
            dict: Movement modifications to apply (e.g., {'vx': 10, 'vy': -5})
                 or None if ability doesn't modify movement directly
        """
        pass

    @abstractmethod
    def update(self, dt, player_state):
        """
        Update ability state (timers, cooldowns, etc.).

        Args:
            dt: Delta time since last frame
            player_state: Dictionary containing current player state

        Returns:
            dict: Any state modifications to apply to the player (e.g., invulnerability)
        """
        pass

    def reset(self):
        """
        Reset ability to initial state.
        Called when entering a new level or respawning.
        """
        pass

    def is_active(self):
        """
        Check if the ability is currently active.

        Returns:
            bool: True if the ability is currently executing
        """
        return False

    def get_debug_info(self):
        """
        Get debug information about the ability's current state.

        Returns:
            dict: Debug information (cooldowns, charges, etc.)
        """
        return {"name": self.name, "enabled": self.enabled}


class ResourceAbility(Ability):
    """
    Base class for abilities that consume a resource (charges, stamina, etc.).
    """

    def __init__(self, name, max_resource, resource_name="charges"):
        """
        Initialize resource-based ability.

        Args:
            name: Ability name
            max_resource: Maximum resource amount (e.g., max charges)
            resource_name: Name of the resource (for debugging)
        """
        super().__init__(name)
        self.max_resource = max_resource
        self.resource = max_resource
        self.resource_name = resource_name

    def consume_resource(self, amount=1):
        """
        Consume resource and return success status.

        Args:
            amount: Amount of resource to consume

        Returns:
            bool: True if resource was consumed, False if insufficient
        """
        if self.resource >= amount:
            self.resource -= amount
            return True
        return False

    def restore_resource(self, amount=1):
        """
        Restore resource up to maximum.

        Args:
            amount: Amount of resource to restore
        """
        self.resource = min(self.max_resource, self.resource + amount)

    def reset(self):
        """Reset resource to maximum."""
        self.resource = self.max_resource

    def get_debug_info(self):
        """Include resource information in debug output."""
        info = super().get_debug_info()
        info[self.resource_name] = f"{self.resource}/{self.max_resource}"
        return info


class CooldownAbility(Ability):
    """
    Base class for abilities with cooldown timers.
    Supports cooldown modifiers from the modifier system.
    """

    def __init__(self, name, cooldown_duration):
        """
        Initialize cooldown-based ability.

        Args:
            name: Ability name
            cooldown_duration: Base cooldown time in seconds (before modifiers)
        """
        super().__init__(name)
        self.base_cooldown_duration = cooldown_duration
        self.cooldown_duration = cooldown_duration
        self.cooldown_timer = 0.0

    def get_modified_cooldown(self) -> float:
        """
        Get cooldown duration with modifiers applied.

        Returns:
            Modified cooldown duration
        """
        mgr = _get_modifier_manager()
        if mgr is None:
            return self.base_cooldown_duration

        from abilities.modifiers import ModifierType
        return mgr.apply_modifiers(
            self.base_cooldown_duration,
            ModifierType.COOLDOWN,
            self.name
        )

    def start_cooldown(self):
        """Start the cooldown timer with modifiers applied."""
        self.cooldown_duration = self.get_modified_cooldown()
        self.cooldown_timer = self.cooldown_duration

    def update_cooldown(self, dt):
        """
        Update cooldown timer.

        Args:
            dt: Delta time since last frame
        """
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

    def is_on_cooldown(self):
        """
        Check if ability is on cooldown.

        Returns:
            bool: True if on cooldown, False if ready
        """
        return self.cooldown_timer > 0

    def get_debug_info(self):
        """Include cooldown information in debug output."""
        info = super().get_debug_info()
        info["cooldown"] = f"{self.cooldown_timer:.2f}s" if self.is_on_cooldown() else "ready"

        # Show modifier effect if present
        modified_cd = self.get_modified_cooldown()
        if abs(modified_cd - self.base_cooldown_duration) > 0.01:
            reduction_pct = 100 * (1 - modified_cd / self.base_cooldown_duration)
            info["cooldown_mod"] = f"{reduction_pct:+.0f}%"

        return info


class StaminaAbility(ResourceAbility):
    """
    Base class for abilities that use stamina with automatic regeneration.
    Supports stamina cost modifiers from the modifier system.
    """

    def __init__(self, name, max_stamina, regen_rate, drain_rate=0):
        """
        Initialize stamina-based ability.

        Args:
            name: Ability name
            max_stamina: Maximum stamina amount
            regen_rate: Stamina regeneration per second when not in use
            drain_rate: Base stamina drain per second when active (0 for instant consumption)
        """
        super().__init__(name, max_stamina, "stamina")
        self.base_regen_rate = regen_rate
        self.base_drain_rate = drain_rate
        self.regen_rate = regen_rate
        self.drain_rate = drain_rate

    def get_modified_drain_rate(self) -> float:
        """
        Get drain rate with modifiers applied.

        Returns:
            Modified drain rate
        """
        mgr = _get_modifier_manager()
        if mgr is None:
            return self.base_drain_rate

        from abilities.modifiers import ModifierType
        return mgr.apply_modifiers(
            self.base_drain_rate,
            ModifierType.STAMINA_COST,
            self.name
        )

    def get_modified_regen_rate(self) -> float:
        """
        Get regen rate with modifiers applied.

        Returns:
            Modified regen rate
        """
        mgr = _get_modifier_manager()
        if mgr is None:
            return self.base_regen_rate

        from abilities.modifiers import ModifierType
        return mgr.apply_modifiers(
            self.base_regen_rate,
            ModifierType.CHARGE_REGEN,
            self.name
        )

    def regenerate_stamina(self, dt):
        """
        Regenerate stamina over time with modifiers applied.

        Args:
            dt: Delta time since last frame
        """
        self.regen_rate = self.get_modified_regen_rate()
        self.restore_resource(self.regen_rate * dt)

    def drain_stamina(self, dt):
        """
        Drain stamina over time while active with modifiers applied.

        Args:
            dt: Delta time since last frame

        Returns:
            bool: True if stamina was drained, False if depleted
        """
        self.drain_rate = self.get_modified_drain_rate()
        drain_amount = self.drain_rate * dt
        return self.consume_resource(drain_amount)

    def get_debug_info(self):
        """Include stamina regen info in debug output."""
        info = super().get_debug_info()
        info["regen_rate"] = f"{self.regen_rate:.2f}/s"
        if self.drain_rate > 0:
            info["drain_rate"] = f"{self.drain_rate:.2f}/s"

            # Show modifier effect if present
            modified_drain = self.get_modified_drain_rate()
            if abs(modified_drain - self.base_drain_rate) > 0.01:
                reduction_pct = 100 * (1 - modified_drain / self.base_drain_rate)
                info["cost_mod"] = f"{reduction_pct:+.0f}%"

        return info


class AmmoAbility(Ability):
    """
    Base class for abilities that use consumable ammo/items.
    Ammo must be collected and doesn't regenerate automatically.
    """

    def __init__(self, name, max_ammo=0, starting_ammo=0):
        """
        Initialize ammo-based ability.

        Args:
            name: Ability name
            max_ammo: Maximum ammo capacity (0 = unlimited capacity)
            starting_ammo: Starting ammo count
        """
        super().__init__(name)
        self.max_ammo = max_ammo
        self.ammo = starting_ammo

    def consume_ammo(self, amount=1):
        """
        Consume ammo and return success status.

        Args:
            amount: Amount of ammo to consume

        Returns:
            bool: True if ammo was consumed, False if insufficient
        """
        if self.ammo >= amount:
            self.ammo -= amount
            return True
        return False

    def add_ammo(self, amount=1):
        """
        Add ammo up to maximum capacity.

        Args:
            amount: Amount of ammo to add

        Returns:
            int: Actual amount added (may be less if at capacity)
        """
        old_ammo = self.ammo
        if self.max_ammo > 0:
            self.ammo = min(self.max_ammo, self.ammo + amount)
        else:
            self.ammo += amount
        return self.ammo - old_ammo

    def has_ammo(self, amount=1):
        """
        Check if ability has sufficient ammo.

        Args:
            amount: Amount of ammo to check for

        Returns:
            bool: True if sufficient ammo available
        """
        return self.ammo >= amount

    def reset(self):
        """Reset ammo to starting amount (not max)."""
        pass  # Ammo persists across resets unless explicitly refilled

    def get_debug_info(self):
        """Include ammo information in debug output."""
        info = super().get_debug_info()
        if self.max_ammo > 0:
            info["ammo"] = f"{self.ammo}/{self.max_ammo}"
        else:
            info["ammo"] = str(self.ammo)
        return info


class CombinedCostAbility(CooldownAbility):
    """
    Base class for abilities that have both cooldown and resource costs.
    Useful for abilities like "3 charges, each with a cooldown".
    """

    def __init__(self, name, cooldown_duration, max_charges, charge_regen_per_level=0):
        """
        Initialize ability with cooldown and charges.

        Args:
            name: Ability name
            cooldown_duration: Cooldown time between uses in seconds
            max_charges: Maximum number of charges
            charge_regen_per_level: Charges restored when entering new level
        """
        super().__init__(name, cooldown_duration)
        self.max_charges = max_charges
        self.charges = max_charges
        self.charge_regen_per_level = charge_regen_per_level

    def consume_charge(self):
        """
        Consume a charge and return success status.

        Returns:
            bool: True if charge was consumed, False if no charges available
        """
        if self.charges > 0:
            self.charges -= 1
            return True
        return False

    def restore_charges(self, amount=None):
        """
        Restore charges up to maximum.

        Args:
            amount: Amount to restore, or None to restore all charges
        """
        if amount is None:
            self.charges = self.max_charges
        else:
            self.charges = min(self.max_charges, self.charges + amount)

    def reset(self):
        """Reset charges based on regen settings."""
        if self.charge_regen_per_level > 0:
            self.restore_charges(self.charge_regen_per_level)
        else:
            self.restore_charges()  # Full restore
        self.cooldown_timer = 0.0

    def get_debug_info(self):
        """Include both cooldown and charge information."""
        info = super().get_debug_info()
        info["charges"] = f"{self.charges}/{self.max_charges}"
        return info


# Export base classes
__all__ = ['Ability', 'ResourceAbility', 'CooldownAbility', 'StaminaAbility', 'AmmoAbility', 'CombinedCostAbility']
