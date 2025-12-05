# Hollowed Ninja Campaign - Complete Test Guide (Stage 5)

This guide provides comprehensive testing instructions for the complete Hollowed Ninja campaign system, including stats, equipment, hubs, and the full story arc from Act 0 to the ending.

## 🎮 Quick Start

```python
# In-game
1. Start the game
2. Select "Campaign" from main menu (or use debug command)
3. You'll start in Lantern Hub (Act 0)

# Debug Commands (in game code/console if available):
game.start_campaign()              # Start campaign at beginning
game.set_campaign_act(3, 0)       # Jump to Act 3 (Ember Hub with shop)
game.campaign_state.currency = 1000  # Add currency for testing shop
```

## 📋 Complete Test Checklist

### ✅ Part 1: Hub System & NPCs

**Test in Lantern Hub (Act 0):**
- [ ] Press A/D to move around hub
- [ ] Approach Elder Guide (yellow prompt appears: [E] Talk)
- [ ] Press E to talk, read dialogue
- [ ] Press SPACE to advance through dialogue lines
- [ ] Talk to all 3 NPCs (Elder Guide, Master Jin, Lorekeeper)
- [ ] Approach Mission Board (center-right)
- [ ] Press SPACE at Mission Board to start mission
- [ ] Complete mission (reach exit)
- [ ] Verify return to Lantern Hub after mission

**Test in Ember Hub (Act 3) - Equipment Shop:**
```python
# Jump to Ember Hub for shop testing:
game.set_campaign_act(3, 0)
game.campaign_state.currency = 1000
game.campaign_state.max_equipment_tier = 3
```

- [ ] Approach Smith Monk (orange NPC)
- [ ] Verify prompt shows [E] Shop (not "Talk")
- [ ] Press E to open shop
- [ ] Shop UI appears with equipment list
- [ ] Press W/S to navigate equipment
- [ ] Selected item highlights
- [ ] Stats preview shows at bottom
- [ ] Currency display shows fragments
- [ ] Press ENTER to purchase item
- [ ] Verify currency decreases
- [ ] Verify item shows [EQUIPPED]
- [ ] Press ESC to close shop
- [ ] Re-open shop, verify equipment still equipped

### ✅ Part 2: Stats & Equipment System

**Test Stat Application:**
```python
# Check current stats:
stats = game.campaign_state.get_total_stats()
print(f"HP: {stats.hp}, SPD: {stats.spd}, STG: {stats.stg}, DEF: {stats.def_}")

# Compare player speed before/after equipment:
print(f"Player speed: {game.player.user_max_speed}")
```

- [ ] Start mission, note player health bar
- [ ] Purchase armor, start new mission
- [ ] Verify health bar is longer (more HP)
- [ ] Purchase boots, start mission
- [ ] Verify player moves faster (higher SPD)
- [ ] Test with different equipment tiers (Basic → Forged → Blessed)

**Test Equipment Tiers:**
- [ ] Tier 1 (Basic) - Available from start (free items)
- [ ] Tier 2 (Forged) - Available after Act 2 boss
- [ ] Tier 3 (Blessed) - Available after Act 3 boss
- [ ] Tier 4 (Hollowed) - Available in Act 4

**Test All Equipment Slots:**
- [ ] Weapon: Training Blade → Forged Katana → Blessed Edge → Void Fang
- [ ] Armor: Cloth Gi → Iron Vest → Blessed Plate → Hollow Carapace
- [ ] Boots: Worn Sandals → Steel Greaves → Blessed Stride → Void Walkers
- [ ] Charm: Wooden Talisman → Ember Pendant → Sacred Amulet → Heart of Void

### ✅ Part 3: Currency System

**Test Currency Rewards:**
- [ ] Complete mission in Act 0, verify currency +50
- [ ] Complete mission in Act 1, verify currency +75
- [ ] Complete mission in Act 2, verify currency +100
- [ ] Complete mission in Act 3, verify currency +125
- [ ] Complete mission in Act 4, verify currency +150
- [ ] Verify currency persists across missions
- [ ] Verify currency survives death (return to hub)

**Formula:** `Currency = 50 + (act * 25)`

### ✅ Part 4: Complete Campaign Playthrough

**Act 0: Lantern Heights**
```
Theme: Welcoming tutorial
Hub: Lantern Hub
NPCs: Elder Guide, Master Jin, Lorekeeper
Biome: Golden/warm lanterns
Abilities: JUMP, ATTACK, WALL_JUMP, DASH
```
- [ ] Start campaign
- [ ] Talk to NPCs in Lantern Hub
- [ ] Complete 2-3 missions
- [ ] Verify smooth hub-mission-hub flow
- [ ] Collect ability orbs (no scroll system yet in Act 0)

**Act 1: Veil Maiden Boss Fight**
```
Theme: First major challenge
Abilities: Same as Act 0 (full kit for boss)
```
- [ ] Progress to Act 1 (trigger via story progression)
- [ ] Face Veil Maiden boss (narrative encounter)
- [ ] *Note: Boss is narrative, not fully implemented*

**Act 2: Hollow Depths**
```
Theme: Post-hollowing recovery
Hub: Hollow Hub
NPCs: Shade Hermit, Lost Warrior, Hollow Watcher
Biome: Dark purple/black with vignette
Abilities: JUMP, WEAK_ATTACK (weakened!)
Scrolls: clarity_sense (SHADOW_STEP), resilience_step (DOUBLE_JUMP), phase_drift (WALL_CLING)
```
- [ ] Enter Hollow Hub (dark, atmospheric)
- [ ] Note weakened abilities (no dash, weak attack)
- [ ] Complete missions, collect ability orbs
- [ ] Verify scroll fragments accumulate
- [ ] Unlock abilities from completed scrolls
- [ ] Verify abilities restore gradually

**Act 3: Ember Monastery**
```
Theme: Rebuilding power
Hub: Ember Hub
NPCs: Smith Monk (SHOP!), Listening Elder, Master Kenzo
Biome: Warm orange/red with forge glow
Abilities: JUMP, ATTACK (basic restored)
Scrolls: flame_dash (DASH), iron_form (SLIDE), sky_walker (GLIDE)
Equipment: Shop unlocked!
```
- [ ] Enter Ember Hub (warm, hopeful)
- [ ] Test equipment shop with Smith Monk
- [ ] Purchase upgrades with earned currency
- [ ] Complete missions with new equipment
- [ ] Verify stat bonuses apply (HP, SPD)
- [ ] Collect scrolls for advanced abilities

**Act 4: Skyroad Summit**
```
Theme: Final ascent
Hub: Sky Hub
NPCs: The Advocate, Peak Guardian, Weathered Monk
Biome: Airy blue with clouds
Abilities: JUMP, ATTACK, WALL_JUMP (near full power)
Scrolls: wind_step (AIR_DODGE), mountain_soul (CROUCH_JUMP_BOOST)
Boss: Hollow Reflection (Mission 3)
```
- [ ] Enter Sky Hub (lofty, climactic)
- [ ] Complete Mission 1
- [ ] Complete Mission 2
- [ ] Complete Mission 3 (triggers boss/ending)
- [ ] **Hollow Reflection defeated**
- [ ] **Ending cutscene triggers**

### ✅ Part 5: Ending Sequence

**Campaign Ending Cutscene:**
- [ ] Complete Act 4, Mission 3
- [ ] Boss defeat message appears
- [ ] Screen transitions to ending cutscene
- [ ] Scene 1: Hollow Reflection shatters, Inner Lantern emerges
- [ ] Scene 2: Beacon awakens, lanterns rekindle
- [ ] Scene 3: Hollow recedes, world breathes
- [ ] Scene 4: Summit, curse broken
- [ ] Scene 5: "Hollowed Ninja: Complete" title
- [ ] Verify SPACE skips to next scene
- [ ] Verify ESC returns to main menu
- [ ] Auto-return to menu after all scenes

**Visual Elements:**
- [ ] Background brightens with each scene
- [ ] Lantern glow in center grows stronger
- [ ] Text fades in smoothly
- [ ] Progress indicator shows scene count

### ✅ Part 6: Death & Game Over

**Test Death Handling:**
- [ ] Start campaign mission
- [ ] Die (fall in pit or take damage)
- [ ] Verify return to hub (NOT game over screen)
- [ ] Verify lives restored at hub
- [ ] Verify mission_index resets to 0
- [ ] Verify campaign progress kept (abilities, equipment, currency)

**Compare to Arcade Mode:**
- [ ] Start arcade game
- [ ] Die with 0 lives
- [ ] Verify proper game over screen (not hub)

### ✅ Part 7: Visual Themes

**Verify Each Hub's Unique Atmosphere:**

| Hub | Act | Background | Special FX | Color Palette |
|-----|-----|------------|-----------|---------------|
| Lantern Hub | 0, 1 | Warm welcoming | - | Golden/warm |
| Hollow Hub | 2 | Dark, oppressive | Vignette | Purple/black |
| Ember Hub | 3 | Monastery forge | Glow effect | Orange/red |
| Sky Hub | 4 | Mountain summit | Cloud effects | Airy blue |

- [ ] Test each hub's visual identity
- [ ] Verify special effects render correctly
- [ ] Confirm color themes match biome

**Verify Level Biomes Match Act:**
- [ ] Act 0 levels: Lantern biome (golden platforms)
- [ ] Act 2 levels: Hollow biome (dark purple)
- [ ] Act 3 levels: Ember biome (warm orange)
- [ ] Act 4 levels: Sky biome (airy blue)

### ✅ Part 8: Debug Commands

**Useful Debug Commands:**
```python
# Campaign navigation
game.start_campaign()                    # Start from beginning
game.set_campaign_act(2, 0)             # Jump to Act 2, Mission 0
game.campaign_state.act = 4             # Set act (0-4)
game.campaign_state.mission_index = 2   # Set mission

# Currency & Equipment
game.campaign_state.currency = 1000     # Add currency
game.campaign_state.max_equipment_tier = 4  # Unlock all tiers
game.campaign_state.purchase_equipment("void_fang")  # Buy specific item

# Stats viewing
stats = game.campaign_state.get_total_stats()
print(f"Total Stats: HP={stats.hp}, MP={stats.mp}, STM={stats.stm}")
print(f"STG={stats.stg}, DEF={stats.def_}, SPD={stats.spd:.2f}x, DEXT={stats.dext}")

# Equipment viewing
print(game.campaign_state.equipped_items)  # Current equipment

# Force ending
game.change_state("campaign_ending")    # Jump to ending cutscene

# Boss flags
game.campaign_state.on_boss_defeated("hollow_reflection")  # Mark boss beaten
```

## 🎯 Core Features Summary

### Implemented Systems:
✅ Campaign State Management (Acts 0-4)
✅ Hub States (Lantern, Hollow, Ember, Sky)
✅ NPC Dialogue System
✅ Mission Board (hub → mission → hub cycle)
✅ Stats System (HP, MP, STM, STG, DEF, SPD, DEXT)
✅ Equipment System (4 tiers × 4 slots = 16 pieces)
✅ Equipment Shop (Smith Monk in Ember Hub)
✅ Currency Rewards (50-150 fragments per mission)
✅ Stat Application (HP → health, SPD → speed)
✅ Boss Trigger (Act 4, Mission 3)
✅ Ending Cutscene (5 scenes, skipable)
✅ Death Handling (return to hub, preserve progress)

### Story Beats:
- Act 0: Tutorial and welcoming (Lantern Heights)
- Act 1: Veil Maiden boss (narrative)
- Act 2: Hollowing - player weakened, rebuilding via scrolls
- Act 3: Equipment upgrades, forge, monk training
- Act 4: Final ascent, peak preparation
- Final Boss: Hollow Reflection (Mission 3 of Act 4)
- Ending: Beacon restored, Inner Lantern achieved

## 🐛 Known Issues / Future Enhancements

**Current Implementation:**
- Boss fight is narrative (triggers ending after Act 4 Mission 3)
- No special boss enemy AI (simple mission completion)
- Equipment costs are placeholder values
- Stats affect HP and SPD directly, STG/DEF are stored but not deeply integrated into combat

**Future Enhancements:**
- Boss entity with custom AI and phases
- More combat integration for STG/DEF stats
- Equipment visual changes on player sprite
- Save/load campaign progress
- Campaign-specific achievements

## 📊 Quick Reference Tables

### Currency Per Act:
| Act | Reward |
|-----|--------|
| 0 | 50 |
| 1 | 75 |
| 2 | 100 |
| 3 | 125 |
| 4 | 150 |

### Equipment Costs:
| Tier | Name | Cost |
|------|------|------|
| 1 | Basic | 0 |
| 2 | Forged | 100 |
| 3 | Blessed | 250 |
| 4 | Hollowed | 500 |

### Base Stats By Act:
| Act | HP | MP | STM | STG | DEF | SPD | DEXT |
|-----|----|----|-----|-----|-----|-----|------|
| 0 | 100 | 50 | 50 | 10 | 5 | 1.0x | 10 |
| 2 | 80 | 30 | 30 | 5 | 3 | 0.9x | 5 |
| 3 | 120 | 60 | 60 | 12 | 8 | 1.05x | 12 |
| 4 | 150 | 80 | 80 | 15 | 10 | 1.1x | 15 |

---

**Test Duration:** Full campaign ~30-45 minutes
**Key Test Path:** Act 0 → Act 3 (shop) → Act 4 → Ending
**Critical Features:** Hub system, Shop, Stats, Ending
