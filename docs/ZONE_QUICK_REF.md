# Zone Generation Quick Reference

## Essential Imports

```python
from level_gen import (
    RoomNode, assign_zone_roles_for_room, generate_room_from_zones,
    TileSet, draw_tiles, validate_tiles,
    ROOM_COMBAT, ROOM_TREASURE, ROOM_SHOP,
    Z_WALK, Z_FILL, Z_PLAT
)
from ui.minimap import Minimap, print_world
```

## Quick Start

### 1. Create a Room

```python
import random
room = RoomNode(x=0, y=0, type=ROOM_COMBAT, seed=12345)
rng = random.Random(room.seed)
```

### 2. Assign Zones (5x5 Grid)

```python
zone_roles = assign_zone_roles_for_room(room, rng)
# Returns: [[Z_WALK, Z_FILL, ...], [...], ...]  # 5x5 grid
```

### 3. Generate Tilemap

```python
from settings import ROOM_W, ROOM_H
tilemap, anchors = generate_room_from_zones(room, zone_roles, rng, ROOM_W, ROOM_H)
# Returns: ([AIR/WALL/PLATFORM], [(feature_name, pos, weight)])
```

### 4. Load Tileset

```python
from pathlib import Path
tileset = TileSet("lantern", tile_size=32, root=Path("assets/tiles"))
```

### 5. Render

```python
import pygame
screen = pygame.display.set_mode((960, 540))
camera = pygame.Vector2(0, 0)

draw_tiles(screen, tilemap, camera, tileset, seed=42)
```

## Room Types

| Type | Symbol | Usage |
|------|--------|-------|
| `ROOM_START` | S | Player spawn |
| `ROOM_EXIT` | X | Level goal |
| `ROOM_COMBAT` | C | Enemy encounters |
| `ROOM_PLATFORM` | P | Platforming challenges |
| `ROOM_TREASURE` | T | Loot rooms |
| `ROOM_SHOP` | $ | NPC shop |
| `ROOM_BOSS` | B | Boss arena |
| `ROOM_SAFE` | . | No hazards |

## Zone Roles

| Role | Symbol | Effect |
|------|--------|--------|
| `Z_WALK` | `.` | Open walkway with floor |
| `Z_FILL` | `#` | Filled with walls |
| `Z_PLAT` | `=` | Platform patterns |
| `Z_DECOR` | ` ` | Minimal decoration |
| `Z_SAVE` | S | Save point location |
| `Z_SHOP` | $ | Shopkeeper NPC |
| `Z_LOOT` | T | Treasure chest |
| `Z_SECRET` | ? | Secret area |

## Tile IDs

```python
AIR = 0      # Empty space
WALL = 1     # Solid walls
EXIT = 2     # Exit gate
PLATFORM = 3 # Platforms
DOOR = 4     # Doors
```

## Platform Patterns

Available in Z_PLAT zones:
- `bridge` - Simple horizontal bridge
- `islands` - Multiple small platforms
- `split` - Two-level platforms
- `stair` - Ascending staircase
- `zigzag` - Alternating sides
- `pedestal` - Elevated center
- `arena_sides` - Boss arena sides
- `pillar` - Vertical obstacle

## Minimap

```python
minimap = Minimap(cell_size=10)

minimap.draw(
    screen=screen,
    rooms=rooms_dict,
    current_room=(0, 0),
    player_rect=player.rect,
    room_px_w=ROOM_W * 32,
    room_px_h=ROOM_H * 32,
    minx=0, miny=0
)
```

## Console Logging

```python
from level_gen.zone_integration import log_*

log_generation_start(seed=42, config_name="hard")
log_room_generation(coord=(0,0), room_type="combat", room_count=1, total=10)
log_generation_complete(room_count=10, duration=0.5)
```

## Asset Structure

```
assets/tiles/{biome}/
├── wall/
│   ├── top_left_0.png (8x8)
│   ├── top_mid_0.png
│   └── ... (9 total)
├── platform/
│   └── ... (9 total)
├── world/
│   └── void_0.png
├── door/
│   └── door_0.png
└── feature/
    └── marker_0.png
```

## Common Patterns

### Generate World with Zones

```python
rooms = {}
for coord in room_coords:
    room = RoomNode(*coord, type=random.choice(ROOM_TYPES), seed=rng.randrange(10**9))
    room.zone_roles = assign_zone_roles_for_room(room, rng)
    room.tilemap, room.anchor_candidates = generate_room_from_zones(
        room, room.zone_roles, rng, ROOM_W, ROOM_H
    )
    rooms[coord] = room
```

### Stitch Rooms into Mega Map

```python
minx = min(x for x, _ in rooms.keys())
miny = min(y for _, y in rooms.keys())

world_w = (maxx - minx + 1) * ROOM_W
world_h = (maxy - miny + 1) * ROOM_H
mega = [[AIR] * world_w for _ in range(world_h)]

for (rx, ry), room in rooms.items():
    ox = (rx - minx) * ROOM_W
    oy = (ry - miny) * ROOM_H
    for y in range(ROOM_H):
        for x in range(ROOM_W):
            mega[oy + y][ox + x] = room.tilemap[y][x]
```

### Custom Zone Assignment

```python
# Override specific zones
zone_roles = assign_zone_roles_for_room(room, rng)

# Force center to be a loot zone
zone_roles[2][2] = Z_LOOT

# Force edges to be walls
for x in range(5):
    zone_roles[0][x] = Z_FILL
    zone_roles[4][x] = Z_FILL
```

## Debugging

### Enable Debug Grid

```python
draw_tiles(screen, tilemap, camera, tileset, seed, debug_grid=True)
```

### Print Zone Assignments

```python
from level_gen.zone_generator import print_zone_roles
print_zone_roles(room.zone_roles, room.type, (room.x, room.y))
```

### Print ASCII World

```python
from ui.minimap import print_world
print_world(rooms, start=(0,0), exitp=(5,0), grid=(6,4), style="branchy")
```

### Validate Tileset

```python
from level_gen.tileset import validate_tiles
validate_tiles(tileset)  # Prints missing sprite keys
```

## Tips

✅ **DO**:
- Use zone roles to guide room design
- Enable console logging during development
- Start with placeholder tiles
- Test individual room types in demo
- Leverage data-driven feature placement

❌ **DON'T**:
- Don't hardcode room layouts
- Don't skip zone connectivity checks
- Don't make all zones Z_FILL (blocks movement)
- Don't forget to validate tileset
- Don't ignore console warnings

## Demo

Run the demo to experiment:
```bash
python examples/zone_generation_demo.py
```

Press **M** for minimap, **G** to regenerate, **WASD** to move.

---

For complete documentation, see `docs/ZONE_GENERATION_GUIDE.md`
