# Zone-Based World Generation Guide

This guide explains the new zone-based world generation system and how to use it in your game.

## Overview

The zone-based generation system provides **granular room customization** by dividing each room into a **5x5 grid of zones**. Each zone can have different roles (WALK, FILL, PLAT, etc.), allowing for data-driven, varied room layouts.

### Key Features

1. **Minimap** - Visual overview of the world with room types and player position
2. **Granular Room Customization** - 5x5 zone grid for detailed room design
3. **Tile-Based Rendering** - Auto-tiling system with folder-based assets
4. **Biome Support** - Organized asset structure by biome (lantern, hollow, ember, sky)
5. **Console Logging** - Debug output for generation progress

## Architecture

### Module Structure

```
level_gen/
├── zone_generator.py       # Core zone system and room types
├── zone_integration.py     # Integration with existing level gen
└── tileset.py              # Tile loading and auto-tiling

ui/
└── minimap.py              # Minimap rendering

assets/tiles/
├── lantern/                # Lantern biome tiles
│   ├── wall/               # Wall tiles (3x3 patterns)
│   ├── platform/           # Platform tiles (3x3 patterns)
│   ├── world/              # Background tiles
│   ├── door/               # Door tiles
│   └── feature/            # Feature markers
├── hollow/                 # Hollow biome tiles
├── ember/                  # Ember biome tiles
└── sky/                    # Sky biome tiles
```

## Zone Roles

Each of the 25 zones (5x5 grid) in a room can have one of these roles:

| Role | Symbol | Purpose |
|------|--------|---------|
| `Z_WALK` | `.` | Keep open for travel, simple floor |
| `Z_FILL` | `#` | Fill with walls (room shaping) |
| `Z_PLAT` | `=` | Platform-heavy areas with patterns |
| `Z_DECOR` | ` ` | Decorative/minimal geometry |
| `Z_SAVE` | `S` | Save point location |
| `Z_SHOP` | `$` | Shopkeeper NPC |
| `Z_LOOT` | `T` | Treasure chest |
| `Z_SECRET` | `?` | Secret area |

## Room Types

The system supports various room types, each with different zone assignment rules:

- `ROOM_START` - Player spawn room
- `ROOM_EXIT` - Level exit room
- `ROOM_COMBAT` - Combat-focused with enemies
- `ROOM_PLATFORM` - Platforming challenges
- `ROOM_TREASURE` - Contains loot
- `ROOM_SHOP` - Contains shopkeeper NPC
- `ROOM_BOSS` - Boss arena
- `ROOM_SAFE` - No hazards, safe area

## Usage Examples

### Basic Room Generation

```python
from level_gen.zone_generator import RoomNode, assign_zone_roles_for_room, ROOM_COMBAT
from level_gen.zone_integration import generate_room_from_zones
from settings import ROOM_W, ROOM_H
import random

# Create a room node
room = RoomNode(x=0, y=0, type=ROOM_COMBAT, seed=12345)
rng = random.Random(room.seed)

# Assign zone roles (5x5 grid of role strings)
zone_roles = assign_zone_roles_for_room(room, rng)

# Generate tilemap from zones
tilemap, anchors = generate_room_from_zones(room, zone_roles, rng, ROOM_W, ROOM_H)

# tilemap is now a 2D array of tile IDs (0=air, 1=wall, 3=platform, etc.)
```

### Using the Tileset System

```python
from pathlib import Path
from level_gen.tileset import TileSet, draw_tiles, validate_tiles
import pygame

# Load tileset for a specific biome
assets_root = Path("assets/tiles")
tileset = TileSet("lantern", tile_size=32, root=assets_root)
validate_tiles(tileset)  # Check for missing sprites

# Draw tiles to screen
screen = pygame.display.set_mode((960, 540))
camera = pygame.Vector2(0, 0)
seed = 42

draw_tiles(screen, tilemap, camera, tileset, seed, debug_grid=False)
```

### Rendering a Minimap

```python
from ui.minimap import Minimap, print_world

# Create minimap renderer
minimap = Minimap(cell_size=10, padding=8)

# Draw minimap (top-right corner)
minimap.draw(
    screen=screen,
    rooms=rooms_dict,
    current_room=(0, 0),
    player_rect=player.rect,
    room_px_w=ROOM_W * TILE_SIZE,
    room_px_h=ROOM_H * TILE_SIZE,
    minx=0,
    miny=0
)

# Print ASCII map to console
print_world(rooms_dict, start=(0,0), exitp=(5,0), grid=(6,4), style="demo")
```

### Console Logging

```python
from level_gen.zone_integration import (
    log_generation_start,
    log_room_generation,
    log_feature_placement,
    log_generation_complete
)

# Log generation process
log_generation_start(seed=42, config_name="hard")

for i, (coord, room) in enumerate(rooms.items()):
    log_room_generation(coord, room.type, i + 1, len(rooms))

    # Log features if present
    if room.resolved_anchors:
        log_feature_placement(coord, room.resolved_anchors)

log_generation_complete(len(rooms), duration=0.5)
```

## Platform Patterns

The PLAT zones can generate various platform patterns based on room type:

| Pattern | Description | Good For |
|---------|-------------|----------|
| `bridge` | Simple horizontal bridge | All room types |
| `islands` | Multiple small platforms | Combat, Treasure |
| `split` | Two-level platforms | Combat, Boss |
| `stair` | Ascending staircase | Platform rooms |
| `zigzag` | Alternating sides | Platform rooms |
| `pedestal` | Elevated center platform | Treasure rooms |
| `arena_sides` | Side platforms | Boss arenas |
| `pillar` | Vertical pillar obstacle | Combat rooms |

These patterns are automatically selected based on room type to create appropriate challenges.

## Integration with Existing System

The zone system is designed to **complement** the existing level generator, not replace it. You can:

### Option 1: Use for Specific Rooms Only

```python
# Use zone generation for special rooms (shops, treasure)
if room_type in (ROOM_SHOP, ROOM_TREASURE, ROOM_BOSS):
    zone_roles = assign_zone_roles_for_room(room, rng)
    tilemap, anchors = generate_room_from_zones(room, zone_roles, rng, ROOM_W, ROOM_H)
else:
    # Use existing generation for combat rooms
    tilemap = generate_standard_room(room_type, rng)
```

### Option 2: Full Integration

Replace the room generation in `level_gen/generator.py`:

```python
# In generate_level():
for room_coord, room_node in rooms.items():
    # Assign zones
    zone_roles = assign_zone_roles_for_room(room_node, rng)

    # Generate tilemap
    room_node.tilemap, room_node.anchor_candidates = generate_room_from_zones(
        room_node, zone_roles, rng, ROOM_W, ROOM_H
    )
```

## Asset Creation

### Tile Requirements

Each biome needs these sprite keys:

**Walls** (9 tiles for 3x3 auto-tiling):
- `wall/top_left_0.png`
- `wall/top_mid_0.png`
- `wall/top_right_0.png`
- `wall/mid_left_0.png`
- `wall/mid_mid_0.png`
- `wall/mid_right_0.png`
- `wall/bottom_left_0.png`
- `wall/bottom_mid_0.png`
- `wall/bottom_right_0.png`

**Platforms** (same 9 tiles):
- `platform/top_left_0.png` through `platform/bottom_right_0.png`

**Other**:
- `world/void_0.png` - Background/void tile
- `door/door_0.png` - Door/entrance tile
- `feature/marker_0.png` - Feature marker

### Creating Tiles

1. Create 8x8 pixel art in your editor (Aseprite, GraphicsGale, etc.)
2. Export as PNG with transparency
3. Name following the convention above
4. Add variants by incrementing: `_0.png`, `_1.png`, `_2.png`
5. System auto-scales 8x8 to 32x32

### Placeholder Tiles

If tiles are missing, the system will:
- Generate colored placeholder tiles automatically
- Print warnings listing missing sprite keys
- Render missing tiles as magenta squares in-game

## Running the Demo

Try the included demo to see the system in action:

```bash
python examples/zone_generation_demo.py
```

Controls:
- **WASD / Arrow Keys** - Move player
- **M** - Toggle minimap
- **G** - Regenerate world with new seed
- **Esc** - Quit

## Customization

### Adding New Room Types

```python
# In zone_generator.py
ROOM_PUZZLE = "puzzle"
ROOM_SYMBOL[ROOM_PUZZLE] = "?"

# In assign_zone_roles_for_room():
if room.type == ROOM_PUZZLE:
    features["puzzle_mechanic"] = (ZONES_W // 2, ZONES_H // 2)
    max_fills = rng.randint(4, 7)  # More walls for puzzle rooms
```

### Adding New Zone Roles

```python
# Define new role
Z_SPIKE = "SPIKE"  # Hazardous zone

# In generate_room_from_zones():
elif role == Z_SPIKE:
    clear_air(tilemap, x0i, y0i, x1i, y1i)
    # Add spike hazards here
    candidates.append(("spike_trap", (cx, cy), 1.0))
```

### Custom Platform Patterns

```python
# In generate_room_from_zones(), add to platform generation:
elif kind == "my_custom_pattern":
    # Your custom platform logic
    for i in range(5):
        x = x0i + i * 3
        y = y0i + i * 2
        stamp_platform(tilemap, x, y, 4)
```

## Best Practices

1. **Use console logging** - Enable logging during development to debug generation
2. **Start with placeholders** - Don't wait for final art; placeholders work great
3. **Test room types separately** - Use the demo to iterate on specific room types
4. **Balance zone complexity** - Too many FILL zones can make rooms cramped
5. **Maintain connectivity** - The system ensures zones stay connected, but verify manually
6. **Leverage data-driven design** - Add features through room metadata, not hardcoding

## Troubleshooting

### "Biome folder not found"

```
[Tiles] Warning: Biome folder not found: /path/to/assets/tiles/lantern
[Tiles] Creating placeholder tiles...
```

**Solution**: Create the folder structure or tiles will use colored placeholders.

### "Missing sprite keys"

```
[Tiles] Missing sprite keys (will render as magenta):
  - wall/top_left
  - platform/mid_mid
```

**Solution**: Create the missing PNGs or ignore (magenta = missing tile indicator).

### Disconnected zones

If zones become unreachable, check:
- Too many Z_FILL zones blocking paths
- `ensure_zone_connectivity()` is working correctly
- Door zones are marked as Z_WALK

## Performance Notes

- **Tileset caching**: Tiles are loaded once per biome
- **Variant hashing**: Deterministic selection ensures consistency
- **Camera culling**: Only visible tiles are rendered

## Future Enhancements

Potential improvements:
- **Rule-based zone templates** - Pre-designed 5x5 patterns
- **Procedural decorations** - Props, particles in zones
- **Dynamic lighting** - Per-biome lighting systems
- **Zone transitions** - Animated zone state changes
- **Save/load zone layouts** - Cache generated rooms

## Reference

For complete implementation details, see:
- `level_gen/zone_generator.py` - Core zone system
- `level_gen/zone_integration.py` - Integration helpers
- `level_gen/tileset.py` - Asset loading
- `ui/minimap.py` - Minimap rendering
- `examples/zone_generation_demo.py` - Working example

---

**Happy generating!** 🎮
