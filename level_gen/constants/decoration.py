"""
Decoration Constants

Configuration values for visual and structural decorations including platforms,
pillars, holes, and room layout parameters.
"""

# Platform Generation
DEFAULT_PLATFORM_BAND_STEP = 4
"""Int: Vertical spacing between platform bands in rooms (in tiles)

Controls how frequently horizontal platforms appear vertically.
Smaller values create denser platform arrangements.

Examples:
    - 2: Very dense platforms (every 2 tiles)
    - 4: Balanced platform density (default)
    - 6: Sparse platforms (larger gaps)
"""

DEFAULT_PLATFORM_LEN_RANGE = (3, 7)
"""Tuple[int, int]: Min and max platform lengths (in tiles)

Randomly generated platforms will have lengths between these values.

Examples:
    - (2, 4): Short, frequent platforms
    - (3, 7): Varied lengths (default)
    - (5, 12): Long platforms with big gaps
"""

# Structural Decorations
DEFAULT_PILLAR_CHANCE = 0.3
"""Float: Probability of generating pillars in a room (0.0-1.0)

Pillars are vertical obstacles that create navigation challenges.
Higher values create more cluttered rooms.

Examples:
    - 0.0: No pillars
    - 0.3: Occasional pillars (default)
    - 0.7: Many pillars (challenging navigation)
"""

DEFAULT_HOLE_CHANCE = 0.2
"""Float: Probability of creating holes in floor (0.0-1.0)

Holes are 2x2 gaps in solid surfaces creating pitfalls.
Higher values create more dangerous floors.

Examples:
    - 0.0: No holes (safe floors)
    - 0.2: Occasional holes (default)
    - 0.5: Many holes (risky traversal)
"""

# Room Layout
ROOM_FLOOR_OFFSET = 3
"""Int: Offset from bottom of room for floor placement (in tiles)

Floor is placed at: room_bottom_y - ROOM_FLOOR_OFFSET
Determines how much unused space is below the main floor.

Technical Note:
    Actual floor position = base_y + ROOM_H - ROOM_FLOOR_OFFSET
"""
