# Next Steps - Quick Reference Checklist
**For detailed explanations, see MASTER_PLAN.md**

---

## 🎯 PHASE A: Quick Wins (This Week)

### A1. Integrate Controls Viewer (1 hour) ⬜
- [ ] Add "Controls" button to `states/pause.py` line ~58
- [ ] Add "Controls" button to `states/help_state.py` line ~78
- [ ] Verify ControlsViewer registered in `core/game.py`
- [ ] Test: Pause → Controls → Back navigation
- [ ] Test: Help → View Controls → Back navigation

### A2. Polish Ability Orb System (2-3 hours) ⬜
- [ ] Test collection: Spawn orb, collect, verify count increases
- [ ] Add particle effect on collection (hook into effects system)
- [ ] Add UI notification on collection ("Ability Orb +1!")
- [ ] Add UI notification on ability unlock ("New Ability Unlocked: [Name]!")
- [ ] Verify all 14 ability unlock thresholds in `unlocks.py`
- [ ] Test: Collect enough orbs to unlock an ability
- [ ] Add sound effect hook for collection

### A3. Organize States Directory (1 hour) ⬜
- [ ] Create `states/gameplay/` directory
- [ ] Move: `play.py`, `pause.py`, `gameover.py`
- [ ] Create `states/menus/` directory
- [ ] Move: `menu.py`, `options_state.py`, `help_state.py`, `controls_viewer.py`, `settings_state.py`
- [ ] Create `states/meta/` directory
- [ ] Move: `unlocks.py`, `highscores.py`, `name_entry.py`, `seed_entry.py`
- [ ] Update imports in `states/__init__.py`
- [ ] Update imports in `core/game.py`
- [ ] Test: Launch game, verify all states still work

### A4. Add Missing Tests (3 hours) ⬜
- [ ] Create `tests/test_controls.py`
  - [ ] Test keybinding loading from JSON
  - [ ] Test conflict detection
  - [ ] Test user overrides
- [ ] Create `tests/test_physics.py`
  - [ ] Test PlayerCollider boundary checks
  - [ ] Test collision detection accuracy
  - [ ] Test velocity calculations
- [ ] Create `tests/test_state_transitions.py`
  - [ ] Test Menu → Play transition
  - [ ] Test Play → Pause → Play
  - [ ] Test GameOver → HighScores
- [ ] Run: `python -m pytest tests/ -v`
- [ ] Verify: All tests pass

**✅ Phase A Complete When**: All 4 tasks checked off

---

## 🎯 PHASE B: Combat Foundation (Weeks 2-3)

### B1. Player Combat Integration (Week 2)

#### Day 1-2: SwordAttack Integration (3 hours) ⬜
- [ ] Open `player.py`
- [ ] Import SwordAttack from abilities.combat
- [ ] Add to `self.abilities['SWORD_ATTACK'] = SwordAttack()`
- [ ] In update loop, check if J key pressed
- [ ] Call `sword_attack.use(player_state)` on J press
- [ ] Create attack hitbox: `attack_rect = pygame.Rect(self.rect.right, self.rect.y, 30, self.rect.h)`
  - Adjust based on facing direction
- [ ] Test: Press J, verify attack state activates

#### Day 2: Damage System (2 hours) ⬜
- [ ] Create `combat_system.py` in root or `core/`
- [ ] Add function: `deal_damage(attacker, target, damage_amount)`
- [ ] Implement knockback calculation
- [ ] Create damage number display class
- [ ] Add to HUD update: show floating damage numbers
- [ ] Test: Attack, see damage numbers appear

#### Day 3: Combat Testing (2 hours) ⬜
- [ ] Create `tests/test_combat.py`
- [ ] Test: Attack hitbox creation
- [ ] Test: Damage calculation
- [ ] Test: Knockback application
- [ ] Test: Attack cooldown timing
- [ ] Run: `python -m pytest tests/test_combat.py -v`

#### Day 4: Polish (1 hour) ⬜
- [ ] Add attack animation hook to animation_events
- [ ] Add sound effect hook for sword swing
- [ ] Add visual feedback (flash, motion trail)
- [ ] Optional: Screen shake on hit

**✅ B1 Complete When**: Player can attack with visible feedback

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
- [ ] Phase A: Quick Wins
- [ ] Phase B1: Player Combat
- [ ] Phase B2: Enemy System

### Current Phase
**Phase**: _________
**Started**: _________
**Target Completion**: _________

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
**Next Review**: After Phase A completion
