"""
Maze Generation Constants

Configuration values that control the macro maze structure and room connectivity.
"""

# Maze Structure
DEFAULT_VERTICALITY_BIAS = 0.5
"""Float: Vertical vs horizontal preference in maze generation (0.0-1.0)

Higher values create more vertical mazes with emphasis on climbing.
Lower values create more horizontal mazes with emphasis on running.

Examples:
    - 0.0: Purely horizontal maze (all side-by-side rooms)
    - 0.5: Balanced vertical and horizontal (default)
    - 1.0: Purely vertical maze (all stacked rooms)
"""

DEFAULT_BRANCHINESS = 0.25
"""Float: Probability of creating additional connections in maze (0.0-1.0)

Controls how many extra connections are added beyond the minimum spanning tree.
Higher values create more loops and alternate paths.

Examples:
    - 0.0: Minimal connections (tree structure, one path)
    - 0.25: Some branches and shortcuts (default)
    - 0.5: Many alternate paths
    - 1.0: Highly connected (almost fully connected grid)
"""
