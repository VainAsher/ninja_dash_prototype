"""
Settings and Control Presets - Save and load configuration presets
"""

import json
import os
from typing import Dict, Any, List


class PresetsManager:
    """Manages settings and control presets."""

    def __init__(self, presets_file: str = "user_presets.json"):
        self.presets_file = presets_file
        self.presets: Dict[str, Dict[str, Any]] = {}
        self.load_presets()

    def load_presets(self):
        """Load presets from file."""
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r') as f:
                    self.presets = json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load presets: {e}")
                self.presets = {}
        else:
            self.presets = self._get_default_presets()
            self.save_presets()

    def save_presets(self):
        """Save presets to file."""
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            print(f"[WARNING] Failed to save presets: {e}")

    def _get_default_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get default presets."""
        return {
            "performance": {
                "name": "Performance",
                "description": "Optimized for smooth gameplay on lower-end systems",
                "settings": {
                    "particles_enabled": False,
                    "screen_shake_enabled": False,
                    "vsync": False,
                    "show_fps": True,
                }
            },
            "quality": {
                "name": "Quality",
                "description": "Maximum visual quality for powerful systems",
                "settings": {
                    "particles_enabled": True,
                    "screen_shake_enabled": True,
                    "vsync": True,
                    "show_fps": False,
                }
            },
            "balanced": {
                "name": "Balanced",
                "description": "Good balance between performance and visuals",
                "settings": {
                    "particles_enabled": True,
                    "screen_shake_enabled": True,
                    "vsync": True,
                    "show_fps": False,
                }
            },
        }

    def get_preset_names(self) -> List[str]:
        """Get list of preset names."""
        return list(self.presets.keys())

    def get_preset(self, name: str) -> Dict[str, Any]:
        """Get a specific preset."""
        return self.presets.get(name, {})

    def apply_preset(self, name: str, game_obj: Any):
        """Apply a preset to the game object."""
        preset = self.get_preset(name)
        if not preset or 'settings' not in preset:
            return False

        settings = preset['settings']
        for key, value in settings.items():
            setattr(game_obj, key, value)

        print(f"[INFO] Applied preset: {preset.get('name', name)}")
        return True

    def save_custom_preset(self, name: str, description: str, settings: Dict[str, Any]):
        """Save a custom preset."""
        self.presets[name] = {
            "name": name,
            "description": description,
            "settings": settings,
            "custom": True
        }
        self.save_presets()

    def delete_preset(self, name: str):
        """Delete a custom preset."""
        if name in self.presets and self.presets[name].get("custom", False):
            del self.presets[name]
            self.save_presets()
            return True
        return False


class ControlPresets:
    """Predefined control schemes."""

    @staticmethod
    def get_default_scheme() -> Dict[str, List[str]]:
        """Default control scheme."""
        return {
            "movement.move_left": ["left", "a"],
            "movement.move_right": ["right", "d"],
            "movement.jump": ["space", "w", "up"],
            "movement.crouch_down": ["down", "s"],
            "abilities.dash": ["left shift", "right shift"],
            "abilities.double_jump": ["space"],
            "abilities.wall_jump": ["space"],
            "abilities.air_dodge": ["c"],
            "abilities.slide": ["v"],
            "abilities.shadow_step": ["q"],
            "abilities.grapple": ["e"],
            "ui.pause": ["escape"],
        }

    @staticmethod
    def get_wasd_scheme() -> Dict[str, List[str]]:
        """WASD-focused control scheme."""
        return {
            "movement.move_left": ["a"],
            "movement.move_right": ["d"],
            "movement.jump": ["w", "space"],
            "movement.crouch_down": ["s"],
            "abilities.dash": ["left shift"],
            "abilities.double_jump": ["w"],
            "abilities.wall_jump": ["w"],
            "abilities.air_dodge": ["e"],
            "abilities.slide": ["q"],
            "abilities.shadow_step": ["r"],
            "abilities.grapple": ["f"],
            "ui.pause": ["escape"],
        }

    @staticmethod
    def get_arrows_scheme() -> Dict[str, List[str]]:
        """Arrow keys control scheme."""
        return {
            "movement.move_left": ["left"],
            "movement.move_right": ["right"],
            "movement.jump": ["up", "space"],
            "movement.crouch_down": ["down"],
            "abilities.dash": ["right shift"],
            "abilities.double_jump": ["up"],
            "abilities.wall_jump": ["up"],
            "abilities.air_dodge": ["right ctrl"],
            "abilities.slide": ["/"],
            "abilities.shadow_step": ["."],
            "abilities.grapple": [","],
            "ui.pause": ["escape"],
        }

    @staticmethod
    def get_scheme(scheme_name: str) -> Dict[str, List[str]]:
        """Get a control scheme by name."""
        schemes = {
            "default": ControlPresets.get_default_scheme(),
            "wasd": ControlPresets.get_wasd_scheme(),
            "arrows": ControlPresets.get_arrows_scheme(),
        }
        return schemes.get(scheme_name, ControlPresets.get_default_scheme())

    @staticmethod
    def apply_scheme(scheme_name: str, controls_manager):
        """Apply a control scheme to the controls manager."""
        scheme = ControlPresets.get_scheme(scheme_name)
        for action_id, keys in scheme.items():
            controls_manager.rebind_action(action_id, keys, allow_conflicts=True)
        print(f"[INFO] Applied control scheme: {scheme_name}")
