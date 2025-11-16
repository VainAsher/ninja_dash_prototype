"""Unlocks Module - Orb-based progression system."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Set, Dict, Any, List, Optional
from datetime import datetime

from save_paths import get_save_path


UNLOCKS_FILE = "unlocks.json"

# Updated ability order with orb costs
ABILITY_ORDER: List[str] = [
    "DOUBLE_JUMP",
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
ABILITY_ORB_COSTS: Dict[str, int] = {
    "DOUBLE_JUMP": 5,
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
ABILITY_PREREQUISITES: Dict[str, Optional[str]] = {
    "DOUBLE_JUMP": None,  # Starter ability
    "DASH": None,  # Starter ability
    "WALL_JUMP": None,  # Starter ability
    "SLIDE": "DASH",  # Requires dash first
    "WALL_CLING": "WALL_JUMP",  # Enhanced wall interaction
    "SHADOW_STEP": "DASH",  # Advanced dash variant
    "AIR_DODGE": "DOUBLE_JUMP",  # Advanced air mobility
    "GLIDE": "DOUBLE_JUMP",  # Advanced air mobility
    "GRAPPLE": "WALL_JUMP",  # Advanced wall interaction
    "GROUND_POUND": "DOUBLE_JUMP",  # Advanced air attack
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

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "unlocked": sorted(self.unlocked),
            "ability_orbs_total": self.ability_orbs_total,
            "ability_orbs_spent": self.ability_orbs_spent,
            "orb_collection_history": self.orb_collection_history,
        }

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]) -> "UnlockState":
        if not isinstance(data, dict):
            return cls(
                unlocked=set(),
                ability_orbs_total=0,
                ability_orbs_spent=0,
                orb_collection_history=[]
            )

        unlocked = data.get("unlocked", [])
        if not isinstance(unlocked, list):
            unlocked = []

        return cls(
            unlocked=set(str(x) for x in unlocked),
            ability_orbs_total=int(data.get("ability_orbs_total", 0)),
            ability_orbs_spent=int(data.get("ability_orbs_spent", 0)),
            orb_collection_history=data.get("orb_collection_history", [])
        )


def _unlocks_path():
    return get_save_path(UNLOCKS_FILE)


class UnlockManager:
    def __init__(self) -> None:
        self._state = UnlockState(
            unlocked=set(),
            ability_orbs_total=0,
            ability_orbs_spent=0,
            orb_collection_history=[]
        )
        self.load()

    def load(self) -> None:
        p = _unlocks_path()
        if not p.exists():
            self._state = UnlockState(
                unlocked=set(),
                ability_orbs_total=0,
                ability_orbs_spent=0,
                orb_collection_history=[]
            )
            return
        try:
            with p.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._state = UnlockState(
                unlocked=set(),
                ability_orbs_total=0,
                ability_orbs_spent=0,
                orb_collection_history=[]
            )
            return
        self._state = UnlockState.from_jsonable(raw)

    def save(self) -> None:
        try:
            with _unlocks_path().open("w", encoding="utf-8") as f:
                json.dump(self._state.to_jsonable(), f, indent=2)
        except OSError:
            pass

    def add_ability_orb(self, count: int = 1) -> None:
        """
        Add collected ability orb(s) and check for auto-unlocks.

        Args:
            count: Number of orbs to add (default 1)
        """
        self._state.ability_orbs_total += count

        # Record collection timestamp
        timestamp = datetime.now().isoformat()
        for _ in range(count):
            self._state.orb_collection_history.append(timestamp)

        # Check if we can auto-unlock any abilities
        self._check_auto_unlocks()

        self.save()

    def _check_auto_unlocks(self) -> None:
        """Automatically unlock abilities when orb threshold is reached and prerequisites are met."""
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

                prereq_msg = f" (upgraded from {ABILITY_INFO[prerequisite]['name']})" if prerequisite else ""
                print(f"🎉 Unlocked: {ABILITY_INFO[ability_id]['name']} (Cost: {cost} orbs){prereq_msg}")

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

        Returns:
            True if newly unlocked, False if already unlocked
        """
        if ability_id in self._state.unlocked:
            return False
        self._state.unlocked.add(ability_id)
        self.save()
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
        return [a for a in ABILITY_ORDER if a in self._state.unlocked]

    def reset(self) -> None:
        self._state = UnlockState(
            unlocked=set(),
            ability_orbs_total=0,
            ability_orbs_spent=0,
            orb_collection_history=[]
        )
        self.save()

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
