"""
UI Package - User interface components
"""

# Export main HUD components
from .hud_components import (
    ScoreSection,
    VitalsSection,
    LevelInfoSection,
    TimeAbilitiesSection,
    AbilityProgressSection,
    PowerupIndicators,
    AbilityResourceBars,
    ExitGateIndicator
)

# Keep legacy components accessible
from .legacy_ui import Button, Toggle, Slider, TextInput

__all__ = [
    'ScoreSection',
    'VitalsSection',
    'LevelInfoSection',
    'TimeAbilitiesSection',
    'AbilityProgressSection',
    'PowerupIndicators',
    'AbilityResourceBars',
    'ExitGateIndicator',
    'Button',
    'Toggle',
    'Slider',
    'TextInput',
]
