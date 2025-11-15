# Abilities Specification

## Core Movement Abilities

### 1. Double Jump (DOUBLE_JUMP)
- **Unlock Cost**: 5 orbs
- **Controls**: Press Jump while airborne
- **Effect**: Second jump in mid-air with 100% jump power
- **Cooldown**: None
- **Max Uses**: 1 per ground touch
- **Visual**: Blue energy burst from feet

### 2. Dash (DASH)
- **Unlock Cost**: 8 orbs
- **Controls**: Shift key
- **Effect**: Quick horizontal burst (16 units/frame) for 0.16s
- **Cooldown**: 0.45s
- **Direction**: Current facing direction
- **Visual**: Motion blur trail + speed lines

### 3. Wall Jump (WALL_JUMP)
- **Unlock Cost**: 12 orbs
- **Controls**: Press Jump while touching wall
- **Effect**: Launch away from wall (8.5x horizontal, 14.5y vertical power)
- **Cooldown**: None
- **Special**: Brief input lock after wall jump
- **Visual**: Wall spark particles

### 4. Slide (SLIDE)
- **Unlock Cost**: 15 orbs
- **Controls**: Crouch while running (S/Down + movement)
- **Effect**: Low-profile slide under obstacles, maintains momentum
- **Duration**: 0.8s or until speed < 3.0
- **Speed**: 1.3x current speed
- **Visual**: Dust trail particles

## Advanced Movement Abilities

### 5. Wall Cling (WALL_CLING)
- **Unlock Cost**: 18 orbs
- **Controls**: Hold movement toward wall while touching
- **Effect**: Stick to wall, slowly slide down (1 unit/frame)
- **Duration**: Unlimited
- **Stamina**: Optional stamina meter (5s)
- **Visual**: Hand glow effect on wall

### 6. Shadow Step (SHADOW_STEP)
- **Unlock Cost**: 25 orbs
- **Controls**: Q key
- **Effect**: Phase through walls/hazards for 0.75s, invulnerable
- **Charges**: 3 per level
- **Speed**: 18 units/frame
- **Cooldown**: 0.5s between uses
- **Visual**: Purple ghost trail, semi-transparent player

### 7. Air Dodge (AIR_DODGE)
- **Unlock Cost**: 30 orbs
- **Controls**: X key while airborne
- **Effect**: Quick directional dodge with brief invincibility (0.3s)
- **Direction**: 8-directional based on input
- **Cooldown**: 1.0s
- **Max Uses**: 2 per ground touch
- **Visual**: Flash step effect

### 8. Glide (GLIDE)
- **Unlock Cost**: 35 orbs
- **Controls**: Hold Jump while falling
- **Effect**: Slow descent (fall speed reduced to 2.0), horizontal control
- **Duration**: Unlimited while held
- **Speed Mod**: Horizontal speed 0.8x
- **Visual**: Energy wings emanating from back

### 9. Grappling Hook (GRAPPLE)
- **Unlock Cost**: 40 orbs
- **Controls**: E key + direction
- **Effect**: Shoot hook, pull to grapple points or swing
- **Range**: 15 tiles
- **Speed**: Pull speed 12 units/frame
- **Cooldown**: 0.3s
- **Visual**: Energy rope with hook projectile

### 10. Ground Pound (GROUND_POUND)
- **Unlock Cost**: 45 orbs
- **Controls**: Ctrl while airborne
- **Effect**: Fast downward slam, shockwave on impact
- **Speed**: 25 units/frame downward
- **Damage**: 3 damage to enemies in 3-tile radius
- **Utility**: Break special blocks, activate switches
- **Visual**: Downward thrust + ground crack effect

## Expert Abilities

### 11. Double Dash (DOUBLE_DASH)
- **Unlock Cost**: 50 orbs
- **Controls**: Shift twice rapidly
- **Effect**: Perform second dash in air without cooldown
- **Cooldown**: 2.0s after second dash
- **Requirement**: Must have unlocked Dash
- **Visual**: Enhanced trail with after-images

### 12. Time Slow (TIME_SLOW)
- **Unlock Cost**: 60 orbs
- **Controls**: Z key
- **Effect**: Slow game time to 0.3x for 3 seconds (player at 1.0x)
- **Charges**: 1 per level
- **Cooldown**: N/A (charge-based)
- **Visual**: Blue tint, trail effects on everything

### 13. Teleport (TELEPORT)
- **Unlock Cost**: 75 orbs
- **Controls**: R key + direction
- **Effect**: Instant teleport 5 tiles in direction (ignores walls)
- **Cooldown**: 3.0s
- **Max Uses**: 3 per level
- **Visual**: Vanish particles + reappear particles

### 14. Stomp Jump (STOMP_JUMP)
- **Unlock Cost**: 90 orbs
- **Controls**: Jump while landing on enemy
- **Effect**: Bounce high off enemy (1.5x jump power), damage enemy
- **Damage**: 2 damage
- **Bounce Height**: 1.5x normal jump
- **Chain**: Can chain stomp multiple enemies
- **Visual**: Downward thrust + bounce stars

## Passive Abilities (Always Active When Unlocked)

### 15. Coin Magnet (COIN_MAGNET)
- **Unlock Cost**: 20 orbs
- **Effect**: Attracts coins within 3 tiles radius
- **Visual**: Faint gold aura around player

### 16. Hazard Sense (HAZARD_SENSE)
- **Unlock Cost**: 35 orbs
- **Effect**: Hazards glow red when within 4 tiles
- **Visual**: Red pulse on hazards

### 17. Enemy Radar (ENEMY_RADAR)
- **Unlock Cost**: 55 orbs
- **Effect**: Show enemies on minimap, direction arrows for off-screen enemies
- **Visual**: Red arrows at screen edges

## Ability Synergies

### Combo Mechanics
- **Dash → Wall Jump**: Enhanced wall jump (1.2x power)
- **Double Jump → Ground Pound**: Extra damage (4 instead of 3)
- **Grapple → Dash**: Slingshot effect (2x dash speed)
- **Slide → Dash**: Slide maintains full dash speed
- **Time Slow → All abilities**: Better precision, easier combos

### Ability Trees (Future Expansion)
```
Movement Tree:
├─ Double Jump
│  ├─ Triple Jump (100 orbs)
│  └─ Infinite Jump (150 orbs)
├─ Dash
│  ├─ Double Dash
│  └─ Omni-Dash (125 orbs)
└─ Wall Jump
   ├─ Wall Cling
   └─ Wall Run (110 orbs)

Combat Tree:
├─ Ground Pound
│  ├─ Meteor Strike (120 orbs)
│  └─ Shockwave Pulse (140 orbs)
└─ Stomp Jump
   └─ Chain Stomp (105 orbs)

Utility Tree:
├─ Shadow Step
│  └─ Extended Phase (95 orbs)
├─ Time Slow
│  └─ Time Freeze (200 orbs)
└─ Teleport
   └─ Blink Strike (180 orbs)
```

## Implementation Priority

### Phase 1 (Core)
1. Double Jump
2. Dash
3. Wall Jump
4. Shadow Step

### Phase 2 (Advanced)
5. Slide
6. Wall Cling
7. Air Dodge
8. Glide

### Phase 3 (Expert)
9. Grappling Hook
10. Ground Pound
11. Double Dash

### Phase 4 (Master)
12. Time Slow
13. Teleport
14. Stomp Jump

### Phase 5 (Polish)
15-17. Passive abilities

## Balance Notes

- **Difficulty Scaling**: Higher difficulties reduce cooldowns and increase charges
- **Speedrun Mode**: All abilities unlocked, no cooldowns
- **Challenge Mode**: Disable specific abilities for extra rewards
- **Ability Loadouts**: Allow players to equip only 6 active abilities at once (strategic choice)
