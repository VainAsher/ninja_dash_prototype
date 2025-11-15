# Ability Unlock System Design

## Overview
The new ability unlock system replaces the previous "unlock after each level" mechanic with a collectible-based progression system that encourages replayability.

## Core Mechanic

### Ability Orbs (Skill Shards)
- **Spawn Rate**: 0.3% per valid spawn location in each level
- **Persistence**: Total collected across ALL playthroughs (not per run)
- **Visual**: Glowing crystalline orb with swirling energy effect
- **Collection**: Automatically picked up on contact, cannot be lost

### Unlock Requirements

Each ability requires a specific number of Ability Orbs to unlock:

| Ability | Orbs Required | Tier |
|---------|---------------|------|
| Double Jump | 5 | Basic |
| Dash | 8 | Basic |
| Wall Jump | 12 | Basic |
| Slide | 15 | Intermediate |
| Wall Cling | 18 | Intermediate |
| Shadow Step | 25 | Intermediate |
| Air Dodge | 30 | Advanced |
| Glide | 35 | Advanced |
| Grappling Hook | 40 | Advanced |
| Ground Pound | 45 | Advanced |
| Double Dash | 50 | Expert |
| Time Slow | 60 | Expert |
| Teleport | 75 | Expert |
| Stomp Jump | 90 | Master |

## Expected Play Patterns

### Math
- **Average spawn per level**: ~0.3% of spawn locations
- **Typical level spawn locations**: ~100-200 valid spots
- **Expected orbs per level**: 0-1 (sometimes none, occasionally 2)
- **To unlock all abilities**: 528 orbs total
- **Estimated playthroughs**: 300-500+ level completions

### Player Experience
1. Players must replay levels multiple times
2. Encourages exploration (more spawn points = more chances)
3. RNG provides excitement when orb spawns
4. Tangible progression even on failed runs
5. Long-term goals for dedicated players

## Progression Tracking

### Save Data Structure
```json
{
  "ability_orbs": {
    "total_collected": 47,
    "orbs_per_session": [3, 2, 5, 1, ...],
    "last_collection_timestamp": "2025-11-15T12:34:56"
  },
  "unlocked_abilities": [
    "DOUBLE_JUMP",
    "DASH",
    "WALL_JUMP",
    "SLIDE"
  ],
  "unlock_history": {
    "DOUBLE_JUMP": "2025-11-10T10:23:45",
    "DASH": "2025-11-12T14:12:33"
  }
}
```

### UI Display
- Main menu: "Ability Orbs: 47/528 (Next unlock: Wall Cling at 18)"
- In-game HUD: Small orb counter in corner
- Pause menu: Full ability tree showing locked/unlocked status
- Collection notification: Screen flash + sound + "+1 Ability Orb!" message

## Spawn System

### Level Generation Integration
```python
def generate_ability_orb_spawns(world, rng, spawn_rate=0.003):
    """
    Generate rare ability orb spawn points.

    Args:
        world: 2D level array
        rng: Random number generator
        spawn_rate: Probability per valid location (default 0.3%)

    Returns:
        List of ability orb spawn rectangles
    """
    orbs = []
    valid_locations = find_valid_spawn_locations(world)

    for location in valid_locations:
        if rng.random() < spawn_rate:
            orbs.append(create_ability_orb(location))

    return orbs
```

### Valid Spawn Locations
- Must be in open air (not in walls)
- Must have floor below (within 2 tiles)
- Not too close to player spawn (minimum 5 tiles away)
- Not overlapping with other collectibles
- Not in hazard zones
- Prefer hidden/hard-to-reach areas (weight bonus)

## Visual Feedback

### Ability Orb Appearance
- **Color**: Shifting rainbow gradient (purple → blue → cyan)
- **Size**: 24x24 pixels (1.5x larger than regular coins)
- **Animation**: Gentle pulsing + rotation
- **Particle effect**: Sparkles orbiting the orb
- **Glow**: Soft radial glow visible through walls (subtle hint)

### Collection Feedback
1. Screen flash (white)
2. Freeze frame (0.1 seconds)
3. Sound effect (crystalline chime)
4. Particle burst (rainbow sparkles)
5. UI notification: "+1 Ability Orb! (47/528)"
6. Progress bar update in pause menu

## Balancing Considerations

### Preventing Frustration
- **Pity System**: After 50 levels without an orb, spawn rate increases to 1% for next 10 levels
- **Guaranteed Spawn**: Every 25th level guarantees at least 1 orb
- **Bonus Orbs**: Boss defeats award 3-5 orbs
- **Quest Rewards**: Some quests grant orbs directly

### Encouraging Variety
- Different difficulty levels have same spawn rate
- Longer/harder levels have more spawn locations (naturally more orbs)
- Secret areas have higher spawn rate (0.5% vs 0.3%)

## Migration from Old System

Players who already unlocked abilities in the old system:
1. Grant equivalent orbs retroactively based on level reached
2. Formula: `orbs_granted = level_reached * 2`
3. Maintain unlocked abilities
4. Add bonus "legacy player" orbs (+10)

## Future Expansion

- **Ability Orb Types**: Different colored orbs for specific ability trees
- **Trading System**: Exchange excess orbs for power-ups
- **Prestige System**: Reset progression for cosmetic rewards
- **Challenges**: "Collect 5 orbs in one run" achievements
