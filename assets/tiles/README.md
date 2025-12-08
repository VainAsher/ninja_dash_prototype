# Tile Assets Structure

This directory contains tile assets organized by biome and category.

## Folder Structure

```
tiles/
├── {biome}/          # e.g., lantern, hollow, ember, sky
│   ├── wall/         # Wall tiles with 3x3 patterns
│   ├── platform/     # Platform tiles with 3x3 patterns
│   ├── world/        # Background tiles (void, etc.)
│   ├── door/         # Door/entrance tiles
│   └── feature/      # Special feature markers
```

## Tile Naming Convention

Tiles should be 8x8 pixels and follow this naming pattern:

- **3x3 Pattern Tiles** (wall, platform):
  - `top_left_0.png`, `top_left_1.png` (variants)
  - `top_mid_0.png`, `top_mid_1.png`
  - `top_right_0.png`, `top_right_1.png`
  - `mid_left_0.png`, `mid_left_1.png`
  - `mid_mid_0.png`, `mid_mid_1.png`
  - `mid_right_0.png`, `mid_right_1.png`
  - `bottom_left_0.png`, `bottom_left_1.png`
  - `bottom_mid_0.png`, `bottom_mid_1.png`
  - `bottom_right_0.png`, `bottom_right_1.png`

- **Simple Tiles**:
  - `void_0.png` (background/world)
  - `door_0.png` (entrances)
  - `marker_0.png` (features)

## Auto-Tiling

The system automatically selects the correct 3x3 pattern tile based on neighbors:

```
┌─┬─┬─┐
│TL│TM│TR│   TL = top_left, TM = top_mid, TR = top_right
├─┼─┼─┤
│ML│MM│MR│   ML = mid_left, MM = mid_mid, MR = mid_right
├─┼─┼─┤
│BL│BM│BR│   BL = bottom_left, BM = bottom_mid, BR = bottom_right
└─┴─┴─┘
```

## Placeholder Tiles

If tiles are missing, the system will render magenta placeholders.
Run the game to see which tiles need to be created.

## Creating Tiles

1. Create 8x8 pixel art PNGs in your favorite editor
2. Save with proper naming convention
3. Add variants by incrementing the number (e.g., `_0`, `_1`, `_2`)
4. Restart the game - tiles will be automatically scaled to 32x32

## Biome Themes

- **Lantern**: Warm, welcoming starter area (wooden platforms, stone walls)
- **Hollow**: Dark, cramped depths (dark stone, twisted roots)
- **Ember**: Monastery-style (red brick, ornate tiles)
- **Sky**: Summit area (clouds, light materials)
