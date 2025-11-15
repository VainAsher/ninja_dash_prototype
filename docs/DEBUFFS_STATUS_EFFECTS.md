# Debuffs and Status Effects Specification

## Status Effect System Architecture

### Base Status Effect Class
```python
class StatusEffect:
    - effect_id: str
    - name: str
    - duration: float
    - tick_rate: float (for DOT/HOT)
    - stack_count: int
    - max_stacks: int
    - visual_effect: str
    - can_cleanse: bool
    - priority: int (for display order)
```

## Negative Status Effects (Debuffs)

### 1. Poison ☠️
- **Duration**: 5 seconds
- **Effect**: Lose 1 HP every 2 seconds (DOT)
- **Stacks**: Yes, up to 3 stacks (independent timers)
- **Applied By**:
  - Spiker enemies (toxic variant)
  - Poison traps
  - Boss "Toxic Slime" phase 2
- **Visual**: Green dripping effect, health bar turns green
- **Cleanse**: Yes (with Antidote item or time)
- **Immunity**: Invincibility power-up, Ghost Mode

### 2. Burn 🔥
- **Duration**: 4 seconds
- **Effect**: Lose 1 HP every 1.5 seconds (fast DOT)
- **Stacks**: Yes, up to 5 stacks (damage increases per stack)
- **Applied By**:
  - Fire hazards
  - Exploder enemy explosion
  - Flamethrower traps
  - Fire boss attacks
- **Visual**: Orange flames on player, flickering
- **Cleanse**: Yes (water areas, cleanse item)
- **Special**: Moving quickly reduces duration by 50%

### 3. Freeze ❄️
- **Duration**: 2 seconds
- **Effect**: Cannot move, takes 50% more damage
- **Stacks**: No (refreshes duration)
- **Applied By**:
  - Ice enemies
  - Freeze traps
  - Boss ice attacks
  - Freeze power-down
- **Visual**: Blue ice cage around player, shivering
- **Cleanse**: Yes (Burn effect cancels Freeze, cleanse item)
- **Counter**: Button mashing reduces duration by 30%

### 4. Slow 🐌
- **Duration**: 6 seconds
- **Effect**: Movement speed reduced by 40%, jump height -30%
- **Stacks**: Yes, up to 2 stacks (20% additional slow per stack)
- **Applied By**:
  - Shooter enemies (special ammo)
  - Slow traps
  - Mud/tar terrain
  - Gravity wells
- **Visual**: Blue aura, movement trail fades slower
- **Cleanse**: Yes
- **Immunity**: Speed Boost power-up prevents Slow

### 5. Stun ⚡
- **Duration**: 1 second
- **Effect**: Cannot move, act, or use abilities
- **Stacks**: No (refreshes duration)
- **Applied By**:
  - Charger enemy charge attack
  - Lightning hazards
  - Boss stun attacks
  - Flash grenades (future item)
- **Visual**: Yellow stars circling head, player flashes
- **Cleanse**: No (must wait out)
- **Resistance**: Each consecutive stun within 5s has 50% reduced duration

### 6. Weakness 💔
- **Duration**: 8 seconds
- **Effect**: Damage output reduced by 50%
- **Stacks**: No
- **Applied By**:
  - Curse enemies
  - Weakness traps
  - Boss debuff aura
- **Visual**: Red downward arrow above player, dim glow
- **Cleanse**: Yes
- **Immunity**: Giant Mode power-up

### 7. Curse 🌙
- **Duration**: 10 seconds
- **Effect**: Cannot heal (health pickups/regen don't work)
- **Stacks**: No (refreshes duration)
- **Applied By**:
  - Shadow Beast boss
  - Cursed chests
  - Dark magic enemies
- **Visual**: Purple skull icon, dark aura
- **Cleanse**: Rare (requires Holy Water item)
- **Danger**: Extremely dangerous in boss fights

### 8. Bleed 🩸
- **Duration**: 6 seconds
- **Effect**: Lose 1 HP every 3 seconds, leave blood trail
- **Stacks**: Yes, up to 3 stacks (increases tick rate)
- **Applied By**:
  - Blade traps
  - Slashing enemies
  - Sharp hazards
- **Visual**: Red drips, blood trail behind player
- **Cleanse**: Yes (Bandage item, time)
- **Special**: Moving stops bleeding faster, standing still extends it

### 9. Confusion 🌀
- **Duration**: 4 seconds
- **Effect**: Controls randomly inverted (left→right, jump→crouch, etc.)
- **Stacks**: No (refreshes duration)
- **Applied By**:
  - Psychic enemies
  - Confusion gas traps
  - Hallucination zones
- **Visual**: Swirling stars, screen slight rotation wobble
- **Cleanse**: Yes (rare, or wait it out)
- **Difficulty**: Extremely frustrating, rare application

### 10. Silence 🔇
- **Duration**: 5 seconds
- **Effect**: Cannot use abilities (movement only)
- **Stacks**: No
- **Applied By**:
  - Silence enemies
  - Anti-magic zones
  - Boss dispel attack
- **Visual**: Gray aura, crossed-out ability icons
- **Cleanse**: Yes (Echo Stone item)
- **Tactical**: Forces basic movement skills

### 11. Gravity Well 🕳️
- **Duration**: 3 seconds
- **Effect**: Pulled toward center point, reduced jump height
- **Stacks**: No (multiple wells apply strongest effect)
- **Applied By**:
  - Gravity traps
  - Black hole enemies
  - Boss gravity attacks
- **Visual**: Purple vortex particles pulling toward center
- **Cleanse**: No (environmental)
- **Counter**: Dash can escape pull

### 12. Doom ☠️💀
- **Duration**: 10 seconds
- **Effect**: Die when timer expires (instant death)
- **Stacks**: No
- **Applied By**:
  - Rare boss ultimate attacks
  - Death traps
  - Cursed items
- **Visual**: Skull countdown timer, screen darkens
- **Cleanse**: Extremely rare (Revival item, boss phase change)
- **Counter**: Must defeat boss or find cleanse before timer ends
- **Rarity**: Only used in epic boss encounters

## Positive Status Effects (Buffs)

### 13. Regeneration 💚
- **Duration**: 20 seconds
- **Effect**: Heal 1 HP every 4 seconds
- **Stacks**: No
- **Applied By**:
  - Regeneration power-up
  - Healing zones
  - Buff items
- **Visual**: Green plus signs floating up
- **Cancels**: Poison, Bleed (cleanse on application)

### 14. Haste ⚡
- **Duration**: 12 seconds
- **Effect**: +40% movement speed, +20% attack speed
- **Stacks**: Yes, up to 2 stacks
- **Applied By**:
  - Speed Boost power-up
  - Haste zones
  - Speed items
- **Visual**: Yellow speed lines, after-images
- **Cancels**: Slow (opposite effect)

### 15. Shield 🛡️
- **Duration**: Until broken or 30 seconds
- **Effect**: Absorb next X hits (based on source)
- **Stacks**: No (takes strongest shield)
- **Applied By**:
  - Shield power-up (3 hits)
  - Shield items
  - Boss phases
- **Visual**: Blue energy barrier, cracks form as damaged
- **Breaks**: Visual shatter effect + sound

### 16. Invincibility ⭐
- **Duration**: Varies (usually 8 seconds)
- **Effect**: Immune to all damage, destroy enemies on contact
- **Stacks**: No (refreshes duration)
- **Applied By**:
  - Invincibility power-up
  - Star items
  - Respawn protection (3s)
- **Visual**: Rainbow flashing, star particles
- **Note**: Most powerful buff

## Status Effect Interactions

### Cancellation Pairs
- **Burn ↔ Freeze**: Cancel each other
- **Slow ↔ Haste**: Cancel each other
- **Poison ↔ Regeneration**: Regen removes Poison
- **Weakness ↔ Giant Mode**: Giant Mode prevents Weakness

### Synergy Combinations
- **Burn + Poison**: Take damage from both (painful combo)
- **Slow + Gravity Well**: Nearly impossible to move
- **Curse + Doom**: Cannot heal while dying (boss combo)
- **Freeze + Weakness**: Trapped and vulnerable

### Immunity Hierarchy
1. **Invincibility**: Immune to ALL negative effects
2. **Ghost Mode**: Immune to damage-based effects (Poison, Burn)
3. **Giant Mode**: Immune to crowd control (Stun, Freeze, Slow)
4. **Shield**: Absorbs damage but not debuffs

## Visual UI System

### Status Bar Display
```
┌─────────────────────────────────┐
│ HP: ❤❤❤ Lives: 💖💖💖        │
├─────────────────────────────────┤
│ Buffs:   ⚡ Haste (8.3s)       │
│          🛡️ Shield (2 hits)     │
├─────────────────────────────────┤
│ Debuffs: ☠️ Poison (3.2s) x2   │
│          🐌 Slow (5.1s)         │
└─────────────────────────────────┘
```

### In-World Visual Priority
1. **Doom**: Massive skull, screen darkening
2. **Invincibility**: Rainbow flash (overrides all)
3. **Freeze**: Ice cage encasement
4. **Burn**: Flames on player
5. **Poison**: Drip effects
6. **Slow**: Blue aura
7. **Haste**: Speed lines
8. **Others**: Icon above head

### Color Coding
- **Debuffs**: Red background
- **Buffs**: Green/blue background
- **Neutral**: Gray background
- **Critical (Doom)**: Black with red border

## Cleanse System

### Cleanse Items
1. **Antidote**: Removes Poison
2. **Fire Extinguisher**: Removes Burn
3. **Stimpack**: Removes Slow
4. **Bandage**: Removes Bleed
5. **Holy Water**: Removes Curse
6. **Echo Stone**: Removes Silence
7. **Universal Cleanse**: Removes all debuffs (rare)

### Natural Cleanse
- **Water pools**: Remove Burn
- **Healing zones**: Remove all DOT effects
- **Safe rooms**: Remove all debuffs over 5 seconds
- **Boss phase transitions**: Clear all effects

### Cleanse Priorities
When multiple debuffs are active and partial cleanse is used:
1. Doom (if possible)
2. Curse
3. Silence
4. Freeze/Stun
5. DOT effects (Poison, Burn, Bleed)
6. Movement debuffs (Slow, Gravity Well)
7. Damage debuffs (Weakness)

## Difficulty Scaling

| Difficulty | Debuff Duration | Stack Limit | Cleanse Availability |
|------------|-----------------|-------------|---------------------|
| Easy       | 0.7x            | -1 stack    | Common              |
| Medium     | 1.0x            | Normal      | Normal              |
| Hard       | 1.3x            | +1 stack    | Rare                |
| Expert     | 1.5x            | +2 stacks   | Very Rare           |

## Implementation Priority

### Phase 1 - Basic Debuffs
1. Poison (DOT)
2. Slow (movement)
3. Stun (control)
4. Basic visual indicators

### Phase 2 - Environmental
5. Burn (DOT)
6. Freeze (control)
7. Bleed (DOT)
8. Status bar UI

### Phase 3 - Advanced
9. Weakness (damage)
10. Curse (healing)
11. Silence (abilities)
12. Cleanse items

### Phase 4 - Expert
13. Confusion (control chaos)
14. Gravity Well (physics)
15. Doom (ultimate)
16. Full interaction system

## Code Structure Example

```python
class StatusEffectManager:
    def __init__(self, entity):
        self.entity = entity
        self.active_effects = {}
        self.immunities = set()

    def apply_effect(self, effect_id, duration, **kwargs):
        # Check immunity
        if effect_id in self.immunities:
            return False

        # Check cancellation
        if self._should_cancel(effect_id):
            return False

        # Apply or stack
        if effect_id in self.active_effects:
            self._stack_or_refresh(effect_id, duration, kwargs)
        else:
            self._add_new_effect(effect_id, duration, kwargs)

        return True

    def update(self, dt):
        for effect_id in list(self.active_effects.keys()):
            effect = self.active_effects[effect_id]
            effect.update(dt)

            # Tick damage/heal
            if effect.should_tick():
                effect.apply_tick(self.entity)

            # Remove if expired
            if effect.is_expired():
                self._remove_effect(effect_id)

    def cleanse(self, effect_types=None):
        # Remove specific or all debuffs
        pass
```

This system provides rich gameplay depth while maintaining clarity for the player!
