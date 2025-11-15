# Player Module Refactoring - Ability System

## Overview

The player module has been refactored to separate physics from ability implementations, reducing complexity and improving testability.

**Before:** 684 lines with all ability logic mixed into Player class
**After:** 613 lines in Player + modular ability classes

## Architecture

### Abilities Package (`abilities/`)

A new package containing all player abilities, organized into:

1. **Base Classes** (`abilities/__init__.py`)
   - `Ability`: Abstract base class for all abilities
   - `ResourceAbility`: Base for abilities with consumable resources (charges, stamina)
   - `CooldownAbility`: Base for abilities with cooldown timers

2. **Movement Abilities** (`abilities/movement.py`)
   - `DoubleJump`: Multi-jump system with coyote time and jump buffering
   - `Dash`: Quick horizontal burst with cooldown
   - `WallJump`: Jump off walls with input locking
   - `Slide`: Fast ground slide requiring minimum speed

3. **Advanced Abilities** (`abilities/advanced.py`)
   - `ShadowStep`: Invulnerable teleport dash with charge system
   - `WallCling`: Stick to walls using stamina (regenerates when not clinging)
   - `AirDodge`: Directional dodge with i-frames and limited air uses
   - `Glide`: Slow descent while holding jump

### Powerup System (`powerups.py`)

Extracted temporary power-up effects into dedicated classes:

- `SpeedBoost`: Increases movement speed by a factor
- `TripleJump`: Grants additional jumps
- `CoinMagnet`: Attracts coins within radius
- `PowerupManager`: Centralized manager for all active powerups

## Key Improvements

### 1. Separation of Concerns

Each ability is now self-contained with its own:
- State (timers, cooldowns, charges, stamina)
- Logic (`can_use()`, `use()`, `update()`)
- Activation conditions

### 2. Testability

Abilities can be tested independently without requiring a full Player instance:

```python
ability = Dash()
player_state = {'facing': 1}

if ability.can_use(player_state):
    modifications = ability.use(player_state, {})
```

### 3. Maintainability

- Adding new abilities: Create a new class inheriting from appropriate base
- Modifying abilities: Edit only the ability's own file
- Debugging: Clear separation makes issues easier to trace

### 4. Extensibility

The ability system supports:
- Runtime ability unlocking
- Multiple instances of the same ability (if needed)
- Debug info for each ability's state
- Easy modification of ability parameters

## Player Class Changes

### New Structure

```python
class Player:
    def __init__(self, x, y):
        # Physics and collision state
        self.vx, self.vy = 0.0, 0.0
        self.on_ground = False
        # ...

        # Ability instances
        self.abilities = {
            'double_jump': DoubleJump(),
            'dash': Dash(),
            'wall_jump': WallJump(),
            'slide': Slide(),
            'shadow_step': ShadowStep(),
            'wall_cling': WallCling(),
            'air_dodge': AirDodge(),
            'glide': Glide(),
        }

        # Powerup manager
        self.powerup_manager = PowerupManager()
```

### Update Loop

The player update now follows a clear pipeline:

1. **Update timers and powerups** - Track durations and expirations
2. **Update all abilities** - Each ability updates its state
3. **Handle input** - Check ability activation conditions
4. **Apply gravity** - Standard physics (unless overridden by ability)
5. **Move and collide** - Standard collision resolution

### Backward Compatibility

Properties maintain compatibility with existing code:

```python
@property
def jumps_left(self):
    return self.abilities['double_jump'].jumps_left

@property
def shadow_step_charges(self):
    return self.abilities['shadow_step'].resource
```

## Testing

### Unit Tests (`test_abilities.py`)

Comprehensive test coverage for:

- **Cooldown Logic**: Dash, AirDodge cooldown timers
- **State Transitions**: Ability activation → active → cooldown → ready
- **Resource Consumption**: ShadowStep charges, WallCling stamina
- **Activation Conditions**: Ground/air states, velocity requirements
- **Timer Accuracy**: Coyote time, jump buffering, ability durations
- **Powerup Effects**: Speed multipliers, extra jumps, magnet radius

Run tests with: `python test_abilities.py`

Note: Requires pygame to be installed.

## Migration Guide

### For Ability Developers

To create a new ability:

1. Choose appropriate base class:
   - `Ability` - Basic ability
   - `CooldownAbility` - Has cooldown timer
   - `ResourceAbility` - Consumes charges/stamina

2. Implement required methods:
   ```python
   class MyAbility(CooldownAbility):
       def __init__(self):
           super().__init__("MY_ABILITY", cooldown=2.0)

       def can_use(self, player_state):
           # Check if ability can activate
           return not self.is_on_cooldown()

       def use(self, player_state, input_state):
           # Activate ability, return modifications
           return {'vx': 20, 'special_flag': True}

       def update(self, dt, player_state):
           # Update ability state
           self.update_cooldown(dt)
           return {}
   ```

3. Add to Player's `abilities` dict
4. Add ability name mapping in `unlock_ability()`

### For Existing Code

No changes needed! The refactored Player maintains the same external interface:

- `player.is_dashing` - Still works
- `player.jumps_left` - Still works
- `player.apply_speed_boost()` - Still works
- All existing methods and properties maintained

## Performance Considerations

- **Memory**: Slight increase (~8 ability instances per player)
- **CPU**: Negligible overhead from abstraction
- **Benefit**: Cleaner code, easier debugging worth the minimal cost

## Future Refinement Opportunities

1. **Ability Combos**: Chain abilities together with special effects
2. **Ability Upgrades**: Different tiers or variants of abilities
3. **Cooldown Reduction**: Powerups or items that modify cooldowns
4. **Ability Swap System**: Runtime ability loadout changes
5. **Animation Events**: Ability hooks for sprite animation
6. **Sound Integration**: Per-ability sound effect triggers
7. **Particle Effects**: Ability-specific visual effects
8. **Ability Canceling**: Cancel one ability with another

## Files Changed

- ✨ **New**: `abilities/__init__.py` - Base ability classes
- ✨ **New**: `abilities/movement.py` - Movement abilities
- ✨ **New**: `abilities/advanced.py` - Advanced abilities
- ✨ **New**: `powerups.py` - Powerup system
- ✨ **New**: `test_abilities.py` - Unit tests
- 🔄 **Modified**: `player.py` - Refactored to use ability system

## Summary

This refactoring successfully separates concerns, improves code organization, and sets up a solid foundation for future development. The ability system is now:

- ✅ Modular and self-contained
- ✅ Easy to test independently
- ✅ Simple to extend with new abilities
- ✅ Backward compatible with existing code
- ✅ Well-documented with comprehensive tests

**Lines of Code:**
- Before: 684 lines (player.py)
- After: 613 (player.py) + 200 (base) + 330 (movement) + 370 (advanced) + 280 (powerups) = 1793 total
- **Trade-off**: More total lines, but much better organization and maintainability
