# 🎮 Hollowed Ninja Campaign - Test Guide

This guide walks you through testing the new campaign system and verifying all implemented features work correctly.

---

## Prerequisites

1. **Environment Setup:**
   ```bash
   cd /home/user/ninja_dash_prototype
   source venv/bin/activate  # Activate virtual environment
   ```

2. **Run the Game:**
   ```bash
   python main.py --env=test
   ```

   This runs in TEST mode with console output visible and debug features enabled.

---

## Test 1: Campaign Menu Option ✅

**Goal:** Verify the Campaign button appears and launches campaign mode

**Steps:**
1. Start the game
2. Observe the main menu
3. Verify "📖 Campaign" button appears (should be second or third option)
4. Click "📖 Campaign"

**Expected Results:**
- Campaign button is visible and clickable
- Console shows: `🎮 Campaign started: Lantern Heights - Act 0`
- Game transitions to Play state
- Level generates and is playable

**What to Check:**
- Level should have **golden-colored tiles** (Lantern biome)
- Background should be **dark blue-black** (10, 10, 20)
- Exit portal should be **golden** (255, 220, 120) when unlocked

---

## Test 2: Act 0 - Lantern Heights (Welcoming) 🏮

**Goal:** Verify Act 0 has the correct feel and configuration

**How to Test:**
1. Start Campaign mode
2. Play through a level

**Expected Characteristics:**
- **Visual:**
  - Golden/warm tile colors (200, 180, 120)
  - Dark blue-black background
  - Golden exit portal

- **Level Design:**
  - Mostly **horizontal** layout (low verticality)
  - Wide platforms (4-8 tiles)
  - Not too cramped
  - Exit at **right edge** of final room

- **Gameplay:**
  - 10-18 coins per level
  - Low hazard density
  - 40% coin collection requirement for exit
  - 2 extra lives per level

- **Abilities:**
  - Console should show base abilities: `{'JUMP', 'ATTACK', 'WALL_JUMP', 'DASH'}`

**Pass Criteria:**
- ✅ Level feels open and welcoming
- ✅ Colors match Lantern theme
- ✅ Exit is accessible at right edge
- ✅ Player has full starting ability set

---

## Test 3: Act 2 - Hollow Depths (Cramped) 💀

**Goal:** Verify Act 2 has the harsh, vertical feel

**How to Test:**
1. Start game, press F1 to open console (if available)
2. In Python console or by modifying code, run:
   ```python
   # Option A: Add this to a debug menu or pause menu
   game.set_campaign_act(2, 0)

   # Option B: Restart campaign and manually set act
   # Edit core/game.py start_campaign() to set act=2 temporarily
   ```

**Expected Characteristics:**
- **Visual:**
  - **Deep purple-gray tiles** (40, 40, 70)
  - Very dark purple-black background (5, 5, 15)
  - Purple exit portal (120, 0, 150)

- **Level Design:**
  - **Very vertical** (70% verticality bias)
  - Narrow platforms (3-6 tiles)
  - Cramped feeling with lots of pillars
  - Exit at **center of floor** (not right edge)

- **Gameplay:**
  - Only 10-16 coins
  - Higher hazard density
  - 50% coin requirement
  - Only 1 extra life per level

- **Abilities (if hollowed):**
  - Only `{'JUMP', 'WEAK_ATTACK'}` - very limited!

**Pass Criteria:**
- ✅ Level feels cramped and vertical
- ✅ Purple/dark color palette
- ✅ Exit in center of room, not right edge
- ✅ Noticeably harder than Act 0

---

## Test 4: Act 3 - Ember Monastery (Balanced) 🔥

**Goal:** Verify Act 3 has monastery feel with balanced gameplay

**How to Test:**
```python
game.set_campaign_act(3, 0)
```

**Expected Characteristics:**
- **Visual:**
  - **Burnt orange-brown tiles** (150, 80, 40)
  - Dark reddish-brown background (20, 10, 5)
  - Orange-red exit portal (255, 150, 80)

- **Level Design:**
  - Balanced verticality (50%)
  - Medium platforms (4-9 tiles)
  - Mixed horizontal and vertical sections
  - Exit at **right edge** (Mission 0) or **top-center** (Mission 1)

- **Gameplay:**
  - 16-24 coins (more rewards)
  - 65% coin requirement
  - Moderate hazard density

- **Abilities:**
  - Base: `{'JUMP', 'ATTACK'}`
  - Can unlock: Dash, Slide, Glide via scrolls

**Pass Criteria:**
- ✅ Warm orange/red color scheme
- ✅ Balanced between horizontal and vertical
- ✅ Feels like rebuilding power
- ✅ More coins than Hollow

---

## Test 5: Act 4 - Skyroad Summit (Extreme Vertical) ☁️

**Goal:** Verify Act 4 is extremely vertical with summit exit

**How to Test:**
```python
game.set_campaign_act(4, 0)
```

**Expected Characteristics:**
- **Visual:**
  - **Light sky blue tiles** (180, 220, 255)
  - Dark blue-gray background (15, 25, 40)
  - Cyan-white exit portal (200, 255, 255)

- **Level Design:**
  - **Extreme verticality** (90%!)
  - Exit at **very top of world** (y=1)
  - Requires climbing to summit
  - Narrow vertical paths

- **Gameplay:**
  - 18-28 coins
  - 70% coin requirement
  - Score multiplier: 2.0x

- **Abilities:**
  - Base: `{'JUMP', 'ATTACK', 'WALL_JUMP'}`
  - Can unlock: Air Dodge, advanced movement

**Pass Criteria:**
- ✅ Sky/cloud color theme
- ✅ Exit is at very top of level
- ✅ Requires significant vertical climbing
- ✅ Highest coin multiplier

---

## Test 6: Ability Orbs & Scroll Fragments 📜

**Goal:** Verify ability orb collection adds scroll fragments

**How to Test:**
1. Start campaign in Act 2 (has scrolls):
   ```python
   game.set_campaign_act(2, 0)
   ```
2. Play until you find an **Ability Orb** (glowing rainbow orb)
3. Collect it
4. Watch console output

**Expected Results:**
- Console shows: `📜 Scroll fragment collected: [scroll_id] (1/4)`
  - Example: `clarity_sense (1/4)` for Shadow Step scroll
  - Note: Some scrolls need 4 fragments, others need 3

- After collecting 4 fragments of same scroll:
  - Console shows: `✨ SHADOW_STEP unlocked from scroll: clarity_sense!`
  - Ability is immediately available

**Act 2 Scrolls (3 available):**
- `clarity_sense` → SHADOW_STEP (4 fragments)
- `resilience_step` → DOUBLE_JUMP (3 fragments)
- `phase_drift` → WALL_CLING (3 fragments)

**Act 3 Scrolls:**
- `flame_dash` → DASH (4 fragments)
- `iron_form` → SLIDE (3 fragments)
- `sky_walker` → GLIDE (3 fragments)

**Act 4 Scrolls:**
- `wind_step` → AIR_DODGE (4 fragments)
- `mountain_soul` → CROUCH_JUMP_BOOST (3 fragments)

**Pass Criteria:**
- ✅ Collecting orb shows scroll progress
- ✅ Completing scroll unlocks ability
- ✅ Acts 0 and 1 show "No scrolls available" message
- ✅ Each act has different scrolls

---

## Test 7: Exit Placement Styles 🚪

**Goal:** Verify exit gates appear in different locations per act

**Visual Reference:**

```
Act 0 (right_edge):          Act 2 (center_floor):       Act 4 (world_top):
┌──────────────────┐         ┌──────────────────┐        ┌────────🚪────────┐
│                  │         │                  │        │                  │
│              🚪  │         │         🚪        │        │                  │
│                  │         │                  │        │                  │
│                  │         └──────────────────┘        │                  │
└──────────────────┘                                     └──────────────────┘
  Exit at right edge          Exit at center floor       Exit at world top
```

**How to Test:**
1. Test each act and note exit position:
   - **Act 0:** Exit at right edge of room
   - **Act 1:** Exit at center of room floor (boss arena)
   - **Act 2:** Exit at center or top-center
   - **Act 3:** Exit at right edge or top-center
   - **Act 4:** Exit at very top of world (summit!)

**Pass Criteria:**
- ✅ Each exit style is visually distinct
- ✅ Summit exits (Act 4) require climbing to top
- ✅ Center exits (Act 1/2) feel like arena/descent

---

## Test 8: Biome Color Transitions 🎨

**Goal:** Verify smooth visual transitions between biomes

**Quick Color Test:**
1. Start Act 0 - note golden/warm colors
2. Switch to Act 2 - should feel cold/dark/purple
3. Switch to Act 3 - should feel warm/fiery
4. Switch to Act 4 - should feel airy/bright

**Color Reference Chart:**

| Biome | Background RGB | Tiles RGB | Exit RGB | Feel |
|-------|---------------|-----------|----------|------|
| Lantern | (10,10,20) | (200,180,120) | (255,220,120) | Warm, golden |
| Hollow | (5,5,15) | (40,40,70) | (120,0,150) | Cold, purple |
| Ember | (20,10,5) | (150,80,40) | (255,150,80) | Hot, orange |
| Sky | (15,25,40) | (180,220,255) | (200,255,255) | Airy, cyan |

**Pass Criteria:**
- ✅ Each biome has distinct visual identity
- ✅ Colors match the thematic intent
- ✅ Transitions feel natural

---

## Test 9: Arcade Mode Still Works 🕹️

**Goal:** Ensure arcade mode is unaffected by campaign changes

**How to Test:**
1. From main menu, select "🆕 New Game" (NOT Campaign)
2. Play a level

**Expected Results:**
- Level generates normally
- Uses difficulty-based configs (not act-based)
- Always uses Lantern biome (default)
- Ability orbs use unlock manager (not scrolls)
- Exit always at right edge

**Pass Criteria:**
- ✅ Arcade mode unchanged
- ✅ No campaign features active
- ✅ Original gameplay preserved

---

## Test 10: Console Debug Output 🖥️

**Goal:** Verify console shows useful debug info

**How to Test:**
1. Run with `--env=test` for console output
2. Start campaign
3. Watch console

**Expected Console Output:**

```
🎮 Campaign started: Lantern Heights - Act 0
   Biome: lantern
   Base abilities: {'JUMP', 'ATTACK', 'WALL_JUMP', 'DASH'}

# When collecting ability orb in Act 2:
📜 Scroll fragment collected: clarity_sense (1/4)
📜 Scroll fragment collected: clarity_sense (2/4)
📜 Scroll fragment collected: clarity_sense (3/4)
📜 Scroll fragment collected: clarity_sense (4/4)
✨ SHADOW_STEP unlocked from scroll: clarity_sense!

# When switching acts:
🎮 Campaign set to: Act 2 - Hollow Depths (Mission 0)
   Biome: hollow
   Base abilities: {'JUMP', 'WEAK_ATTACK'}
```

**Pass Criteria:**
- ✅ Console shows campaign start
- ✅ Scroll progress is visible
- ✅ Ability unlocks are announced
- ✅ Act switches show info

---

## Quick Test Checklist ☑️

Use this for rapid verification:

- [ ] Campaign menu button appears
- [ ] Campaign starts in Act 0 (Lantern)
- [ ] Act 0: Golden colors, horizontal, easy
- [ ] Act 2: Purple colors, vertical, hard
- [ ] Act 3: Orange colors, balanced
- [ ] Act 4: Blue colors, extreme vertical
- [ ] Ability orbs add scroll fragments
- [ ] Completing scrolls unlocks abilities
- [ ] Exit styles vary by act
- [ ] Biome colors are distinct
- [ ] Arcade mode still works
- [ ] Console output is helpful

---

## Debug Commands for Testing

If you add a debug console or pause menu, these commands are useful:

```python
# Switch to different acts
game.set_campaign_act(0, 0)  # Lantern Heights
game.set_campaign_act(2, 0)  # Hollow Depths
game.set_campaign_act(3, 0)  # Ember Monastery
game.set_campaign_act(4, 0)  # Skyroad Summit

# Check current campaign state
print(f"Act: {game.campaign_state.act}")
print(f"Mission: {game.campaign_state.mission_index}")
print(f"Biome: {game.current_biome}")
print(f"Abilities: {game.abilities}")
print(f"Scroll fragments: {game.campaign_state.scroll_fragments}")
print(f"Unlocked abilities: {game.campaign_state.abilities_unlocked}")

# Manually add scroll fragment (for testing)
from core.campaign import get_required_fragments_for_scroll
game.campaign_state.add_scroll_fragment("clarity_sense", 4)

# Simulate hollowing (Veil Maiden defeat)
game.campaign_state._trigger_hollowing()
```

---

## Known Limitations (Future Work)

These features are **not yet implemented** (coming in Stages 4-5):

- ❌ Hub states (no Lantern/Hollow/Ember/Sky hubs yet)
- ❌ NPCs and dialogue
- ❌ Boss fights (Veil Maiden, etc.)
- ❌ Stats system (HP, MP, STM, etc.)
- ❌ Equipment tiers
- ❌ Story cutscenes
- ❌ Mission progression (currently only 1 mission per act works)

For now, **focus on testing level generation, biomes, and scroll fragments**.

---

## Troubleshooting

**Problem:** Campaign button doesn't appear
- **Solution:** Check that `states/menus/menu.py` was updated correctly

**Problem:** Wrong colors/biome
- **Solution:** Verify `game.current_biome` is set correctly in console

**Problem:** Exit in wrong location
- **Solution:** Check `config.exit_style` in console output

**Problem:** Ability orbs don't give scroll fragments
- **Solution:** Verify you're in campaign mode (not arcade mode)
- Check console for "No scrolls available" message (Acts 0/1)

**Problem:** Can't switch acts manually
- **Solution:** Use `game.set_campaign_act()` from debug console
- Or temporarily modify `start_campaign()` to set different act

---

## Reporting Issues

When reporting issues, please include:

1. **What you were testing** (which test case)
2. **Expected result** (from this guide)
3. **Actual result** (what happened instead)
4. **Console output** (copy relevant lines)
5. **Screenshots** (especially for visual issues)

Example:
```
Test: Act 2 - Hollow Depths
Expected: Purple tiles (40,40,70)
Actual: Golden tiles still showing
Console: "Biome: hollow" shows correctly
Screenshot: [attach]
```

---

## Next Steps After Testing

Once these tests pass, we'll implement:

1. **Stage 4:** Hub states with NPCs
2. **Stage 5:** Stats, equipment, and bosses

**Happy testing! 🥷**
