"""Unlocks Module - Orb-based progression system."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Set, Dict, Any, List, Optional
from datetime import datetime

from save_paths import get_save_path


UNLOCKS_FILE = "unlocks.json"

# Default abilities that are always unlocked (starting abilities)
DEFAULT_UNLOCKED_ABILITIES: Set[str] = {"DOUBLE_JUMP", "SWORD_ATTACK"}

# Updated ability order with orb costs
# Note: DOUBLE_JUMP is a default/starting ability and not in this progression list
ABILITY_ORDER: List[str] = [
    "DASH",
    "WALL_JUMP",
    "SLIDE",
    "WALL_CLING",
    "SHADOW_STEP",
    "AIR_DODGE",
    "GLIDE",
    "GRAPPLE",
    "GROUND_POUND",
    "DOUBLE_DASH",
    "TIME_SLOW",
    "TELEPORT",
    "STOMP_JUMP",
]

# Orb cost for each ability
# Note: DOUBLE_JUMP is a default/starting ability with no cost
ABILITY_ORB_COSTS: Dict[str, int] = {
    "DASH": 8,
    "WALL_JUMP": 12,
    "SLIDE": 15,
    "WALL_CLING": 18,
    "SHADOW_STEP": 25,
    "AIR_DODGE": 30,
    "GLIDE": 35,
    "GRAPPLE": 40,
    "GROUND_POUND": 45,
    "DOUBLE_DASH": 50,
    "TIME_SLOW": 60,
    "TELEPORT": 75,
    "STOMP_JUMP": 90,
}

# Ability prerequisites (ability -> required ability)
# Represents upgrade paths (e.g., DOUBLE_DASH is an upgrade of DASH)
# Note: DOUBLE_JUMP is a default/starting ability and not in prerequisites
ABILITY_PREREQUISITES: Dict[str, Optional[str]] = {
    "DASH": None,  # Starter ability
    "WALL_JUMP": None,  # Starter ability
    "SLIDE": "DASH",  # Requires dash first
    "WALL_CLING": "WALL_JUMP",  # Enhanced wall interaction
    "SHADOW_STEP": "DASH",  # Advanced dash variant
    "AIR_DODGE": None,  # Advanced air mobility (was DOUBLE_JUMP, now None since DOUBLE_JUMP is default)
    "GLIDE": None,  # Advanced air mobility (was DOUBLE_JUMP, now None since DOUBLE_JUMP is default)
    "GRAPPLE": "WALL_JUMP",  # Advanced wall interaction
    "GROUND_POUND": None,  # Advanced air attack (was DOUBLE_JUMP, now None since DOUBLE_JUMP is default)
    "DOUBLE_DASH": "DASH",  # Upgrade: dash -> double dash
    "TIME_SLOW": "SHADOW_STEP",  # Advanced evasion
    "TELEPORT": "SHADOW_STEP",  # Ultimate mobility
    "STOMP_JUMP": "GROUND_POUND",  # Ultimate air attack
}

# Ability categories for UI organization
ABILITY_CATEGORIES: Dict[str, str] = {
    "DOUBLE_JUMP": "movement",
    "DASH": "movement",
    "WALL_JUMP": "movement",
    "SLIDE": "movement",
    "WALL_CLING": "advanced",
    "SHADOW_STEP": "advanced",
    "AIR_DODGE": "advanced",
    "GLIDE": "advanced",
    "GRAPPLE": "utility",
    "GROUND_POUND": "combat",
    "DOUBLE_DASH": "movement",
    "TIME_SLOW": "advanced",
    "TELEPORT": "advanced",
    "STOMP_JUMP": "combat",
}

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
    "SLIDE": {
        "name": "Slide",
        "short": "SL",
        "description": "Slide under obstacles while maintaining speed.",
        "color": (255, 180, 100),
    },
    "WALL_CLING": {
        "name": "Wall Cling",
        "short": "WC",
        "description": "Hold onto walls to rest and plan your next move.",
        "color": (150, 200, 150),
    },
    "SHADOW_STEP": {
        "name": "Shadow Step",
        "short": "SS",
        "description": "Briefly phase through hazards and enemies.",
        "color": (200, 150, 255),
    },
    "AIR_DODGE": {
        "name": "Air Dodge",
        "short": "AD",
        "description": "Quick dodge with brief invincibility frames.",
        "color": (255, 150, 200),
    },
    "GLIDE": {
        "name": "Glide",
        "short": "GL",
        "description": "Hold jump while falling to glide gracefully.",
        "color": (150, 220, 255),
    },
    "GRAPPLE": {
        "name": "Grappling Hook",
        "short": "GR",
        "description": "Launch a grappling hook to swing or pull yourself.",
        "color": (200, 200, 100),
    },
    "GROUND_POUND": {
        "name": "Ground Pound",
        "short": "GP",
        "description": "Slam down with force, damaging enemies below.",
        "color": (180, 100, 100),
    },
    "DOUBLE_DASH": {
        "name": "Double Dash",
        "short": "DD",
        "description": "Perform a second dash in mid-air.",
        "color": (255, 200, 100),
    },
    "TIME_SLOW": {
        "name": "Time Slow",
        "short": "TS",
        "description": "Slow down time while you move normally.",
        "color": (100, 180, 255),
    },
    "TELEPORT": {
        "name": "Teleport",
        "short": "TP",
        "description": "Instantly teleport a short distance.",
        "color": (255, 100, 255),
    },
    "STOMP_JUMP": {
        "name": "Stomp Jump",
        "short": "SJ",
        "description": "Bounce off enemies to chain attacks.",
        "color": (255, 150, 100),
    },
}


@dataclass
class UnlockState:
    """State tracking ability unlocks and orb collection."""
    unlocked: Set[str]
    ability_orbs_total: int
    ability_orbs_spent: int
    orb_collection_history: List[str]  # Timestamps of collections
    # Game state fields for save/load
    level_index: int = 1
    lives: int = 3
    total_score: int = 0
    game_time: float = 0.0

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "unlocked": sorted(self.unlocked),
            "ability_orbs_total": self.ability_orbs_total,
            "ability_orbs_spent": self.ability_orbs_spent,
            "orb_collection_history": self.orb_collection_history,
            "level_index": self.level_index,
            "lives": self.lives,
            "total_score": self.total_score,
            "game_time": self.game_time,
        }

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]) -> "UnlockState":
        if not isinstance(data, dict):
            return cls(
                unlocked=DEFAULT_UNLOCKED_ABILITIES.copy(),
                ability_orbs_total=0,
                ability_orbs_spent=0,
                orb_collection_history=[],
                level_index=1,
                lives=3,
                total_score=0,
                game_time=0.0,
            )

        unlocked = data.get("unlocked", [])
        if not isinstance(unlocked, list):
            unlocked = []

        # Ensure default abilities are always included (for backwards compatibility with old saves)
        unlocked_set = set(str(x) for x in unlocked)
        unlocked_set.update(DEFAULT_UNLOCKED_ABILITIES)

        return cls(
            unlocked=unlocked_set,
            ability_orbs_total=int(data.get("ability_orbs_total", 0)),
            ability_orbs_spent=int(data.get("ability_orbs_spent", 0)),
            orb_collection_history=data.get("orb_collection_history", []),
            level_index=int(data.get("level_index", 1)),
            lives=int(data.get("lives", 3)),
            total_score=int(data.get("total_score", 0)),
            game_time=float(data.get("game_time", 0.0)),
        )


def _unlocks_path():
    return get_save_path(UNLOCKS_FILE)


class UnlockManager:
    def __init__(self) -> None:
        self._state = UnlockState(
            unlocked=DEFAULT_UNLOCKED_ABILITIES.copy(),
            ability_orbs_total=0,
            ability_orbs_spent=0,
            orb_collection_history=[],
            level_index=1,
            lives=3,
            total_score=0,
            game_time=0.0,
        )
        # Don't auto-load on init - game will call load_game_state() when continuing

    def load(self) -> None:
        """Legacy load method - kept for backwards compatibility."""
        p = _unlocks_path()
        if not p.exists():
            self._state = UnlockState(
                unlocked=DEFAULT_UNLOCKED_ABILITIES.copy(),
                ability_orbs_total=0,
                ability_orbs_spent=0,
                orb_collection_history=[],
                level_index=1,
                lives=3,
                total_score=0,
                game_time=0.0,
            )
            return
        try:
            with p.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._state = UnlockState(
                unlocked=DEFAULT_UNLOCKED_ABILITIES.copy(),
                ability_orbs_total=0,
                ability_orbs_spent=0,
                orb_collection_history=[],
                level_index=1,
                lives=3,
                total_score=0,
                game_time=0.0,
            )
            return
        self._state = UnlockState.from_jsonable(raw)

    def save(self) -> None:
        """Internal save method - use save_game_state() for explicit saves."""
        try:
            with _unlocks_path().open("w", encoding="utf-8") as f:
                json.dump(self._state.to_jsonable(), f, indent=2)
        except OSError:
            pass

    def has_save(self) -> bool:
        """Check if a save file exists."""
        return _unlocks_path().exists()

    def save_game_state(self, level_index: int, lives: int, total_score: int, game_time: float) -> None:
        """
        Save complete game state to disk.
        Called on quit or at auto-save checkpoints.
        """
        self._state.level_index = level_index
        self._state.lives = lives
        self._state.total_score = total_score
        self._state.game_time = game_time
        self.save()
        print(f"💾 Game saved: Level {level_index}, {lives} lives, {total_score} score")

    def load_game_state(self) -> Dict[str, Any]:
        """
        Load complete game state from disk.
        Returns dict with level_index, lives, total_score, game_time.
        """
        self.load()
        return {
            "level_index": self._state.level_index,
            "lives": self._state.lives,
            "total_score": self._state.total_score,
            "game_time": self._state.game_time,
        }

    def delete_save(self) -> None:
        """Delete save file (called on Game Over)."""
        p = _unlocks_path()
        if p.exists():
            try:
                p.unlink()
                print("🗑️  Save file deleted (Game Over)")
            except OSError:
                pass
        # Reset to defaults
        self._state = UnlockState(
            unlocked=DEFAULT_UNLOCKED_ABILITIES.copy(),
            ability_orbs_total=0,
            ability_orbs_spent=0,
            orb_collection_history=[],
            level_index=1,
            lives=3,
            total_score=0,
            game_time=0.0,
        )

    def reset_to_defaults(self) -> None:
        """Reset to default state (called on New Game)."""
        self._state = UnlockState(
            unlocked=DEFAULT_UNLOCKED_ABILITIES.copy(),
            ability_orbs_total=0,
            ability_orbs_spent=0,
            orb_collection_history=[],
            level_index=1,
            lives=3,
            total_score=0,
            game_time=0.0,
        )

    def add_ability_orb(self, count: int = 1) -> List[str]:
        """
        Add collected ability orb(s) and check for auto-unlocks.
        Note: Does NOT auto-save. Save is only triggered on quit or checkpoints.

        Args:
            count: Number of orbs to add (default 1)

        Returns:
            List of ability IDs that were unlocked
        """
        self._state.ability_orbs_total += count

        # Record collection timestamp
        timestamp = datetime.now().isoformat()
        for _ in range(count):
            self._state.orb_collection_history.append(timestamp)

        # Check if we can auto-unlock any abilities
        newly_unlocked = self._check_auto_unlocks()

        # NO AUTO-SAVE - progression is temporary until explicit save

        return newly_unlocked

    def _check_auto_unlocks(self) -> List[str]:
        """
        Automatically unlock abilities when orb threshold is reached and prerequisites are met.

        Returns:
            List of ability IDs that were newly unlocked
        """
        newly_unlocked = []
        available_orbs = self._state.ability_orbs_total - self._state.ability_orbs_spent

        for ability_id in ABILITY_ORDER:
            # Skip if already unlocked
            if ability_id in self._state.unlocked:
                continue

            # Check prerequisites
            prerequisite = ABILITY_PREREQUISITES.get(ability_id)
            if prerequisite and prerequisite not in self._state.unlocked:
                # Cannot unlock - missing prerequisite
                continue

            # Check if we have enough orbs
            cost = ABILITY_ORB_COSTS.get(ability_id, 9999)
            if available_orbs >= cost:
                # Unlock it!
                self._state.unlocked.add(ability_id)
                self._state.ability_orbs_spent += cost
                available_orbs -= cost
                newly_unlocked.append(ability_id)

                prereq_msg = f" (upgraded from {ABILITY_INFO[prerequisite]['name']})" if prerequisite else ""
                print(f"🎉 Unlocked: {ABILITY_INFO[ability_id]['name']} (Cost: {cost} orbs){prereq_msg}")

        return newly_unlocked

    def get_ability_orbs_available(self) -> int:
        """Get number of unspent ability orbs."""
        return self._state.ability_orbs_total - self._state.ability_orbs_spent

    def get_ability_orbs_total(self) -> int:
        """Get total orbs collected ever."""
        return self._state.ability_orbs_total

    def get_next_unlock(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the next ability to unlock.

        Returns:
            Dict with 'ability_id', 'name', 'cost', 'orbs_needed', 'prerequisite', 'can_unlock'
            or None if all abilities are unlocked
        """
        for ability_id in ABILITY_ORDER:
            if ability_id not in self._state.unlocked:
                cost = ABILITY_ORB_COSTS.get(ability_id, 9999)
                available = self.get_ability_orbs_available()
                orbs_needed = max(0, cost - available)

                prerequisite = ABILITY_PREREQUISITES.get(ability_id)
                prerequisite_met = prerequisite is None or prerequisite in self._state.unlocked
                can_unlock = available >= cost and prerequisite_met

                return {
                    'ability_id': ability_id,
                    'name': ABILITY_INFO[ability_id]['name'],
                    'cost': cost,
                    'orbs_needed': orbs_needed,
                    'progress': min(1.0, available / cost if cost > 0 else 1.0),
                    'prerequisite': prerequisite,
                    'prerequisite_met': prerequisite_met,
                    'prerequisite_name': ABILITY_INFO[prerequisite]['name'] if prerequisite else None,
                    'can_unlock': can_unlock,
                }

        return None  # All unlocked

    def get_unlock_progress_summary(self) -> str:
        """Get a formatted string showing unlock progress."""
        total_orbs = self._state.ability_orbs_total
        available_orbs = self.get_ability_orbs_available()
        unlocked_count = len(self._state.unlocked)
        total_abilities = len(ABILITY_ORDER)

        next_unlock = self.get_next_unlock()

        if next_unlock:
            return (
                f"Ability Orbs: {available_orbs} available ({total_orbs} total) | "
                f"Unlocked: {unlocked_count}/{total_abilities} | "
                f"Next: {next_unlock['name']} ({next_unlock['orbs_needed']} more needed)"
            )
        else:
            return (
                f"Ability Orbs: {available_orbs} | "
                f"All abilities unlocked! ({total_abilities}/{total_abilities})"
            )

    def is_unlocked(self, ability_id: str) -> bool:
        return ability_id in self._state.unlocked

    def is_enabled(self, ability_id: str) -> bool:
        return self.is_unlocked(ability_id)

    def unlock(self, ability_id: str) -> bool:
        """
        Manually unlock an ability (for debugging/cheats).
        Note: Does NOT auto-save.

        Returns:
            True if newly unlocked, False if already unlocked
        """
        if ability_id in self._state.unlocked:
            return False
        self._state.unlocked.add(ability_id)
        # NO AUTO-SAVE
        return True

    def unlock_next(self) -> Optional[str]:
        """
        Legacy method - now just checks auto-unlock.
        Use add_ability_orb() instead for new system.
        """
        self._check_auto_unlocks()
        # Return first unlocked ability
        for ability_id in ABILITY_ORDER:
            if ability_id in self._state.unlocked:
                return ability_id
        return None

    def get_enabled_abilities(self) -> List[str]:
        # Include default abilities plus any unlocked progression abilities
        enabled = list(DEFAULT_UNLOCKED_ABILITIES)
        enabled.extend([a for a in ABILITY_ORDER if a in self._state.unlocked])
        return enabled

    def reset(self) -> None:
        """Reset unlocks only (deprecated - use reset_to_defaults() or delete_save())."""
        self._state = UnlockState(
            unlocked=DEFAULT_UNLOCKED_ABILITIES.copy(),
            ability_orbs_total=0,
            ability_orbs_spent=0,
            orb_collection_history=[],
            level_index=1,
            lives=3,
            total_score=0,
            game_time=0.0,
        )
        # NO AUTO-SAVE

    def get_all_ability_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all abilities for UI display.

        Returns:
            List of dicts with ability info and unlock status, including prerequisites
        """
        result = []
        available_orbs = self.get_ability_orbs_available()

        for ability_id in ABILITY_ORDER:
            cost = ABILITY_ORB_COSTS.get(ability_id, 9999)
            is_unlocked = ability_id in self._state.unlocked
            info = ABILITY_INFO.get(ability_id, {})

            prerequisite = ABILITY_PREREQUISITES.get(ability_id)
            prerequisite_met = prerequisite is None or prerequisite in self._state.unlocked
            can_unlock = available_orbs >= cost and prerequisite_met

            result.append({
                'ability_id': ability_id,
                'name': info.get('name', ability_id),
                'short': info.get('short', '??'),
                'description': info.get('description', ''),
                'color': info.get('color', (200, 200, 200)),
                'category': ABILITY_CATEGORIES.get(ability_id, 'other'),
                'cost': cost,
                'unlocked': is_unlocked,
                'can_afford': available_orbs >= cost,
                'can_unlock': can_unlock,
                'prerequisite': prerequisite,
                'prerequisite_met': prerequisite_met,
                'prerequisite_name': ABILITY_INFO[prerequisite]['name'] if prerequisite else None,
                'progress': min(1.0, available_orbs / cost if cost > 0 else 1.0) if not is_unlocked else 1.0,
            })

        return result

    def get_upgrade_tree(self) -> Dict[str, List[str]]:
        """
        Get the upgrade tree showing which abilities upgrade from others.

        Returns:
            Dict mapping base abilities to their upgrades
        """
        tree = {}
        for ability_id, prerequisite in ABILITY_PREREQUISITES.items():
            if prerequisite:
                if prerequisite not in tree:
                    tree[prerequisite] = []
                tree[prerequisite].append(ability_id)
        return tree

    def get_ability_category(self, ability_id: str) -> str:
        """Get the category of an ability."""
        return ABILITY_CATEGORIES.get(ability_id, "other")

    def get_abilities_by_category(self) -> Dict[str, List[str]]:
        """
        Get abilities organized by category.

        Returns:
            Dict mapping categories to lists of ability IDs
        """
        by_category = {}
        for ability_id in ABILITY_ORDER:
            category = ABILITY_CATEGORIES.get(ability_id, "other")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(ability_id)
        return by_category


# Global instance
_unlock_manager: UnlockManager | None = None


def get_unlock_manager() -> UnlockManager:
    global _unlock_manager
    if _unlock_manager is None:
        _unlock_manager = UnlockManager()
    return _unlock_manager


def get_enabled_abilities() -> List[str]:
    return get_unlock_manager().get_enabled_abilities()
