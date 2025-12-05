# UI/UX Testing Guide - Ninja Dash

## Purpose
This guide provides systematic testing steps for evaluating the user interface, menu flows, controls, tooltips, and overall user experience. Use this to identify bugs, usability issues, and areas for improvement.

---

## 🧪 Testing Environment Setup

### Prerequisites
1. Launch the game: `python main.py`
2. Have a notepad ready for recording issues
3. Test with both keyboard and mouse
4. Test at default resolution (1280x720)

### What to Focus On
- **Navigation Flow**: Can you get where you need to go intuitively?
- **Visual Clarity**: Is information easy to read and understand?
- **Feedback**: Does the UI respond to your actions?
- **Consistency**: Do similar elements behave similarly?
- **Errors**: Missing labels, overlapping text, confusing interactions

---

## 📋 Section 1: Main Menu Flow

### Test Steps

#### 1.1 Initial Menu Screen
- [ ] **Launch the game** and observe the main menu
- [ ] **Check title positioning** - Is "NINJA DASH" centered and visible?
- [ ] **Count the menu buttons** - How many are visible?
- [ ] **Read each button label** - Are they clear and understandable?

**Look for:**
- Emoji rendering issues (boxes instead of emojis)
- Button text truncation
- Inconsistent button sizes
- Buttons too close together or overlapping
- Unclear button order/priority

**Document:**
```
Issue: [What you see]
Expected: [What should happen]
Screenshot: [If possible]
```

#### 1.2 Button Hover States
- [ ] **Hover over each button** with mouse
- [ ] **Observe color changes** - Does the button highlight?
- [ ] **Move cursor between buttons** - Are transitions smooth?
- [ ] **Hover on button edges** - Is the hitbox accurate?

**Look for:**
- No hover feedback
- Delayed hover response
- Hover state incorrect color (too similar to normal state)
- Hitbox too small or too large

#### 1.3 Button Click Feedback
- [ ] **Click and hold** a button - Does it show pressed state?
- [ ] **Release on button** - Does action trigger?
- [ ] **Click and drag off button** - Does it cancel properly?
- [ ] **Double-click buttons** - Any unexpected behavior?

**Look for:**
- No visual pressed state
- Action triggers on press instead of release
- Can accidentally trigger actions
- Buttons stay highlighted after click

#### 1.4 Navigation to Sub-Menus
Test each menu option:

- [ ] **▶ Continue** (if save exists)
  - Does it load your save properly?
  - Any loading indicator?

- [ ] **📖 Campaign**
  - Goes to hub world?
  - Can you return to main menu?

- [ ] **🆕 New Game**
  - Starts arcade mode?
  - Any confirmation dialog?

- [ ] **🎲 Custom Seed Run**
  - Opens seed entry screen?
  - Clear instructions?

- [ ] **🏆 High Scores**
  - Displays scores correctly?
  - Easy to read?

- [ ] **⭐ Unlocks**
  - Shows progression clearly?
  - Locked abilities visible?

- [ ] **⚙ Options**
  - Opens settings menu?

- [ ] **❓ Help**
  - Provides useful info?

- [ ] **✕ Quit**
  - Exits cleanly?
  - Any confirmation?

**Look for:**
- Wrong state transition
- No way to go back
- Crash on selection
- Missing content in sub-menus
- Confusing navigation

---

## 📋 Section 2: Options & Settings Menu

### Test Steps

#### 2.1 Options Menu Structure
- [ ] **Open Options** from main menu
- [ ] **Identify tabs or sections** - What categories exist?
- [ ] **Try to navigate** between sections
- [ ] **Look for a back button** - Can you return to main menu?

**Look for:**
- Missing back/return option
- Unclear tab labels
- Can't tell which section is active
- Settings grouped illogically

#### 2.2 Control Rebinding
- [ ] **Find controls section** in options
- [ ] **Identify rebind interface** - How do you change keys?
- [ ] **Try rebinding a key**:
  1. Select an action (e.g., "Jump")
  2. Press a new key
  3. Confirm the change
  4. Test in game
- [ ] **Try binding to an already-used key** - What happens?
- [ ] **Try binding invalid keys** (Escape, etc.)
- [ ] **Reset to defaults** - Is there an option?

**Look for:**
- No way to rebind controls
- Unclear which action you're rebinding
- Conflicts not detected or handled
- Can't see current bindings
- Changes don't persist
- No confirmation of successful rebind
- Can bind to system keys (Escape, Alt+F4, etc.)

#### 2.3 Visual Settings (if available)
- [ ] **Fullscreen toggle** - Does it work?
- [ ] **Resolution options** - Any choices?
- [ ] **Graphics quality** - Effects noticeable?

**Look for:**
- Settings that don't apply
- Need to restart for changes
- No visual feedback

#### 2.4 Audio Settings (if available)
- [ ] **Volume sliders** - Do they work?
- [ ] **Mute toggles** - Effective?
- [ ] **Test audio** - Hear changes immediately?

**Look for:**
- Sliders that don't affect volume
- No way to test audio
- Volume ranges incorrect (0-100 vs 0-1)

---

## 📋 Section 3: In-Game HUD

### Test Steps

#### 3.1 HUD Startup
- [ ] **Start a new game** (arcade or campaign)
- [ ] **Wait for game to load**
- [ ] **Observe the HUD** at game start

**Document what you see:**
```
Top-left: [What's displayed]
Top-center: [What's displayed]
Top-right: [What's displayed]
Other areas: [Any floating elements]
```

**Look for:**
- Missing HUD elements
- Overlapping text/icons
- Unreadable fonts (too small, low contrast)
- Elements off-screen or cut off
- Placeholder text ("PLACEHOLDER", "TODO", etc.)

#### 3.2 Score & Progress Section (Top-Left)
- [ ] **Locate score display**
- [ ] **Collect a coin** - Does score update?
- [ ] **Find coin progress bar** - Is it visible?
- [ ] **Collect more coins** - Does bar fill?
- [ ] **Reach required coins** - Does bar change color/indicate ready?

**Look for:**
- Score doesn't update
- Progress bar not visible or unclear
- Can't tell how many coins needed
- Text overlaps with bar
- Numbers truncated or formatted poorly

#### 3.3 Vitals Section (Health & Lives)
- [ ] **Locate health display** - Hearts, bars, or numbers?
- [ ] **Take damage** - Does health update?
- [ ] **Die and respawn** - Do lives decrease?
- [ ] **Find stamina bar** (if dash unlocked)

**Look for:**
- Health not visible or unclear
- Wrong max health shown
- Lives counter missing
- Stamina bar missing when dash is unlocked
- Visual states unclear (full vs empty hearts)

#### 3.4 Level Info Section
- [ ] **Find level number** - Displayed clearly?
- [ ] **Find difficulty indicator** - Easy, Medium, Hard, Expert?
- [ ] **Advance to next level** - Does number update?

**Look for:**
- Level number missing
- Difficulty not shown
- Info not updated between levels

#### 3.5 Time & Abilities Display
- [ ] **Locate game timer** - Running correctly?
- [ ] **Find ability indicators** - What format?
- [ ] **Unlock an ability** - Does it appear in HUD?
- [ ] **Count ability slots** - How many visible?

**Look for:**
- Timer not visible
- Timer not running or running incorrectly
- Ability indicators missing
- Can't tell which abilities are unlocked
- Abbreviations unclear ("WJ" = Wall Jump?)
- More than 6 abilities causing overflow

#### 3.6 Ability Progress Section
- [ ] **Find "Next Unlock" section** - Visible?
- [ ] **Check current orb count** - Displayed?
- [ ] **Find progress bar** - Shows progress to next unlock?
- [ ] **Collect an ability orb** - Does count update?

**Look for:**
- Section missing or unclear
- Can't see next ability name
- Progress bar confusing
- Orb count not updating
- No indication of cost

#### 3.7 Powerup Indicators
- [ ] **Collect a speed boost powerup**
- [ ] **Look for timer indicator** - Where does it appear?
- [ ] **Observe countdown** - Smooth or jumpy?
- [ ] **Collect multiple powerups** - Do they stack visually?

**Look for:**
- No powerup indicators
- Indicators overlap
- Can't tell time remaining
- Unclear which powerup is which

#### 3.8 Ability Resource Bars
- [ ] **Use Shadow Step** (if unlocked) - See charges?
- [ ] **Use Air Dodge** (if unlocked) - See uses remaining?
- [ ] **Regenerate charges** - Visual update?

**Look for:**
- Resource bars missing
- Can't tell current charges
- Bars don't update when abilities used
- Confusing placement (overlapping other UI)

---

## 📋 Section 4: Pause Menu & In-Game Menus

### Test Steps

#### 4.1 Accessing Pause Menu
- [ ] **Press ESC** during gameplay
- [ ] **Observe pause menu** appearance
- [ ] **Check game state** - Did game actually pause?

**Look for:**
- Game doesn't pause
- Menu doesn't appear
- Menu partially transparent (can't read)
- Game still running in background

#### 4.2 Pause Menu Options
- [ ] **Count menu items** - What options available?
- [ ] **Test "Resume"** - Returns to game?
- [ ] **Test "Options"** - Opens settings?
- [ ] **Test "Controls"** - Shows controls viewer?
- [ ] **Test "Debug"** (if available) - Opens debug menu?
- [ ] **Test "Quit to Menu"** - Returns to main menu?

**Look for:**
- Options don't work
- Can't return to game
- Quit doesn't confirm (lose progress?)
- Options overlap with game elements

#### 4.3 Controls Viewer
- [ ] **Open Controls** from pause menu
- [ ] **Scan for all controls** - Movement, abilities, UI, debug
- [ ] **Check if custom bindings shown** - If you rebound keys
- [ ] **Look for close/back option**

**Look for:**
- Controls not organized by category
- Custom bindings not reflected
- Missing controls
- Overlapping text
- Can't close controls viewer
- Scrolling needed but not available

#### 4.4 Debug Menu (F-keys)
- [ ] **Press F3** - Toggle debug overlay
- [ ] **Press F4** - Toggle hitboxes
- [ ] **Press F5** - Reload level
- [ ] **Press Tab** (during F3) - Toggle overlay mode

**Look for:**
- Debug overlays missing
- Overlays obstruct gameplay
- Hitboxes incorrect or not showing
- Level reload doesn't work
- Debug info overwhelming

---

## 📋 Section 5: Campaign Hub & NPCs

### Test Steps

#### 5.1 Hub Navigation
- [ ] **Start campaign mode**
- [ ] **Observe hub world** - Where are you?
- [ ] **Look for NPCs** - Any characters to talk to?
- [ ] **Find mission board** - How to start missions?
- [ ] **Find shop** (if available) - How to access?

**Look for:**
- No guidance on what to do
- NPCs not clearly marked
- Can't tell who is interactable
- No indication of objective

#### 5.2 NPC Interactions
- [ ] **Approach an NPC** - Any indicator to interact?
- [ ] **Press interact key** - Opens dialogue?
- [ ] **Read dialogue** - Readable and formatted well?
- [ ] **Navigate dialogue options** - Clear choices?
- [ ] **Exit dialogue** - Easy to leave?

**Look for:**
- No visual prompt to interact (e.g., "Press E")
- Dialogue box too small or large
- Text overflow or cut off
- Can't tell who's speaking
- Choices unclear
- Can't close dialogue
- Softlock if dialogue bugs

#### 5.3 Shop Interface
- [ ] **Open shop** (talk to merchant NPC)
- [ ] **View items for sale** - Clear presentation?
- [ ] **Check your currency** - Displayed prominently?
- [ ] **Attempt to buy item** - Purchase flow clear?
- [ ] **Try buying without enough money** - Proper feedback?
- [ ] **Exit shop** - Return to hub?

**Look for:**
- Can't see prices
- Currency not displayed
- Can't tell what items do
- No confirmation on purchase
- Can buy items you can't afford
- Items not applied after purchase

#### 5.4 Mission Board
- [ ] **Access mission board**
- [ ] **View available missions** - List or menu?
- [ ] **Select a mission** - See mission details?
- [ ] **Start mission** - Transitions to gameplay?
- [ ] **Complete or fail mission** - Return to hub?

**Look for:**
- Mission details unclear
- Can't tell difficulty or rewards
- No confirmation before starting
- Can't return to hub without completing
- Progress not saved

---

## 📋 Section 6: Tooltips & Contextual Help

### Test Steps

#### 6.1 Button Tooltips
- [ ] **Hover over buttons** in menus - Any tooltips appear?
- [ ] **Wait on hover** - Delayed or instant?
- [ ] **Move between buttons** - Tooltips update?

**Look for:**
- No tooltips where expected
- Tooltips appear off-screen
- Tooltips overlap other UI
- Tooltips don't disappear

#### 6.2 HUD Element Tooltips
- [ ] **Hover over ability icons** - Explain what they are?
- [ ] **Hover over health/stamina** - Additional info?
- [ ] **Hover over powerup timers** - Details?

**Look for:**
- No in-game tooltips
- Tooltips obstruct view
- Information not helpful

#### 6.3 First-Time Guidance
- [ ] **Start new game** - Any tutorial or hints?
- [ ] **Unlock first ability** - Explanation provided?
- [ ] **Find first powerup** - Told what it does?

**Look for:**
- No onboarding for new players
- Abilities unlocked without explanation
- Controls not introduced

---

## 📋 Section 7: Controls & Input

### Test Steps

#### 7.1 Movement Controls
- [ ] **Press Arrow Keys** - Character moves?
- [ ] **Press WASD** - Alternative movement works?
- [ ] **Press Space** - Jump?
- [ ] **Press Down while airborne** - Fast fall?

**Look for:**
- Keys don't respond
- Delayed input
- Double-press required
- Conflicts between arrow and WASD

#### 7.2 Ability Controls
For each unlocked ability:
- [ ] **Shadow Step (Q)** - Activates?
- [ ] **Grapple Hook (E)** - Works?
- [ ] **Air Dodge (C)** - Responsive?
- [ ] **Slide (V)** - Executes?
- [ ] **Dash (Shift)** - Speed boost?

**Look for:**
- Abilities don't trigger
- Wrong ability activates
- No visual/audio feedback
- Cooldowns not clear
- Can't tell if ability is available

#### 7.3 UI Navigation Controls
- [ ] **ESC** - Pause/back
- [ ] **F1** - Help (if available)
- [ ] **Tab** - Inventory/map (if available)
- [ ] **Mouse click** - Select buttons
- [ ] **Arrow keys** in menus - Navigate options?
- [ ] **Enter** in menus - Confirm selection?

**Look for:**
- ESC doesn't work consistently
- Can't navigate menus with keyboard
- Mouse required for all interactions
- Keyboard navigation skips elements

#### 7.4 Control Consistency
- [ ] **ESC in main menu** - Quit game
- [ ] **ESC in gameplay** - Pause menu
- [ ] **ESC in submenu** - Go back
- [ ] **ESC in dialogue** - Close dialogue

**Look for:**
- ESC does different things in similar contexts
- No way to go back in some screens
- Inconsistent confirm/cancel keys

---

## 📋 Section 8: Visual Clarity & Readability

### Test Steps

#### 8.1 Font Sizes
- [ ] **Read menu text** - Comfortable size?
- [ ] **Read HUD text** - Legible during gameplay?
- [ ] **Read dialogue** - Easy to read?
- [ ] **View from typical distance** - Still clear?

**Look for:**
- Text too small to read
- Inconsistent font sizes
- Important info in small font

#### 8.2 Color Contrast
- [ ] **Check text on backgrounds** - Enough contrast?
- [ ] **View health when low** - Red on red?
- [ ] **Colorblind consideration** - Only color-coded info?

**Look for:**
- Low contrast text (gray on dark gray)
- Similar colors for different states
- No alternative to color-coding

#### 8.3 Icon Clarity
- [ ] **Identify ability icons** - Recognizable?
- [ ] **Distinguish powerups** - Clear differences?
- [ ] **UI button icons** - Meaningful?

**Look for:**
- Icons too similar
- Abstract icons without labels
- Emoji as critical UI elements (may not render)

---

## 📋 Section 9: Edge Cases & Stress Testing

### Test Steps

#### 9.1 Rapid Input
- [ ] **Spam click buttons** - Double-trigger?
- [ ] **Mash ability keys** - Game lag?
- [ ] **Rapid menu navigation** - UI keeps up?

**Look for:**
- Actions trigger multiple times
- Game freezes
- UI elements duplicate

#### 9.2 Long Play Session
- [ ] **Play for 10+ minutes**
- [ ] **Unlock multiple abilities**
- [ ] **Collect many powerups**
- [ ] **Progress several levels**

**Look for:**
- HUD elements overlap over time
- Memory leaks (performance degradation)
- UI elements not clearing

#### 9.3 Unusual Sequences
- [ ] **Open pause, then options, then back, then resume**
- [ ] **Start mission, quit immediately, start another**
- [ ] **Buy item, immediately buy another**
- [ ] **Rebind controls during gameplay**

**Look for:**
- State confusion
- Softlocks (can't progress)
- Lost progress
- UI stuck

---

## 🐛 Bug Reporting Template

When you find an issue, document it like this:

### Bug Report

**Title:** [Short, descriptive title]

**Severity:**
- 🔴 Critical (game crashes, softlock, data loss)
- 🟠 Major (feature broken, major UX issue)
- 🟡 Minor (cosmetic, minor annoyance)
- 🔵 Enhancement (nice-to-have improvement)

**Category:**
- [ ] Menu/Navigation
- [ ] HUD/Display
- [ ] Controls/Input
- [ ] Visual/Clarity
- [ ] Performance
- [ ] Other: ___________

**Description:**
[What happened? Be specific.]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [Result]

**Expected Behavior:**
[What should happen instead?]

**Actual Behavior:**
[What actually happened?]

**Screenshot/Video:**
[If available]

**Additional Context:**
[Any other relevant info]

---

## 📊 UX Feedback Categories

### Navigation & Flow
**Questions to ask:**
- Can I get where I want in 3 clicks or less?
- Is the back button always obvious?
- Do I know where I am in the menu structure?
- Can I access settings from anywhere?

### Information Density
**Questions to ask:**
- Is the screen too cluttered or too sparse?
- Can I find critical info quickly (health, ammo, etc.)?
- Is there irrelevant info taking up space?
- Am I overwhelmed by numbers/stats?

### Affordances & Signifiers
**Questions to ask:**
- Can I tell what's clickable vs non-clickable?
- Do buttons look like buttons?
- Are interactive elements highlighted on hover?
- Do I know what an icon/button will do before clicking?

### Feedback & Response
**Questions to ask:**
- Does the UI acknowledge my actions?
- Are loading states indicated?
- Do I know when something succeeds or fails?
- Is error messaging helpful or cryptic?

### Consistency
**Questions to ask:**
- Do similar actions work the same way everywhere?
- Are colors/icons used consistently?
- Is the visual style unified?
- Are keybindings consistent?

---

## 💡 Common UI/UX Issues to Watch For

### Menu Issues
- ❌ No way to go back without ESC
- ❌ Buttons too small or too close together
- ❌ Unclear button hierarchy (no visual primary button)
- ❌ Modal dialogs can be clicked through
- ❌ No confirmation on destructive actions

### HUD Issues
- ❌ Information overload (too many numbers)
- ❌ Critical info in corners (out of peripheral vision)
- ❌ HUD elements block gameplay
- ❌ No scaling for different resolutions
- ❌ Placeholder text in production

### Control Issues
- ❌ Can't rebind all keys
- ❌ Keybinding conflicts not prevented
- ❌ No way to reset to defaults
- ❌ Controls not explained anywhere
- ❌ Actions require key combinations not shown in UI

### Visual Issues
- ❌ Low contrast text
- ❌ Inconsistent fonts/sizes
- ❌ Emoji used for critical UI (platform-dependent)
- ❌ Elements overlap or misalign
- ❌ Animations too fast/slow

### Flow Issues
- ❌ Dead ends (can't proceed or go back)
- ❌ Unclear objectives
- ❌ Tutorial missing or insufficient
- ❌ No indication of progress
- ❌ Softlocks in specific sequences

---

## 🎯 Priority Testing Areas (As Requested)

Based on your focus on **UI, menu flows, tooltips, configuration, and controls**, prioritize:

### 🔥 High Priority
1. **Controls System**
   - Rebinding interface
   - Conflict detection
   - Display of current bindings
   - Persistence of settings

2. **Menu Navigation**
   - Main menu → Options → Controls → Back
   - Pause menu → Options → Resume
   - Campaign hub navigation
   - Consistency of ESC/back behavior

3. **HUD Clarity**
   - Can you tell health at a glance?
   - Ability cooldowns/charges visible?
   - Score and progress intuitive?
   - Not too cluttered?

4. **Tooltips & Help**
   - Do tooltips exist?
   - Are they helpful?
   - First-time user experience
   - In-game help (F1, etc.)

### 🔶 Medium Priority
5. **Options Menu**
   - All settings functional?
   - Changes persist?
   - Organized logically?

6. **Visual Polish**
   - Consistent styling
   - Readable fonts
   - Proper contrast
   - Icon clarity

### 🔹 Lower Priority
7. **Edge Cases**
   - Rapid input handling
   - Long session stability
   - Unusual sequences

---

## 📝 Testing Session Template

Use this for each testing session:

```
=== Testing Session ===
Date: ___________
Tester: ___________
Build/Version: ___________
Duration: ___________

Focus Areas:
- [ ] Main Menu
- [ ] Options/Settings
- [ ] In-Game HUD
- [ ] Pause Menu
- [ ] Controls
- [ ] Campaign Hub
- [ ] Other: ___________

Bugs Found: _____ (🔴 Critical, 🟠 Major, 🟡 Minor, 🔵 Enhancement)

Critical Issues:
1. [If any]

Major Issues:
1. [If any]

Minor Issues:
1. [List]

Enhancement Suggestions:
1. [List]

General Notes:
[Free-form feedback]

Next Session Focus:
[What to test next]
```

---

## 🚀 Quick Start Testing Path

**If you have limited time, test this path:**

1. ✅ Launch game → Main menu (visual check)
2. ✅ Main menu → Options → Controls (check rebinding)
3. ✅ Back to main menu → New Game (start arcade)
4. ✅ Observe HUD (check all elements visible)
5. ✅ Collect coin (check score updates)
6. ✅ Press ESC (pause menu)
7. ✅ Pause → Controls (viewer)
8. ✅ Resume game
9. ✅ Unlock an ability (check HUD updates)
10. ✅ Quit to menu → Campaign (hub navigation)

**This covers the core UX flow in ~10 minutes.**

---

## 🔍 Final Notes

- **Be thorough but not destructive** - Test normally, but also try unusual actions
- **Document everything** - Screenshots help tremendously
- **Focus on user perspective** - Pretend you've never played before
- **Note positive findings too** - What works well?
- **Suggest solutions when possible** - Not just "this is bad" but "maybe try..."

Good luck testing! 🎮
