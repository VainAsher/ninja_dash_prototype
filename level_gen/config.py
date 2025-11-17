"""
Level Generation Configuration Dataclass

Provides type-safe configuration for level generation with validation and defaults.
Replaces the dictionary-based diff_cfg parameter throughout the codebase.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any

from .constants import (
    DEFAULT_VERTICALITY_BIAS,
    DEFAULT_BRANCHINESS,
    DEFAULT_PLATFORM_BAND_STEP,
    DEFAULT_PLATFORM_LEN_RANGE,
    DEFAULT_PILLAR_CHANCE,
    DEFAULT_HOLE_CHANCE,
    DEFAULT_HAZARD_RATE,
    DEFAULT_COIN_DENSITY,
    DEFAULT_COIN_COUNT_RANGE,
    DEFAULT_HEALTH_DENSITY,
    DEFAULT_LIVES_PER_LEVEL,
    DEFAULT_POWERUP_DENSITY,
    DEFAULT_ABILITY_ORB_SPAWN_RATE,
    DEFAULT_PHASEABLE_WALL_CHANCE,
    DEFAULT_ENABLE_ABILITY_SUBROOMS,
    DEFAULT_SUBROOM_INTENSITY,
    DEFAULT_ENABLE_ABILITY_CHALLENGES,
    DEFAULT_ENEMY_DENSITY,
    ENEMY_MIN_SEPARATION,
)


@dataclass
class LevelGenConfig:
    """
    Configuration for procedural level generation.

    This dataclass provides type-safe configuration with auto-completion support
    and validation for all level generation parameters.

    Attributes:
        # Maze Generation
        verticality_bias: Preference for vertical vs horizontal maze generation (0.0-1.0)
        branchiness: Probability of creating additional maze connections (0.0-1.0)

        # World Decoration
        platform_band_step: Vertical spacing between platform bands in tiles
        platform_len_range: Min and max platform lengths as (min, max) tuple
        pillar_chance: Probability of generating pillars in a room (0.0-1.0)
        hole_chance: Probability of creating holes in floors (0.0-1.0)

        # Hazards & Enemies
        hazard_rate: Density of spike hazard spawns (0.0-1.0)
        enemy_density: Density of enemy spawns (0.0-1.0)
        enemy_min_separation: Minimum distance between enemies (in tiles)

        # Pickups & Collectibles
        coin_density: (Deprecated) Density of coin spawns (0.0-1.0)
        coin_count_range: Range of coins to spawn per level (min, max)
        health_density: Density of health pickup spawns (0.0-1.0)
        lives_per_level: Number of extra life pickups to spawn
        powerup_density: Density of power-up spawns (0.0-1.0)

        # Ability System
        ability_orb_spawn_rate: Spawn rate for ability orbs (0.0-1.0)
        phaseable_wall_chance: Probability of marking walls as phaseable (0.0-1.0)
        enable_ability_subrooms: Whether to generate ability-gated challenge subrooms
        subroom_intensity: Intensity of ability subroom generation (0.0-1.0)
        enable_ability_challenges: Whether to add ability-aware coin challenges

        # Scoring & Difficulty (optional gameplay parameters)
        coin_ratio: Coin collection ratio requirement for progression (0.0-1.0)
        multiplier: Score multiplier for this difficulty level

    Example:
        >>> # Create easy difficulty config
        >>> easy_config = LevelGenConfig(
        ...     verticality_bias=0.3,
        ...     branchiness=0.15,
        ...     hazard_rate=0.015,
        ...     coin_density=0.05
        ... )

        >>> # Create hard difficulty with custom settings
        >>> hard_config = LevelGenConfig(
        ...     verticality_bias=0.7,
        ...     branchiness=0.4,
        ...     hazard_rate=0.06,
        ...     platform_len_range=(2, 5),
        ...     hole_chance=0.4
        ... )

        >>> # Use in level generation
        >>> from level_gen import generate_level
        >>> world, *rest = generate_level(seed=42, config=easy_config)
    """

    # Maze Generation
    verticality_bias: float = DEFAULT_VERTICALITY_BIAS
    branchiness: float = DEFAULT_BRANCHINESS

    # World Decoration
    platform_band_step: int = DEFAULT_PLATFORM_BAND_STEP
    platform_len_range: Tuple[int, int] = DEFAULT_PLATFORM_LEN_RANGE
    pillar_chance: float = DEFAULT_PILLAR_CHANCE
    hole_chance: float = DEFAULT_HOLE_CHANCE

    # Hazards & Enemies
    hazard_rate: float = DEFAULT_HAZARD_RATE
    enemy_density: float = DEFAULT_ENEMY_DENSITY  # Default ~1.67% enemy spawn rate
    enemy_min_separation: int = ENEMY_MIN_SEPARATION  # Minimum 20 tiles between enemies

    # Pickups & Collectibles
    coin_density: float = DEFAULT_COIN_DENSITY  # Deprecated - use coin_count_range instead
    coin_count_range: Tuple[int, int] = DEFAULT_COIN_COUNT_RANGE  # Target coin count range
    health_density: float = DEFAULT_HEALTH_DENSITY
    lives_per_level: int = DEFAULT_LIVES_PER_LEVEL
    powerup_density: float = DEFAULT_POWERUP_DENSITY

    # Ability System
    ability_orb_spawn_rate: float = DEFAULT_ABILITY_ORB_SPAWN_RATE
    phaseable_wall_chance: float = DEFAULT_PHASEABLE_WALL_CHANCE
    enable_ability_subrooms: bool = DEFAULT_ENABLE_ABILITY_SUBROOMS
    subroom_intensity: float = DEFAULT_SUBROOM_INTENSITY
    enable_ability_challenges: bool = DEFAULT_ENABLE_ABILITY_CHALLENGES

    # Optional: Scoring & Difficulty (not used in generation, but kept for compatibility)
    coin_ratio: float = 0.5
    multiplier: float = 1.0

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'LevelGenConfig':
        """
        Create a LevelGenConfig from a dictionary (for backward compatibility).

        This method allows seamless migration from the old dict-based config system.
        Unknown keys are silently ignored.

        Args:
            config_dict: Dictionary containing configuration parameters

        Returns:
            LevelGenConfig instance with values from the dictionary

        Example:
            >>> old_config = {
            ...     'verticality_bias': 0.5,
            ...     'hazard_rate': 0.03,
            ...     'unknown_key': 'ignored'
            ... }
            >>> config = LevelGenConfig.from_dict(old_config)
            >>> config.verticality_bias
            0.5
        """
        # Get all field names for this dataclass
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}

        # Filter to only valid fields
        filtered = {k: v for k, v in config_dict.items() if k in valid_fields}

        return cls(**filtered)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this config to a dictionary (for backward compatibility).

        Returns:
            Dictionary representation of this configuration

        Example:
            >>> config = LevelGenConfig(verticality_bias=0.7)
            >>> config_dict = config.to_dict()
            >>> config_dict['verticality_bias']
            0.7
        """
        return {
            'verticality_bias': self.verticality_bias,
            'branchiness': self.branchiness,
            'platform_band_step': self.platform_band_step,
            'platform_len_range': self.platform_len_range,
            'pillar_chance': self.pillar_chance,
            'hole_chance': self.hole_chance,
            'hazard_rate': self.hazard_rate,
            'enemy_density': self.enemy_density,
            'enemy_min_separation': self.enemy_min_separation,
            'coin_density': self.coin_density,
            'coin_count_range': self.coin_count_range,
            'health_density': self.health_density,
            'lives_per_level': self.lives_per_level,
            'powerup_density': self.powerup_density,
            'ability_orb_spawn_rate': self.ability_orb_spawn_rate,
            'phaseable_wall_chance': self.phaseable_wall_chance,
            'enable_ability_subrooms': self.enable_ability_subrooms,
            'subroom_intensity': self.subroom_intensity,
            'enable_ability_challenges': self.enable_ability_challenges,
            'coin_ratio': self.coin_ratio,
            'multiplier': self.multiplier,
        }

    def validate(self) -> None:
        """
        Validate configuration parameters are within acceptable ranges.

        Raises:
            ValueError: If any parameter is out of acceptable range

        Example:
            >>> config = LevelGenConfig(verticality_bias=1.5)  # Invalid
            >>> config.validate()
            Traceback (most recent call last):
                ...
            ValueError: verticality_bias must be between 0.0 and 1.0, got 1.5
        """
        # Validate probability ranges (0.0-1.0)
        prob_fields = [
            ('verticality_bias', self.verticality_bias),
            ('branchiness', self.branchiness),
            ('pillar_chance', self.pillar_chance),
            ('hole_chance', self.hole_chance),
            ('hazard_rate', self.hazard_rate),
            ('enemy_density', self.enemy_density),
            ('coin_density', self.coin_density),
            ('health_density', self.health_density),
            ('powerup_density', self.powerup_density),
            ('ability_orb_spawn_rate', self.ability_orb_spawn_rate),
            ('phaseable_wall_chance', self.phaseable_wall_chance),
            ('subroom_intensity', self.subroom_intensity),
            ('coin_ratio', self.coin_ratio),
        ]

        for name, value in prob_fields:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0, got {value}")

        # Validate positive integers
        if self.platform_band_step < 1:
            raise ValueError(f"platform_band_step must be >= 1, got {self.platform_band_step}")

        if self.lives_per_level < 0:
            raise ValueError(f"lives_per_level must be >= 0, got {self.lives_per_level}")

        # Validate platform length range
        min_len, max_len = self.platform_len_range
        if min_len < 1 or max_len < min_len:
            raise ValueError(f"platform_len_range must be (min, max) with min >= 1 and max >= min, got {self.platform_len_range}")

        # Validate multiplier
        if self.multiplier < 0:
            raise ValueError(f"multiplier must be >= 0, got {self.multiplier}")


# Preset difficulty configurations
EASY_CONFIG = LevelGenConfig(
    verticality_bias=0.3,
    branchiness=0.15,
    platform_band_step=4,
    platform_len_range=(3, 7),
    pillar_chance=0.20,
    hole_chance=0.15,
    hazard_rate=0.015,
    enemy_density=0.0083,  # Reduced to 1/6th of 0.05 (was 5%)
    enemy_min_separation=20,
    coin_density=0.05,  # Deprecated
    coin_count_range=(10, 15),  # Easy: 10-15 coins
    health_density=0.010,
    lives_per_level=2,
    powerup_density=0.004,
    phaseable_wall_chance=0.25,
    coin_ratio=0.40,
    multiplier=1.0,
)

MEDIUM_CONFIG = LevelGenConfig(
    verticality_bias=0.5,
    branchiness=0.25,
    platform_band_step=4,
    platform_len_range=(4, 8),
    pillar_chance=0.30,
    hole_chance=0.22,
    hazard_rate=0.03,
    enemy_density=0.0167,  # Reduced to 1/6th of 0.10 (was 10%)
    enemy_min_separation=20,
    coin_density=0.045,  # Deprecated
    coin_count_range=(14, 21),  # Medium: 14-21 coins
    health_density=0.004,
    lives_per_level=1,
    powerup_density=0.003,
    phaseable_wall_chance=0.20,
    coin_ratio=0.60,
    multiplier=1.5,
)

HARD_CONFIG = LevelGenConfig(
    verticality_bias=0.65,
    branchiness=0.35,
    platform_band_step=3,
    platform_len_range=(4, 10),
    pillar_chance=0.40,
    hole_chance=0.30,
    hazard_rate=0.045,
    enemy_density=0.025,  # Reduced to 1/6th of 0.15 (was 15%)
    enemy_min_separation=20,
    coin_density=0.04,  # Deprecated
    coin_count_range=(19, 28),  # Hard: 19-28 coins
    health_density=0.003,
    lives_per_level=1,
    powerup_density=0.002,
    phaseable_wall_chance=0.15,
    coin_ratio=0.75,
    multiplier=2.0,
)

EXPERT_CONFIG = LevelGenConfig(
    verticality_bias=0.8,
    branchiness=0.45,
    platform_band_step=3,
    platform_len_range=(5, 12),
    pillar_chance=0.50,
    hole_chance=0.38,
    hazard_rate=0.065,
    enemy_density=0.0333,  # Reduced to 1/6th of 0.20 (was 20%)
    enemy_min_separation=20,
    coin_density=0.035,  # Deprecated
    coin_count_range=(35, 48),  # Expert: 35-48 coins
    health_density=0.001,
    lives_per_level=1,
    powerup_density=0.004,
    phaseable_wall_chance=0.12,
    coin_ratio=0.85,
    multiplier=3.0,
)
