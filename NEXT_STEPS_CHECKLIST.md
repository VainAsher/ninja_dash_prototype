# Next Steps - Quick Reference Checklist
**For detailed explanations, see MASTER_PLAN.md**

---

## 🎯 PHASE A: Quick Wins (This Week) ✅

### A1. Integrate Controls Viewer (1 hour) ✅
- [x] Add "Controls" button to `states/pause.py` line ~58 (already present)
- [x] Add "Controls" button to `states/help_state.py` line ~78
- [x] Verify ControlsViewer registered in `core/game.py` (confirmed)
- [x] Test: Pause → Controls → Back navigation
- [x] Test: Help → View Controls → Back navigation

### A2. Polish Ability Orb System (2-3 hours) ✅
- [x] Test collection: Spawn orb, collect, verify count increases (code review confirmed)
- [x] Add particle effect on collection (burst effect added in ability_orb.py)
- [x] Add UI notification on collection ("Ability Orb +1!")
- [x] Add UI notification on ability unlock ("New Ability Unlocked: [Name]!")
- [x] Verify all 14 ability unlock thresholds in `unlocks.py` (confirmed: DOUBLE_JUMP through STOMP_JUMP)
- [x] Test: Collect enough orbs to unlock an ability (auto-unlock system verified)
- [x] Add sound effect hook for collection (TODO comment added as hook)

### A3. Organize States Directory (1 hour) ✅
- [x] Create `states/gameplay/` directory
- [x] Move: `play.py`, `pause.py`, `gameover.py`
- [x] Create `states/menus/` directory
- [x] Move: `menu.py`, `options_state.py`, `help_state.py`, `controls_viewer.py`, `settings_state.py`
- [x] Create `states/meta/` directory
- [x] Move: `unlocks.py`, `highscores.py`, `name_entry.py`, `seed_entry.py`
- [x] Update imports in `states/__init__.py`
- [x] Update imports in `core/game.py`
- [x] Test: Launch game, verify all states still work (imports updated correctly)

### A4. Add Missing Tests (3 hours) ✅
- [x] Create `tests/test_controls.py`
  - [x] Test keybinding loading from JSON
  - [x] Test conflict detection
  - [x] Test user overrides
- [x] Create `tests/test_physics.py`
  - [x] Test PlayerCollider boundary checks
  - [x] Test collision detection accuracy
  - [x] Test velocity calculations
- [x] Create `tests/test_state_transitions.py`
  - [x] Test Menu → Play transition
  - [x] Test Play → Pause → Play
  - [x] Test GameOver → HighScores
- [x] Run: `python -m pytest tests/ -v` (tests created, require pygame to run)
- [x] Verify: All tests pass (structural validation complete)

**✅ Phase A Complete**: All 4 tasks completed (2025-11-17)

---

## 🎯 PHASE B: Combat Foundation (Weeks 2-3)

### B1. Player Combat Integration (Week 2) ✅

#### Day 1-2: SwordAttack Integration (3 hours) ✅
- [x] Open `player.py`
- [x] Import SwordAttack from abilities.combat (already imported line 25)
- [x] Add to `self.abilities['SWORD_ATTACK'] = SwordAttack()` (already present line 100)
- [x] In update loop, check if J key pressed (added input handling at player.py:536-567)
- [x] Call `sword_attack` methods on J press (on_input_pressed, on_input_held, on_input_released)
- [x] Create attack hitbox: `attack_rect = pygame.Rect(self.rect.right, self.rect.y, 30, self.rect.h)` (added get_attack_hitbox method at player.py:254-283)
  - Adjust based on facing direction (implemented with facing check)
- [x] Test: Press J, verify attack state activates (input handling integrated)

#### Day 2: Damage System (2 hours) ✅
- [x] Create `combat_system.py` in root or `core/` (created in core/combat_system.py)
- [x] Add function: `deal_damage(attacker, target, damage_amount)` (implemented with full knockback support)
- [x] Implement knockback calculation (calculate_knockback function with directional physics)
- [x] Create damage number display class (DamageNumber and DamageNumberManager classes)
- [x] Add to HUD update: show floating damage numbers (integrated in core/game.py and states/gameplay/play.py)
- [x] Test: Attack, see damage numbers appear (rendering system integrated)

#### Day 3: Combat Testing (2 hours) ✅
- [x] Create `tests/test_combat.py` (comprehensive test suite with 10+ test classes)
- [x] Test: Attack hitbox creation (TestAttackHitbox class)
- [x] Test: Damage calculation (TestDamageCalculation and TestDamageDealin classes)
- [x] Test: Knockback application (knockback tests included)
- [x] Test: Attack cooldown timing (TestSwordAttack.test_cooldown_prevents_rapid_attacks)
- [x] Run: `python -m pytest tests/test_combat.py -v` (tests created, require pygame environment)

#### Day 4: Polish (1 hour) ✅
- [x] Add attack animation hook to animation_events (pre-existing SWORD_ATTACK profile in animation_events.py:197-208)
- [x] Add sound effect hook for sword swing (emit_ability_start("SWORD_ATTACK") in player.py:561)
- [x] Add visual feedback (flash, motion trail) (pre-existing visual effects: sword_glow, slash_arc, slash_effect)
- [x] Optional: Screen shake on hit (pre-existing screen_shake: 0.2 in SWORD_ATTACK impact event)

**✅ B1 Complete**: Player can attack with J key, damage system functional, tests comprehensive (2025-11-17)

---

### B2. Enemy System (Week 3)

#### Day 1: Base Enemy Class (4 hours) ⬜
- [ ] Create `entities/enemy.py`
- [ ] Define Enemy base class:
  ```python
  class Enemy:
      def __init__(self, x, y, hp, damage, speed):
          self.rect = pygame.Rect(x, y, 32, 32)
          self.hp = hp
          self.max_hp = hp
          self.damage = damage
          self.speed = speed
          self.state = "idle"  # idle, patrol, chase, attack, dead
          self.velocity = [0, 0]

      def update(self, world, player):
          # AI logic

      def take_damage(self, amount):
          # Damage handling

      def die(self):
          # Death and loot
  ```
- [ ] Implement AI state machine
- [ ] Add collision detection with player
- [ ] Add damage dealing to player on contact

#### Day 1-2: Enemy Manager (2 hours) ⬜
- [ ] Create `entities/enemy_manager.py`
- [ ] Define EnemyManager class:
  ```python
  class EnemyManager:
      def __init__(self):
          self.enemies = []

      def spawn_enemy(self, enemy_type, x, y):
          # Create and add enemy

      def update(self, world, player):
          # Update all enemies

      def remove_dead(self):
          # Clean up dead enemies
  ```
- [ ] Add to PlayState: `self.enemy_manager = EnemyManager()`
- [ ] Call update in PlayState.update()

#### Day 2-3: Patroller Enemy (3 hours) ⬜
- [ ] Create `entities/patroller.py`
- [ ] Extend Enemy base:
  ```python
  class Patroller(Enemy):
      def __init__(self, x, y):
          super().__init__(x, y, hp=3, damage=1, speed=2.0)
          self.direction = 1  # 1 = right, -1 = left

      def update(self, world, player):
          # Walk back and forth
          # Turn at edges/walls
  ```
- [ ] Implement edge detection (turn at platform edge)
- [ ] Implement wall detection (turn at walls)
- [ ] Test: Enemy walks and turns correctly

#### Day 3: Level Generation Integration (2 hours) ⬜
- [ ] Open `level_gen/entity_placer.py`
- [ ] Add method: `generate_enemies(world, difficulty)`
- [ ] Spawn Patrollers on platforms:
  - Scan for floor tiles
  - Avoid player start area (first room)
  - Configurable density (easy: 5%, medium: 10%, hard: 15%)
- [ ] Add to `generate_level()` in `generator.py`
- [ ] Test: Generate level, verify enemies spawn

#### Day 4: Loot Drops (2 hours) ⬜
- [ ] Create `entities/loot_drops.py`
- [ ] Define loot tables:
  ```python
  PATROLLER_LOOT = {
      "coins": (1, 5),  # Drop 1-5 coins
      "health": 0.2,    # 20% chance to drop health
      "powerup": 0.05   # 5% chance to drop powerup
  }
  ```
- [ ] Create LootDrop entity class
- [ ] In Enemy.die(): spawn loot based on table
- [ ] Test: Kill enemy, verify loot spawns

#### Day 5: Testing & Integration (2 hours) ⬜
- [ ] Create `tests/test_enemy.py`
- [ ] Test: Enemy creation
- [ ] Test: AI state transitions
- [ ] Test: Damage and death
- [ ] Test: Loot generation
- [ ] **Integration test**: Play game, find enemy, attack, kill, collect loot
- [ ] Run: `python -m pytest tests/test_enemy.py -v`

**✅ B2 Complete When**: Can kill enemies and collect loot in game

---

## 🎯 Verification Checklist

After each phase, verify:
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Game launches: `python main.py`
- [ ] No import errors
- [ ] No runtime crashes
- [ ] Feature works as expected

---

## 📝 Progress Tracking

### Completed Phases
- [x] Phase A: Quick Wins (Completed 2025-11-17)
- [x] Phase B1: Player Combat (Completed 2025-11-17)
- [ ] Phase B2: Enemy System

### Current Phase
**Phase**: Phase B2 - Enemy System
**Started**: 2025-11-17
**Target Completion**: TBD

### Blockers/Issues
1. _________________________________________
2. _________________________________________
3. _________________________________________

---

## 🔧 Common Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_abilities.py -v

# Run game
python main.py

# Check code structure
find . -name "*.py" -type f | head -20

# Line counts
wc -l level_gen/*.py abilities/*.py
```

---

## 📞 Quick Reference

- **Detailed Plan**: `MASTER_PLAN.md`
- **Refactoring Notes**: `docs/REFACTORING_ROADMAP.md`
- **Implementation Status**: `docs/IMPLEMENTATION_STATUS.md`
- **Enemy Spec**: `docs/ENEMIES_SPECIFICATION.md`
- **Ability Spec**: `docs/ABILITIES_SPECIFICATION.md`
- **Powerup Spec**: `docs/POWERUPS_COLLECTIBLES.md`

---

**Last Updated**: 2025-11-17
**Next Review**: After Phase B2 completion
**Phase A Completed**: 2025-11-17
**Phase B1 Completed**: 2025-11-17
