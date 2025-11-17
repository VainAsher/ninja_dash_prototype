"""
Gameplay Modifiers System

Provides player-accessible debug features and practice mode aids:
- God Mode (invincibility)
- Infinite Resources (stamina, charges, etc.)
- Flight Mode (no gravity)
- Slow Motion (time scaling)
- Ability Toggles (enable/disable individual abilities)
- Visual Debug Options (hitboxes, grid, etc.)
"""

import json
import os
from typing import Dict, Any


class GameplayModifiers:
    """
    Manages gameplay modifiers for practice mode and debugging.

    All settings are saved to user preferences and persist between sessions.
    """

    def __init__(self):
        # Gameplay Assists
        self.god_mode = False           # Invincibility
        self.infinite_stamina = False   # Abilities never deplete
        self.infinite_charges = False   # Shadow step/grapple never deplete
        self.flight_mode = False        # No gravity
        self.time_scale = 1.0          # Game speed (0.1 - 2.0)

        # Ability Toggles (managed by player, but exposed here for UI)
        self.ability_states = {
            'double_jump': True,
            'dash': True,
            'wall_jump': True,
            'slide': True,
            'shadow_step': True,
            'wall_cling': True,
            'air_dodge': True,
            'glide': True,
            'sword_attack': True,
            'grapple_hook': True,
        }

        # Visual Options
        self.show_debug_overlay = False  # F3 overlay
        self.show_hitboxes = False       # Collision boxes
        self.show_grid = False           # Level grid
        self.show_fps = False            # FPS counter

        # Level Options
        self.disable_hazards = False     # Hazards don't damage

        # Load saved preferences
        self.load_preferences()

    def is_god_mode_active(self):
        """Check if god mode is currently active."""
        return self.god_mode

    def is_infinite_stamina_active(self):
        """Check if infinite stamina is active."""
        return self.infinite_stamina

    def is_infinite_charges_active(self):
        """Check if infinite charges is active."""
        return self.infinite_charges

    def is_flight_mode_active(self):
        """Check if flight mode is active."""
        return self.flight_mode

    def get_time_scale(self):
        """Get current time scale multiplier."""
        return self.time_scale

    def set_time_scale(self, scale: float):
        """Set time scale (0.1 - 2.0)."""
        self.time_scale = max(0.1, min(2.0, scale))
        self.save_preferences()

    def toggle_god_mode(self):
        """Toggle god mode on/off."""
        self.god_mode = not self.god_mode
        self.save_preferences()
        return self.god_mode

    def toggle_infinite_stamina(self):
        """Toggle infinite stamina on/off."""
        self.infinite_stamina = not self.infinite_stamina
        self.save_preferences()
        return self.infinite_stamina

    def toggle_infinite_charges(self):
        """Toggle infinite charges on/off."""
        self.infinite_charges = not self.infinite_charges
        self.save_preferences()
        return self.infinite_charges

    def toggle_flight_mode(self):
        """Toggle flight mode on/off."""
        self.flight_mode = not self.flight_mode
        self.save_preferences()
        return self.flight_mode

    def toggle_ability(self, ability_name: str):
        """Toggle an ability on/off."""
        if ability_name in self.ability_states:
            self.ability_states[ability_name] = not self.ability_states[ability_name]
            self.save_preferences()
            return self.ability_states[ability_name]
        return None

    def set_ability_state(self, ability_name: str, enabled: bool):
        """Set an ability's enabled state."""
        if ability_name in self.ability_states:
            self.ability_states[ability_name] = enabled
            self.save_preferences()

    def reset_all_abilities(self):
        """Enable all abilities."""
        for ability in self.ability_states:
            self.ability_states[ability] = True
        self.save_preferences()

    def toggle_debug_overlay(self):
        """Toggle debug overlay on/off."""
        self.show_debug_overlay = not self.show_debug_overlay
        self.save_preferences()
        return self.show_debug_overlay

    def toggle_hitboxes(self):
        """Toggle hitbox rendering on/off."""
        self.show_hitboxes = not self.show_hitboxes
        self.save_preferences()
        return self.show_hitboxes

    def toggle_grid(self):
        """Toggle grid rendering on/off."""
        self.show_grid = not self.show_grid
        self.save_preferences()
        return self.show_grid

    def toggle_fps(self):
        """Toggle FPS counter on/off."""
        self.show_fps = not self.show_fps
        self.save_preferences()
        return self.show_fps

    def toggle_hazards(self):
        """Toggle hazard damage on/off."""
        self.disable_hazards = not self.disable_hazards
        self.save_preferences()
        return self.disable_hazards

    def reset_to_defaults(self):
        """Reset all modifiers to default values."""
        self.god_mode = False
        self.infinite_stamina = False
        self.infinite_charges = False
        self.flight_mode = False
        self.time_scale = 1.0
        self.show_debug_overlay = False
        self.show_hitboxes = False
        self.show_grid = False
        self.show_fps = False
        self.disable_hazards = False
        self.reset_all_abilities()
        self.save_preferences()

    def get_preferences_path(self):
        """Get path to preferences file."""
        # Use user's home directory for persistent settings
        home = os.path.expanduser("~")
        config_dir = os.path.join(home, ".ninja_dash")

        # Create config directory if it doesn't exist
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        return os.path.join(config_dir, "modifiers.json")

    def save_preferences(self):
        """Save modifiers to JSON file."""
        try:
            data = {
                'god_mode': self.god_mode,
                'infinite_stamina': self.infinite_stamina,
                'infinite_charges': self.infinite_charges,
                'flight_mode': self.flight_mode,
                'time_scale': self.time_scale,
                'ability_states': self.ability_states,
                'show_debug_overlay': self.show_debug_overlay,
                'show_hitboxes': self.show_hitboxes,
                'show_grid': self.show_grid,
                'show_fps': self.show_fps,
                'disable_hazards': self.disable_hazards,
            }

            with open(self.get_preferences_path(), 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save modifiers preferences: {e}")

    def load_preferences(self):
        """Load modifiers from JSON file."""
        try:
            path = self.get_preferences_path()
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)

                # Load values
                self.god_mode = data.get('god_mode', False)
                self.infinite_stamina = data.get('infinite_stamina', False)
                self.infinite_charges = data.get('infinite_charges', False)
                self.flight_mode = data.get('flight_mode', False)
                self.time_scale = data.get('time_scale', 1.0)
                self.ability_states = data.get('ability_states', self.ability_states)
                self.show_debug_overlay = data.get('show_debug_overlay', False)
                self.show_hitboxes = data.get('show_hitboxes', False)
                self.show_grid = data.get('show_grid', False)
                self.show_fps = data.get('show_fps', False)
                self.disable_hazards = data.get('disable_hazards', False)
        except Exception as e:
            print(f"Warning: Could not load modifiers preferences: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Export all modifiers as a dictionary."""
        return {
            'god_mode': self.god_mode,
            'infinite_stamina': self.infinite_stamina,
            'infinite_charges': self.infinite_charges,
            'flight_mode': self.flight_mode,
            'time_scale': self.time_scale,
            'ability_states': self.ability_states.copy(),
            'show_debug_overlay': self.show_debug_overlay,
            'show_hitboxes': self.show_hitboxes,
            'show_grid': self.show_grid,
            'show_fps': self.show_fps,
            'disable_hazards': self.disable_hazards,
        }

    def from_dict(self, data: Dict[str, Any]):
        """Import modifiers from a dictionary."""
        self.god_mode = data.get('god_mode', False)
        self.infinite_stamina = data.get('infinite_stamina', False)
        self.infinite_charges = data.get('infinite_charges', False)
        self.flight_mode = data.get('flight_mode', False)
        self.time_scale = data.get('time_scale', 1.0)
        self.ability_states = data.get('ability_states', self.ability_states)
        self.show_debug_overlay = data.get('show_debug_overlay', False)
        self.show_hitboxes = data.get('show_hitboxes', False)
        self.show_grid = data.get('show_grid', False)
        self.show_fps = data.get('show_fps', False)
        self.disable_hazards = data.get('disable_hazards', False)
        self.save_preferences()


# Global instance
_modifiers_instance = None


def get_modifiers() -> GameplayModifiers:
    """Get the global gameplay modifiers instance."""
    global _modifiers_instance
    if _modifiers_instance is None:
        _modifiers_instance = GameplayModifiers()
    return _modifiers_instance
