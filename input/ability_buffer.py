"""Ability Input Buffering System

Provides centralized input buffering for all abilities to improve responsiveness.
When a player presses an ability input during an animation or when the ability
can't be used, the input is buffered and automatically executed when possible.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Callable
from enum import Enum


class AbilityType(Enum):
    """Enumeration of all bufferable abilities."""
    JUMP = "jump"
    DASH = "dash"
    SLIDE = "slide"
    AIR_DODGE = "air_dodge"
    SHADOW_STEP = "shadow_step"
    WALL_JUMP = "wall_jump"
    GRAPPLE = "grapple"
    ATTACK = "attack"


@dataclass
class BufferedInput:
    """Represents a buffered ability input."""
    ability_type: AbilityType
    time_remaining: float  # Time left before buffer expires
    input_data: Optional[Dict] = None  # Optional additional input data (e.g., direction)

    def update(self, dt: float) -> bool:
        """
        Update the buffer timer.

        Args:
            dt: Delta time in seconds

        Returns:
            True if buffer is still active, False if expired
        """
        self.time_remaining = max(0.0, self.time_remaining - dt)
        return self.time_remaining > 0


class AbilityInputBuffer:
    """
    Centralized input buffering system for all abilities.

    Features:
    - Configurable buffer window per ability type
    - Automatic buffer expiration
    - Priority system for conflicting inputs
    - Debug information

    Usage:
        # Initialize
        buffer = AbilityInputBuffer()

        # Buffer an input
        buffer.buffer_input(AbilityType.DASH)

        # Check and consume buffered input
        if buffer.has_buffered_input(AbilityType.DASH):
            buffer.consume_buffered_input(AbilityType.DASH)
            # Execute dash ability

        # Update each frame
        buffer.update(dt)
    """

    # Default buffer times for each ability (in seconds)
    DEFAULT_BUFFER_TIMES = {
        AbilityType.JUMP: 0.14,
        AbilityType.DASH: 0.12,
        AbilityType.SLIDE: 0.10,
        AbilityType.AIR_DODGE: 0.12,
        AbilityType.SHADOW_STEP: 0.15,
        AbilityType.WALL_JUMP: 0.14,
        AbilityType.GRAPPLE: 0.12,
        AbilityType.ATTACK: 0.10,
    }

    def __init__(self, custom_buffer_times: Optional[Dict[AbilityType, float]] = None):
        """
        Initialize the ability input buffer.

        Args:
            custom_buffer_times: Optional dict to override default buffer times
        """
        self._buffers: Dict[AbilityType, BufferedInput] = {}

        # Merge custom buffer times with defaults
        self._buffer_times = self.DEFAULT_BUFFER_TIMES.copy()
        if custom_buffer_times:
            self._buffer_times.update(custom_buffer_times)

        # Statistics for debugging
        self._stats = {
            'total_buffered': 0,
            'total_consumed': 0,
            'total_expired': 0,
            'per_ability': {ability: {'buffered': 0, 'consumed': 0, 'expired': 0}
                          for ability in AbilityType}
        }

    def buffer_input(
        self,
        ability_type: AbilityType,
        input_data: Optional[Dict] = None,
        override_time: Optional[float] = None
    ) -> None:
        """
        Buffer an ability input.

        Args:
            ability_type: The ability to buffer
            input_data: Optional additional input data (e.g., direction)
            override_time: Optional custom buffer duration (overrides default)
        """
        buffer_time = override_time if override_time is not None else self._buffer_times.get(
            ability_type, 0.12
        )

        self._buffers[ability_type] = BufferedInput(
            ability_type=ability_type,
            time_remaining=buffer_time,
            input_data=input_data
        )

        # Update stats
        self._stats['total_buffered'] += 1
        self._stats['per_ability'][ability_type]['buffered'] += 1

    def has_buffered_input(self, ability_type: AbilityType) -> bool:
        """
        Check if there's an active buffered input for an ability.

        Args:
            ability_type: The ability to check

        Returns:
            True if there's an active buffer, False otherwise
        """
        buffered_input = self._buffers.get(ability_type)
        return buffered_input is not None and buffered_input.time_remaining > 0

    def get_buffered_input(self, ability_type: AbilityType) -> Optional[BufferedInput]:
        """
        Get the buffered input without consuming it.

        Args:
            ability_type: The ability to check

        Returns:
            The BufferedInput if active, None otherwise
        """
        buffered_input = self._buffers.get(ability_type)
        if buffered_input and buffered_input.time_remaining > 0:
            return buffered_input
        return None

    def consume_buffered_input(self, ability_type: AbilityType) -> Optional[Dict]:
        """
        Consume (clear) a buffered input and return its data.

        Args:
            ability_type: The ability to consume

        Returns:
            The input data if there was a buffered input, None otherwise
        """
        buffered_input = self._buffers.get(ability_type)
        if buffered_input and buffered_input.time_remaining > 0:
            input_data = buffered_input.input_data
            del self._buffers[ability_type]

            # Update stats
            self._stats['total_consumed'] += 1
            self._stats['per_ability'][ability_type]['consumed'] += 1

            return input_data
        return None

    def clear_buffer(self, ability_type: AbilityType) -> None:
        """
        Clear a buffered input without counting it as consumed.

        Args:
            ability_type: The ability to clear
        """
        if ability_type in self._buffers:
            del self._buffers[ability_type]

    def clear_all_buffers(self) -> None:
        """Clear all buffered inputs."""
        self._buffers.clear()

    def update(self, dt: float) -> None:
        """
        Update all buffered inputs, removing expired ones.

        Args:
            dt: Delta time in seconds
        """
        expired = []

        for ability_type, buffered_input in self._buffers.items():
            if not buffered_input.update(dt):
                expired.append(ability_type)
                self._stats['total_expired'] += 1
                self._stats['per_ability'][ability_type]['expired'] += 1

        # Remove expired buffers
        for ability_type in expired:
            del self._buffers[ability_type]

    def get_debug_info(self) -> Dict:
        """
        Get debug information about buffered inputs.

        Returns:
            Dict with active buffers and statistics
        """
        active_buffers = {}
        for ability_type, buffered_input in self._buffers.items():
            if buffered_input.time_remaining > 0:
                active_buffers[ability_type.value] = {
                    'time_remaining': f"{buffered_input.time_remaining:.3f}s",
                    'has_data': buffered_input.input_data is not None
                }

        return {
            'active_buffers': active_buffers,
            'buffer_count': len(active_buffers),
            'stats': {
                'total_buffered': self._stats['total_buffered'],
                'total_consumed': self._stats['total_consumed'],
                'total_expired': self._stats['total_expired'],
                'success_rate': (
                    f"{100 * self._stats['total_consumed'] / max(1, self._stats['total_buffered']):.1f}%"
                )
            }
        }

    def get_stats(self) -> Dict:
        """Get full statistics including per-ability breakdown."""
        return self._stats.copy()

    def reset_stats(self) -> None:
        """Reset all statistics."""
        self._stats = {
            'total_buffered': 0,
            'total_consumed': 0,
            'total_expired': 0,
            'per_ability': {ability: {'buffered': 0, 'consumed': 0, 'expired': 0}
                          for ability in AbilityType}
        }


class ConditionalBufferExecutor:
    """
    Helper class to execute buffered abilities when conditions are met.

    This class checks buffered inputs against condition functions and
    automatically executes them when possible.
    """

    def __init__(self, input_buffer: AbilityInputBuffer):
        """
        Initialize the executor.

        Args:
            input_buffer: The AbilityInputBuffer to manage
        """
        self.input_buffer = input_buffer
        self._conditions: Dict[AbilityType, Callable[[], bool]] = {}
        self._executors: Dict[AbilityType, Callable[[Optional[Dict]], None]] = {}

    def register_ability(
        self,
        ability_type: AbilityType,
        condition_fn: Callable[[], bool],
        executor_fn: Callable[[Optional[Dict]], None]
    ) -> None:
        """
        Register an ability with its condition check and execution function.

        Args:
            ability_type: The ability to register
            condition_fn: Function that returns True if ability can execute
            executor_fn: Function to execute the ability (receives input_data)
        """
        self._conditions[ability_type] = condition_fn
        self._executors[ability_type] = executor_fn

    def check_and_execute_buffers(self) -> int:
        """
        Check all buffered abilities and execute those whose conditions are met.

        Returns:
            Number of abilities executed
        """
        executed_count = 0

        for ability_type in list(self.input_buffer._buffers.keys()):
            # Check if we have condition and executor registered
            if ability_type not in self._conditions or ability_type not in self._executors:
                continue

            # Check if buffered input is still active
            if not self.input_buffer.has_buffered_input(ability_type):
                continue

            # Check condition
            if self._conditions[ability_type]():
                # Consume and execute
                input_data = self.input_buffer.consume_buffered_input(ability_type)
                self._executors[ability_type](input_data)
                executed_count += 1

        return executed_count

    def unregister_ability(self, ability_type: AbilityType) -> None:
        """Unregister an ability."""
        self._conditions.pop(ability_type, None)
        self._executors.pop(ability_type, None)
