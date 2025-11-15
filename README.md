Ninja Dash
A fast-paced platformer with advanced movement mechanics and collectible-based progression

Overview
Ninja Dash is a Python-based platformer built with Pygame that combines precision platforming with deep movement mechanics and RPG-style progression. Master advanced abilities like wall jumping, dashing, and shadow stepping while collecting rare ability orbs to unlock even more powerful moves.

The game features procedurally generated levels, ensuring each playthrough offers fresh challenges, and a collectible-based unlock system that rewards both skill and exploration.

Current Features
Core Gameplay
Precision Platforming: Tight, responsive controls with advanced movement mechanics
Procedural Level Generation: Unique, randomly generated levels every playthrough
Advanced Movement System:
Multi-jump mechanics (configurable, default: double jump)
Wall jumping and wall sliding
Air dashing with cooldown management
Shadow step ability (3 charges per level, phase through walls)
Crouch mechanics and fast falling
Progression System
Ability Orb Collection: Rare collectibles (0.3% spawn rate) that persist across all playthroughs
14 Planned Abilities: From basic double jumps to expert-level teleportation
Unlock Progression: Each ability requires a specific number of orbs (5-90 orbs)
High Score Tracking: Compete against your best runs
Power-ups & Collectibles
Temporary Power-ups: Speed boost, triple jump, coin magnet, and more
Coins & Gems: Collect for points and progression
Multiple Collectible Types: Keys, fragments, chests, and special items
User Experience
Data-Driven Controls: Fully customizable keybindings via JSON configuration
In-Game Controls Viewer: View and manage keybindings during gameplay
Settings System: Persistent user preferences with override support
Multiple Game States: Menu, gameplay, pause, settings, high scores, and more
Installation
Requirements
Python 3.7 or higher
Pygame 2.0.0 or higher
Quick Start
Clone the repository:
git clone https://github.com/VainAsher/ninja_dash_prototype.git
cd ninja_dash_prototype
Install dependencies:
pip install -r requirements.txt
Run the game:
Linux/Mac:

./run_game.sh
Windows:

run_game.bat
With Virtual Environment (Windows):

run_game_venv.bat
Direct Python:

python main.py
How to Play
Navigate the procedurally generated levels by jumping, dashing, and wall-jumping through obstacles
Collect coins and gems for points
Find rare Ability Orbs (rainbow crystalline orbs) to unlock new abilities
Reach the exit gate to complete each level
Unlock new abilities in the pause menu as you collect orbs
Master advanced techniques to achieve higher scores and faster times
Controls
Default Keybindings
Movement:

A / Left Arrow - Move left
D / Right Arrow - Move right
W / Space - Jump
S / Down Arrow - Crouch
Shift - Dash
Advanced Movement:

Q - Shadow Step (phase through walls)
Wall Jump - Jump while touching a wall
Fast Fall - Hold Down while in air
Game Controls:

Escape - Pause menu
F1 - View controls in-game
All controls are fully customizable through the settings menu or by editing data/controls.json.

Project Status
Current Progress: ~15% Complete

Completed Systems
Core movement and physics engine
Procedural level generation
Data-driven controls system
Controls viewer UI
High score tracking
Basic collectibles and power-ups
Save/load system
Complete design documentation
In Active Development
Combat system (player attacks, damage system)
Enemy AI and behaviors
Ability orb collection mechanics
Extended abilities (slide, glide, grapple)
See docs/IMPLEMENTATION_STATUS.md for detailed progress tracking.

Planned Features
Combat & Enemies
12+ Enemy Types: From basic patrollers to advanced teleporting enemies
5 Boss Battles: Multi-phase boss fights with unique mechanics
Combat System: Melee attacks, combos, and special abilities
Loot System: Enemies drop coins, health, power-ups, and rare items
Advanced Abilities
Unlock 14 unique abilities using collected orbs:

Basic Tier (5-15 orbs): Double Jump, Dash, Wall Jump, Slide
Intermediate (18-30 orbs): Wall Cling, Shadow Step, Air Dodge, Glide
Advanced (35-50 orbs): Grappling Hook, Ground Pound, Double Dash
Expert (60-90 orbs): Time Slow, Teleport, Stomp Jump
RPG Elements
Character stats (STR, AGI, VIT, etc.)
Experience and leveling system
Equipment system (weapons, armor)
Inventory management
Skill trees with branching paths
Campaign Mode
World map navigation
Story/narrative framework
Quest system
NPC dialogues
Save game system
Additional Features
Multiple game modes (Time Trial, Survival, Endless, Boss Rush)
Status effects and debuffs system
Advanced visual effects (particles, lighting, weather)
Sound and music system
Daily challenges and achievements
See the full specifications in the docs/ directory.
