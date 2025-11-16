"""
Ability Combo System

Tracks ability usage and detects combos for special effects and bonuses.
Rewards skilled play by providing benefits when abilities are chained together.
"""

import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class ComboPattern:
    """
    Definition of an ability combo.

    Attributes:
        name: Display name of the combo
        abilities: List of ability names that must be used in order
        timing_window: Maximum time (seconds) between abilities
        effect: Bonus effect to apply when combo is triggered
        description: Human-readable description
    """
    name: str
    abilities: List[str]
    timing_window: float
    effect: Dict[str, Any]
    description: str


@dataclass
class AbilityUsage:
    """Record of when an ability was used."""
    ability_name: str
    timestamp: float


class ComboTracker:
    """
    Tracks ability usage and detects combo patterns.

    This class maintains a history of recently used abilities and
    checks for matching combo patterns. When a combo is detected,
    it applies the associated effects.
    """

    def __init__(self):
        """Initialize the combo tracker."""
        self.usage_history: List[AbilityUsage] = []
        self.combo_patterns: Dict[str, ComboPattern] = {}
        self.active_combo: Optional[str] = None
        self.combo_effect_timer = 0.0
        self.last_combo_name = ""

        # Register default combo patterns
        self._register_default_combos()

    def _register_default_combos(self):
        """Register default ability combo patterns."""

        # Wall Jump -> Air Dodge: "Wall Dancer"
        # Extra air mobility after wall jump
        self.register_combo(ComboPattern(
            name="Wall Dancer",
            abilities=["WALL_JUMP", "AIR_DODGE"],
            timing_window=0.5,
            effect={
                'air_dodge_speed_boost': 1.3,  # 30% faster air dodge
                'duration': 0.8,
            },
            description="Wall Jump + Air Dodge: Enhanced aerial mobility"
        ))

        # Dash -> Slide: "Speed Demon"
        # Extended slide with more speed
        self.register_combo(ComboPattern(
            name="Speed Demon",
            abilities=["DASH", "SLIDE"],
            timing_window=0.3,
            effect={
                'slide_speed_boost': 1.4,  # 40% faster slide
                'slide_duration_boost': 1.2,  # 20% longer slide
                'duration': 1.0,
            },
            description="Dash + Slide: Blazing fast ground movement"
        ))

        # Air Dodge -> Glide: "Sky Master"
        # Better glide control after dodge
        self.register_combo(ComboPattern(
            name="Sky Master",
            abilities=["AIR_DODGE", "GLIDE"],
            timing_window=0.4,
            effect={
                'glide_control_boost': 1.5,  # 50% better air control
                'glide_speed_boost': 1.2,  # 20% faster horizontal
                'duration': 2.0,
            },
            description="Air Dodge + Glide: Superior aerial control"
        ))

        # Double Jump -> Dash: "Aerial Burst"
        # Speed boost in air
        self.register_combo(ComboPattern(
            name="Aerial Burst",
            abilities=["DOUBLE_JUMP", "DASH"],
            timing_window=0.5,
            effect={
                'air_speed_boost': 1.5,  # 50% faster air movement
                'duration': 0.6,
            },
            description="Double Jump + Dash: Explosive aerial speed"
        ))

        # Shadow Step -> Wall Jump: "Shadow Leap"
        # Enhanced wall jump out of shadow step
        self.register_combo(ComboPattern(
            name="Shadow Leap",
            abilities=["SHADOW_STEP", "WALL_JUMP"],
            timing_window=0.3,
            effect={
                'wall_jump_power_boost': 1.4,  # 40% stronger wall jump
                'invuln_extension': 0.2,  # Extra invuln frames
                'duration': 0.5,
            },
            description="Shadow Step + Wall Jump: Powerful evasive leap"
        ))

        # Wall Cling -> Air Dodge: "Wall Dodge"
        # Quick dodge off wall
        self.register_combo(ComboPattern(
            name="Wall Dodge",
            abilities=["WALL_CLING", "AIR_DODGE"],
            timing_window=0.4,
            effect={
                'air_dodge_invuln_boost': 1.3,  # 30% longer invuln
                'air_dodge_speed_boost': 1.2,  # 20% faster
                'duration': 0.5,
            },
            description="Wall Cling + Air Dodge: Swift wall evasion"
        ))

    def register_combo(self, pattern: ComboPattern):
        """
        Register a new combo pattern.

        Args:
            pattern: The combo pattern to register
        """
        self.combo_patterns[pattern.name] = pattern

    def record_ability_use(self, ability_name: str):
        """
        Record that an ability was used.

        Args:
            ability_name: Name of the ability that was used
        """
        current_time = time.time()
        self.usage_history.append(AbilityUsage(ability_name, current_time))

        # Clean up old history (keep last 10 seconds)
        cutoff_time = current_time - 10.0
        self.usage_history = [
            usage for usage in self.usage_history
            if usage.timestamp > cutoff_time
        ]

        # Check for combo matches
        self._check_combos(current_time)

    def _check_combos(self, current_time: float):
        """
        Check if recent ability usage matches any combo patterns.

        Args:
            current_time: Current timestamp
        """
        for combo_name, pattern in self.combo_patterns.items():
            if self._matches_pattern(pattern, current_time):
                self._trigger_combo(pattern)
                break  # Only trigger one combo at a time

    def _matches_pattern(self, pattern: ComboPattern, current_time: float) -> bool:
        """
        Check if recent history matches a combo pattern.

        Args:
            pattern: Combo pattern to check
            current_time: Current timestamp

        Returns:
            True if pattern matches recent usage
        """
        if len(self.usage_history) < len(pattern.abilities):
            return False

        # Get the most recent abilities matching the pattern length
        recent_abilities = self.usage_history[-len(pattern.abilities):]

        # Check if abilities match in order
        for i, required_ability in enumerate(pattern.abilities):
            if recent_abilities[i].ability_name != required_ability:
                return False

        # Check timing window
        first_time = recent_abilities[0].timestamp
        last_time = recent_abilities[-1].timestamp

        if (last_time - first_time) > pattern.timing_window:
            return False

        return True

    def _trigger_combo(self, pattern: ComboPattern):
        """
        Trigger a combo and apply its effects.

        Args:
            pattern: The combo pattern that was triggered
        """
        self.active_combo = pattern.name
        self.combo_effect_timer = pattern.effect.get('duration', 1.0)
        self.last_combo_name = pattern.name

        # Clear history to prevent re-triggering
        self.usage_history.clear()

    def update(self, dt: float) -> Dict[str, Any]:
        """
        Update combo timers.

        Args:
            dt: Delta time since last update

        Returns:
            Active combo effects
        """
        if self.combo_effect_timer > 0:
            self.combo_effect_timer -= dt

            if self.combo_effect_timer <= 0:
                self.active_combo = None

        return self.get_active_effects()

    def get_active_effects(self) -> Dict[str, Any]:
        """
        Get currently active combo effects.

        Returns:
            Dictionary of active effects and their values
        """
        if self.active_combo and self.combo_effect_timer > 0:
            pattern = self.combo_patterns[self.active_combo]
            effects = pattern.effect.copy()
            effects['combo_name'] = pattern.name
            effects['time_remaining'] = self.combo_effect_timer
            return effects
        return {}

    def is_combo_active(self) -> bool:
        """Check if any combo is currently active."""
        return self.active_combo is not None and self.combo_effect_timer > 0

    def get_combo_name(self) -> Optional[str]:
        """Get the name of the active combo, if any."""
        return self.active_combo if self.is_combo_active() else None

    def clear(self):
        """Clear all combo history and active effects."""
        self.usage_history.clear()
        self.active_combo = None
        self.combo_effect_timer = 0.0

    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information about combo system state.

        Returns:
            Debug information dictionary
        """
        return {
            'active_combo': self.active_combo,
            'combo_timer': f"{self.combo_effect_timer:.2f}s" if self.combo_effect_timer > 0 else "none",
            'history_size': len(self.usage_history),
            'last_combo': self.last_combo_name,
            'registered_combos': len(self.combo_patterns),
        }
