"""
Settings Module - Enhanced configuration for Ninja Dash
All game constants, toggles, and configuration parameters including power-ups.
"""

import pygame

# Import environment configuration
try:
    import env_config
    _env_loaded = True
except ImportError:
    _env_loaded = False

# ================= SCREEN / RENDERING =================
LOGICAL_W, LOGICAL_H = 1280, 720
FPS = 60

WINDOW_FLAGS = pygame.RESIZABLE
VSYNC = env_config.VSYNC if _env_loaded else 1

# ================= WORLD GRID =================
TILE_SIZE = 32

ROOM_COLS = 6
ROOM_ROWS = 4

ROOM_W = 16
ROOM_H = 12

WORLD_W = ROOM_COLS * ROOM_W
WORLD_H = ROOM_ROWS * ROOM_H

WORLD_PX_W = WORLD_W * TILE_SIZE
WORLD_PX_H = WORLD_H * TILE_SIZE

# ================= GAME / META TOGGLES =================
FEATURES = {
    "double_jump": False,  # Unlockable
    "wall_jump": False,    # Unlockable
    "dash": False,         # Unlockable
    "crouch": True,
    "fast_fall": True,
}

DEBUG_DEFAULT = env_config.DEBUG_DEFAULT if _env_loaded else False
DEBUG_SHOW_GRID = env_config.DEBUG_SHOW_GRID if _env_loaded else True
DEBUG_SHOW_BBOX = env_config.DEBUG_SHOW_BBOX if _env_loaded else False

DEFAULT_SEED = env_config.DEFAULT_SEED_OVERRIDE if _env_loaded and env_config.DEFAULT_SEED_OVERRIDE is not None else None

# Difficulty and scoring (extended knobs)
DIFFICULTY = "medium"
DIFFICULTY_CONFIG = {
    "easy": {
        "coin_ratio": 0.40, "multiplier": 1.0,
        "coin_density": 0.05,  # Deprecated - use coin_count_range
        "coin_count_range": (10, 15),  # Easy: 10-15 coins
        "hazard_rate": 0.015,
        "verticality_bias": 0.3, "branchiness": 0.15,
        "platform_band_step": 4, "platform_len_range": (3, 7),
        "pillar_chance": 0.20, "hole_chance": 0.15,
        "health_density": 0.010,
        "lives_per_level": 2,
        "powerup_density": 0.004,
        "phaseable_wall_chance": 0.25,
        "enemy_density": 0.0083,  # Reduced to 1/6th (was 5%)
        "enemy_min_separation": 20,
    },
    "medium": {
        "coin_ratio": 0.60, "multiplier": 1.5,
        "coin_density": 0.045,  # Deprecated - use coin_count_range
        "coin_count_range": (14, 21),  # Medium: 14-21 coins
        "hazard_rate": 0.03,
        "verticality_bias": 0.5, "branchiness": 0.25,
        "platform_band_step": 4, "platform_len_range": (4, 8),
        "pillar_chance": 0.30, "hole_chance": 0.22,
        "health_density": 0.004,
        "lives_per_level": 1,
        "powerup_density": 0.003,
        "phaseable_wall_chance": 0.20,
        "enemy_density": 0.0167,  # Reduced to 1/6th (was 10%)
        "enemy_min_separation": 20,
    },
    "hard": {
        "coin_ratio": 0.75, "multiplier": 2.0,
        "coin_density": 0.04,  # Deprecated - use coin_count_range
        "coin_count_range": (19, 28),  # Hard: 19-28 coins
        "hazard_rate": 0.045,
        "verticality_bias": 0.65, "branchiness": 0.35,
        "platform_band_step": 3, "platform_len_range": (4, 10),
        "pillar_chance": 0.40, "hole_chance": 0.30,
        "health_density": 0.003,
        "lives_per_level": 1,
        "powerup_density": 0.0025,
        "phaseable_wall_chance": 0.15,
        "enemy_density": 0.025,  # Reduced to 1/6th (was 15%)
        "enemy_min_separation": 20,
    },
    "expert": {
        "coin_ratio": 0.85, "multiplier": 3.0,
        "coin_density": 0.035,  # Deprecated - use coin_count_range
        "coin_count_range": (35, 48),  # Expert: 35-48 coins
        "hazard_rate": 0.065,
        "verticality_bias": 0.8, "branchiness": 0.45,
        "platform_band_step": 3, "platform_len_range": (5, 12),
        "pillar_chance": 0.50, "hole_chance": 0.38,
        "health_density": 0.001,
        "lives_per_level": 1,
        "powerup_density": 0.004,
        "phaseable_wall_chance": 0.12,
        "enemy_density": 0.0333,  # Reduced to 1/6th (was 20%)
        "enemy_min_separation": 20,
    },
}

BASE_TIME_SCORE = 100000.0
COIN_SCORE_VALUE = 100

# Lives & health
PLAYER_MAX_HEALTH = 3
PLAYER_LIVES = 3
INVINCIBILITY_TIME = 1.2

HEALTH_VALUE = 1
LIFE_VALUE = 1

# ================= PLAYER MOVEMENT =================
MAX_RUN_SPEED = 8.0
RUN_ACCEL_GROUND = 0.9
RUN_DECEL_GROUND = 1.1
RUN_ACCEL_AIR = 0.5
RUN_DECEL_AIR = 0.6

GRAVITY = 0.7

# Jump system - differentiated jump mechanics
JUMP_POWER = 14.5  # Base power for first jump (balanced)
JUMP_POWER_SECOND = 10.0  # Reduced vertical power for second jump (more horizontal)
JUMP_HORIZONTAL_BOOST_SECOND = 1.4  # Multiplier for horizontal velocity on second jump

MAX_JUMPS = 2
COYOTE_TIME = 0.12
JUMP_BUFFER_TIME = 0.14
FALL_GRAVITY_MULT = 1.25
JUMP_CUT_MULT = 2.0

WALL_SLIDE_SPEED = 2.2
WALL_JUMP_POWER_X = 8.5
WALL_JUMP_POWER_Y = 14.5
WALL_JUMP_INPUT_LOCK = 0.12

# Dash - now stamina-based run speed modifier
DASH_STAMINA_MAX = 3.0  # Maximum stamina (seconds of dashing)
DASH_STAMINA_DRAIN = 1.0  # Stamina drain per second while active
DASH_STAMINA_REGEN = 0.8  # Stamina regen per second when inactive
DASH_SPEED_MULT = 1.8  # Speed multiplier when dashing (1.8x normal speed)

FAST_FALL_MULT = 2.4
MAX_FALL_SPEED = 22.0

CROUCH_SPEED_MULT = 0.75  # 25% slower movement when crouched
CROUCH_JUMP_MULT = 1.2

# ================= SHADOW STEP (SMOKE BOMB) ABILITY =================
# Reworked as defensive evasion tool rather than offensive dash
SHADOW_STEP_CHARGES = 3  # Charges per level
SHADOW_STEP_DURATION = 0.85  # Smoke duration (slightly longer for positioning)
SHADOW_STEP_INVULN_TIME = 0.85  # Full invulnerability during smoke (defensive focus)
SHADOW_STEP_SPEED = 12.0  # Reduced speed (evasion/escape, not aggressive dash)
SHADOW_STEP_COOLDOWN = 0.6  # Cooldown between uses
SHADOW_STEP_PHASE_DOORS_ONLY = True  # Only phase through phaseable walls (doors), not floors

# ================= NEW MOVEMENT ABILITIES =================
# Slide
SLIDE_SPEED_MULT = 1.3  # Speed multiplier while sliding
SLIDE_DURATION = 0.8  # Maximum slide duration
SLIDE_MIN_SPEED = 3.0  # Minimum speed to maintain slide
SLIDE_COOLDOWN = 0.3  # Cooldown after slide ends

# Wall Cling
WALL_CLING_SLIDE_SPEED = 1.0  # Slow slide down wall
WALL_CLING_STAMINA = 5.0  # Maximum cling time (seconds)
WALL_CLING_STAMINA_REGEN = 0.5  # Regen rate when not clinging

# Air Dodge - with hang time for directional input
AIR_DODGE_SPEED = 14.0  # Dodge speed
AIR_DODGE_DURATION = 0.25  # Dodge duration
AIR_DODGE_HANG_TIME = 0.15  # Hang time for directional input (brief pause)
AIR_DODGE_HANG_GRAVITY_MULT = 0.1  # Reduced gravity during hang time
AIR_DODGE_INVULN_TIME = 0.3  # Invincibility frames
AIR_DODGE_COOLDOWN = 1.0  # Cooldown between dodges
AIR_DODGE_MAX_USES = 2  # Maximum uses per ground touch

# Glide - descent control with enhanced horizontal movement
GLIDE_FALL_SPEED = 2.0  # Reduced fall speed while gliding
GLIDE_HORIZONTAL_MULT = 1.3  # ENHANCED horizontal movement (was 0.8, now 1.3x)
GLIDE_MAX_DURATION = 10.0  # Maximum glide time (optional limit)
GLIDE_HORIZONTAL_ACCEL = 1.5  # Faster air control while gliding

# ================= POWER-UPS =================
POWERUP_TYPES = [
    ("speed", 35),      # (type, weight)
    ("triple", 20),     # Duration-based extra jump
    ("extra_jump", 30), # Use/damage-based extra jump
    ("magnet", 35),
]

# Power-up durations (seconds)
POWERUP_SPEED_DURATION = 8.0
POWERUP_SPEED_FACTOR = 1.6

POWERUP_TRIPLE_DURATION = 10.0
POWERUP_TRIPLE_EXTRA_JUMPS = 1

# Extra Jump powerup (use-based or damage-based)
POWERUP_EXTRA_JUMP_USES = 5          # Number of extra jumps granted
POWERUP_EXTRA_JUMP_DAMAGE_LIMIT = 2  # Expires after this much damage taken

POWERUP_MAGNET_DURATION = 12.0
POWERUP_MAGNET_RADIUS = 150.0

# ================= COLORS / FONT =================
COLOR_BG = (10, 10, 20)
COLOR_TILE = (200, 200, 200)
COLOR_PLAYER = (255, 80, 80)
COLOR_EXIT = (80, 255, 120)
COLOR_EXIT_LOCKED = (220, 80, 80)
COLOR_TEXT = (230, 230, 255)
COLOR_COIN = (255, 215, 0)
COLOR_HAZARD = (255, 90, 0)
COLOR_HEALTH = (120, 200, 255)
COLOR_LIFE = (255, 120, 255)
COLOR_HUD_BG = (0, 0, 0)
COLOR_BTN_BG = (40, 40, 60)
COLOR_BTN_BG_HOVER = (70, 70, 100)

# Shadow Step colors
COLOR_PHASEABLE_WALL = (140, 100, 200)  # Purple for phaseable walls
COLOR_SHADOW_STEP = (180, 100, 255)  # Player color during shadow step

# Power-up colors
COLOR_POWERUP_SPEED = (255, 200, 50)
COLOR_POWERUP_TRIPLE = (100, 255, 200)
COLOR_POWERUP_EXTRA_JUMP = (150, 255, 150)  # Light green for extra jump
COLOR_POWERUP_MAGNET = (255, 215, 0)

HUD_HEIGHT = 100

pygame.font.init()
FONT = pygame.font.SysFont("consolas", 24)
FONT_BIG = pygame.font.SysFont("consolas", 42)
FONT_SMALL = pygame.font.SysFont("consolas", 16)
