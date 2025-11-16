"""Performance Optimization Utilities for Ability System

This module provides utilities for optimizing ability system performance:
- Cached property decorators
- State snapshot caching
- Lazy evaluation helpers
- Performance profiling tools
"""

from __future__ import annotations
import time
from typing import Dict, Any, Callable, Optional
from functools import wraps
from dataclasses import dataclass


@dataclass
class PerformanceStats:
    """Statistics for ability system performance."""
    total_updates: int = 0
    total_time: float = 0.0
    ability_update_times: Dict[str, float] = None
    ability_update_counts: Dict[str, int] = None
    cache_hits: int = 0
    cache_misses: int = 0

    def __post_init__(self):
        if self.ability_update_times is None:
            self.ability_update_times = {}
        if self.ability_update_counts is None:
            self.ability_update_counts = {}

    def get_average_time(self, ability_name: Optional[str] = None) -> float:
        """Get average update time for an ability or all abilities."""
        if ability_name:
            count = self.ability_update_counts.get(ability_name, 0)
            if count == 0:
                return 0.0
            return self.ability_update_times.get(ability_name, 0.0) / count
        else:
            if self.total_updates == 0:
                return 0.0
            return self.total_time / self.total_updates

    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate as a percentage."""
        total_accesses = self.cache_hits + self.cache_misses
        if total_accesses == 0:
            return 0.0
        return 100.0 * self.cache_hits / total_accesses


class PlayerStateCache:
    """
    Cache for player state to avoid repeated dictionary lookups.

    The player state is queried many times per frame by different abilities.
    This cache reduces redundant dictionary accesses and provides optimized
    attribute-style access.
    """

    __slots__ = (
        '_on_ground', '_on_wall', '_wall_dir', '_vx', '_vy',
        '_facing', '_crouching', '_jump_power', '_timestamp',
        '_dirty'
    )

    def __init__(self):
        """Initialize empty cache."""
        self._on_ground = False
        self._on_wall = False
        self._wall_dir = 0
        self._vx = 0.0
        self._vy = 0.0
        self._facing = 1
        self._crouching = False
        self._jump_power = 0.0
        self._timestamp = 0.0
        self._dirty = True

    def update(self, player_state: Dict[str, Any], timestamp: float) -> None:
        """
        Update cache from player state dictionary.

        Args:
            player_state: Current player state
            timestamp: Current game timestamp
        """
        # Only update if state has changed or is stale
        if self._timestamp == timestamp and not self._dirty:
            return

        self._on_ground = player_state.get('on_ground', False)
        self._on_wall = player_state.get('on_wall', False)
        self._wall_dir = player_state.get('wall_dir', 0)
        self._vx = player_state.get('vx', 0.0)
        self._vy = player_state.get('vy', 0.0)
        self._facing = player_state.get('facing', 1)
        self._crouching = player_state.get('crouching', False)
        self._jump_power = player_state.get('jump_power', 0.0)
        self._timestamp = timestamp
        self._dirty = False

    def invalidate(self) -> None:
        """Mark cache as dirty (needs refresh)."""
        self._dirty = True

    # Optimized property access
    @property
    def on_ground(self) -> bool:
        return self._on_ground

    @property
    def on_wall(self) -> bool:
        return self._on_wall

    @property
    def wall_dir(self) -> int:
        return self._wall_dir

    @property
    def vx(self) -> float:
        return self._vx

    @property
    def vy(self) -> float:
        return self._vy

    @property
    def facing(self) -> int:
        return self._facing

    @property
    def crouching(self) -> bool:
        return self._crouching

    @property
    def jump_power(self) -> float:
        return self._jump_power

    def to_dict(self) -> Dict[str, Any]:
        """Convert cache to dictionary (for compatibility)."""
        return {
            'on_ground': self._on_ground,
            'on_wall': self._on_wall,
            'wall_dir': self._wall_dir,
            'vx': self._vx,
            'vy': self._vy,
            'facing': self._facing,
            'crouching': self._crouching,
            'jump_power': self._jump_power,
        }


class AbilityUpdateOptimizer:
    """
    Optimizer for ability updates.

    Features:
    - Lazy evaluation (only update abilities that need it)
    - Performance profiling
    - Batched updates
    """

    def __init__(self):
        """Initialize optimizer."""
        self._stats = PerformanceStats()
        self._enabled = True
        self._profiling_enabled = False

    def should_update_ability(self, ability, player_state: Dict) -> bool:
        """
        Determine if an ability needs updating.

        Abilities can skip updates if:
        - They're not enabled
        - They have no active state (no timers, buffers, etc.)
        - They're not affected by current player state

        Args:
            ability: The ability to check
            player_state: Current player state

        Returns:
            True if ability should update, False to skip
        """
        if not ability.enabled:
            return False

        # Always update if ability is active
        if hasattr(ability, 'is_active') and callable(ability.is_active):
            if ability.is_active():
                return True

        # Update if ability has active timers
        if hasattr(ability, 'cooldown_timer') and ability.cooldown_timer > 0:
            return True

        if hasattr(ability, 'jump_buffer_timer') and ability.jump_buffer_timer > 0:
            return True

        if hasattr(ability, 'dash_buffer_timer') and ability.dash_buffer_timer > 0:
            return True

        if hasattr(ability, 'slide_buffer_timer') and ability.slide_buffer_timer > 0:
            return True

        if hasattr(ability, 'air_dodge_buffer_timer') and ability.air_dodge_buffer_timer > 0:
            return True

        if hasattr(ability, 'shadow_step_buffer_timer') and ability.shadow_step_buffer_timer > 0:
            return True

        # Update if ability has regenerating resources
        if hasattr(ability, 'resource') and hasattr(ability, 'max_resource'):
            if ability.resource < ability.max_resource:
                return True

        # Update if on ground and ability cares (e.g., reset states)
        on_ground = player_state.get('on_ground', False)
        if on_ground and hasattr(ability, 'uses_left'):
            # Air abilities may need to reset uses on ground
            return True

        # Default: skip update for inactive abilities with no timers
        return False

    def update_ability_optimized(
        self,
        ability,
        dt: float,
        player_state: Dict,
        force: bool = False
    ) -> Dict:
        """
        Update an ability with optimization checks.

        Args:
            ability: The ability to update
            dt: Delta time
            player_state: Current player state
            force: Force update even if optimization says skip

        Returns:
            Update result from ability
        """
        # Check if we should skip this update
        if not force and self._enabled and not self.should_update_ability(ability, player_state):
            return {}

        # Profile if enabled
        if self._profiling_enabled:
            start_time = time.perf_counter()
            result = ability.update(dt, player_state)
            elapsed = time.perf_counter() - start_time

            # Update stats
            self._stats.total_updates += 1
            self._stats.total_time += elapsed

            ability_name = ability.name if hasattr(ability, 'name') else str(type(ability).__name__)
            self._stats.ability_update_times[ability_name] = \
                self._stats.ability_update_times.get(ability_name, 0.0) + elapsed
            self._stats.ability_update_counts[ability_name] = \
                self._stats.ability_update_counts.get(ability_name, 0) + 1

            return result
        else:
            return ability.update(dt, player_state)

    def enable_profiling(self, enabled: bool = True) -> None:
        """Enable or disable performance profiling."""
        self._profiling_enabled = enabled

    def enable_optimization(self, enabled: bool = True) -> None:
        """Enable or disable lazy update optimization."""
        self._enabled = enabled

    def get_stats(self) -> PerformanceStats:
        """Get performance statistics."""
        return self._stats

    def reset_stats(self) -> None:
        """Reset performance statistics."""
        self._stats = PerformanceStats()

    def get_performance_report(self) -> str:
        """Generate a human-readable performance report."""
        lines = ["=== Ability System Performance Report ==="]
        lines.append(f"Total Updates: {self._stats.total_updates}")
        lines.append(f"Total Time: {self._stats.total_time * 1000:.2f}ms")
        lines.append(f"Average Time: {self._stats.get_average_time() * 1000:.3f}ms")
        lines.append("")
        lines.append("Per-Ability Stats:")

        # Sort by total time
        sorted_abilities = sorted(
            self._stats.ability_update_times.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for ability_name, total_time in sorted_abilities:
            count = self._stats.ability_update_counts.get(ability_name, 0)
            avg_time = total_time / count if count > 0 else 0.0
            pct = 100.0 * total_time / max(0.001, self._stats.total_time)
            lines.append(
                f"  {ability_name:20s}: {count:6d} updates, "
                f"{total_time * 1000:8.2f}ms total, "
                f"{avg_time * 1000:6.3f}ms avg, "
                f"{pct:5.1f}%"
            )

        if self._stats.cache_hits > 0 or self._stats.cache_misses > 0:
            lines.append("")
            lines.append(f"Cache Hit Rate: {self._stats.get_cache_hit_rate():.1f}%")
            lines.append(f"  Hits: {self._stats.cache_hits}")
            lines.append(f"  Misses: {self._stats.cache_misses}")

        return "\n".join(lines)


# Global optimizer instance
_global_optimizer: Optional[AbilityUpdateOptimizer] = None


def get_ability_optimizer() -> AbilityUpdateOptimizer:
    """Get or create the global ability optimizer."""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = AbilityUpdateOptimizer()
    return _global_optimizer


def profile_ability_update(func: Callable) -> Callable:
    """
    Decorator to profile ability update methods.

    Usage:
        @profile_ability_update
        def update(self, dt, player_state):
            ...
    """
    @wraps(func)
    def wrapper(self, dt, player_state):
        optimizer = get_ability_optimizer()
        if optimizer._profiling_enabled:
            start_time = time.perf_counter()
            result = func(self, dt, player_state)
            elapsed = time.perf_counter() - start_time

            ability_name = self.name if hasattr(self, 'name') else str(type(self).__name__)
            optimizer._stats.ability_update_times[ability_name] = \
                optimizer._stats.ability_update_times.get(ability_name, 0.0) + elapsed
            optimizer._stats.ability_update_counts[ability_name] = \
                optimizer._stats.ability_update_counts.get(ability_name, 0) + 1
            optimizer._stats.total_updates += 1
            optimizer._stats.total_time += elapsed

            return result
        else:
            return func(self, dt, player_state)

    return wrapper
