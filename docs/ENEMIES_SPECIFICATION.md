# Enemies Specification

## Enemy System Architecture

### Base Enemy Class
```python
class Enemy:
    - health: int
    - damage: int
    - speed: float
    - ai_type: str
    - loot_table: dict
    - vulnerable_to: list[str]
    - resistances: list[str]
    - behaviors: list[Behavior]
```

## Basic Enemies (Tier 1)

### 1. Patroller (Ground Walker)
- **HP**: 3
- **Damage**: 1
- **Speed**: 2.0
- **AI**: Walk back and forth on platform, turn at edges/walls
- **Attack**: Contact damage
- **Loot**: 50% coin (10 points), 20% health
- **Visual**: Small robot or slime
- **Spawn Weight**: 40%

### 2. Jumper (Hopper)
- **HP**: 2
- **Damage**: 1
- **Speed**: 3.0
- **AI**: Jump periodically, leap toward player when within 8 tiles
- **Attack**: Contact damage + leap attack
- **Loot**: 40% coin (15 points), 10% health
- **Visual**: Spring creature or bouncing enemy
- **Spawn Weight**: 25%

### 3. Flyer (Aerial)
- **HP**: 2
- **Damage**: 1
- **Speed**: 2.5
- **AI**: Fly in sine wave pattern, dive at player
- **Attack**: Contact damage + dive bomb (2 damage)
- **Loot**: 45% coin (20 points), 15% power-up fragment
- **Visual**: Drone or flying creature
- **Spawn Weight**: 20%

### 4. Spiker (Stationary Hazard)
- **HP**: 5
- **Damage**: 2
- **Speed**: 0
- **AI**: Stationary, shoots spike projectiles every 3s
- **Attack**: Ranged spike (5 tile range)
- **Loot**: 60% coin (30 points), 25% health
- **Visual**: Turret or spiky plant
- **Spawn Weight**: 15%

## Intermediate Enemies (Tier 2)

### 5. Charger (Rusher)
- **HP**: 4
- **Damage**: 2
- **Speed**: 6.0 (when charging)
- **AI**: Detect player in line of sight, charge in straight line
- **Attack**: Charge attack (stuns on hit), contact damage
- **Cooldown**: 4s between charges
- **Loot**: 50% coin (40 points), 15% health, 10% power-up
- **Spawn Weight**: 15%

### 6. Shooter (Ranged Attacker)
- **HP**: 3
- **Damage**: 1 (projectile)
- **Speed**: 1.5
- **AI**: Keep distance from player, shoot when in range
- **Attack**: Projectile (8 tile range, 1s fire rate)
- **Loot**: 45% coin (35 points), 20% ammo/power-up
- **Spawn Weight**: 20%

### 7. Shielded Guard
- **HP**: 6
- **Damage**: 1
- **Speed**: 1.5
- **AI**: Walk patrol, block frontal attacks with shield
- **Attack**: Contact damage, shield bash (3s cooldown, 2 damage)
- **Weakness**: Attacks from behind bypass shield
- **Loot**: 40% coin (50 points), 25% health, 15% key fragment
- **Spawn Weight**: 10%

### 8. Teleporter (Blinker)
- **HP**: 3
- **Damage**: 1
- **Speed**: 2.0
- **AI**: Teleport away when player gets close (< 4 tiles)
- **Attack**: Contact damage, teleport behind player
- **Cooldown**: 5s between teleports
- **Loot**: 35% coin (45 points), 30% power-up, 5% ability orb
- **Spawn Weight**: 8%

## Advanced Enemies (Tier 3)

### 9. Tank (Heavy Unit)
- **HP**: 12
- **Damage**: 3
- **Speed**: 1.0
- **AI**: Slow but relentless pursuit, shockwave attack
- **Attack**: Heavy punch (3 damage), ground slam (4 damage, 5 tile radius)
- **Armor**: Takes 50% reduced damage from melee
- **Loot**: 70% coin (100 points), 30% health, 20% rare item
- **Spawn Weight**: 5%

### 10. Spawner (Summoner)
- **HP**: 8
- **Damage**: 0
- **Speed**: 0
- **AI**: Stationary, spawns Patrollers every 10s (max 4 active)
- **Attack**: None directly, summons add 1 HP
- **Priority**: High (should be killed first)
- **Loot**: 80% coin (80 points), 40% power-up, 10% key
- **Spawn Weight**: 5%

### 11. Elite Variant (Enhanced)
- **HP**: 2x base enemy HP
- **Damage**: 1.5x base damage
- **Speed**: 1.2x base speed
- **AI**: Same as base + one special ability
- **Visual**: Glowing aura, larger size, different color
- **Loot**: 2x base loot rates + guaranteed rare
- **Spawn Weight**: 3% (replaces normal enemy)
- **Special Abilities**:
  - **Elite Patroller**: Dash attack
  - **Elite Jumper**: Double jump
  - **Elite Flyer**: Split into 2 on death
  - **Elite Shooter**: Burst fire (3 shots)

### 12. Exploder (Suicide Bomber)
- **HP**: 2
- **Damage**: 4 (explosion)
- **Speed**: 3.5
- **AI**: Chase player, explode when within 2 tiles or on death
- **Attack**: Explosion (3 tile radius)
- **Warning**: Beeps and flashes red before exploding
- **Loot**: None (destroyed in explosion)
- **Spawn Weight**: 7%

## Boss Enemies (Unique)

### Boss 1: "The Crusher" (Level 5)
- **HP**: 50
- **Phases**: 2
- **Phase 1**:
  - Slow ground pound attacks
  - Summon 2 Patrollers
- **Phase 2** (< 50% HP):
  - Faster attacks
  - Jump smash attacks
  - Shockwave rings
- **Loot**: Guaranteed key, 500 coins, 5 ability orbs

### Boss 2: "Storm Drone" (Level 10)
- **HP**: 75
- **Phases**: 3
- **Phase 1**:
  - Fly around, shoot single projectiles
- **Phase 2** (< 66% HP):
  - Spiral projectile pattern
  - Summon 3 Flyers
- **Phase 3** (< 33% HP):
  - Dive bomb attacks
  - Lightning strikes (telegraphed)
- **Loot**: Guaranteed rare item, 750 coins, 7 ability orbs

### Boss 3: "Shadow Beast" (Level 15)
- **HP**: 100
- **Phases**: 4
- **Mechanics**:
  - Teleport frequently
  - Clone copies (fake, 1 HP)
  - Shadow Step invulnerability periods
- **Loot**: Guaranteed epic item, 1000 coins, 10 ability orbs

### Boss 4: "The Gauntlet" (Level 20)
- **Type**: Boss rush - fight 3 mini-bosses
- **HP**: 40 each
- **Mechanics**: Each has unique pattern
- **Loot**: Guaranteed legendary item, 1500 coins, 12 ability orbs

### Boss 5: "Final Guardian" (Level 25+)
- **HP**: 200
- **Phases**: 5
- **Mechanics**:
  - Uses all enemy abilities
  - Environmental hazards activated
  - Multiple attack patterns per phase
- **Loot**: Campaign completion reward, 2500 coins, 15 ability orbs

## AI Behavior Patterns

### Detection System
- **Vision Cone**: 12 tiles forward, 90° cone
- **Alert State**: Changes to aggressive when player detected
- **Memory**: Chases last known position for 5s
- **Return**: Returns to patrol after losing player

### Difficulty Scaling
| Difficulty | HP Mult | Damage Mult | Speed Mult | Spawn Rate |
|------------|---------|-------------|------------|------------|
| Easy       | 0.75x   | 0.75x       | 0.9x       | 0.7x       |
| Medium     | 1.0x    | 1.0x        | 1.0x       | 1.0x       |
| Hard       | 1.5x    | 1.25x       | 1.1x       | 1.3x       |
| Expert     | 2.0x    | 1.5x        | 1.2x       | 1.5x       |

## Loot Drop System

### Drop Tables
```json
{
  "common_enemy": {
    "coins": {"chance": 0.5, "amount": [10, 30]},
    "health": {"chance": 0.2, "amount": 1},
    "power_up": {"chance": 0.05},
    "nothing": {"chance": 0.25}
  },
  "elite_enemy": {
    "coins": {"chance": 0.8, "amount": [50, 100]},
    "health": {"chance": 0.3, "amount": 1},
    "power_up": {"chance": 0.2},
    "key_fragment": {"chance": 0.1},
    "ability_orb": {"chance": 0.05}
  },
  "boss": {
    "coins": {"chance": 1.0, "amount": [500, 1000]},
    "rare_item": {"chance": 1.0},
    "ability_orbs": {"chance": 1.0, "amount": [5, 15]},
    "key": {"chance": 1.0}
  }
}
```

## Enemy Spawning System

### Spawn Rules
1. Minimum distance from player: 10 tiles
2. Not in player's view cone
3. Valid ground or air position
4. Maximum enemies per room: 8
5. Budget system: Total enemy "cost" ≤ room budget

### Enemy Costs
- Basic (Patroller, Jumper): 1 point
- Intermediate (Charger, Shooter): 2 points
- Advanced (Tank, Elite): 4 points
- Spawner: 3 points

### Room Budget
- Small room: 6 points
- Medium room: 10 points
- Large room: 15 points

## Status Effects Enemies Can Apply

- **Slow**: Shooter's special ammo (30% chance)
- **Poison**: Spiker's toxic variant (damage over time)
- **Stun**: Charger's charge attack (0.5s stun)
- **Burn**: Exploder's explosion (2s DOT)
- **Curse**: Shadow Beast boss (prevents healing)

## Implementation Priority

### Phase 1 - Basic Combat
1. Patroller
2. Jumper
3. Flyer
4. Basic loot drops

### Phase 2 - Ranged & Special
5. Spiker
6. Shooter
7. Charger
8. Loot table system

### Phase 3 - Advanced
9. Tank
10. Spawner
11. Elite variants
12. Exploder

### Phase 4 - Bosses
13. Boss 1-3
14. Boss 4-5
15. Boss-specific mechanics
