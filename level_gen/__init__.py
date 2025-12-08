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
    EXPERT_CONFIG,
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
    'EXPERT_CONFIG',
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

# =========================================================
# ZONE-BASED GENERATION (NEW SYSTEM)
# =========================================================
# Import zone-based generation components for granular room customization
try:
    from .zone_generator import (
        RoomNode,
        assign_zone_roles_for_room,
        ROOM_START, ROOM_EXIT, ROOM_SHOP, ROOM_COMBAT,
        ROOM_PLATFORM, ROOM_TREASURE, ROOM_BOSS, ROOM_SAFE,
        Z_WALK, Z_FILL, Z_PLAT, Z_DECOR, Z_SAVE, Z_SHOP, Z_LOOT, Z_SECRET,
        print_zone_roles,
    )
    from .zone_integration import (
        generate_room_from_zones,
        log_generation_start,
        log_room_generation,
        log_generation_complete,
        log_feature_placement,
    )
    from .tileset import TileSet, draw_tiles, validate_tiles

    # Add to public API
    __all__.extend([
        # Zone system core
        'RoomNode',
        'assign_zone_roles_for_room',
        'generate_room_from_zones',
        'print_zone_roles',
        # Room types
        'ROOM_START', 'ROOM_EXIT', 'ROOM_SHOP', 'ROOM_COMBAT',
        'ROOM_PLATFORM', 'ROOM_TREASURE', 'ROOM_BOSS', 'ROOM_SAFE',
        # Zone roles
        'Z_WALK', 'Z_FILL', 'Z_PLAT', 'Z_DECOR',
        'Z_SAVE', 'Z_SHOP', 'Z_LOOT', 'Z_SECRET',
        # Tileset rendering
        'TileSet', 'draw_tiles', 'validate_tiles',
        # Logging utilities
        'log_generation_start', 'log_room_generation',
        'log_generation_complete', 'log_feature_placement',
    ])
except ImportError as e:
    # Zone system is optional - game will work without it
    print(f"[Level Gen] Zone system not available: {e}")
    print("[Level Gen] Using standard generation only")
