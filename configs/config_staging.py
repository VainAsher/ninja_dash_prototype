"""
Staging Environment Configuration
- Debug mode disabled
- Moderate logging
- Production-like settings
- QA testing focus
"""

# Environment identifier
ENV_NAME = "STAGING"
ENV_DISPLAY_NAME = "Staging"

# Debug settings (minimal, but accessible)
DEBUG_DEFAULT = False
DEBUG_SHOW_GRID = False
DEBUG_SHOW_BBOX = False
DEBUG_SHOW_FPS = True  # Keep FPS visible for performance testing
DEBUG_SHOW_COORDS = False

# Logging
LOG_LEVEL = "INFO"
CONSOLE_VISIBLE = True  # Keep console for QA logs
ENABLE_VERBOSE_LOGGING = False

# Performance
VSYNC = 1  # Enabled like production
FPS_UNLIMITED = False

# Feature flags
ENABLE_ALL_FEATURES = False  # Use standard feature flags
ENABLE_EXPERIMENTAL_FEATURES = True  # Test experimental features

# Testing helpers (limited set for QA)
ENABLE_QUICK_RESTART = True  # Press F5 to quick restart
ENABLE_LEVEL_SKIP = True     # Press F6 to skip level
ENABLE_GOD_MODE_TOGGLE = False
ENABLE_NOCLIP_TOGGLE = False

# Asset settings
TEXTURE_QUALITY = "high"  # Full quality for visual QA

# Seed
DEFAULT_SEED = None  # Random like production

# Window settings
WINDOW_TITLE_SUFFIX = " [STAGING]"

# Error handling
CRASH_ON_ERROR = False  # Capture errors for QA reporting
SHOW_ERROR_DIALOGS = True
