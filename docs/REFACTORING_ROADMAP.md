# Ninja Dash - Incremental Refactoring & Enhancement Roadmap

**Created**: 2025-11-15
**Purpose**: Small, incremental changes to align codebase with documented goals while improving modularity and maintainability

---

## Overview

This roadmap outlines **50+ small, focused tasks** organized into phases. Each task is designed to be:
- **Small**: 30 minutes to 2 hours of work
- **Incremental**: Can be tested independently
- **Non-breaking**: Maintains existing functionality
- **Modular**: Improves code organization

---

## Phase 1: Code Organization & Modularity (Week 1-2)

### 1.1 Split Level Generation Module
**Current State**: `level_gen.py` is 618 lines with multiple responsibilities
**Goal**: Break into focused modules

**Tasks**:
1. **Create `level_gen/` package structure** (30 min)
   - Create `level_gen/__init__.py`
   - Move constants to `level_gen/constants.py`
   - Export main function from `__init__.py`

2. **Extract maze generation** (1 hour)
   - Create `level_gen/maze_generator.py`
   - Move `generate_macro_maze()` and related functions
   - Add unit tests for maze connectivity

3. **Extract decoration system** (1 hour)
   - Create `level_gen/decorations.py`
   - Move `add_pillars()`, `add_holes()`, platform generation
   - Keep decoration logic together

4. **Extract entity placement** (1.5 hours)
   - Create `level_gen/entity_placer.py`
   - Move coin, health, life, powerup, orb spawning
   - Centralize spawn logic

5. **Extract ability features** (1 hour)
   - Create `level_gen/ability_features.py`
   - Move ability-aware coin patterns
   - Move ability subroom generation

6. **Update imports throughout codebase** (30 min)
   - Replace `from level_gen import ...`
   - Test all imports work correctly

**Benefits**: Easier to understand, test, and extend each system independently

---

### 1.2 Refactor Player Module
**Current State**: `player.py` is 684 lines with all ability logic mixed
**Goal**: Separate player physics from ability implementations

**Tasks**:
1. **Create `abilities/` package** (30 min)
   - Create `abilities/__init__.py`
   - Define `Ability` base class with `update()`, `can_use()`, `use()`

2. **Extract movement abilities** (2 hours)
   - Create `abilities/movement.py`
   - Classes: `DoubleJump`, `Dash`, `WallJump`, `Slide`
   - Each has own state and logic

3. **Extract advanced abilities** (2 hours)
   - Create `abilities/advanced.py`
   - Classes: `WallCling`, `ShadowStep`, `AirDodge`, `Glide`
   - Self-contained with timers and cooldowns

4. **Refactor Player to use ability system** (2 hours)
   - Replace inline ability logic with ability instances
   - `self.abilities = {'dash': Dash(), 'double_jump': DoubleJump(), ...}`
   - Call `ability.update(player_state)` each frame

5. **Extract powerup system** (1 hour)
   - Create `powerups.py` module
   - Classes: `SpeedBoost`, `TripleJump`, `CoinMagnet`
   - Player holds list of active powerups

6. **Add ability unit tests** (1.5 hours)
   - Test cooldown logic
   - Test state transitions
   - Test resource consumption (charges, stamina)

**Benefits**: Each ability is testable, new abilities easy to add, player.py reduced to ~300 lines

---

### 1.3 Organize State Files
**Current State**: 13 state files in flat `states/` directory
**Goal**: Group related states

**Tasks**:
1. **Create state subdirectories** (20 min)
   - `states/gameplay/` - play, pause, gameover
   - `states/menus/` - menu, settings, help, controls_viewer
   - `states/meta/` - unlocks, highscores, name_entry, seed_entry

2. **Move files to subdirectories** (30 min)
   - Reorganize state modules
   - Update `__init__.py` imports

3. **Update Game class state registry** (20 min)
   - Fix import paths in `core/game.py`
   - Test all state transitions

**Benefits**: Clearer organization, easier to find related states

---

## Phase 2: Documentation & Code Quality (Week 2-3)

### 2.1 Add Missing Docstrings
**Current State**: Some functions lack detailed documentation
**Goal**: Complete docstring coverage

**Tasks**:
1. **Document level_gen modules** (1 hour)
   - Add module-level docstrings explaining each system
   - Document all public functions with examples

2. **Document player abilities** (1 hour)
   - Add docstrings to all ability methods
   - Document state machine transitions

3. **Document entities** (30 min)
   - Add entity lifecycle documentation
   - Document collision behavior

4. **Add architecture documentation** (1 hour)
   - Create `docs/ARCHITECTURE.md`
   - Diagram state machine, entity system, ability system

**Benefits**: Easier onboarding, better IDE support

---

### 2.2 Add Unit Tests
**Current State**: No test files
**Goal**: Cover critical systems

**Tasks**:
1. **Set up test infrastructure** (1 hour)
   - Create `tests/` directory
   - Add `pytest` to requirements
   - Create `conftest.py` with fixtures

2. **Test physics calculations** (2 hours)
   - Test jump trajectories
   - Test collision detection
   - Test movement acceleration

3. **Test unlock system** (1.5 hours)
   - Test orb collection tracking
   - Test auto-unlock thresholds
   - Test save/load persistence

4. **Test maze generation** (2 hours)
   - Test connectivity (start to exit)
   - Test room placement
   - Test seed determinism

5. **Test ability cooldowns** (1.5 hours)
   - Test dash cooldown timing
   - Test shadow step charges
   - Test air dodge uses

**Benefits**: Catch regressions, enable confident refactoring

---

## Phase 3: Missing Features from Docs (Week 3-5)

### 3.1 Integrate Controls Viewer
**Current State**: ControlsViewer exists but not registered
**Goal**: Add to pause menu and help menu

**Tasks**:
1. **Register ControlsViewer state** (15 min)
   - Add to `core/game.py` state registry
   - File: `core/game.py:60`

2. **Add to pause menu** (30 min)
   - Add "Controls" button in `states/pause.py`
   - Transition to controls_viewer state

3. **Add to help menu** (30 min)
   - Add "View Controls" button in `states/help_state.py`
   - Link to controls viewer

4. **Test keyboard navigation** (30 min)
   - Verify arrow key scrolling
   - Test back button to return

**Benefits**: Users can view/customize controls in-game

---

### 3.2 Implement Missing Collectibles
**Current State**: Only coins, health, lives, 3 powerups exist
**Goal**: Add gems, key fragments, treasure chests (Phase 2 from POWERUPS_COLLECTIBLES.md)

**Tasks**:
1. **Create Gem entity** (1 hour)
   - File: `entities/collectibles.py`
   - 3 sizes: Small (50pts), Medium (150pts), Large (500pts)
   - Different colors and pulse animations

2. **Add gem spawning to level_gen** (1 hour)
   - File: `level_gen/entity_placer.py` (after refactor)
   - Spawn rates: 1.5%, 0.8%, 0.3%
   - Prefer elevated/hidden positions

3. **Create KeyFragment entity** (1.5 hours)
   - File: `entities/collectibles.py`
   - Track in player inventory
   - 3 fragments = 1 key (combine automatically)

4. **Add key fragment spawning** (45 min)
   - Bronze (1%), Silver (0.4%), Gold (0.1%)
   - Drop from tougher platforming sections

5. **Create TreasureChest entity** (2 hours)
   - File: `entities/treasure_chest.py`
   - 3 types: Wooden, Silver, Gold
   - Loot tables with random rewards
   - Opening animation

6. **Add chest spawning** (1 hour)
   - Spawn in hidden alcoves
   - Require specific abilities to reach
   - Rates: 2%, 0.5%, 0.1%

7. **Update HUD to show keys/fragments** (1 hour)
   - File: `ui.py`
   - Add key counter to top-right
   - Show fragment progress (e.g., "2/3")

**Benefits**: Adds depth and collection goals beyond orbs

---

### 3.3 Add Missing Power-ups (Priority Set)
**Current State**: 3/15 power-ups implemented
**Goal**: Add 4 high-priority power-ups from docs

**Tasks**:
1. **Implement Invincibility power-up** (1.5 hours)
   - 8 second duration
   - Immune to damage, destroy enemies on contact
   - Rainbow flashing aura effect

2. **Implement Shield power-up** (1.5 hours)
   - Absorbs next 3 hits
   - Visual shield sphere around player
   - Break effect when depleted

3. **Implement Double Points power-up** (1 hour)
   - 15 second duration
   - 2x multiplier on all score gains
   - Gold aura with coin symbols

4. **Implement Flight power-up** (2 hours)
   - 10 second duration
   - Free flight with directional control
   - Wing visual effect

5. **Add power-up visual effects** (2 hours)
   - Particle systems for each power-up
   - Screen border glow for active power-ups
   - Timer countdown UI

6. **Update level generation for new power-ups** (30 min)
   - Add to spawn tables with proper weights
   - Adjust total spawn rates

**Benefits**: More gameplay variety, better ability testing opportunities

---

### 3.4 Create README.md
**Current State**: No README in root directory
**Goal**: Professional project documentation

**Tasks**:
1. **Create comprehensive README** (1.5 hours)
   - Project overview and screenshots (use ASCII art)
   - Features list (abilities, progression, procedural generation)
   - Installation instructions
   - How to play (controls, objectives)
   - Architecture overview
   - Contributing guidelines
   - Link to docs/ folder

**Benefits**: Better project presentation, easier onboarding

---

## Phase 4: Enemy System Foundation (Week 5-7)

### 4.1 Create Enemy Base Infrastructure
**Current State**: No enemies implemented
**Goal**: Build foundation for combat system

**Tasks**:
1. **Create enemy base class** (2 hours)
   - File: `entities/enemy.py`
   - Health, damage, speed properties
   - AI state machine (idle, patrol, chase, attack)
   - Collision and damage dealing

2. **Create enemy manager** (1.5 hours)
   - File: `entities/enemy_manager.py`
   - Spawn, update, remove enemies
   - Track active enemies per room

3. **Implement player melee attack** (2 hours)
   - File: `abilities/combat.py`
   - J key for basic attack
   - Attack hitbox and animation
   - Damage dealing to enemies

4. **Add health bars for enemies** (1 hour)
   - Small bar above enemy
   - Color-coded by health percentage

5. **Implement loot drop system** (1.5 hours)
   - File: `entities/loot_drops.py`
   - Drop tables from ENEMIES_SPECIFICATION.md
   - Spawn coins/health on enemy death

**Benefits**: Foundation for all enemy types

---

### 4.2 Implement First Enemy (Patroller)
**Current State**: No enemies
**Goal**: Fully functional basic enemy

**Tasks**:
1. **Create Patroller enemy class** (2 hours)
   - Extends Enemy base
   - Walk back and forth on platforms
   - Turn at edges and walls
   - 3 HP, 1 damage, 2.0 speed

2. **Add to level generation** (1 hour)
   - Spawn on platforms (40% weight)
   - Avoid spawning near player start
   - Respect room budget system

3. **Test combat loop** (1 hour)
   - Player can attack and kill enemy
   - Enemy damages player on contact
   - Loot drops correctly

4. **Add death animation** (1 hour)
   - Fade out effect
   - Particle burst
   - Sound effect placeholder

**Benefits**: Validates entire enemy system, playable combat

---

### 4.3 Add More Basic Enemies
**Current State**: Only Patroller
**Goal**: 3 enemy variety

**Tasks**:
1. **Implement Jumper enemy** (2 hours)
   - Hop periodically
   - Leap toward player when close
   - 2 HP, 1 damage, 3.0 speed

2. **Implement Flyer enemy** (2.5 hours)
   - Sine wave flight pattern
   - Dive bomb attack
   - 2 HP, 1-2 damage, 2.5 speed

3. **Implement Spiker enemy** (2 hours)
   - Stationary turret
   - Shoot spike projectiles every 3s
   - 5 HP, 2 damage (ranged)

4. **Balance enemy spawning** (1 hour)
   - Adjust spawn weights
   - Test difficulty curves
   - Ensure fair distribution

**Benefits**: Varied combat encounters, tests different enemy behaviors

---

## Phase 5: Ability Expansion (Week 7-9)

### 5.1 Implement Remaining Documented Abilities
**Current State**: 8/14 abilities implemented
**Goal**: Complete all Phase 1-3 abilities

**Tasks**:
1. **Implement Grappling Hook** (3 hours)
   - E key + direction
   - Shoot hook projectile (15 tile range)
   - Pull to grapple points or swing
   - Unlock cost: 40 orbs

2. **Implement Ground Pound** (2 hours)
   - Ctrl while airborne
   - Fast downward slam (25 px/frame)
   - Shockwave on impact (3 tile radius, 3 damage)
   - Unlock cost: 45 orbs

3. **Implement Double Dash** (1.5 hours)
   - Shift twice rapidly
   - Second dash in air without cooldown
   - 2s cooldown after second dash
   - Unlock cost: 50 orbs
   - Requires Dash unlocked first

4. **Implement Time Slow** (2.5 hours)
   - Z key
   - Slow game time to 0.3x for 3 seconds
   - Player at 1.0x speed
   - 1 charge per level
   - Unlock cost: 60 orbs

5. **Implement Teleport** (2 hours)
   - R key + direction
   - Instant teleport 5 tiles
   - Ignores walls
   - 3 uses per level, 3s cooldown
   - Unlock cost: 75 orbs

6. **Implement Stomp Jump** (2 hours)
   - Automatic on landing on enemy
   - 1.5x jump power bounce
   - 2 damage to enemy
   - Chain stomp multiple enemies
   - Unlock cost: 90 orbs

7. **Update level generation for new abilities** (2 hours)
   - Add grapple points to levels
   - Add breakable blocks for ground pound
   - Add time slow challenges
   - Add teleport-required secrets

**Benefits**: Full ability roster matches documentation

---

### 5.2 Implement Passive Abilities
**Current State**: All abilities are active
**Goal**: Add 3 passive abilities from docs

**Tasks**:
1. **Implement Coin Magnet passive** (1 hour)
   - 3 tile radius attraction
   - Faint gold aura visual
   - Unlock cost: 20 orbs
   - Different from Coin Magnet power-up

2. **Implement Hazard Sense** (1.5 hours)
   - Hazards glow red within 4 tiles
   - Red pulse effect
   - Unlock cost: 35 orbs

3. **Implement Enemy Radar** (2 hours)
   - Show enemies on minimap
   - Direction arrows for off-screen enemies
   - Unlock cost: 55 orbs
   - Requires minimap implementation first

4. **Create minimap system** (3 hours)
   - Small map in corner
   - Shows room layout
   - Player position
   - Enemy/collectible markers

**Benefits**: More progression options, QoL improvements

---

## Phase 6: RPG Elements (Week 9-12)

### 6.1 Character Stats System
**Current State**: No stats, fixed player capabilities
**Goal**: RPG-style stat progression

**Tasks**:
1. **Create stats system** (2 hours)
   - File: `core/stats.py`
   - STR (melee damage), AGI (speed), VIT (health), LUK (drop rates)
   - Base values and level-up growth

2. **Integrate stats with player** (2 hours)
   - File: `player.py`
   - Apply stat modifiers to movement, damage
   - Display stats in pause menu

3. **Create experience system** (2 hours)
   - File: `core/experience.py`
   - XP from enemies, collectibles, level completion
   - Level-up formula and rewards

4. **Add level-up UI** (1.5 hours)
   - Screen notification on level-up
   - Stat point allocation screen
   - Stat preview before allocation

5. **Save/load stats and XP** (1 hour)
   - Extend save file format
   - Persist across runs

**Benefits**: Long-term progression beyond abilities

---

### 6.2 Equipment System
**Current State**: No equipment
**Goal**: Weapons and armor

**Tasks**:
1. **Create equipment base classes** (2 hours)
   - File: `equipment/base.py`
   - Weapon (damage, speed, range)
   - Armor (defense, effects)
   - Accessory (special bonuses)

2. **Design equipment database** (2 hours)
   - File: `data/equipment.json`
   - 10 weapons, 10 armor pieces, 5 accessories
   - Stats and rarity

3. **Implement equipment drops** (1.5 hours)
   - Enemies drop equipment
   - Chests contain equipment
   - Rarity-based drop rates

4. **Create inventory system** (3 hours)
   - File: `core/inventory.py`
   - Grid-based or list-based storage
   - Equip/unequip functionality

5. **Add inventory UI** (3 hours)
   - File: `states/inventory_state.py`
   - Show all items
   - Equip/unequip interface
   - Stat comparison

**Benefits**: Customization, loot excitement

---

## Phase 7: Visual & Polish (Week 12-14)

### 7.1 Particle System Enhancement
**Current State**: Basic particle effects
**Goal**: Rich visual feedback

**Tasks**:
1. **Create particle system** (3 hours)
   - File: `core/particles.py`
   - Emitter class with lifetime, velocity, fade
   - Particle pools for performance

2. **Add particle effects to abilities** (2 hours)
   - Dash: motion blur trail
   - Double jump: energy burst
   - Wall jump: wall spark
   - Shadow step: ghost trail

3. **Add particle effects to collectibles** (1.5 hours)
   - Coins: sparkle on collect
   - Gems: color burst
   - Orbs: rainbow explosion

4. **Add particle effects to combat** (2 hours)
   - Hit sparks
   - Death explosions
   - Damage numbers floating up

**Benefits**: Game feels more polished and responsive

---

### 7.2 Animation System
**Current State**: All rectangles, no sprite animations
**Goal**: Basic sprite support

**Tasks**:
1. **Create animation framework** (3 hours)
   - File: `core/animation.py`
   - Sprite sheet support
   - Frame timing and looping

2. **Add player animations** (4 hours)
   - Idle, run, jump, fall, crouch, dash
   - Ability-specific animations
   - Direction facing

3. **Add enemy animations** (3 hours)
   - Walk, attack, death per enemy type
   - Flight animation for Flyer

4. **Add collectible animations** (2 hours)
   - Coin spin (already has rotation)
   - Gem pulse
   - Orb glow cycle

**Benefits**: Visual appeal, professional look

---

## Phase 8: Campaign Structure (Week 14-16)

### 8.1 World Map System
**Current State**: Linear level progression
**Goal**: Non-linear world navigation

**Tasks**:
1. **Create world map state** (3 hours)
   - File: `states/world_map.py`
   - Grid of level nodes
   - Unlocked/locked states
   - Current position marker

2. **Design world layout** (2 hours)
   - 25 levels in 5 worlds (5 levels each)
   - Branching paths
   - Boss levels at world ends

3. **Implement level unlocking** (2 hours)
   - Complete level to unlock next
   - Some levels require keys
   - Boss gates require all collectibles

4. **Add world map UI** (3 hours)
   - Navigate with arrow keys
   - Level preview (difficulty, collectibles)
   - Enter level on select

**Benefits**: Player choice, replayability

---

### 8.2 Save Game System
**Current State**: Only high scores and unlocks persist
**Goal**: Full game state saving

**Tasks**:
1. **Design save file format** (1.5 hours)
   - Player stats, equipment, inventory
   - World map progress
   - Collectibles per level
   - Ability unlocks, orb count

2. **Implement save/load** (3 hours)
   - File: `core/save_system.py`
   - Save on level completion
   - Load on game start
   - Multiple save slots

3. **Add save slot UI** (2 hours)
   - File: `states/save_slot_select.py`
   - 3 save slots
   - Show progress summary per slot
   - Delete save option

**Benefits**: Long campaign sessions, no lost progress

---

## Phase 9: Additional Content (Week 16-20)

### 9.1 Boss Battles
**Current State**: No bosses
**Goal**: 5 boss encounters

**Tasks**:
1. **Create boss base class** (2 hours)
   - Multi-phase health system
   - Phase transitions at HP thresholds
   - Unique attack patterns

2. **Implement Boss 1: The Crusher** (4 hours)
   - Level 5 boss
   - 50 HP, 2 phases
   - Ground pound and summon attacks
   - Arena design

3. **Implement Boss 2: Storm Drone** (4 hours)
   - Level 10 boss
   - 75 HP, 3 phases
   - Flight and projectile patterns
   - Phase-specific mechanics

4. **Implement Boss 3-5** (12 hours total, 4 each)
   - Shadow Beast, The Gauntlet, Final Guardian
   - Progressive complexity
   - Unique mechanics per boss

5. **Add boss arenas to level gen** (2 hours)
   - Special room type for bosses
   - No normal enemies in boss rooms
   - Boss gate at entrance

**Benefits**: Major progression milestones, exciting gameplay

---

### 9.2 Additional Game Modes
**Current State**: Only normal mode
**Goal**: 3 additional modes

**Tasks**:
1. **Implement Time Trial mode** (3 hours)
   - Race to finish level
   - Time orbs add seconds
   - Leaderboard per level

2. **Implement Survival mode** (4 hours)
   - Wave-based enemy spawning
   - Endless until death
   - Score based on waves survived

3. **Implement Boss Rush mode** (2 hours)
   - Fight all bosses back-to-back
   - Limited healing between
   - Unlock after beating campaign

4. **Add mode selection UI** (2 hours)
   - Menu screen for mode selection
   - Mode descriptions and requirements

**Benefits**: Replayability, different skill challenges

---

## Phase 10: Performance & Optimization (Week 20-22)

### 10.1 Performance Profiling
**Tasks**:
1. **Add performance monitoring** (2 hours)
   - FPS counter
   - Frame time graph
   - Memory usage tracking

2. **Profile level generation** (1 hour)
   - Identify slow functions
   - Measure generation time by difficulty

3. **Optimize collision detection** (2 hours)
   - Spatial partitioning (quadtree)
   - Only check nearby entities
   - Cache collision results where possible

4. **Optimize rendering** (2 hours)
   - Batch draw calls
   - Cull off-screen entities
   - Dirty rectangle optimization

5. **Object pooling for particles** (2 hours)
   - Reuse particle objects
   - Pre-allocate pools
   - Reduce garbage collection

**Benefits**: Smooth gameplay even on lower-end hardware

---

## Summary

### Total Tasks: 90+
### Estimated Time: 20-22 weeks for complete roadmap
### Priority Order:
1. **Phase 1-2** (Weeks 1-3): Foundation - Code organization, tests, docs
2. **Phase 3** (Weeks 3-5): Missing features - Controls integration, collectibles, README
3. **Phase 4** (Weeks 5-7): Enemies - Combat system foundation
4. **Phase 5** (Weeks 7-9): Abilities - Complete ability roster
5. **Phase 6** (Weeks 9-12): RPG elements - Stats, equipment, inventory
6. **Phase 7** (Weeks 12-14): Polish - Particles, animations
7. **Phase 8** (Weeks 14-16): Campaign - World map, save system
8. **Phase 9** (Weeks 16-20): Content - Bosses, game modes
9. **Phase 10** (Weeks 20-22): Performance - Optimization

---

## Quick Wins (Can Start Immediately)

1. Create README.md (1.5 hours)
2. Register ControlsViewer state (15 min)
3. Add controls button to pause menu (30 min)
4. Create level_gen package structure (30 min)
5. Add module docstrings to level_gen (1 hour)
6. Create abilities package structure (30 min)
7. Add pytest to requirements (15 min)
8. Create docs/ARCHITECTURE.md (1 hour)

**Total Quick Wins: ~6 hours of high-value, low-risk improvements**

---

## Long-term Vision Alignment

This roadmap aligns with documentation goals:
- ✅ Modular codebase (Phases 1-2)
- ✅ Complete ability system (Phase 5)
- ✅ Enemy system (Phase 4)
- ✅ RPG elements (Phase 6)
- ✅ Campaign structure (Phase 8)
- ✅ Polish & content (Phases 7, 9)
- ✅ Performance (Phase 10)

All while maintaining small, testable, incremental steps that don't break existing functionality.
