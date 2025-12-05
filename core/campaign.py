"""
Campaign State Management for Hollowed Ninja

This module defines the CampaignState dataclass that tracks player progression
through the multi-act story campaign. It manages:
- Current act and mission progress
- Boss defeats and major story beats
- NPC unlocks and interactions
- Ability progression through scroll fragments
- Equipment tiers and hollowing state

The campaign follows this structure:
- Act 0: Lantern Heights (tutorial/welcoming)
- Act 1: Veil Maiden Boss Fight
- Act 2: Hollow Depths (post-hollowing, stripped abilities)
- Act 3: Ember Monastery (rebuilding power)
- Act 4: Skyroad Summit (final ascent)
- Final Boss: Hollow Reflection
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, Optional


@dataclass
class CampaignState:
    """
    Tracks all campaign progression state for Hollowed Ninja.

    This includes:
    - Act/mission progression
    - Boss defeats
    - NPC unlocks
    - Ability unlocks via scroll fragments
    - Equipment tier progression
    - Hollowing state (post-Veil Maiden)

    Attributes:
        act: Current act number (0-4)
            0 = Lantern Heights
            1 = Veil Maiden fight
            2 = Hollow Depths
            3 = Ember Monastery
            4 = Skyroad Summit
        mission_index: Current mission within the act

        boss_flags: Dict tracking which bosses have been defeated
        npc_unlocked: Dict tracking which NPCs are available in hubs
        abilities_unlocked: Set of ability names unlocked via scrolls
        scrolls_completed: Set of scroll IDs that have been fully assembled
        scroll_fragments: Dict tracking fragment count per scroll

        max_equipment_tier: Maximum equipment tier available (1-4)
        has_yin_yang: Whether player still has Yin/Yang (lost at Veil Maiden)
        is_hollowed: Whether player has been hollowed (post-Veil Maiden)
    """

    # Progression tracking
    act: int = 0
    mission_index: int = 0

    # Boss defeats
    boss_flags: Dict[str, bool] = field(default_factory=lambda: {
        "veil_maiden": False,        # Act 1 - strips abilities
        "weightbound_ogre": False,   # Act 2 - unlocks deeper Hollow
        "shatter_moth_queen": False, # Act 2 - unlocks Ember
        "stone_judge": False,        # Act 3 - unlocks tier 3 gear
        "hollow_reflection": False,  # Final boss
    })

    # NPC availability in hubs
    npc_unlocked: Dict[str, bool] = field(default_factory=lambda: {
        "shade_hermit": False,       # Hollow hub - cryptic advice
        "smith_monk": False,         # Ember hub - equipment upgrades
        "listening_elder": False,    # Ember hub - lore and guidance
        "advocate": False,           # Skyroad - final upgrade vendor
        # Could add: hearth brothers, merchants, etc.
    })

    # Ability progression system
    abilities_unlocked: Set[str] = field(default_factory=set)
    scrolls_completed: Set[str] = field(default_factory=set)
    scroll_fragments: Dict[str, int] = field(default_factory=dict)

    # Equipment and power level
    max_equipment_tier: int = 1
    equipped_items: Dict[str, str] = field(default_factory=lambda: {
        "weapon": "training_blade",
        "armor": "cloth_gi",
        "boots": "worn_sandals",
        "charm": "wooden_talisman",
    })
    currency: int = 0  # Fragments available for equipment purchases

    # Story state
    has_yin_yang: bool = True
    is_hollowed: bool = False

    def advance_mission(self) -> None:
        """Progress to next mission in current act."""
        self.mission_index += 1

    def advance_act(self, new_act: int) -> None:
        """Move to a new act, resetting mission index."""
        self.act = new_act
        self.mission_index = 0

    def on_boss_defeated(self, boss_id: str) -> None:
        """
        Mark a boss as defeated and trigger associated unlocks.

        Args:
            boss_id: String identifier for the boss (e.g., "veil_maiden")
        """
        if boss_id not in self.boss_flags:
            print(f"⚠️  Unknown boss ID: {boss_id}")
            return

        self.boss_flags[boss_id] = True

        # Trigger special events based on boss
        if boss_id == "veil_maiden":
            # Veil Maiden defeat - the hollowing
            self._trigger_hollowing()
        elif boss_id == "weightbound_ogre":
            # Unlock smith monk in Ember hub
            self.npc_unlocked["smith_monk"] = True
            self.max_equipment_tier = 2
        elif boss_id == "stone_judge":
            # Unlock tier 3 equipment
            self.max_equipment_tier = 3
        elif boss_id == "shatter_moth_queen":
            # Unlock listening elder
            self.npc_unlocked["listening_elder"] = True
        elif boss_id == "hollow_reflection":
            # Final boss - unlock Inner Lantern
            self.abilities_unlocked.add("INNER_LANTERN")

    def _trigger_hollowing(self) -> None:
        """
        Execute the hollowing event - the Veil Maiden strips the player's power.

        This is the major turning point of the campaign where:
        - Yin/Yang is taken
        - All unlocked abilities are lost
        - Player becomes hollowed
        - Equipment tier resets to 0
        """
        print("💀 The Veil Maiden tears away your light...")
        self.has_yin_yang = False
        self.is_hollowed = True
        self.abilities_unlocked.clear()
        self.max_equipment_tier = 0
        # Note: scroll_fragments are NOT cleared - progress is remembered

    def add_scroll_fragment(self, scroll_id: str, required_fragments: int = 3) -> bool:
        """
        Add a fragment to a scroll. Returns True if scroll is completed.

        Args:
            scroll_id: Identifier for the scroll (e.g., "clarity_sense")
            required_fragments: Number of fragments needed to complete (default: 3)

        Returns:
            True if this fragment completed the scroll, False otherwise
        """
        if scroll_id in self.scrolls_completed:
            return False

        current = self.scroll_fragments.get(scroll_id, 0)
        current += 1
        self.scroll_fragments[scroll_id] = current

        if current >= required_fragments:
            self.scrolls_completed.add(scroll_id)
            return True

        return False

    def get_scroll_progress(self, scroll_id: str, required_fragments: int = 3) -> Tuple[int, int]:
        """
        Get current progress on a scroll.

        Args:
            scroll_id: Identifier for the scroll
            required_fragments: Total fragments needed

        Returns:
            Tuple of (current_fragments, required_fragments)
        """
        current = self.scroll_fragments.get(scroll_id, 0)
        return (current, required_fragments)

    def unlock_ability_from_scroll(self, scroll_id: str, ability_name: str) -> None:
        """
        Unlock an ability when its scroll is completed.

        Args:
            scroll_id: The scroll that was completed
            ability_name: The ability to unlock (e.g., "SHADOW_STEP")
        """
        if scroll_id in self.scrolls_completed:
            self.abilities_unlocked.add(ability_name)
            print(f"✨ Ability unlocked: {ability_name}")

    def get_total_stats(self):
        """
        Calculate total stats (base + equipment bonuses).

        Returns:
            Stats object with combined base and equipment stats
        """
        from core.equipment import get_base_stats_for_act, ALL_EQUIPMENT, Stats

        # Start with base stats for current act
        total = get_base_stats_for_act(self.act).copy()

        # Add bonuses from equipped items
        for slot, item_id in self.equipped_items.items():
            if item_id in ALL_EQUIPMENT:
                equipment = ALL_EQUIPMENT[item_id]
                total = total + equipment.stats

        return total

    def equip_item(self, item_id: str) -> bool:
        """
        Equip an item to the appropriate slot.

        Args:
            item_id: ID of the equipment to equip

        Returns:
            True if equipped successfully, False otherwise
        """
        from core.equipment import ALL_EQUIPMENT

        if item_id not in ALL_EQUIPMENT:
            print(f"⚠️  Unknown equipment: {item_id}")
            return False

        equipment = ALL_EQUIPMENT[item_id]

        # Check tier requirement
        if equipment.tier > self.max_equipment_tier:
            print(f"⚠️  Equipment tier {equipment.tier} not yet unlocked (max: {self.max_equipment_tier})")
            return False

        # Equip to slot
        self.equipped_items[equipment.slot] = item_id
        print(f"⚙️  Equipped: {equipment.name}")
        return True

    def purchase_equipment(self, item_id: str) -> bool:
        """
        Purchase and equip an item using currency.

        Args:
            item_id: ID of the equipment to purchase

        Returns:
            True if purchased successfully, False otherwise
        """
        from core.equipment import ALL_EQUIPMENT

        if item_id not in ALL_EQUIPMENT:
            print(f"⚠️  Unknown equipment: {item_id}")
            return False

        equipment = ALL_EQUIPMENT[item_id]

        # Check tier requirement
        if equipment.tier > self.max_equipment_tier:
            print(f"⚠️  Equipment tier {equipment.tier} not yet unlocked")
            return False

        # Check currency
        if self.currency < equipment.cost:
            print(f"⚠️  Not enough currency: {self.currency}/{equipment.cost}")
            return False

        # Purchase and equip
        self.currency -= equipment.cost
        self.equip_item(item_id)
        print(f"💰 Purchased {equipment.name} for {equipment.cost} fragments")
        return True

    def add_currency(self, amount: int) -> None:
        """Add currency (fragments) for equipment purchases."""
        self.currency += amount
        print(f"💎 +{amount} fragments (Total: {self.currency})")


def get_base_abilities_for_act(state: CampaignState) -> Set[str]:
    """
    Get the base abilities available for the current act.

    These are abilities that are always available (not from scrolls),
    representing the player's fundamental skills at each stage of the journey.

    Args:
        state: Current campaign state

    Returns:
        Set of ability names that should always be enabled

    Example:
        >>> state = CampaignState(act=0)
        >>> abilities = get_base_abilities_for_act(state)
        >>> "JUMP" in abilities
        True
    """
    if state.act == 0:
        # Act 0: Lantern Heights - full starting kit
        return {"JUMP", "ATTACK", "WALL_JUMP", "DASH"}

    if state.act == 1:
        # Act 1: Veil Maiden fight - keep full kit for the boss
        return {"JUMP", "ATTACK", "WALL_JUMP", "DASH"}

    if state.act == 2 and state.is_hollowed:
        # Act 2: Hollow Depths - stripped down after Veil Maiden
        return {"JUMP", "WEAK_ATTACK"}

    if state.act == 3:
        # Act 3: Ember Monastery - rebuilding, basic combat restored
        return {"JUMP", "ATTACK"}

    if state.act == 4:
        # Act 4: Skyroad Summit - base kit plus wall jump
        return {"JUMP", "ATTACK", "WALL_JUMP"}

    # Default: just jump
    return {"JUMP"}


def get_scroll_for_act(act: int) -> Dict[str, str]:
    """
    Get the mapping of scroll IDs to ability names for a given act.

    Each act has specific scrolls that can be found, teaching new abilities.
    This defines what abilities can be learned in each act.

    Args:
        act: Act number (0-4)

    Returns:
        Dictionary mapping scroll_id -> ability_name

    Example:
        >>> scrolls = get_scroll_for_act(2)
        >>> scrolls["clarity_sense"]
        'SHADOW_STEP'
    """
    if act == 0:
        # Lantern Heights - no scrolls yet, abilities are base
        return {}

    if act == 1:
        # Veil Maiden fight - no scrolls
        return {}

    if act == 2:
        # Hollow Depths - rebuild movement and survival
        return {
            "clarity_sense": "SHADOW_STEP",
            "resilience_step": "DOUBLE_JUMP",
            "phase_drift": "WALL_CLING",
        }

    if act == 3:
        # Ember Monastery - advanced movement and combat
        return {
            "flame_dash": "DASH",
            "iron_form": "SLIDE",
            "sky_walker": "GLIDE",
        }

    if act == 4:
        # Skyroad Summit - mastery abilities
        return {
            "wind_step": "AIR_DODGE",
            "mountain_soul": "CROUCH_JUMP_BOOST",
        }

    return {}


def get_required_fragments_for_scroll(scroll_id: str) -> int:
    """
    Get the number of fragments required to complete a scroll.

    Args:
        scroll_id: Identifier for the scroll

    Returns:
        Number of fragments required (default: 3)
    """
    # Most scrolls need 3 fragments
    # Could make some rarer scrolls need 4-5 fragments
    rare_scrolls = {"clarity_sense", "flame_dash", "wind_step"}

    if scroll_id in rare_scrolls:
        return 4

    return 3
