"""
Level Generation Package

This package provides procedural level generation with ability-aware features.
Main entry point is the generate_level() function.
"""

from .generator import (
    generate_level,
    Room,
    generate_macro_maze,
    find_room_path,
    build_world_from_path,
    find_spawn,
    mark_phaseable_walls,
)

from .entity_placer import (
    generate_hazards,
    generate_coins_and_pickups,
    generate_powerups,
    generate_ability_orbs,
)

from .decorations import (
    decorate_world,
    build_solid_rects,
)

from .ability_features import (
    add_ability_challenges,
    add_ability_subrooms,
)

from .config import (
    LevelGenConfig,
    EASY_CONFIG,
    MEDIUM_CONFIG,
    HARD_CONFIG,
)

from .constants import (
    DEFAULT_VERTICALITY_BIAS,
    DEFAULT_BRANCHINESS,
    DEFAULT_PLATFORM_BAND_STEP,
    DEFAULT_PLATFORM_LEN_RANGE,
    DEFAULT_PILLAR_CHANCE,
    DEFAULT_HOLE_CHANCE,
    DEFAULT_HAZARD_RATE,
    DEFAULT_COIN_DENSITY,
    DEFAULT_HEALTH_DENSITY,
    DEFAULT_LIVES_PER_LEVEL,
    DEFAULT_POWERUP_DENSITY,
    DEFAULT_ABILITY_ORB_SPAWN_RATE,
    DEFAULT_PHASEABLE_WALL_CHANCE,
    DEFAULT_ENABLE_ABILITY_SUBROOMS,
    DEFAULT_SUBROOM_INTENSITY,
    DEFAULT_ENABLE_ABILITY_CHALLENGES,
    CHALLENGE_ATTEMPTS,
    SUBROOM_EMPTY_THRESHOLD,
)

# Main public API
__all__ = [
    'generate_level',
    'Room',
    'generate_macro_maze',
    'find_room_path',
    'build_world_from_path',
    'decorate_world',
    'generate_hazards',
    'generate_coins_and_pickups',
    'generate_powerups',
    'add_ability_challenges',
    'add_ability_subrooms',
    'build_solid_rects',
    'find_spawn',
    'mark_phaseable_walls',
    'generate_ability_orbs',
    # Configuration
    'LevelGenConfig',
    'EASY_CONFIG',
    'MEDIUM_CONFIG',
    'HARD_CONFIG',
    # Constants
    'DEFAULT_VERTICALITY_BIAS',
    'DEFAULT_BRANCHINESS',
    'DEFAULT_PLATFORM_BAND_STEP',
    'DEFAULT_PLATFORM_LEN_RANGE',
    'DEFAULT_PILLAR_CHANCE',
    'DEFAULT_HOLE_CHANCE',
    'DEFAULT_HAZARD_RATE',
    'DEFAULT_COIN_DENSITY',
    'DEFAULT_HEALTH_DENSITY',
    'DEFAULT_LIVES_PER_LEVEL',
    'DEFAULT_POWERUP_DENSITY',
    'DEFAULT_ABILITY_ORB_SPAWN_RATE',
    'DEFAULT_PHASEABLE_WALL_CHANCE',
    'DEFAULT_ENABLE_ABILITY_SUBROOMS',
    'DEFAULT_SUBROOM_INTENSITY',
    'DEFAULT_ENABLE_ABILITY_CHALLENGES',
    'CHALLENGE_ATTEMPTS',
    'SUBROOM_EMPTY_THRESHOLD',
]

__version__ = '1.0.0'
