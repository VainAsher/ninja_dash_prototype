"""
Level Generation Constants and Default Configuration Values

This module contains all constants and default configuration parameters
used in procedural level generation.
"""

# Maze Generation Defaults
DEFAULT_VERTICALITY_BIAS = 0.5
"""Float: Vertical vs horizontal preference in maze generation (0.0-1.0)"""

DEFAULT_BRANCHINESS = 0.25
"""Float: Probability of creating additional connections in maze (0.0-1.0)"""

# World Decoration Defaults
DEFAULT_PLATFORM_BAND_STEP = 4
"""Int: Vertical spacing between platform bands in rooms"""

DEFAULT_PLATFORM_LEN_RANGE = (3, 7)
"""Tuple[int, int]: Min and max platform lengths"""

DEFAULT_PILLAR_CHANCE = 0.3
"""Float: Probability of generating a pillar (0.0-1.0)"""

DEFAULT_HOLE_CHANCE = 0.2
"""Float: Probability of creating a hole in floor (0.0-1.0)"""

# Hazard Generation Defaults
DEFAULT_HAZARD_RATE = 0.03
"""Float: Density of hazard spawns (0.0-1.0)"""

# Pickup Generation Defaults
DEFAULT_COIN_DENSITY = 0.04
"""Float: Density of coin spawns (0.0-1.0)"""

DEFAULT_HEALTH_DENSITY = 0.006
"""Float: Density of health pickup spawns (0.0-1.0)"""

DEFAULT_LIVES_PER_LEVEL = 1
"""Int: Number of extra life pickups per level"""

# Power-up Generation Defaults
DEFAULT_POWERUP_DENSITY = 0.005
"""Float: Density of power-up spawns (0.0-1.0)"""

# Ability System Defaults
DEFAULT_ABILITY_ORB_SPAWN_RATE = 0.003
"""Float: Spawn rate for ability orbs (0.3% default)"""

DEFAULT_PHASEABLE_WALL_CHANCE = 0.35
"""Float: Probability of marking a wall as phaseable (0.0-1.0)"""

DEFAULT_ENABLE_ABILITY_SUBROOMS = True
"""Bool: Whether to generate ability-gated challenge subrooms"""

DEFAULT_SUBROOM_INTENSITY = 0.5
"""Float: Intensity of ability subroom generation (0.0-1.0)"""

DEFAULT_ENABLE_ABILITY_CHALLENGES = True
"""Bool: Whether to add ability-aware coin challenges"""

# Challenge Generation
CHALLENGE_ATTEMPTS = 50
"""Int: Maximum attempts to find suitable challenge locations"""

SUBROOM_EMPTY_THRESHOLD = 0.6
"""Float: Minimum empty space fraction required for subroom placement"""
