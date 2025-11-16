"""
Player State Management Module

Centralizes player state tracking and provides a clean interface
for querying and modifying player state.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class PlayerState:
    """
    Immutable snapshot of player state for ability evaluation.

    This is passed to abilities to help them decide if they can activate
    and what effects they should apply.
    """
    on_ground: bool
    on_wall: bool
    wall_dir: int
    vx: float
    vy: float
    facing: int
    crouching: bool
    jump_power: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for backward compatibility."""
        return {
            'on_ground': self.on_ground,
            'on_wall': self.on_wall,
            'wall_dir': self.wall_dir,
            'vx': self.vx,
            'vy': self.vy,
            'facing': self.facing,
            'crouching': self.crouching,
            'jump_power': self.jump_power,
        }


class PlayerStateManager:
    """
    Manages player state flags and provides helper methods for state queries.

    This class centralizes all the various state flags that track what
    the player is currently doing (dashing, gliding, attacking, etc.).
    """

    def __init__(self):
        """Initialize all state flags to default values."""
        # Movement state
        self.on_ground = False
        self.on_wall = False
        self.wall_dir = 0
        self.crouching = False
        self.facing = 1

        # Active ability states
        self.is_dashing = False
        self.is_smoke_stepping = False
        self.is_sliding = False
        self.is_air_dodging = False
        self.is_air_dodge_hanging = False
        self.is_gliding = False
        self.is_wall_clinging = False
        self.is_attacking = False
        self.is_blocking = False
        self.is_grappling = False

    def get_snapshot(self, vx: float, vy: float, jump_power: float) -> PlayerState:
        """
        Create an immutable snapshot of current player state.

        Args:
            vx: Current horizontal velocity
            vy: Current vertical velocity
            jump_power: Current jump power value

        Returns:
            PlayerState: Immutable state snapshot
        """
        return PlayerState(
            on_ground=self.on_ground,
            on_wall=self.on_wall,
            wall_dir=self.wall_dir,
            vx=vx,
            vy=vy,
            facing=self.facing,
            crouching=self.crouching,
            jump_power=jump_power,
        )

    def update_from_abilities(self, ability_states: Dict[str, Any]):
        """
        Update state flags based on ability states.

        Args:
            ability_states: Dictionary mapping ability names to their active states
        """
        self.is_dashing = ability_states.get('dash', False)
        self.is_smoke_stepping = ability_states.get('shadow_step', False)
        self.is_sliding = ability_states.get('slide', False)
        self.is_air_dodging = ability_states.get('air_dodge_dodging', False)
        self.is_air_dodge_hanging = ability_states.get('air_dodge_hanging', False)
        self.is_gliding = ability_states.get('glide', False)
        self.is_wall_clinging = ability_states.get('wall_cling', False)
        self.is_attacking = ability_states.get('sword_attacking', False)
        self.is_blocking = ability_states.get('sword_blocking', False)
        self.is_grappling = ability_states.get('grapple', False)

    def apply_modifications(self, modifications: Dict[str, Any]):
        """
        Apply state modifications from abilities.

        Args:
            modifications: Dictionary of state changes to apply
        """
        if not modifications:
            return

        if 'on_ground' in modifications:
            self.on_ground = modifications['on_ground']
        if 'on_wall' in modifications:
            self.on_wall = modifications['on_wall']
        if 'wall_dir' in modifications:
            self.wall_dir = modifications['wall_dir']
        if 'facing' in modifications:
            self.facing = modifications['facing']
        if 'crouching' in modifications:
            self.crouching = modifications['crouching']

        # Update active ability states
        if 'is_dashing' in modifications:
            self.is_dashing = modifications['is_dashing']
        if 'is_smoke_stepping' in modifications:
            self.is_smoke_stepping = modifications['is_smoke_stepping']
        if 'is_shadow_stepping' in modifications:  # Legacy support
            self.is_smoke_stepping = modifications['is_shadow_stepping']
        if 'is_sliding' in modifications:
            self.is_sliding = modifications['is_sliding']
        if 'is_air_dodging' in modifications:
            self.is_air_dodging = modifications['is_air_dodging']
        if 'is_air_dodge_hanging' in modifications:
            self.is_air_dodge_hanging = modifications['is_air_dodge_hanging']
        if 'is_gliding' in modifications:
            self.is_gliding = modifications['is_gliding']
        if 'is_wall_clinging' in modifications:
            self.is_wall_clinging = modifications['is_wall_clinging']
        if 'is_attacking' in modifications:
            self.is_attacking = modifications['is_attacking']
        if 'is_blocking' in modifications:
            self.is_blocking = modifications['is_blocking']
        if 'is_grappling' in modifications:
            self.is_grappling = modifications['is_grappling']

    def is_ability_controlling_movement(self) -> bool:
        """
        Check if any ability is currently controlling player movement.

        Returns:
            bool: True if an ability is controlling movement
        """
        return (self.is_smoke_stepping or
                self.is_air_dodging or
                self.is_sliding)

    def is_invulnerable_from_state(self) -> bool:
        """
        Check if player is invulnerable based on current state.

        Note: This only checks state-based invulnerability.
        Ability-specific invulnerability should be checked separately.

        Returns:
            bool: True if player is invulnerable from state
        """
        # Currently no state-based invulnerability
        # (abilities handle their own invulnerability)
        return False
