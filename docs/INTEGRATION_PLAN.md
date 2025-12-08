# Integration Plan: Zone System → Active Game

## Current Status
✅ Infrastructure complete (zone generator, tileset, minimap)
❌ **NOT integrated** into actual level generation or rendering
❌ **NOT visible** in campaign or arcade modes

## What Needs to Connect

### 1. Level Generation (`generate_level()`)
**Current**: Uses `build_world_from_path()` → simple 2D tile array
**Needed**: Option to use zone-based room generation

### 2. Rendering (`draw_world()`)
**Current**: Draws colored rectangles for tiles (line 143-150 in `core/game.py`)
**Needed**: Use `draw_tiles()` with TileSet for sprite-based rendering

### 3. HUD
**Current**: No minimap
**Needed**: Add minimap component to show room layout

## Integration Approaches

### Option A: Full Integration (Recommended)
Replace existing generation with zone system everywhere.

**Pros**: Consistent experience, uses all new features
**Cons**: More work, need to ensure compatibility

### Option B: Hybrid (Easiest)
Use zone system only for special rooms (shops, treasures, bosses).

**Pros**: Minimal changes, gradual adoption
**Cons**: Inconsistent visual style

### Option C: Toggle (Most Flexible)
Add a settings flag to choose generation system.

**Pros**: Can compare systems, user choice
**Cons**: Maintain both systems

## Recommended Steps

### Step 1: Add Tileset Rendering (Minimal Impact)
Replace simple rect rendering with tileset rendering.

**File**: `core/game.py`
**Function**: `draw_world()`
**Change**: Replace lines 143-150 with tileset drawing

```python
# BEFORE (lines 143-150):
for t in tiles:
    if cam.colliderect(t):
        color = COLOR_PHASEABLE_WALL if t in phaseable_walls else ground_color
        pygame.draw.rect(play_surf, color, (t.x - cam.x, t.y - cam.y, t.w, t.h))

# AFTER (with tileset):
if hasattr(game, 'tileset') and hasattr(game, 'world'):
    # Use tileset rendering
    from level_gen.tileset import draw_tiles
    draw_tiles(play_surf, game.world, pygame.Vector2(cam.x, cam.y),
               game.tileset, game.seed, debug_grid=debug)
else:
    # Fallback to colored rects
    for t in tiles:
        if cam.colliderect(t):
            color = COLOR_PHASEABLE_WALL if t in phaseable_walls else ground_color
            pygame.draw.rect(play_surf, color, (t.x - cam.x, t.y - cam.y, t.w, t.h))
```

### Step 2: Initialize Tileset in Game
**File**: `core/game.py`
**Function**: `__init__()` or `setup_level()`

```python
from pathlib import Path
from level_gen.tileset import TileSet, validate_tiles

# In game initialization:
self.assets_root = Path(__file__).parent.parent / "assets" / "tiles"
self.tileset = TileSet(self.current_biome, TILE_SIZE, self.assets_root)
validate_tiles(self.tileset)  # Optional: prints missing tiles
```

### Step 3: Add Minimap to HUD
**File**: `ui/hud_components.py` or create new component

```python
from ui.minimap import Minimap

class MinimapSection:
    def __init__(self):
        self.minimap = Minimap(cell_size=8, padding=6)
        self.enabled = True  # Toggle with key

    def draw(self, surface, game):
        if not self.enabled or not hasattr(game, 'room_nodes'):
            return

        self.minimap.draw(
            surface,
            game.room_nodes,
            game.current_room,
            game.player.rect,
            ROOM_W * TILE_SIZE,
            ROOM_H * TILE_SIZE,
            game.room_offset_x,
            game.room_offset_y
        )
```

### Step 4: Optional Zone Generation
**File**: `level_gen/generator.py`
**Function**: `generate_level()`

Add optional zone-based generation:

```python
def generate_level(seed, config, abilities, use_zones=False):
    # ... existing code ...

    if use_zones:
        # Use zone-based generation
        from .zone_integration import generate_room_from_zones
        from .zone_generator import assign_zone_roles_for_room, RoomNode

        # Generate rooms with zones
        room_nodes = {}
        for room_coord in path:
            rx, ry = room_coord
            room_type = determine_room_type(room_coord, start, goal)  # Your logic
            room = RoomNode(rx, ry, room_type, rng.randrange(10**9))

            # Assign zones
            room.zone_roles = assign_zone_roles_for_room(room, rng)

            # Generate tilemap
            room.tilemap, room.anchor_candidates = generate_room_from_zones(
                room, room.zone_roles, rng, ROOM_W, ROOM_H
            )

            room_nodes[room_coord] = room

        # Stitch rooms into world tilemap
        world = stitch_rooms(room_nodes)  # Helper function needed
        tiles, exit_rect = build_solid_rects(world)

        return world, tiles, exit_rect, spawn, ..., room_nodes
    else:
        # Existing generation
        world, path_mask = build_world_from_path(path)
        # ... rest of existing code ...
```

## Quick Integration (30 Minutes)

For immediate visual improvement without changing generation:

1. **Add tileset loading** to Game.__init__()
2. **Replace tile rendering** in draw_world()
3. **Create placeholder tiles** (colored squares) if assets missing

This gives you:
- Better visual appearance (sprites instead of rects)
- Auto-tiling for walls/platforms
- Biome-specific visuals
- No changes to level generation

## Full Integration (2-3 Hours)

For complete zone system integration:

1. **Modify generate_level()** to support zone generation
2. **Update Game class** to store room_nodes, current_room
3. **Add minimap** to HUD components
4. **Add console logging** for debug output
5. **Test** campaign and arcade modes

## Testing Checklist

- [ ] Tileset loads without errors
- [ ] Tiles render correctly (no magenta placeholders)
- [ ] Camera culling works (only visible tiles rendered)
- [ ] Minimap shows current room
- [ ] Player position updates on minimap
- [ ] Campaign mode works
- [ ] Arcade mode works
- [ ] Performance acceptable (60 FPS)

## Asset Requirements

Minimum assets for basic rendering (placeholder if missing):
- `assets/tiles/lantern/wall/*.png` (9 files)
- `assets/tiles/lantern/platform/*.png` (9 files)
- `assets/tiles/lantern/world/void_0.png`
- `assets/tiles/lantern/door/door_0.png`

System auto-generates colored placeholders if files missing.

## Next Actions

**Choose your integration level:**

1. **Minimal** - Just add tileset rendering (visual upgrade)
2. **Moderate** - Add minimap + tileset rendering
3. **Full** - Complete zone-based generation

Which would you like me to implement?
