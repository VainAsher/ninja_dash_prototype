"""Unlocks Module - Permanent progression system."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Set, Dict, Any, List, Optional

from save_paths import get_save_path


UNLOCKS_FILE = "unlocks.json"

ABILITY_ORDER: List[str] = [
    "DOUBLE_JUMP",
    "DASH",
    "WALL_JUMP",
    "SHADOW_STEP",
    "COIN_MAGNET",
]

ABILITY_INFO: Dict[str, Dict[str, Any]] = {
    "DOUBLE_JUMP": {
        "name": "Double Jump",
        "short": "DJ",
        "description": "Press jump again in mid-air to gain extra height.",
        "color": (100, 200, 255),
    },
    "DASH": {
        "name": "Dash",
        "short": "D",
        "description": "Quickly burst forward in the facing direction.",
        "color": (255, 220, 100),
    },
    "WALL_JUMP": {
        "name": "Wall Jump",
        "short": "WJ",
        "description": "Jump off walls to regain height and change direction.",
        "color": (160, 255, 160),
    },
    "SHADOW_STEP": {
        "name": "Shadow Step",
        "short": "SS",
        "description": "Briefly phase through hazards and enemies.",
        "color": (200, 150, 255),
    },
    "COIN_MAGNET": {
        "name": "Coin Magnet",
        "short": "CM",
        "description": "Attract nearby coins while moving.",
        "color": (255, 255, 120),
    },
}


@dataclass
class UnlockState:
    unlocked: Set[str]

    def to_jsonable(self) -> Dict[str, Any]:
        return {"unlocked": sorted(self.unlocked)}

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]) -> "UnlockState":
        if not isinstance(data, dict):
            return cls(unlocked=set())
        raw = data.get("unlocked", [])
        if not isinstance(raw, list):
            raw = []
        return cls(unlocked=set(str(x) for x in raw))


def _unlocks_path():
    return get_save_path(UNLOCKS_FILE)


class UnlockManager:
    def __init__(self) -> None:
        self._state = UnlockState(unlocked=set())
        self.load()

    def load(self) -> None:
        p = _unlocks_path()
        if not p.exists():
            self._state = UnlockState(unlocked=set())
            return
        try:
            with p.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._state = UnlockState(unlocked=set())
            return
        self._state = UnlockState.from_jsonable(raw)

    def save(self) -> None:
        try:
            with _unlocks_path().open("w", encoding="utf-8") as f:
                json.dump(self._state.to_jsonable(), f, indent=2)
        except OSError:
            pass

    def is_unlocked(self, ability_id: str) -> bool:
        return ability_id in self._state.unlocked

    def is_enabled(self, ability_id: str) -> bool:
        return self.is_unlocked(ability_id)

    def unlock(self, ability_id: str) -> bool:
        if ability_id in self._state.unlocked:
            return False
        self._state.unlocked.add(ability_id)
        self.save()
        return True

    def unlock_next(self) -> Optional[str]:
        for ability_id in ABILITY_ORDER:
            if ability_id not in self._state.unlocked:
                self.unlock(ability_id)
                return ability_id
        return None

    def get_enabled_abilities(self) -> List[str]:
        return [a for a in ABILITY_ORDER if a in self._state.unlocked]

    def reset(self) -> None:
        self._state = UnlockState(unlocked=set())
        self.save()


_unlock_manager: UnlockManager | None = None


def get_unlock_manager() -> UnlockManager:
    global _unlock_manager
    if _unlock_manager is None:
        _unlock_manager = UnlockManager()
    return _unlock_manager


def get_enabled_abilities() -> List[str]:
    return get_unlock_manager().get_enabled_abilities()
