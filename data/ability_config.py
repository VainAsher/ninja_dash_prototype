"""
Ability Configuration Loader

Loads ability parameters from JSON configuration files,
allowing game balance tuning without code changes.
"""

import json
import os
from typing import Any, Dict


class AbilityConfig:
    """
    Singleton loader for ability configuration.

    Loads ability parameters from data/abilities.json and provides
    convenient access to ability settings throughout the game.
    """

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Load configuration on first initialization."""
        if self._config is None:
            self._load_config()

    def _load_config(self):
        """Load configuration from JSON file."""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'abilities.json'
        )

        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            print(f"Warning: abilities.json not found at {config_path}")
            print("Using default hardcoded values from settings.py")
            self._config = {}
        except json.JSONDecodeError as e:
            print(f"Error parsing abilities.json: {e}")
            print("Using default hardcoded values from settings.py")
            self._config = {}

    def get(self, category: str, ability: str, param: str, default: Any = None) -> Any:
        """
        Get an ability parameter value.

        Args:
            category: Ability category (movement, advanced, combat)
            ability: Ability name (double_jump, dash, etc.)
            param: Parameter name (speed, duration, etc.)
            default: Default value if not found in config

        Returns:
            Parameter value or default

        Example:
            >>> config = AbilityConfig()
            >>> speed = config.get('advanced', 'shadow_step', 'speed', 12.0)
        """
        try:
            return self._config[category][ability][param]
        except (KeyError, TypeError):
            return default

    def get_ability(self, category: str, ability: str) -> Dict[str, Any]:
        """
        Get all parameters for a specific ability.

        Args:
            category: Ability category (movement, advanced, combat)
            ability: Ability name (double_jump, dash, etc.)

        Returns:
            Dictionary of all parameters for the ability

        Example:
            >>> config = AbilityConfig()
            >>> dash_params = config.get_ability('movement', 'dash')
        """
        try:
            return self._config[category][ability].copy()
        except (KeyError, TypeError):
            return {}

    def reload(self):
        """Reload configuration from file (useful for development/testing)."""
        self._config = None
        self._load_config()


# Global singleton instance
_ability_config = AbilityConfig()


def get_ability_config() -> AbilityConfig:
    """
    Get the global AbilityConfig instance.

    Returns:
        AbilityConfig: The singleton configuration loader
    """
    return _ability_config
