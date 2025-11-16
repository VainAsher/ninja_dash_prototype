"""Ability Cooldown and Cost Modifier System

Provides a flexible system for modifying ability costs and cooldowns through:
- Equipment bonuses
- Powerup effects
- Skill tree upgrades
- Temporary buffs/debuffs
- Combo bonuses

Modifiers can stack multiplicatively or additively depending on their type.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
import time


class ModifierType(Enum):
    """Types of modifiers that can affect abilities."""
    COOLDOWN = "cooldown"  # Affects cooldown duration
    STAMINA_COST = "stamina_cost"  # Affects stamina consumption
    CHARGE_REGEN = "charge_regen"  # Affects charge regeneration speed
    DURATION = "duration"  # Affects active ability duration
    POWER = "power"  # Affects ability power/effectiveness


class ModifierSource(Enum):
    """Source of a modifier (for tracking and priority)."""
    EQUIPMENT = "equipment"
    POWERUP = "powerup"
    SKILL_TREE = "skill_tree"
    COMBO = "combo"
    BUFF = "buff"
    DEBUFF = "debuff"
    LEVEL = "level"


class StackingType(Enum):
    """How modifiers of the same type combine."""
    MULTIPLICATIVE = "multiplicative"  # Effects multiply: 0.9 * 0.8 = 0.72
    ADDITIVE = "additive"  # Effects add: -10% + -20% = -30%
    MAX = "max"  # Take maximum effect
    MIN = "min"  # Take minimum effect


@dataclass
class AbilityModifier:
    """
    Represents a single modifier to an ability.

    Example multiplicative cooldown reduction:
        modifier = 0.8  # 20% cooldown reduction (cooldown * 0.8)

    Example additive cost reduction:
        modifier = -0.2  # -20% cost (cost + cost * -0.2)
    """
    modifier_id: str  # Unique identifier
    modifier_type: ModifierType
    source: ModifierSource
    value: float  # Modifier value (multiplier or additive)
    stacking_type: StackingType
    duration: Optional[float] = None  # None = permanent, else seconds remaining
    ability_filter: Optional[Set[str]] = None  # None = all abilities, else specific ability names
    description: str = ""
    priority: int = 0  # Higher priority modifiers apply first

    def applies_to_ability(self, ability_name: str) -> bool:
        """Check if this modifier applies to a given ability."""
        if self.ability_filter is None:
            return True
        return ability_name in self.ability_filter

    def is_active(self) -> bool:
        """Check if modifier is still active (for temporary modifiers)."""
        return self.duration is None or self.duration > 0

    def update(self, dt: float) -> bool:
        """
        Update duration for temporary modifiers.

        Args:
            dt: Delta time in seconds

        Returns:
            True if still active, False if expired
        """
        if self.duration is not None:
            self.duration = max(0.0, self.duration - dt)
            return self.duration > 0
        return True


@dataclass
class ModifierStats:
    """Statistics for tracking modifier application."""
    total_applied: int = 0
    total_expired: int = 0
    total_removed: int = 0
    active_count: int = 0
    by_source: Dict[ModifierSource, int] = field(default_factory=dict)
    by_type: Dict[ModifierType, int] = field(default_factory=dict)


class AbilityModifierManager:
    """
    Manages ability modifiers and applies them to ability costs/cooldowns.

    Features:
    - Multiple stacking strategies (multiplicative, additive, max, min)
    - Temporary and permanent modifiers
    - Priority-based application
    - Per-ability filtering
    - Statistics and debugging

    Usage:
        # Create manager
        mgr = AbilityModifierManager()

        # Add a permanent 20% cooldown reduction from equipment
        mgr.add_modifier(AbilityModifier(
            modifier_id="boots_of_speed",
            modifier_type=ModifierType.COOLDOWN,
            source=ModifierSource.EQUIPMENT,
            value=0.8,  # 80% of original cooldown
            stacking_type=StackingType.MULTIPLICATIVE,
            description="Boots of Speed: -20% cooldown"
        ))

        # Add a temporary 50% cooldown reduction for 5 seconds
        mgr.add_modifier(AbilityModifier(
            modifier_id="haste_buff",
            modifier_type=ModifierType.COOLDOWN,
            source=ModifierSource.BUFF,
            value=0.5,
            stacking_type=StackingType.MULTIPLICATIVE,
            duration=5.0,
            description="Haste: -50% cooldown for 5s"
        ))

        # Apply modifiers to a cooldown
        modified_cooldown = mgr.apply_modifiers(
            base_value=2.0,
            modifier_type=ModifierType.COOLDOWN,
            ability_name="dash"
        )
        # Result: 2.0 * 0.8 * 0.5 = 0.8 seconds

        # Update each frame to handle temporary modifiers
        mgr.update(dt)
    """

    def __init__(self):
        """Initialize the modifier manager."""
        self._modifiers: Dict[str, AbilityModifier] = {}
        self._stats = ModifierStats()

    def add_modifier(self, modifier: AbilityModifier) -> None:
        """
        Add a modifier to the system.

        Args:
            modifier: The modifier to add (replaces existing with same ID)
        """
        # Remove old modifier if exists
        if modifier.modifier_id in self._modifiers:
            self.remove_modifier(modifier.modifier_id)

        self._modifiers[modifier.modifier_id] = modifier

        # Update stats
        self._stats.total_applied += 1
        self._stats.active_count = len(self._modifiers)
        self._stats.by_source[modifier.source] = self._stats.by_source.get(modifier.source, 0) + 1
        self._stats.by_type[modifier.modifier_type] = self._stats.by_type.get(modifier.modifier_type, 0) + 1

    def remove_modifier(self, modifier_id: str) -> bool:
        """
        Remove a modifier by ID.

        Args:
            modifier_id: The ID of the modifier to remove

        Returns:
            True if removed, False if not found
        """
        if modifier_id not in self._modifiers:
            return False

        modifier = self._modifiers[modifier_id]
        del self._modifiers[modifier_id]

        # Update stats
        self._stats.total_removed += 1
        self._stats.active_count = len(self._modifiers)
        self._stats.by_source[modifier.source] = max(0, self._stats.by_source.get(modifier.source, 0) - 1)
        self._stats.by_type[modifier.modifier_type] = max(0, self._stats.by_type.get(modifier.modifier_type, 0) - 1)

        return True

    def has_modifier(self, modifier_id: str) -> bool:
        """Check if a modifier is active."""
        return modifier_id in self._modifiers and self._modifiers[modifier_id].is_active()

    def get_modifier(self, modifier_id: str) -> Optional[AbilityModifier]:
        """Get a modifier by ID."""
        return self._modifiers.get(modifier_id)

    def clear_by_source(self, source: ModifierSource) -> int:
        """
        Remove all modifiers from a specific source.

        Args:
            source: The source to clear

        Returns:
            Number of modifiers removed
        """
        to_remove = [
            mod_id for mod_id, mod in self._modifiers.items()
            if mod.source == source
        ]

        for mod_id in to_remove:
            self.remove_modifier(mod_id)

        return len(to_remove)

    def clear_temporary(self) -> int:
        """
        Remove all temporary modifiers (those with duration).

        Returns:
            Number of modifiers removed
        """
        to_remove = [
            mod_id for mod_id, mod in self._modifiers.items()
            if mod.duration is not None
        ]

        for mod_id in to_remove:
            self.remove_modifier(mod_id)

        return len(to_remove)

    def update(self, dt: float) -> int:
        """
        Update all modifiers, removing expired temporary ones.

        Args:
            dt: Delta time in seconds

        Returns:
            Number of modifiers that expired
        """
        expired = []

        for mod_id, modifier in self._modifiers.items():
            if not modifier.update(dt):
                expired.append(mod_id)

        # Remove expired modifiers
        for mod_id in expired:
            self.remove_modifier(mod_id)
            self._stats.total_expired += 1

        return len(expired)

    def get_active_modifiers(
        self,
        modifier_type: ModifierType,
        ability_name: Optional[str] = None
    ) -> List[AbilityModifier]:
        """
        Get all active modifiers of a specific type for an ability.

        Args:
            modifier_type: Type of modifier to get
            ability_name: Optional ability name to filter for

        Returns:
            List of active modifiers, sorted by priority (highest first)
        """
        modifiers = []

        for modifier in self._modifiers.values():
            # Check if modifier is active
            if not modifier.is_active():
                continue

            # Check type
            if modifier.modifier_type != modifier_type:
                continue

            # Check ability filter
            if ability_name is not None and not modifier.applies_to_ability(ability_name):
                continue

            modifiers.append(modifier)

        # Sort by priority (highest first)
        modifiers.sort(key=lambda m: m.priority, reverse=True)

        return modifiers

    def apply_modifiers(
        self,
        base_value: float,
        modifier_type: ModifierType,
        ability_name: Optional[str] = None
    ) -> float:
        """
        Apply all relevant modifiers to a base value.

        Args:
            base_value: The base value to modify
            modifier_type: Type of modification
            ability_name: Optional ability name for filtering

        Returns:
            Modified value after applying all modifiers
        """
        modifiers = self.get_active_modifiers(modifier_type, ability_name)

        if not modifiers:
            return base_value

        # Separate by stacking type
        multiplicative = [m for m in modifiers if m.stacking_type == StackingType.MULTIPLICATIVE]
        additive = [m for m in modifiers if m.stacking_type == StackingType.ADDITIVE]
        max_mods = [m for m in modifiers if m.stacking_type == StackingType.MAX]
        min_mods = [m for m in modifiers if m.stacking_type == StackingType.MIN]

        result = base_value

        # Apply multiplicative modifiers (they multiply together)
        for mod in multiplicative:
            result *= mod.value

        # Apply additive modifiers (they add together then apply to base)
        if additive:
            additive_sum = sum(m.value for m in additive)
            result = result * (1.0 + additive_sum)

        # Apply MAX modifiers (take the best one)
        if max_mods:
            best_max = max(m.value for m in max_mods)
            result = max(result, base_value * best_max)

        # Apply MIN modifiers (take the best one)
        if min_mods:
            best_min = min(m.value for m in min_mods)
            result = min(result, base_value * best_min)

        return result

    def get_effective_multiplier(
        self,
        modifier_type: ModifierType,
        ability_name: Optional[str] = None
    ) -> float:
        """
        Calculate the effective multiplier for a modifier type.

        Args:
            modifier_type: Type of modifier
            ability_name: Optional ability name

        Returns:
            Effective multiplier (e.g., 0.8 = 20% reduction)
        """
        return self.apply_modifiers(1.0, modifier_type, ability_name)

    def get_debug_info(self) -> Dict:
        """Get debug information about active modifiers."""
        active_mods = {}

        for mod_id, modifier in self._modifiers.items():
            if modifier.is_active():
                active_mods[mod_id] = {
                    'type': modifier.modifier_type.value,
                    'source': modifier.source.value,
                    'value': modifier.value,
                    'stacking': modifier.stacking_type.value,
                    'duration': f"{modifier.duration:.2f}s" if modifier.duration else "permanent",
                    'description': modifier.description,
                }

        return {
            'active_modifiers': active_mods,
            'total_count': len(active_mods),
            'stats': {
                'total_applied': self._stats.total_applied,
                'total_expired': self._stats.total_expired,
                'total_removed': self._stats.total_removed,
                'active_count': self._stats.active_count,
            }
        }

    def get_stats(self) -> ModifierStats:
        """Get full statistics."""
        return self._stats


# Global modifier manager instance
_global_modifier_manager: Optional[AbilityModifierManager] = None


def get_modifier_manager() -> AbilityModifierManager:
    """Get or create the global modifier manager instance."""
    global _global_modifier_manager
    if _global_modifier_manager is None:
        _global_modifier_manager = AbilityModifierManager()
    return _global_modifier_manager


def create_cooldown_modifier(
    modifier_id: str,
    reduction_percent: float,
    source: ModifierSource,
    duration: Optional[float] = None,
    ability_filter: Optional[Set[str]] = None,
    description: str = ""
) -> AbilityModifier:
    """
    Helper to create a cooldown reduction modifier.

    Args:
        modifier_id: Unique ID
        reduction_percent: Percent reduction (e.g., 20 for 20% reduction)
        source: Source of modifier
        duration: Optional duration in seconds
        ability_filter: Optional set of ability names
        description: Description for debugging

    Returns:
        AbilityModifier configured for cooldown reduction
    """
    multiplier = 1.0 - (reduction_percent / 100.0)
    return AbilityModifier(
        modifier_id=modifier_id,
        modifier_type=ModifierType.COOLDOWN,
        source=source,
        value=multiplier,
        stacking_type=StackingType.MULTIPLICATIVE,
        duration=duration,
        ability_filter=ability_filter,
        description=description or f"-{reduction_percent}% cooldown"
    )


def create_stamina_modifier(
    modifier_id: str,
    reduction_percent: float,
    source: ModifierSource,
    duration: Optional[float] = None,
    ability_filter: Optional[Set[str]] = None,
    description: str = ""
) -> AbilityModifier:
    """
    Helper to create a stamina cost reduction modifier.

    Args:
        modifier_id: Unique ID
        reduction_percent: Percent reduction (e.g., 20 for 20% reduction)
        source: Source of modifier
        duration: Optional duration in seconds
        ability_filter: Optional set of ability names
        description: Description for debugging

    Returns:
        AbilityModifier configured for stamina reduction
    """
    multiplier = 1.0 - (reduction_percent / 100.0)
    return AbilityModifier(
        modifier_id=modifier_id,
        modifier_type=ModifierType.STAMINA_COST,
        source=source,
        value=multiplier,
        stacking_type=StackingType.MULTIPLICATIVE,
        duration=duration,
        ability_filter=ability_filter,
        description=description or f"-{reduction_percent}% stamina cost"
    )
