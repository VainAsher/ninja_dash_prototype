"""
Equipment System for Hollowed Ninja

Defines equipment tiers, slots, and stat bonuses for campaign progression.

Equipment Structure:
- 4 Tiers: Basic (1), Forged (2), Blessed (3), Hollowed (4)
- 4 Slots: Weapon, Armor, Boots, Charm
- Each piece provides stat bonuses

Stats:
- HP: Health Points (determines max health)
- MP: Magic Points (for special abilities)
- STM: Stamina (for dodges/dashes)
- STG: Strength (damage multiplier)
- DEF: Defense (damage reduction)
- SPD: Speed (movement speed multiplier)
- DEXT: Dexterity (attack speed, precision)
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Stats:
    """Player stats that affect gameplay."""
    hp: int = 100      # Health Points
    mp: int = 50       # Magic Points
    stm: int = 50      # Stamina
    stg: int = 10      # Strength (damage)
    def_: int = 5      # Defense (damage reduction)
    spd: float = 1.0   # Speed multiplier
    dext: int = 10     # Dexterity (attack speed)

    def __add__(self, other: 'Stats') -> 'Stats':
        """Add two stat objects together (for base + equipment)."""
        return Stats(
            hp=self.hp + other.hp,
            mp=self.mp + other.mp,
            stm=self.stm + other.stm,
            stg=self.stg + other.stg,
            def_=self.def_ + other.def_,
            spd=self.spd + other.spd - 1.0,  # Speed is multiplicative
            dext=self.dext + other.dext
        )

    def copy(self) -> 'Stats':
        """Create a copy of this Stats object."""
        return Stats(
            hp=self.hp,
            mp=self.mp,
            stm=self.stm,
            stg=self.stg,
            def_=self.def_,
            spd=self.spd,
            dext=self.dext
        )


# Equipment slot types
SLOT_WEAPON = "weapon"
SLOT_ARMOR = "armor"
SLOT_BOOTS = "boots"
SLOT_CHARM = "charm"

ALL_SLOTS = [SLOT_WEAPON, SLOT_ARMOR, SLOT_BOOTS, SLOT_CHARM]

# Equipment tier names
TIER_BASIC = 1
TIER_FORGED = 2
TIER_BLESSED = 3
TIER_HOLLOWED = 4

TIER_NAMES = {
    1: "Basic",
    2: "Forged",
    3: "Blessed",
    4: "Hollowed"
}


@dataclass
class EquipmentPiece:
    """A single piece of equipment."""
    name: str
    slot: str
    tier: int
    stats: Stats
    description: str
    cost: int  # Cost in fragments or currency


# ============================================================================
# EQUIPMENT DEFINITIONS
# ============================================================================

# WEAPONS - Focus on STG and DEXT
WEAPONS = {
    # Tier 1 - Basic
    "training_blade": EquipmentPiece(
        name="Training Blade",
        slot=SLOT_WEAPON,
        tier=TIER_BASIC,
        stats=Stats(stg=5, dext=3),
        description="A well-worn practice sword.",
        cost=0
    ),
    # Tier 2 - Forged
    "forged_katana": EquipmentPiece(
        name="Forged Katana",
        slot=SLOT_WEAPON,
        tier=TIER_FORGED,
        stats=Stats(stg=12, dext=8),
        description="Monastery-forged blade of tempered steel.",
        cost=100
    ),
    # Tier 3 - Blessed
    "blessed_edge": EquipmentPiece(
        name="Blessed Edge",
        slot=SLOT_WEAPON,
        tier=TIER_BLESSED,
        stats=Stats(stg=20, dext=15, mp=10),
        description="Imbued with ancient monk blessings.",
        cost=250
    ),
    # Tier 4 - Hollowed
    "void_fang": EquipmentPiece(
        name="Void Fang",
        slot=SLOT_WEAPON,
        tier=TIER_HOLLOWED,
        stats=Stats(stg=35, dext=25, mp=20),
        description="Forged from the depths of the Hollow itself.",
        cost=500
    ),
}

# ARMOR - Focus on HP and DEF
ARMOR = {
    # Tier 1 - Basic
    "cloth_gi": EquipmentPiece(
        name="Cloth Gi",
        slot=SLOT_ARMOR,
        tier=TIER_BASIC,
        stats=Stats(hp=20, def_=3),
        description="Simple training robes.",
        cost=0
    ),
    # Tier 2 - Forged
    "iron_vest": EquipmentPiece(
        name="Iron Vest",
        slot=SLOT_ARMOR,
        tier=TIER_FORGED,
        stats=Stats(hp=50, def_=10),
        description="Reinforced chest plate with leather padding.",
        cost=100
    ),
    # Tier 3 - Blessed
    "blessed_plate": EquipmentPiece(
        name="Blessed Plate",
        slot=SLOT_ARMOR,
        tier=TIER_BLESSED,
        stats=Stats(hp=100, def_=20),
        description="Sacred armor blessed by the monastery elders.",
        cost=250
    ),
    # Tier 4 - Hollowed
    "hollow_carapace": EquipmentPiece(
        name="Hollow Carapace",
        slot=SLOT_ARMOR,
        tier=TIER_HOLLOWED,
        stats=Stats(hp=180, def_=35, stm=20),
        description="Living armor born from the Hollow's essence.",
        cost=500
    ),
}

# BOOTS - Focus on SPD and STM
BOOTS = {
    # Tier 1 - Basic
    "worn_sandals": EquipmentPiece(
        name="Worn Sandals",
        slot=SLOT_BOOTS,
        tier=TIER_BASIC,
        stats=Stats(spd=1.0, stm=5),
        description="Well-traveled but reliable footwear.",
        cost=0
    ),
    # Tier 2 - Forged
    "steel_greaves": EquipmentPiece(
        name="Steel Greaves",
        slot=SLOT_BOOTS,
        tier=TIER_FORGED,
        stats=Stats(spd=1.15, stm=15),
        description="Monastery-crafted boots with reinforced soles.",
        cost=100
    ),
    # Tier 3 - Blessed
    "blessed_stride": EquipmentPiece(
        name="Blessed Stride",
        slot=SLOT_BOOTS,
        tier=TIER_BLESSED,
        stats=Stats(spd=1.30, stm=30, dext=5),
        description="Enchanted boots that lighten your steps.",
        cost=250
    ),
    # Tier 4 - Hollowed
    "void_walkers": EquipmentPiece(
        name="Void Walkers",
        slot=SLOT_BOOTS,
        tier=TIER_HOLLOWED,
        stats=Stats(spd=1.50, stm=50, dext=10),
        description="Boots woven from shadow itself.",
        cost=500
    ),
}

# CHARMS - Balanced utility bonuses
CHARMS = {
    # Tier 1 - Basic
    "wooden_talisman": EquipmentPiece(
        name="Wooden Talisman",
        slot=SLOT_CHARM,
        tier=TIER_BASIC,
        stats=Stats(hp=10, mp=10),
        description="Simple carved charm from Lantern Heights.",
        cost=0
    ),
    # Tier 2 - Forged
    "ember_pendant": EquipmentPiece(
        name="Ember Pendant",
        slot=SLOT_CHARM,
        tier=TIER_FORGED,
        stats=Stats(hp=20, mp=20, stm=10),
        description="Warm pendant from the monastery forge.",
        cost=100
    ),
    # Tier 3 - Blessed
    "sacred_amulet": EquipmentPiece(
        name="Sacred Amulet",
        slot=SLOT_CHARM,
        tier=TIER_BLESSED,
        stats=Stats(hp=40, mp=40, stm=20, def_=5),
        description="Ancient amulet blessed with protective wards.",
        cost=250
    ),
    # Tier 4 - Hollowed
    "heart_of_void": EquipmentPiece(
        name="Heart of Void",
        slot=SLOT_CHARM,
        tier=TIER_HOLLOWED,
        stats=Stats(hp=70, mp=70, stm=35, stg=10, def_=10, dext=5),
        description="Crystallized essence of the Hollow's heart.",
        cost=500
    ),
}

# Combine all equipment
ALL_EQUIPMENT = {**WEAPONS, **ARMOR, **BOOTS, **CHARMS}


def get_equipment_for_tier(tier: int) -> Dict[str, EquipmentPiece]:
    """Get all equipment available at a given tier."""
    return {
        item_id: item
        for item_id, item in ALL_EQUIPMENT.items()
        if item.tier == tier
    }


def get_equipment_for_slot(slot: str) -> Dict[str, EquipmentPiece]:
    """Get all equipment for a specific slot."""
    return {
        item_id: item
        for item_id, item in ALL_EQUIPMENT.items()
        if item.slot == slot
    }


def get_base_stats_for_act(act: int) -> Stats:
    """Get base stats for a given act (before equipment bonuses)."""
    if act == 0:
        # Act 0: Lantern Heights - starting stats
        return Stats(hp=100, mp=50, stm=50, stg=10, def_=5, spd=1.0, dext=10)

    if act == 1:
        # Act 1: Veil Maiden - same as Act 0
        return Stats(hp=100, mp=50, stm=50, stg=10, def_=5, spd=1.0, dext=10)

    if act == 2:
        # Act 2: Hollow Depths - weakened after hollowing
        return Stats(hp=80, mp=30, stm=30, stg=5, def_=3, spd=0.9, dext=5)

    if act == 3:
        # Act 3: Ember Monastery - recovering strength
        return Stats(hp=120, mp=60, stm=60, stg=12, def_=8, spd=1.05, dext=12)

    if act == 4:
        # Act 4: Skyroad Summit - near peak power
        return Stats(hp=150, mp=80, stm=80, stg=15, def_=10, spd=1.1, dext=15)

    # Default
    return Stats()
