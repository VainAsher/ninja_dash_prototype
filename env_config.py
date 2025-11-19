"""
Environment Configuration Loader

Detects the current environment and loads appropriate configuration.
Environment can be set via:
1. NINJA_DASH_ENV environment variable
2. --env command line argument
3. Bundled marker file (for PyInstaller builds)
4. Defaults to TEST in development
"""

import os
import sys
from typing import Optional


def get_environment() -> str:
    """
    Determine which environment we're running in.

    Priority order:
    1. Command line argument --env=<ENV>
    2. Environment variable NINJA_DASH_ENV
    3. Bundled marker file (for frozen builds)
    4. Default to TEST

    Returns:
        One of: "test", "staging", "prod"
    """
    # Check command line arguments
    for arg in sys.argv[1:]:
        if arg.startswith('--env='):
            env = arg.split('=', 1)[1].lower()
            if env in ['test', 'staging', 'prod']:
                return env

    # Check environment variable
    env_var = os.environ.get('NINJA_DASH_ENV', '').lower()
    if env_var in ['test', 'staging', 'prod']:
        return env_var

    # Check for bundled marker file (created during PyInstaller build)
    if getattr(sys, 'frozen', False):
        # We're running in a PyInstaller bundle
        bundle_dir = os.path.dirname(sys.executable)

        # Check for environment marker files
        marker_files = {
            'test': os.path.join(bundle_dir, '.env_test'),
            'staging': os.path.join(bundle_dir, '.env_staging'),
            'prod': os.path.join(bundle_dir, '.env_prod'),
        }

        for env, marker_path in marker_files.items():
            if os.path.exists(marker_path):
                return env

    # Default to test for development
    return 'test'


def load_env_config():
    """
    Load the appropriate environment configuration.

    Returns a module with all environment-specific settings.
    """
    env = get_environment()

    # Import the appropriate config module
    if env == 'test':
        from configs import config_test as config
    elif env == 'staging':
        from configs import config_staging as config
    elif env == 'prod':
        from configs import config_prod as config
    else:
        # Fallback to test
        from configs import config_test as config

    return config


# Load configuration on module import
env_config = load_env_config()

# Export commonly used settings
ENV_NAME = env_config.ENV_NAME
ENV_DISPLAY_NAME = env_config.ENV_DISPLAY_NAME

# Debug settings
DEBUG_DEFAULT = env_config.DEBUG_DEFAULT
DEBUG_SHOW_GRID = env_config.DEBUG_SHOW_GRID
DEBUG_SHOW_BBOX = env_config.DEBUG_SHOW_BBOX
DEBUG_SHOW_FPS = getattr(env_config, 'DEBUG_SHOW_FPS', False)
DEBUG_SHOW_COORDS = getattr(env_config, 'DEBUG_SHOW_COORDS', False)

# Logging
LOG_LEVEL = env_config.LOG_LEVEL
CONSOLE_VISIBLE = env_config.CONSOLE_VISIBLE
ENABLE_VERBOSE_LOGGING = env_config.ENABLE_VERBOSE_LOGGING

# Performance
VSYNC = env_config.VSYNC

# Feature flags
ENABLE_ALL_FEATURES = env_config.ENABLE_ALL_FEATURES
ENABLE_EXPERIMENTAL_FEATURES = getattr(env_config, 'ENABLE_EXPERIMENTAL_FEATURES', False)

# Testing helpers
ENABLE_QUICK_RESTART = getattr(env_config, 'ENABLE_QUICK_RESTART', False)
ENABLE_LEVEL_SKIP = getattr(env_config, 'ENABLE_LEVEL_SKIP', False)
ENABLE_GOD_MODE_TOGGLE = getattr(env_config, 'ENABLE_GOD_MODE_TOGGLE', False)
ENABLE_NOCLIP_TOGGLE = getattr(env_config, 'ENABLE_NOCLIP_TOGGLE', False)

# Asset settings
TEXTURE_QUALITY = getattr(env_config, 'TEXTURE_QUALITY', 'high')

# Seed override
DEFAULT_SEED_OVERRIDE = getattr(env_config, 'DEFAULT_SEED', None)

# Window settings
WINDOW_TITLE_SUFFIX = env_config.WINDOW_TITLE_SUFFIX

# Error handling
CRASH_ON_ERROR = env_config.CRASH_ON_ERROR
SHOW_ERROR_DIALOGS = getattr(env_config, 'SHOW_ERROR_DIALOGS', False)


def print_env_info():
    """Print environment information (useful for debugging)"""
    print(f"=" * 60)
    print(f"NINJA DASH - {ENV_DISPLAY_NAME} Environment")
    print(f"=" * 60)
    print(f"Environment: {ENV_NAME}")
    print(f"Debug Mode: {DEBUG_DEFAULT}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"VSync: {VSYNC}")
    print(f"Console: {'Visible' if CONSOLE_VISIBLE else 'Hidden'}")
    if DEFAULT_SEED_OVERRIDE is not None:
        print(f"Fixed Seed: {DEFAULT_SEED_OVERRIDE}")
    print(f"=" * 60)


# Print environment info if console is visible
if CONSOLE_VISIBLE and __name__ != "__main__":
    print_env_info()
