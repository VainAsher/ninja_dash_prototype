"""
Entity Spawn Constants

Configuration values for hazards, pickups, collectibles, and their placement rules.
"""

# Hazard Spawning
DEFAULT_HAZARD_RATE = 0.03
"""Float: Density of hazard spawns (0.0-1.0)

Probability per valid platform tile of spawning a spike hazard.
Higher values create more dangerous levels.

Examples:
    - 0.01: Sparse hazards (easy difficulty)
    - 0.03: Moderate hazards (default)
    - 0.06: Dense hazards (hard difficulty)
"""

HAZARD_SAFE_RADIUS = 3
"""Int: Minimum distance from hazards for safe pickup placement (in tiles)

Pickups won't spawn within this radius of hazards to prevent unfair situations.
Larger values make pickups safer but may limit placement options.

Technical Note:
    Uses Manhattan distance (|dx| + |dy|) for efficiency
"""

# Enemy Spawning
DEFAULT_ENEMY_DENSITY = 0.0167
"""Float: Density of enemy spawns (0.0-1.0)

Probability per valid location of spawning an enemy.
Lower values create less cluttered, more strategic encounters.

Examples:
    - 0.0083: Very sparse enemies (easy difficulty)
    - 0.0167: Sparse enemies (default/medium difficulty)
    - 0.025: Moderate enemies (hard difficulty)
    - 0.0333: Dense enemies (expert difficulty)
"""

ENEMY_MIN_SEPARATION = 20
"""Int: Minimum distance between enemy spawns (in tiles)

Prevents enemies from clustering too close together, ensuring
balanced difficulty and giving players breathing room.

Range: 16-32 tiles recommended
"""

# Pickup Spawning
DEFAULT_COIN_DENSITY = 0.02
"""Float: Density of coin spawns (0.0-1.0) - DEPRECATED

Probability per valid location of spawning a coin.
Higher values create more collectibles and higher scores.

NOTE: This is deprecated in favor of DEFAULT_COIN_COUNT_RANGE for count-based spawning.

Examples:
    - 0.02: Sparse coins (challenging collection)
    - 0.04: Moderate coins (default)
    - 0.08: Dense coins (easy collection)
"""

DEFAULT_COIN_COUNT_RANGE = (10, 20)
"""Tuple[int, int]: Range of coins to spawn per level (min, max)

The actual coin count is randomly selected within this range.
This provides more predictable coin counts compared to probability-based spawning.

Examples:
    - (10, 15): Easy difficulty (lower collection requirement)
    - (14, 21): Medium difficulty (moderate collection requirement)
    - (19, 28): Hard difficulty (higher collection requirement)
    - (35, 48): Expert difficulty (very high collection requirement)
"""

DEFAULT_HEALTH_DENSITY = 0.006
"""Float: Density of health pickup spawns (0.0-1.0)

Probability per valid location of spawning a health pickup.
Lower than coin density since health is more valuable.

Examples:
    - 0.003: Rare health (hard difficulty)
    - 0.006: Occasional health (default)
    - 0.012: Frequent health (easy difficulty)
"""

DEFAULT_LIVES_PER_LEVEL = 1
"""Int: Number of extra life pickups per level

Exact count of extra lives to spawn, not a probability.
Uses random placement with MAX_SPAWN_ATTEMPTS retries.

Examples:
    - 0: No extra lives (hardcore mode)
    - 1: One extra life (default)
    - 3: Multiple extra lives (forgiving mode)
"""

# Power-up Spawning
DEFAULT_POWERUP_DENSITY = 0.005
"""Float: Density of power-up spawns (0.0-1.0)

Probability per valid location of spawning a power-up.
Power-ups are rarer than regular pickups.

Types distributed by weight in POWERUP_TYPES settings.

Examples:
    - 0.002: Very rare power-ups
    - 0.005: Occasional power-ups (default)
    - 0.01: Frequent power-ups
"""

# Entity Placement Limits
MAX_SPAWN_ATTEMPTS = 10000
"""Int: Maximum attempts to spawn entities before giving up

Prevents infinite loops when trying to place entities with strict requirements.
Higher values increase success rate but may slow generation.

Used for:
    - Extra life placement
    - Any entity with specific location requirements
"""
