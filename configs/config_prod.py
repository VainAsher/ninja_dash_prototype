"""
Production Environment Configuration
- Debug mode disabled
- Minimal logging
- Optimized performance
- Clean player experience
"""

# Environment identifier
ENV_NAME = "PRODUCTION"
ENV_DISPLAY_NAME = "Production"

# Debug settings (all disabled)
DEBUG_DEFAULT = False
DEBUG_SHOW_GRID = False
DEBUG_SHOW_BBOX = False
DEBUG_SHOW_FPS = False
DEBUG_SHOW_COORDS = False

# Logging
LOG_LEVEL = "WARNING"  # Only warnings and errors
CONSOLE_VISIBLE = False  # Hide console window
ENABLE_VERBOSE_LOGGING = False

# Performance
VSYNC = 1  # Smooth gameplay
FPS_UNLIMITED = False

# Feature flags
ENABLE_ALL_FEATURES = False  # Use standard progression
ENABLE_EXPERIMENTAL_FEATURES = False  # Stable features only

# Testing helpers (all disabled)
ENABLE_QUICK_RESTART = False
ENABLE_LEVEL_SKIP = False
ENABLE_GOD_MODE_TOGGLE = False
ENABLE_NOCLIP_TOGGLE = False

# Asset settings
TEXTURE_QUALITY = "high"  # Best visual quality

# Seed
DEFAULT_SEED = None  # Random generation

# Window settings
WINDOW_TITLE_SUFFIX = ""  # Clean title

# Error handling
CRASH_ON_ERROR = True  # Clean exit on critical errors
SHOW_ERROR_DIALOGS = False  # No technical dialogs for players
