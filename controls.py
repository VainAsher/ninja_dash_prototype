"""
Controls Module - Data-driven input configuration system
Loads keybindings from JSON, supports rebinding, gamepad support (future)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import pygame

from save_paths import get_save_path


CONTROLS_CONFIG_FILE = "data/controls.json"
USER_BINDINGS_FILE = "keybindings.json"


class ControlAction:
    """Represents a single control action with multiple possible key bindings."""

    def __init__(self, action_id: str, keys: List[str], display_name: str = None):
        self.action_id = action_id
        self.keys = keys  # List of key names (e.g., ["space", "w"])
        self.display_name = display_name or action_id.replace("_", " ").title()
        self.pygame_keys = self._convert_to_pygame_keys(keys)

    def _convert_to_pygame_keys(self, keys: List[str]) -> List[int]:
        """Convert key name strings to pygame key constants."""
        pygame_keys = []
        for key in keys:
            # Handle modifier prefixes like "hold:"
            if ":" in key:
                modifier, key_name = key.split(":", 1)
                # For now, just use the key part
                # TODO: Implement hold/double-tap modifiers
                key = key_name.split("|")[0]  # Take first option

            # Convert common key names to pygame constants
            pygame_key = self._get_pygame_key(key.lower())
            if pygame_key is not None:
                pygame_keys.append(pygame_key)

        return pygame_keys

    def _get_pygame_key(self, key_name: str) -> Optional[int]:
        """Convert string key name to pygame constant."""
        # Direct mapping for letter keys
        if len(key_name) == 1 and key_name.isalpha():
            return getattr(pygame, f"K_{key_name.lower()}")

        # Special keys mapping
        key_map = {
            "space": pygame.K_SPACE,
            "escape": pygame.K_ESCAPE,
            "esc": pygame.K_ESCAPE,
            "enter": pygame.K_RETURN,
            "return": pygame.K_RETURN,
            "tab": pygame.K_TAB,
            "backspace": pygame.K_BACKSPACE,
            "delete": pygame.K_DELETE,

            # Arrow keys
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,

            # Modifiers
            "lshift": pygame.K_LSHIFT,
            "rshift": pygame.K_RSHIFT,
            "lctrl": pygame.K_LCTRL,
            "rctrl": pygame.K_RCTRL,
            "lalt": pygame.K_LALT,
            "ralt": pygame.K_RALT,

            # Function keys
            **{f"f{i}": getattr(pygame, f"K_F{i}") for i in range(1, 13)},

            # Number keys
            **{str(i): getattr(pygame, f"K_{i}") for i in range(10)},
        }

        return key_map.get(key_name.lower())

    def is_pressed(self, keys_state) -> bool:
        """Check if any of the bound keys are currently pressed."""
        for pygame_key in self.pygame_keys:
            if keys_state[pygame_key]:
                return True
        return False

    def get_display_keys(self, display_names: Dict[str, str]) -> str:
        """Get formatted string of key bindings for display."""
        formatted_keys = []
        for key in self.keys:
            # Remove modifiers for display
            clean_key = key.split(":")[-1].split("|")[0]
            display_key = display_names.get(clean_key, clean_key.upper())
            formatted_keys.append(display_key)
        return " / ".join(formatted_keys)


class ControlsManager:
    """Manages all game controls and keybindings."""

    def __init__(self):
        self.actions: Dict[str, ControlAction] = {}
        self.categories: Dict[str, List[str]] = {}  # category -> [action_ids]
        self.display_names: Dict[str, str] = {}
        self.config_data: Dict[str, Any] = {}

        # Load default controls
        self.load_default_controls()

        # Try to load user overrides
        self.load_user_bindings()

    def load_default_controls(self) -> None:
        """Load default control configuration from JSON."""
        config_path = Path(CONTROLS_CONFIG_FILE)

        if not config_path.exists():
            print(f"Warning: Controls config not found at {config_path}")
            self._load_fallback_controls()
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)

            # Load display names
            self.display_names = self.config_data.get("display_names", {})

            # Load keyboard controls
            keyboard_config = self.config_data.get("keyboard", {})
            for category, actions in keyboard_config.items():
                self.categories[category] = []
                for action_id, keys in actions.items():
                    # Ensure keys is a list
                    if isinstance(keys, str):
                        keys = [keys]

                    full_action_id = f"{category}.{action_id}"
                    self.actions[full_action_id] = ControlAction(
                        full_action_id, keys
                    )
                    self.categories[category].append(full_action_id)

            print(f"Loaded {len(self.actions)} control actions from {config_path}")

        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading controls config: {e}")
            self._load_fallback_controls()

    def _load_fallback_controls(self) -> None:
        """Load minimal fallback controls if config file is missing."""
        print("Loading fallback controls...")

        # Essential movement
        self.actions["movement.move_left"] = ControlAction(
            "movement.move_left", ["a", "left"]
        )
        self.actions["movement.move_right"] = ControlAction(
            "movement.move_right", ["d", "right"]
        )
        self.actions["movement.jump"] = ControlAction(
            "movement.jump", ["space", "w", "up"]
        )
        self.actions["movement.crouch_down"] = ControlAction(
            "movement.crouch_down", ["s", "down"]
        )

        # Essential abilities
        self.actions["abilities.dash"] = ControlAction(
            "abilities.dash", ["lshift", "rshift"]
        )

        # Essential UI
        self.actions["ui.pause"] = ControlAction(
            "ui.pause", ["escape"]
        )

        self.categories["movement"] = [
            "movement.move_left", "movement.move_right",
            "movement.jump", "movement.crouch_down"
        ]
        self.categories["abilities"] = ["abilities.dash"]
        self.categories["ui"] = ["ui.pause"]

    def load_user_bindings(self) -> None:
        """Load user-customized keybindings if they exist."""
        user_path = get_save_path(USER_BINDINGS_FILE)

        if not user_path.exists():
            return

        try:
            with open(user_path, 'r', encoding='utf-8') as f:
                user_bindings = json.load(f)

            # Apply user overrides
            for action_id, keys in user_bindings.items():
                if action_id in self.actions:
                    self.actions[action_id].keys = keys
                    self.actions[action_id].pygame_keys = \
                        self.actions[action_id]._convert_to_pygame_keys(keys)

            print(f"Loaded user keybindings from {user_path}")

        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading user keybindings: {e}")

    def save_user_bindings(self) -> None:
        """Save current keybindings to user config."""
        user_path = get_save_path(USER_BINDINGS_FILE)

        # Create save data
        save_data = {}
        for action_id, action in self.actions.items():
            save_data[action_id] = action.keys

        try:
            with open(user_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
            print(f"Saved keybindings to {user_path}")
        except OSError as e:
            print(f"Error saving keybindings: {e}")

    def is_action_pressed(self, action_id: str, keys_state=None) -> bool:
        """Check if action is currently pressed."""
        if keys_state is None:
            keys_state = pygame.key.get_pressed()

        action = self.actions.get(action_id)
        if action is None:
            return False

        return action.is_pressed(keys_state)

    def is_action_just_pressed(self, action_id: str, event: pygame.event.Event) -> bool:
        """Check if action was just pressed this frame (for event-based input)."""
        if event.type != pygame.KEYDOWN:
            return False

        action = self.actions.get(action_id)
        if action is None:
            return False

        return event.key in action.pygame_keys

    def get_conflicting_actions(self, action_id: str, new_keys: List[str]) -> List[str]:
        """Find actions that would conflict with the new keybinding."""
        conflicts = []
        test_action = ControlAction(action_id, new_keys)

        for other_id, other_action in self.actions.items():
            if other_id == action_id:
                continue

            # Check for key overlap
            overlap = set(test_action.pygame_keys) & set(other_action.pygame_keys)
            if overlap:
                conflicts.append(other_id)

        return conflicts

    def rebind_action(self, action_id: str, new_keys: List[str],
                     allow_conflicts: bool = False) -> bool:
        """
        Rebind an action to new keys.

        Args:
            action_id: The action to rebind
            new_keys: List of new key names
            allow_conflicts: If False, check for conflicts first

        Returns:
            True if successful, False if conflicts found (when not allowed)
        """
        if action_id not in self.actions:
            return False

        if not allow_conflicts:
            conflicts = self.get_conflicting_actions(action_id, new_keys)
            if conflicts:
                return False

        # Apply rebinding
        action = self.actions[action_id]
        action.keys = new_keys
        action.pygame_keys = action._convert_to_pygame_keys(new_keys)

        return True

    def get_action_display_name(self, action_id: str) -> str:
        """Get human-readable name for action."""
        action = self.actions.get(action_id)
        if action:
            return action.display_name
        return action_id.split(".")[-1].replace("_", " ").title()

    def get_action_keys_display(self, action_id: str) -> str:
        """Get formatted key bindings for display."""
        action = self.actions.get(action_id)
        if action:
            return action.get_display_keys(self.display_names)
        return "Unbound"

    def get_category_actions(self, category: str) -> List[str]:
        """Get all action IDs in a category."""
        return self.categories.get(category, [])

    def get_all_categories(self) -> List[str]:
        """Get list of all control categories."""
        return list(self.categories.keys())

    def reset_to_defaults(self) -> None:
        """Reset all keybindings to defaults."""
        self.load_default_controls()

        # Delete user bindings file
        user_path = get_save_path(USER_BINDINGS_FILE)
        if user_path.exists():
            try:
                user_path.unlink()
            except OSError:
                pass


# Global instance
_controls_manager: Optional[ControlsManager] = None


def get_controls_manager() -> ControlsManager:
    """Get the global controls manager instance."""
    global _controls_manager
    if _controls_manager is None:
        _controls_manager = ControlsManager()
    return _controls_manager


def is_action_pressed(action_id: str) -> bool:
    """Convenience function to check if action is pressed."""
    return get_controls_manager().is_action_pressed(action_id)


def is_action_just_pressed(action_id: str, event: pygame.event.Event) -> bool:
    """Convenience function to check if action was just pressed."""
    return get_controls_manager().is_action_just_pressed(action_id, event)
