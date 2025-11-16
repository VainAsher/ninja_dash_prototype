"""
Ability Animation Events System

Defines animation trigger points and event hooks for abilities.
Prepares for future animation system integration and provides hooks
for particle effects, sound effects, and screen shake.
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    """Types of animation events."""
    ABILITY_START = "ability_start"
    ABILITY_PEAK = "ability_peak"
    ABILITY_END = "ability_end"
    IMPACT = "impact"
    CHARGE_START = "charge_start"
    CHARGE_RELEASE = "charge_release"
    PARTICLE_BURST = "particle_burst"
    SOUND_EFFECT = "sound_effect"
    SCREEN_SHAKE = "screen_shake"
    VISUAL_EFFECT = "visual_effect"


@dataclass
class AnimationEvent:
    """
    An animation event that can be triggered.

    Attributes:
        event_type: Type of event
        ability_name: Name of ability that triggered it
        timestamp: When the event occurred (relative to ability start)
        data: Additional event data (particles, sound ID, shake intensity, etc.)
    """
    event_type: EventType
    ability_name: str
    timestamp: float = 0.0
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class AnimationEventManager:
    """
    Manages animation events for abilities.

    This system allows abilities to emit events that can be consumed by:
    - Animation systems (for sprite changes, frame timing)
    - Particle systems (for visual effects)
    - Audio systems (for sound effects)
    - Camera systems (for screen shake)
    """

    def __init__(self):
        """Initialize the event manager."""
        self.event_queue: List[AnimationEvent] = []
        self.event_listeners: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }

        # Define ability animation profiles
        self.ability_profiles = self._create_ability_profiles()

    def _create_ability_profiles(self) -> Dict[str, List[AnimationEvent]]:
        """
        Create animation event profiles for each ability.

        Returns:
            Dictionary mapping ability names to their event sequences
        """
        profiles = {}

        # Double Jump
        profiles["DOUBLE_JUMP"] = [
            AnimationEvent(EventType.ABILITY_START, "DOUBLE_JUMP", 0.0, {
                'particle_type': 'jump_burst',
                'particle_count': 10,
                'sound': 'jump_sfx'
            }),
            AnimationEvent(EventType.PARTICLE_BURST, "DOUBLE_JUMP", 0.05, {
                'particle_type': 'air_trail',
                'duration': 0.3
            }),
        ]

        # Dash
        profiles["DASH"] = [
            AnimationEvent(EventType.ABILITY_START, "DASH", 0.0, {
                'particle_type': 'dash_start',
                'sound': 'dash_whoosh',
                'visual_effect': 'speed_lines'
            }),
            AnimationEvent(EventType.VISUAL_EFFECT, "DASH", 0.0, {
                'effect_type': 'motion_blur',
                'intensity': 0.7
            }),
            AnimationEvent(EventType.PARTICLE_BURST, "DASH", 0.1, {
                'particle_type': 'dash_trail',
                'continuous': True
            }),
        ]

        # Wall Jump
        profiles["WALL_JUMP"] = [
            AnimationEvent(EventType.ABILITY_START, "WALL_JUMP", 0.0, {
                'particle_type': 'wall_impact',
                'particle_count': 15,
                'sound': 'wall_kick'
            }),
            AnimationEvent(EventType.IMPACT, "WALL_JUMP", 0.05, {
                'screen_shake': 0.3,
                'particle_type': 'wall_debris'
            }),
        ]

        # Slide
        profiles["SLIDE"] = [
            AnimationEvent(EventType.ABILITY_START, "SLIDE", 0.0, {
                'particle_type': 'slide_dust',
                'sound': 'slide_start'
            }),
            AnimationEvent(EventType.PARTICLE_BURST, "SLIDE", 0.0, {
                'particle_type': 'ground_trail',
                'continuous': True,
                'duration': 0.8
            }),
        ]

        # Shadow Step
        profiles["SHADOW_STEP"] = [
            AnimationEvent(EventType.ABILITY_START, "SHADOW_STEP", 0.0, {
                'particle_type': 'smoke_burst',
                'particle_count': 30,
                'sound': 'smoke_poof',
                'visual_effect': 'fade_out'
            }),
            AnimationEvent(EventType.VISUAL_EFFECT, "SHADOW_STEP", 0.0, {
                'effect_type': 'ghost_trail',
                'duration': 0.85,
                'color': (180, 100, 255)
            }),
            AnimationEvent(EventType.ABILITY_END, "SHADOW_STEP", 0.85, {
                'particle_type': 'smoke_dissipate',
                'visual_effect': 'fade_in'
            }),
        ]

        # Wall Cling
        profiles["WALL_CLING"] = [
            AnimationEvent(EventType.ABILITY_START, "WALL_CLING", 0.0, {
                'particle_type': 'wall_grip',
                'sound': 'cling_attach'
            }),
            AnimationEvent(EventType.PARTICLE_BURST, "WALL_CLING", 0.2, {
                'particle_type': 'wall_slide_sparks',
                'continuous': True
            }),
        ]

        # Air Dodge
        profiles["AIR_DODGE"] = [
            AnimationEvent(EventType.ABILITY_START, "AIR_DODGE", 0.0, {
                'particle_type': 'dodge_burst',
                'particle_count': 20,
                'sound': 'air_dodge_whoosh'
            }),
            AnimationEvent(EventType.VISUAL_EFFECT, "AIR_DODGE", 0.0, {
                'effect_type': 'afterimage',
                'count': 3,
                'duration': 0.25
            }),
            AnimationEvent(EventType.ABILITY_PEAK, "AIR_DODGE", 0.125, {
                'particle_type': 'air_ripple',
                'visual_effect': 'invuln_flash'
            }),
        ]

        # Glide
        profiles["GLIDE"] = [
            AnimationEvent(EventType.ABILITY_START, "GLIDE", 0.0, {
                'particle_type': 'glide_start',
                'sound': 'glide_open'
            }),
            AnimationEvent(EventType.PARTICLE_BURST, "GLIDE", 0.0, {
                'particle_type': 'air_stream',
                'continuous': True
            }),
        ]

        # Sword Attack
        profiles["SWORD_ATTACK"] = [
            AnimationEvent(EventType.CHARGE_START, "SWORD_ATTACK", 0.0, {
                'visual_effect': 'sword_glow'
            }),
            AnimationEvent(EventType.ABILITY_START, "SWORD_ATTACK", 0.05, {
                'sound': 'sword_swing',
                'visual_effect': 'slash_arc'
            }),
            AnimationEvent(EventType.IMPACT, "SWORD_ATTACK", 0.1, {
                'particle_type': 'slash_effect',
                'screen_shake': 0.2
            }),
        ]

        # Grapple Hook
        profiles["GRAPPLE_HOOK"] = [
            AnimationEvent(EventType.ABILITY_START, "GRAPPLE_HOOK", 0.0, {
                'particle_type': 'grapple_launch',
                'sound': 'grapple_shoot',
                'visual_effect': 'rope_extend'
            }),
            AnimationEvent(EventType.IMPACT, "GRAPPLE_HOOK", 0.3, {
                'sound': 'grapple_attach',
                'particle_type': 'grapple_impact',
                'screen_shake': 0.15
            }),
            AnimationEvent(EventType.VISUAL_EFFECT, "GRAPPLE_HOOK", 0.3, {
                'effect_type': 'rope_pull',
                'continuous': True
            }),
        ]

        return profiles

    def emit_ability_event(self, ability_name: str, event_type: EventType,
                          custom_data: Optional[Dict[str, Any]] = None):
        """
        Emit an animation event for an ability.

        Args:
            ability_name: Name of the ability
            event_type: Type of event to emit
            custom_data: Optional custom data to override defaults
        """
        # Get default event data from profile
        profile_events = self.ability_profiles.get(ability_name, [])
        matching_event = next(
            (e for e in profile_events if e.event_type == event_type),
            None
        )

        # Create event
        event_data = {}
        if matching_event:
            event_data.update(matching_event.data)
        if custom_data:
            event_data.update(custom_data)

        event = AnimationEvent(
            event_type=event_type,
            ability_name=ability_name,
            data=event_data
        )

        self.event_queue.append(event)
        self._dispatch_event(event)

    def _dispatch_event(self, event: AnimationEvent):
        """
        Dispatch an event to all registered listeners.

        Args:
            event: The event to dispatch
        """
        listeners = self.event_listeners.get(event.event_type, [])
        for listener in listeners:
            listener(event)

    def register_listener(self, event_type: EventType, callback: Callable[[AnimationEvent], None]):
        """
        Register a listener for a specific event type.

        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs

        Example:
            >>> def on_particle_burst(event):
            ...     print(f"Particle burst: {event.data['particle_type']}")
            >>> manager.register_listener(EventType.PARTICLE_BURST, on_particle_burst)
        """
        self.event_listeners[event_type].append(callback)

    def unregister_listener(self, event_type: EventType, callback: Callable):
        """
        Unregister a listener.

        Args:
            event_type: Type of event
            callback: Callback function to remove
        """
        if callback in self.event_listeners[event_type]:
            self.event_listeners[event_type].remove(callback)

    def get_events(self) -> List[AnimationEvent]:
        """
        Get all queued events and clear the queue.

        Returns:
            List of animation events
        """
        events = self.event_queue.copy()
        self.event_queue.clear()
        return events

    def clear_events(self):
        """Clear all queued events."""
        self.event_queue.clear()

    def get_ability_profile(self, ability_name: str) -> List[AnimationEvent]:
        """
        Get the animation profile for an ability.

        Args:
            ability_name: Name of ability

        Returns:
            List of animation events for the ability
        """
        return self.ability_profiles.get(ability_name, [])


# Global event manager instance
_animation_event_manager = None


def get_animation_event_manager() -> AnimationEventManager:
    """
    Get the global animation event manager instance.

    Returns:
        AnimationEventManager singleton
    """
    global _animation_event_manager
    if _animation_event_manager is None:
        _animation_event_manager = AnimationEventManager()
    return _animation_event_manager


# Helper functions for common event emissions
def emit_ability_start(ability_name: str, custom_data: Optional[Dict[str, Any]] = None):
    """Emit an ability start event."""
    manager = get_animation_event_manager()
    manager.emit_ability_event(ability_name, EventType.ABILITY_START, custom_data)


def emit_ability_end(ability_name: str, custom_data: Optional[Dict[str, Any]] = None):
    """Emit an ability end event."""
    manager = get_animation_event_manager()
    manager.emit_ability_event(ability_name, EventType.ABILITY_END, custom_data)


def emit_impact(ability_name: str, custom_data: Optional[Dict[str, Any]] = None):
    """Emit an impact event."""
    manager = get_animation_event_manager()
    manager.emit_ability_event(ability_name, EventType.IMPACT, custom_data)


def emit_particle_burst(ability_name: str, custom_data: Optional[Dict[str, Any]] = None):
    """Emit a particle burst event."""
    manager = get_animation_event_manager()
    manager.emit_ability_event(ability_name, EventType.PARTICLE_BURST, custom_data)
