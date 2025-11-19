"""
Testing Environment Configuration
- Debug mode enabled
- Extended logging
- All debug overlays visible
- Fast iteration focus
"""

# Environment identifier
ENV_NAME = "TEST"
ENV_DISPLAY_NAME = "Testing"

# Debug settings
DEBUG_DEFAULT = True
DEBUG_SHOW_GRID = True
DEBUG_SHOW_BBOX = True
DEBUG_SHOW_FPS = True
DEBUG_SHOW_COORDS = True

# Logging
LOG_LEVEL = "DEBUG"
CONSOLE_VISIBLE = True
ENABLE_VERBOSE_LOGGING = True

# Performance
VSYNC = 0  # Disabled for faster iteration
FPS_UNLIMITED = False  # Still cap at 60 for consistency

# Feature flags (all enabled for testing)
ENABLE_ALL_FEATURES = True
ENABLE_EXPERIMENTAL_FEATURES = True

# Testing helpers
ENABLE_QUICK_RESTART = True  # Press F5 to quick restart
ENABLE_LEVEL_SKIP = True     # Press F6 to skip level
ENABLE_GOD_MODE_TOGGLE = True  # Press F7 for invincibility
ENABLE_NOCLIP_TOGGLE = True    # Press F8 for no-clip

# Asset settings
TEXTURE_QUALITY = "medium"  # Don't need high quality for testing

# Seed override for reproducible testing
DEFAULT_SEED = 12345  # Fixed seed for consistent testing

# Window settings
WINDOW_TITLE_SUFFIX = " [TEST]"

# Error handling
CRASH_ON_ERROR = False  # Show errors but keep running
SHOW_ERROR_DIALOGS = True
