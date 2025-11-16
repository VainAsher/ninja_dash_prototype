"""
Ability System Constants

Configuration values for ability-gated features including phaseable walls,
ability orbs, and challenge rooms.
"""

# Ability Orb Spawning
DEFAULT_ABILITY_ORB_SPAWN_RATE = 0.003
"""Float: Spawn rate for ability orbs (0.0-1.0)

Probability per valid location of spawning an ability orb.
These are VERY rare pickups that unlock new abilities.

Examples:
    - 0.001: Extremely rare (0.1% spawn rate)
    - 0.003: Very rare (0.3% spawn rate, default)
    - 0.01: Uncommon (1% spawn rate)

Design Note:
    Kept intentionally low to make ability unlocks feel special.
    Players should work through several levels to find one.
"""

# Shadow Step Ability
DEFAULT_PHASEABLE_WALL_CHANCE = 0.35
"""Float: Probability of marking a wall as phaseable (0.0-1.0)

When Shadow Step ability is enabled, this determines what fraction of
eligible walls become phaseable (can be passed through).

Only applies to vertical interior walls (not boundaries).

Examples:
    - 0.15: Few phaseable walls (hard difficulty)
    - 0.35: Moderate phaseable walls (default)
    - 0.70: Many phaseable walls (easy traversal)

Design Note:
    Too high makes Shadow Step trivialize level navigation.
    Too low makes the ability feel useless.
"""

# Ability-Gated Challenge Rooms
DEFAULT_ENABLE_ABILITY_SUBROOMS = True
"""Bool: Whether to generate ability-gated challenge subrooms

When enabled, creates special rooms that require specific abilities to access.
These rooms contain bonus coins and rewards.

Features:
    - Double Jump required rooms (high platforms)
    - Wall Jump required rooms (vertical shafts)
    - Dash required rooms (wide gaps)

Design Note:
    Provides optional challenges that reward ability mastery.
    Doesn't block critical path (always optional).
"""

DEFAULT_SUBROOM_INTENSITY = 0.5
"""Float: Intensity of ability subroom generation (0.0-1.0)

Controls how many subrooms are generated when ability subrooms are enabled.
Higher values create more optional challenges.

Examples:
    - 0.2: Rare subrooms (few optional challenges)
    - 0.5: Moderate subrooms (balanced, default)
    - 0.8: Frequent subrooms (many optional areas)

Technical Note:
    Used as probability multiplier in subroom generation logic.
"""

DEFAULT_ENABLE_ABILITY_CHALLENGES = True
"""Bool: Whether to add ability-aware coin challenges

When enabled, places coins in positions that require specific abilities:
    - High coins requiring Double Jump
    - Coins in narrow gaps requiring precise Dash
    - Coins on walls requiring Wall Jump

Design Note:
    Creates skill-testing coin placements without blocking progress.
    All coins are optional (not required for level completion).
"""

# Challenge Generation Limits
CHALLENGE_ATTEMPTS = 50
"""Int: Maximum attempts to find suitable challenge locations

When placing ability challenges or subrooms, tries this many times
to find a valid location before giving up.

Higher values increase challenge density but may slow generation.

Technical Note:
    Prevents infinite loops when world is too constrained for challenges.
"""

SUBROOM_EMPTY_THRESHOLD = 0.6
"""Float: Minimum empty space fraction required for subroom placement (0.0-1.0)

When carving out a subroom, requires this fraction of the area to be
initially empty (not solid).

Examples:
    - 0.4: Allow subrooms in denser areas
    - 0.6: Require mostly empty space (default)
    - 0.8: Only place in very open areas

Design Note:
    Too low creates cramped, unfair subrooms.
    Too high limits subroom placement options.
"""
