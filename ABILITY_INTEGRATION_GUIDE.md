# Ability System Integration Guide

This document outlines the changes needed in `player.py` and other files to integrate the reworked ability system.

## Overview of Changes

### Core Ability System
- ✅ New base classes: `StaminaAbility`, `AmmoAbility`, `CombinedCostAbility`
- ✅ All abilities now have proper cost systems (stamina, cooldowns, charges, ammo)

### Movement Abilities (abilities/movement.py)

#### 1. DoubleJump - Differentiated Jump Mechanics
**Changes:**
- First jump: Balanced vertical power (existing behavior)
- Second jump: Reduced vertical (`JUMP_POWER_SECOND = 10.0`), increased horizontal (`JUMP_HORIZONTAL_BOOST_SECOND = 1.4x`)
- Wall jumps get special treatment (85% power boost)

**Player.py Integration Needed:**
```python
# In _handle_input() when processing jump:
if jump_ability.use(player_state, input_state):
    modifications = jump_ability.use(player_state, input_state)
    # Apply vx AND vy from modifications (not just vy)
    if 'vx' in modifications:
        self.vx = modifications['vx']  # NEW: Apply horizontal velocity
    if 'vy' in modifications:
        self.vy = modifications['vy']
```

#### 2. Dash - Stamina-Based Speed Modifier
**Changes:**
- OLD: Quick burst dash (0.16s at 16.0 px/s)
- NEW: Hold-to-activate stamina drain, speed multiplier (1.8x)

**Player.py Integration Needed:**
```python
# Change from burst to modifier:
# OLD:
if dash_ability.is_active:
    self.vx = dash_velocity  # Direct velocity set

# NEW:
if dash_ability.is_active:
    # Apply multiplier to MAX_RUN_SPEED
    effective_max_speed = MAX_RUN_SPEED * dash_ability.speed_multiplier
    # Use effective_max_speed in movement calculations

# Input handling - hold vs press:
# OLD: if keys[DASH_KEY] and not_on_cooldown...
# NEW:
if keys[DASH_KEY]:
    dash_ability.use(...)  # Activates if has stamina
else:
    dash_ability.deactivate_dash()  # Release = deactivate

# Stamina management handled automatically in dash_ability.update()
```

**Settings Changes:**
- Added: `DASH_STAMINA_MAX`, `DASH_STAMINA_DRAIN`, `DASH_STAMINA_REGEN`, `DASH_SPEED_MULT`
- Removed: `DASH_SPEED`, `DASH_DURATION`

#### 3. Slide - Collision Safety
**Changes:**
- Added collision safety flags
- Changed from direct velocity set to multiplier

**Player.py Integration Needed:**
```python
# Apply multiplier instead of direct set:
if slide_ability.is_active:
    # OLD: self.vx = slide_velocity
    # NEW:
    self.vx *= modifications.get('vx_mult', 1.0)

# Ensure collision checking remains active during slide
# (slide was glitching through terrain - check collision code)
```

### Advanced Abilities (abilities/advanced.py)

#### 4. ShadowStep - Smoke Bomb Evasion
**Changes:**
- Renamed concept: "shadow step dash" → "smoke bomb evasion"
- Defensive focus (slower speed, longer invulnerability)
- Door phasing only (not floors)

**Player.py Integration Needed:**
```python
# Update state variable names:
# is_shadow_stepping → is_smoke_stepping
# Check for phasing:
if self.abilities['shadow_step'].can_phase_through_doors():
    # Allow phasing through phaseable WALLS only
    # NOT floors or single blocks
    pass
```

**Settings Changes:**
- `SHADOW_STEP_SPEED`: 18.0 → 12.0 (defensive, not aggressive)
- `SHADOW_STEP_DURATION`: 0.75 → 0.85
- `SHADOW_STEP_INVULN_TIME`: 0.4 → 0.85 (full duration invuln)
- Added: `SHADOW_STEP_PHASE_DOORS_ONLY = True`

#### 5. AirDodge - Hang Time Mechanic
**Changes:**
- Added "hang time" phase with reduced gravity
- Player can input direction during hang time
- Two-phase: hang → dodge

**Player.py Integration Needed:**
```python
# Two-state handling:
if air_dodge.is_hanging:
    # Apply reduced gravity
    gravity_mult = modifications.get('gravity_mult', 1.0)
    effective_gravity = GRAVITY * gravity_mult

    # Call update_direction() each frame during hang time
    air_dodge.update_direction(input_state, player_state)

elif air_dodge.is_dodging:
    # Normal dodge movement (existing code)
    pass

# Input state must include dodge_x, dodge_y:
input_state = {
    'dodge_x': ...,  # -1, 0, or 1 (or mouse-derived)
    'dodge_y': ...,  # -1, 0, or 1
}
```

**Settings Changes:**
- Added: `AIR_DODGE_HANG_TIME = 0.15`, `AIR_DODGE_HANG_GRAVITY_MULT = 0.1`

#### 6. Glide - Descent Control Only
**Changes:**
- OLD: Reduced fall speed AND reduced horizontal (0.8x)
- NEW: Reduced fall speed, ENHANCED horizontal (1.3x) and air control (1.5x)

**Player.py Integration Needed:**
```python
# Apply horizontal enhancement (not reduction):
if glide_ability.is_active:
    # Vertical: cap fall speed (existing)
    if self.vy > GLIDE_FALL_SPEED:
        self.vy = GLIDE_FALL_SPEED

    # Horizontal: ENHANCE (NEW)
    horizontal_mult = modifications.get('horizontal_mult', 1.0)  # 1.3
    air_accel_mult = modifications.get('air_accel_mult', 1.0)   # 1.5

    # Apply to max speed and acceleration
    effective_max_speed = MAX_RUN_SPEED * horizontal_mult
    effective_air_accel = RUN_ACCEL_AIR * air_accel_mult
```

**Settings Changes:**
- `GLIDE_HORIZONTAL_MULT`: 0.8 → 1.3 (reversal!)
- Added: `GLIDE_HORIZONTAL_ACCEL = 1.5`

### Powerups (powerups.py)

#### 7. ExtraJump Powerup
**NEW Powerup:**
- Grants consumable extra jump (5 uses OR 2 damage)
- Works with base 1 jump (becomes 2) or 2 jumps (becomes 3)

**Player.py Integration Needed:**
```python
# When player takes damage:
if self.powerup_manager.powerups['extra_jump'].is_active:
    self.powerup_manager.register_damage(1)

# When using extra jump from powerup:
# The powerup.get_extra_jumps() is already integrated into existing
# triple jump logic, but need to consume uses:
if using_powerup_jump:
    self.powerup_manager.consume_extra_jump_use()
```

**Settings Changes:**
- Added to `POWERUP_TYPES`: `("extra_jump", 30)`
- Added: `POWERUP_EXTRA_JUMP_USES = 5`, `POWERUP_EXTRA_JUMP_DAMAGE_LIMIT = 2`
- Added color: `COLOR_POWERUP_EXTRA_JUMP = (150, 255, 150)`

### Combat Abilities (abilities/combat.py) - NEW FILE

#### 8. SwordAttack
**NEW Ability:**
- Tap input = attack
- Hold input (0.15s+) = block

**Player.py Integration Needed:**
```python
# Load combat abilities:
from abilities.combat import SwordAttack, GrappleHook

# In player.__init__:
self.abilities['sword_attack'] = SwordAttack()

# In _handle_input():
sword_key = keys[pygame.K_...]  # Define sword key

if sword_key and not self.sword_key_was_pressed:
    # Pressed this frame
    self.abilities['sword_attack'].on_input_pressed(player_state)
    self.sword_key_was_pressed = True

if sword_key:
    # Held
    mods = self.abilities['sword_attack'].on_input_held(dt, player_state)
    self._apply_modifications(mods)

if not sword_key and self.sword_key_was_pressed:
    # Released
    mods = self.abilities['sword_attack'].on_input_released(player_state)
    self._apply_modifications(mods)
    self.sword_key_was_pressed = False
```

**Settings Integration:**
- Move constants from `abilities/combat.py` to `settings.py` after testing
- Add key binding to `data/controls.json`

#### 9. GrappleHook
**NEW Ability:**
- Pull levers/switches for puzzles
- Maneuver enemies
- NOT for player movement

**Player.py Integration Needed:**
```python
# In player.__init__:
self.abilities['grapple_hook'] = GrappleHook()

# In _handle_input():
if grapple_key_pressed:
    mods = self.abilities['grapple_hook'].use(player_state, input_state)

# In update():
mods = self.abilities['grapple_hook'].update(dt, player_state)
if 'pull_target' in mods:
    # Apply pull force to target (lever, enemy, etc.)
    target = mods['pull_target']
    force = mods['pull_force']
    # Pull logic...
```

**Future Work:**
- Level generation: add grapple points (tiles/entities)
- Puzzle system: levers, switches
- Enemy system: grapple interactions

## Missing Features - Future Implementation

These were in the requirements but need significant additional work:

### 1. Player Facing Direction Indicator
**Requirement:** Visual indicator of which way player is facing

**Implementation Needed:**
- Add to player rendering code
- Arrow/chevron pointing in facing direction
- Or asymmetric player sprite

### 2. Aiming System
**Requirement:** Mouse/cursor aiming with 8-directional fallback

**Implementation Needed:**
```python
# In player.py _handle_input():
# Mouse aiming:
mouse_x, mouse_y = pygame.mouse.get_pos()
player_center = self.rect.center
aim_vector = (mouse_x - player_center[0], mouse_y - player_center[1])

# 8-directional fallback:
if not mouse_moved:
    aim_x = keys[RIGHT] - keys[LEFT]  # -1, 0, 1
    aim_y = keys[DOWN] - keys[UP]     # -1, 0, 1
    aim_vector = (aim_x, aim_y)

# Normalize and store in input_state:
input_state['aim_x'] = aim_vector[0]
input_state['aim_y'] = aim_vector[1]
```

### 3. Ranged Abilities System
**Requirement:** Tab between ranged abilities, hold to aim, release to fire

**Implementation Needed:**
- New ranged ability base class (extends AmmoAbility)
- Ability selection/cycling system
- Aiming cursor/reticle
- Projectile system
- Integration with combat.py

### 4. Phaseable Tiles Review
**Requirement:** Ensure phaseable tiles form doorways/walls, not floors

**Implementation Needed:**
- Review level generation code
- Add constraints: phaseable tiles must be vertical (walls/doors)
- Prevent horizontal (floor) or single-block phaseable tiles
- Update `SHADOW_STEP_PHASE_DOORS_ONLY` logic

## Testing Checklist

Once integrated, test:

- [ ] Jump: First jump balanced, second jump more horizontal
- [ ] Jump: Wall jumps have upward boost
- [ ] Jump: Extra jump powerup works with 1 or 2 base jumps
- [ ] Extra jump powerup: Expires after X uses OR Y damage
- [ ] Dash: Hold to activate, drains stamina, increases speed
- [ ] Dash: Regenerates stamina when not active
- [ ] Slide: Doesn't glitch through collisions
- [ ] Shadow step: Slower, longer invuln, defensive feel
- [ ] Shadow step: Can phase through doors/walls only
- [ ] Air dodge: Hang time activates, allows directional input
- [ ] Air dodge: Executes dodge after hang time
- [ ] Glide: Only slows descent
- [ ] Glide: ENHANCES horizontal movement (not reduces)
- [ ] Sword: Tap = attack, hold = block
- [ ] Grapple: Can target objects (when implemented)

## File Summary

### Modified Files:
1. `abilities/__init__.py` - Added StaminaAbility, AmmoAbility, CombinedCostAbility
2. `abilities/movement.py` - Reworked DoubleJump, Dash, Slide
3. `abilities/advanced.py` - Reworked ShadowStep, AirDodge, Glide
4. `powerups.py` - Added ExtraJump powerup
5. `settings.py` - Added new constants for all ability changes

### New Files:
1. `abilities/combat.py` - SwordAttack, GrappleHook

### Files Needing Integration:
1. `player.py` - Main integration work (see above)
2. `unlocks.py` - May need SWORD_ATTACK, update GRAPPLE entry
3. `data/controls.json` - Add sword, grapple key bindings
4. Level generation - Grapple points, phaseable tile constraints

## Notes

- All ability changes are BACKWARD COMPATIBLE with existing ability system
- Settings constants added alongside old ones (can remove old after testing)
- Combat abilities are in separate module for organization
- Aiming/ranged systems are frameworks only - need full implementation

## Questions for User

1. **Phaseable Tiles:** Should the level generator enforce door/wall-only constraint automatically, or should it be a validation step?

2. **Controls:** What key should be used for sword attack? (currently undefined in combat.py)

3. **Ranged Abilities:** Should we implement a basic projectile system now, or defer to later?

4. **Player Facing Indicator:** Preferred visual style? (arrow, asymmetric sprite, other?)

---

**Status:** All ability mechanics implemented and ready for player.py integration.
**Next Steps:** Integrate into player.py, test, iterate on balance.
