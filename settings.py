"""
Settings Module - Enhanced configuration for Ninja Dash
All game constants, toggles, and configuration parameters including power-ups.
"""

import pygame

# ================= SCREEN / RENDERING =================
LOGICAL_W, LOGICAL_H = 1280, 720
FPS = 60

WINDOW_FLAGS = pygame.RESIZABLE
VSYNC = 1

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

DEBUG_DEFAULT = False
DEBUG_SHOW_GRID = True
DEBUG_SHOW_BBOX = False

DEFAULT_SEED = None

# Difficulty and scoring (extended knobs)
DIFFICULTY = "medium"
DIFFICULTY_CONFIG = {
    "easy": {
        "coin_ratio": 0.40, "multiplier": 1.0,
        "coin_density": 0.05, "hazard_rate": 0.015,
        "verticality_bias": 0.3, "branchiness": 0.15,
        "platform_band_step": 4, "platform_len_range": (3, 7),
        "pillar_chance": 0.20, "hole_chance": 0.15,
        "health_density": 0.010,
        "lives_per_level": 2,
        "powerup_density": 0.004,
        "phaseable_wall_chance": 0.25,
    },
    "medium": {
        "coin_ratio": 0.60, "multiplier": 1.5,
        "coin_density": 0.045, "hazard_rate": 0.03,
        "verticality_bias": 0.5, "branchiness": 0.25,
        "platform_band_step": 4, "platform_len_range": (4, 8),
        "pillar_chance": 0.30, "hole_chance": 0.22,
        "health_density": 0.004,
        "lives_per_level": 1,
        "powerup_density": 0.003,
        "phaseable_wall_chance": 0.20,
    },
    "hard": {
        "coin_ratio": 0.75, "multiplier": 2.0,
        "coin_density": 0.04, "hazard_rate": 0.045,
        "verticality_bias": 0.65, "branchiness": 0.35,
        "platform_band_step": 3, "platform_len_range": (4, 10),
        "pillar_chance": 0.40, "hole_chance": 0.30,
        "health_density": 0.003,
        "lives_per_level": 1,
        "powerup_density": 0.0025,
        "phaseable_wall_chance": 0.15,
    },
    "expert": {
        "coin_ratio": 0.85, "multiplier": 3.0,
        "coin_density": 0.035, "hazard_rate": 0.065,
        "verticality_bias": 0.8, "branchiness": 0.45,
        "platform_band_step": 3, "platform_len_range": (5, 12),
        "pillar_chance": 0.50, "hole_chance": 0.38,
        "health_density": 0.001,
        "lives_per_level": 1,
        "powerup_density": 0.004,
        "phaseable_wall_chance": 0.12,
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
JUMP_POWER = 14.5
MAX_JUMPS = 2
COYOTE_TIME = 0.12
JUMP_BUFFER_TIME = 0.14
FALL_GRAVITY_MULT = 1.25
JUMP_CUT_MULT = 2.0

WALL_SLIDE_SPEED = 2.2
WALL_JUMP_POWER_X = 8.5
WALL_JUMP_POWER_Y = 14.5
WALL_JUMP_INPUT_LOCK = 0.12

DASH_SPEED = 16.0
DASH_DURATION = 0.16
DASH_COOLDOWN = 0.45

FAST_FALL_MULT = 2.4
MAX_FALL_SPEED = 22.0

CROUCH_SPEED_MULT = 0.95
CROUCH_JUMP_MULT = 1.2

# ================= SHADOW STEP ABILITY =================
SHADOW_STEP_CHARGES = 3  # Charges per level
SHADOW_STEP_DURATION = 0.75  # Phase duration
SHADOW_STEP_INVULN_TIME = 0.4  # Invulnerability window
SHADOW_STEP_SPEED = 18.0  # Dash speed
SHADOW_STEP_COOLDOWN = 0.5  # Cooldown between uses

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

# Air Dodge
AIR_DODGE_SPEED = 14.0  # Dodge speed
AIR_DODGE_DURATION = 0.25  # Dodge duration
AIR_DODGE_INVULN_TIME = 0.3  # Invincibility frames
AIR_DODGE_COOLDOWN = 1.0  # Cooldown between dodges
AIR_DODGE_MAX_USES = 2  # Maximum uses per ground touch

# Glide
GLIDE_FALL_SPEED = 2.0  # Fall speed while gliding
GLIDE_HORIZONTAL_MULT = 0.8  # Horizontal speed multiplier
GLIDE_MAX_DURATION = 10.0  # Maximum glide time (optional limit)

# ================= POWER-UPS =================
POWERUP_TYPES = [
    ("speed", 35),      # (type, weight)
    ("triple", 30),
    ("magnet", 35),
]

# Power-up durations (seconds)
POWERUP_SPEED_DURATION = 8.0
POWERUP_SPEED_FACTOR = 1.6

POWERUP_TRIPLE_DURATION = 10.0
POWERUP_TRIPLE_EXTRA_JUMPS = 1

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
COLOR_POWERUP_MAGNET = (255, 215, 0)

HUD_HEIGHT = 48

pygame.font.init()
FONT = pygame.font.SysFont("consolas", 20)
FONT_BIG = pygame.font.SysFont("consolas", 36)
FONT_SMALL = pygame.font.SysFont("consolas", 14)
