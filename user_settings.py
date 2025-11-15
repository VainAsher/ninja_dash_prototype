"""User Settings Module - Player-configurable game settings."""
from __future__ import annotations

import json
from typing import Dict, Any

from save_paths import get_save_path


SETTINGS_FILE = "settings_overrides.json"


# Default overrides (empty means use settings.py defaults)
DEFAULT_OVERRIDES = {
    # Display
    "vsync": True,
    "debug_mode": False,

    # Gameplay feel (these override settings.py values)
    "user_max_run_speed": None,  # None = use default
    "user_gravity": None,
    "user_jump_power": None,

    # Level generation
    "branchiness_override": None,  # 0.0-1.0, None = use difficulty default
    "subroom_intensity": 0.5,      # 0.0-1.0, how many ability-gated side rooms

    # Advanced
    "enable_ability_challenges": True,  # Add optional coin patterns
    "enable_ability_subrooms": True,    # Add ability-gated side areas
}


class UserSettings:
    """Manages user-configurable settings."""

    def __init__(self) -> None:
        self._path = get_save_path(SETTINGS_FILE)
        self.overrides: Dict[str, Any] = DEFAULT_OVERRIDES.copy()
        self.load()

    def load(self) -> None:
        """Load settings from JSON file."""
        if not self._path.exists():
            self.overrides = DEFAULT_OVERRIDES.copy()
            return

        try:
            with self._path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge with defaults (in case new settings added)
                if isinstance(loaded, dict):
                    self.overrides = DEFAULT_OVERRIDES.copy()
                    self.overrides.update(loaded)
                else:
                    self.overrides = DEFAULT_OVERRIDES.copy()
        except (json.JSONDecodeError, OSError):
            self.overrides = DEFAULT_OVERRIDES.copy()

    def save(self) -> None:
        """Save settings to JSON file."""
        try:
            with self._path.open("w", encoding="utf-8") as f:
                json.dump(self.overrides, f, indent=2)
        except OSError:
            pass

    # --- dict-like API used in main.py / UI ------------------------------

    def get(self, key: str, default=None):
        """Get a setting value (dict-like)."""
        return self.overrides.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save (dict-like)."""
        self.overrides[key] = value
        self.save()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.overrides = DEFAULT_OVERRIDES.copy()
        self.save()

    # --- Helpers consumed by main.py -------------------------------------

    def get_gameplay_overrides(self) -> Dict[str, Any]:
        """Get gameplay parameter overrides for physics."""
        result: Dict[str, Any] = {}

        if self.overrides.get("user_max_run_speed") is not None:
            result["MAX_RUN_SPEED"] = self.overrides["user_max_run_speed"]

        if self.overrides.get("user_gravity") is not None:
            result["GRAVITY"] = self.overrides["user_gravity"]

        if self.overrides.get("user_jump_power") is not None:
            result["JUMP_POWER"] = self.overrides["user_jump_power"]

        return result

    def get_generation_overrides(self) -> Dict[str, Any]:
        """Get level generation parameter overrides."""
        result: Dict[str, Any] = {}

        # Branchiness directly maps into DIFFICULTY_CONFIG
        if self.overrides.get("branchiness_override") is not None:
            result["branchiness"] = self.overrides["branchiness_override"]

        # Extra knobs used by level_gen package
        result["subroom_intensity"] = self.overrides.get("subroom_intensity", 0.5)
        result["enable_ability_challenges"] = self.overrides.get(
            "enable_ability_challenges", True
        )
        result["enable_ability_subrooms"] = self.overrides.get(
            "enable_ability_subrooms", True
        )

        return result


# Global instance
_user_settings: UserSettings | None = None


def get_user_settings() -> UserSettings:
    """Get the global user settings instance."""
    global _user_settings
    if _user_settings is None:
        _user_settings = UserSettings()
    return _user_settings
