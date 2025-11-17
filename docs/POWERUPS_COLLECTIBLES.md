# Power-ups and Collectibles Specification

## Power-ups (Temporary Buffs)

### Current Power-ups (Already Implemented)
1. **Speed Boost** ⚡
2. **Triple Jump** 🦘
3. **Coin Magnet** 🧲

### New Power-ups

### 4. Invincibility ⭐
- **Duration**: 8 seconds
- **Effect**: Immune to all damage, destroy enemies on contact
- **Visual**: Rainbow flashing aura, star particles
- **Spawn Rate**: 0.2%
- **Color**: Gold with white sparkles

### 5. Flight 🕊️
- **Duration**: 10 seconds
- **Effect**: Free flight with arrow keys, ignore gravity
- **Visual**: Glowing wings, feather particles
- **Spawn Rate**: 0.3%
- **Color**: White/light blue

### 6. Giant Mode 💪
- **Duration**: 12 seconds
- **Effect**: 2x size, 3x damage, break weak walls, immune to knockback
- **Visual**: Player grows, red power aura
- **Spawn Rate**: 0.25%
- **Color**: Red with orange glow

### 7. Ghost Mode 👻
- **Duration**: 7 seconds
- **Effect**: Pass through all terrain and enemies, semi-transparent
- **Limitation**: Cannot collect items, cannot attack
- **Visual**: 50% transparency, ethereal trail
- **Spawn Rate**: 0.35%
- **Color**: Cyan/white

### 8. Double Points 💰
- **Duration**: 15 seconds
- **Effect**: All score gains doubled (coins, enemies, collectibles)
- **Visual**: Gold aura, coin symbols orbiting player
- **Spawn Rate**: 0.4%
- **Color**: Gold

### 9. Shield 🛡️
- **Duration**: N/A (breaks after absorbing damage)
- **Effect**: Absorbs next 3 hits, visual indicator for remaining hits
- **Visual**: Blue energy shield sphere
- **Spawn Rate**: 0.5%
- **Color**: Blue/cyan

### 10. Reverse Gravity 🔄
- **Duration**: 10 seconds
- **Effect**: Gravity inverted, walk on ceilings
- **Visual**: Purple aura, upside-down orientation
- **Spawn Rate**: 0.2%
- **Color**: Purple

### 11. Super Jump 🚀
- **Duration**: 12 seconds
- **Effect**: Jump power increased 2.5x, reduced gravity
- **Visual**: Green energy legs, jump trails
- **Spawn Rate**: 0.4%
- **Color**: Green

### 12. Freeze Time ⏸️
- **Duration**: 5 seconds
- **Effect**: All enemies and hazards frozen, player moves normally
- **Visual**: Blue time particles, frozen enemies have ice effect
- **Spawn Rate**: 0.15%
- **Color**: Light blue/white

### 13. Multi-Hit 🌟
- **Duration**: 8 seconds
- **Effect**: Attacks hit 3 times, projectiles split into 3
- **Visual**: Orange aura, triple after-images
- **Spawn Rate**: 0.3%
- **Color**: Orange

### 14. Regeneration 💚
- **Duration**: 20 seconds
- **Effect**: Heal 1 HP every 4 seconds
- **Visual**: Green pulse effect, +1 HP floating numbers
- **Spawn Rate**: 0.5%
- **Color**: Green

### 15. Shadow Clone 👥
- **Duration**: 10 seconds
- **Effect**: Create 2 mirror clones that copy your movements
- **Clones**: 1 HP each, deal 1 damage, block projectiles
- **Visual**: Semi-transparent duplicates
- **Spawn Rate**: 0.25%
- **Color**: Dark purple

## Collectibles

### Currency Collectibles

#### 1. Coins 🪙 (Already Implemented)
- **Value**: 10 points (base)
- **Spawn Rate**: 4.5% (Medium difficulty)
- **Visual**: Gold spinning coin

#### 2. Gems 💎 (New)
- **Types**:
  - **Small Gem**: 50 points, 1.5% spawn
  - **Medium Gem**: 150 points, 0.8% spawn
  - **Large Gem**: 500 points, 0.3% spawn
- **Visual**:
  - Small: Green emerald
  - Medium: Blue sapphire
  - Large: Purple amethyst

#### 3. Treasure Chests 📦
- **Types**:
  - **Wooden Chest**: Common loot, 2% spawn
  - **Silver Chest**: Rare loot, 0.5% spawn
  - **Gold Chest**: Legendary loot, 0.1% spawn
- **Loot Tables**:
  - Wooden: 50-100 coins, common power-up
  - Silver: 200-400 coins, rare power-up, gem
  - Gold: 1000 coins, guaranteed ability orb, rare item
- **Visual**: Animated chest, glows when nearby

### Progression Collectibles

#### 4. Ability Orbs ✨ (New - Core System)
- **Purpose**: Unlock abilities permanently
- **Spawn Rate**: 0.3%
- **Visual**: Rainbow crystalline orb, pulsing glow
- **Persistence**: Tracked across all playthroughs
- **Value**: Priceless (cannot be traded)

#### 5. Key Fragments 🔑
- **Purpose**: Combine 3 fragments → 1 key
- **Keys**: Unlock secret areas, bonus levels, chests
- **Types**:
  - **Bronze Fragment**: Common areas (1% spawn)
  - **Silver Fragment**: Rare areas (0.4% spawn)
  - **Gold Fragment**: Legendary areas (0.1% spawn)
- **Visual**: Glowing fragment piece, different colors

#### 6. Scrolls 📜
- **Purpose**: Lore, story, hints, unlockables
- **Count**: 50 unique scrolls hidden in game
- **Spawn**: Specific hidden locations (not random)
- **Reward**: Reading all scrolls unlocks secret ending
- **Visual**: Rolled parchment with glow

#### 7. Fragments of Power 🔮
- **Purpose**: Collect full set (10 fragments) for permanent stat boost
- **Sets**:
  - **Strength Set**: +25% melee damage
  - **Agility Set**: +15% movement speed
  - **Vitality Set**: +2 max HP
  - **Fortune Set**: +50% loot drop rate
- **Spawn Rate**: 0.5% per fragment type
- **Visual**: Colored crystal shards

### Health/Life Collectibles (Already Implemented)

#### 8. Health Pickups ❤️
- **Effect**: Restore 1 HP
- **Spawn Rate**: 0.4%
- **Visual**: Red heart with pulse

#### 9. Life Pickups 💖
- **Effect**: +1 extra life
- **Spawn Rate**: 2 per level (guaranteed spawns)
- **Visual**: Pink heart with wings

### Special Collectibles

#### 10. Secret Stars ⭐
- **Purpose**: 100% completion tracking
- **Count**: 3 hidden per level
- **Locations**:
  - 1 in easy-to-miss area
  - 1 requiring advanced ability
  - 1 extremely hidden
- **Reward**: Unlock secret levels at milestones
- **Visual**: Golden star, sparkle effect

#### 11. Time Orbs ⏱️
- **Effect**: Add +10 seconds to Time Trial mode timer
- **Spawn**: Only in Time Trial mode
- **Spawn Rate**: 1-3 per level
- **Visual**: Clock face in orb

#### 12. Challenge Tokens 🎯
- **Purpose**: Currency for challenge shop
- **Earn**: Complete daily/weekly challenges
- **Shop**: Trade for cosmetics, power-ups, hints
- **Persistence**: Carried across save files
- **Visual**: Hexagonal coin with symbol

## Collectible Spawn System

### Priority Spawning
1. **Guaranteed**: Life Pickups (2), Boss Keys
2. **High Priority**: Ability Orbs (0.3%), Secret Stars (3)
3. **Medium Priority**: Gems, Key Fragments, Scrolls
4. **Low Priority**: Power-ups, Coins
5. **Conditional**: Time Orbs (mode-specific)

### Spawn Location Rules
- **Ground Level**: Coins, Gems, Health
- **Elevated**: Power-ups, Ability Orbs (rewards exploration)
- **Hidden**: Scrolls, Secret Stars, Gold Fragments
- **Enemy Drops**: Coins, Health, Power-ups
- **Chests**: Random loot from table

### Anti-Clutter System
- Maximum 100 active collectibles at once
- Oldest coins despawn first when limit reached
- Power-ups never despawn
- Ability Orbs never despawn (critical)

## Visual Design

### Size Hierarchy
1. **Tiny** (8x8): Coin
2. **Small** (12x12): Health, Gems (small)
3. **Medium** (16x16): Power-ups, Gems (medium)
4. **Large** (24x24): Ability Orbs, Gems (large)
5. **Huge** (32x32): Chests, Secret Stars

### Animation Effects
- **Coins**: Spin rotation
- **Gems**: Pulse glow + rotate
- **Power-ups**: Float bob + particle trail
- **Ability Orbs**: Orbit particles + pulse + glow
- **Chests**: Idle shake, lid opens on proximity
- **Scrolls**: Unfurl animation when collected

### Rarity Colors
- **Common**: White/Gray
- **Uncommon**: Green
- **Rare**: Blue
- **Epic**: Purple
- **Legendary**: Orange/Gold
- **Unique**: Rainbow

## Collection Feedback

### Visual Feedback
- **Coins**: Small pop, +10 text
- **Gems**: Flash, +value text, gem sparkle
- **Power-up**: Screen flash, power-up name display
- **Ability Orb**: Freeze frame, particle burst, persistent notification
- **Key/Fragment**: UI update, jingle sound
- **Health/Life**: Heal effect, HP bar update

### Audio Feedback
- **Coins**: Soft "clink"
- **Gems**: Crystal chime (pitch based on size)
- **Power-ups**: Power-up theme jingle
- **Ability Orbs**: Epic choir/bell sound
- **Chests**: Chest opening creak + treasure jingle
- **Health**: Soft healing tone

## Implementation Checklist

### Phase 1 - Foundation
- [x] Coins (existing)
- [x] Health Pickups (existing)
- [x] Life Pickups (existing)
- [x] Power-ups: Speed, Triple, Magnet (existing)
- [ ] Ability Orbs (NEW SYSTEM)

### Phase 2 - Expansion
- [ ] Gems (3 sizes)
- [ ] Key Fragments
- [ ] Power-ups: Invincibility, Shield, Double Points
- [ ] Treasure Chests (3 types)

### Phase 3 - Advanced
- [ ] Fragments of Power (4 sets)
- [ ] Secret Stars
- [ ] Scrolls
- [ ] Power-ups: Flight, Giant, Ghost, Reverse Gravity

### Phase 4 - Polish
- [ ] Challenge Tokens
- [ ] Time Orbs
- [ ] Power-ups: Super Jump, Freeze Time, Multi-Hit, Regen, Shadow Clone
- [ ] Collection statistics UI
