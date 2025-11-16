"""
Maze Generation Module - Handles procedural maze generation and pathfinding.
"""

from collections import deque

from .constants import DEFAULT_VERTICALITY_BIAS, DEFAULT_BRANCHINESS
from .structures import Room


def generate_macro_maze(cols, rows, rng, verticality_bias=DEFAULT_VERTICALITY_BIAS, branchiness=DEFAULT_BRANCHINESS):
    """Generate room-to-room maze structure.

    Args:
        cols: Number of columns in the maze
        rows: Number of rows in the maze
        rng: Random number generator instance
        verticality_bias: Float 0-1, higher values favor vertical connections
        branchiness: Float 0-1, probability of creating extra connections

    Returns:
        2D list of Room objects with open_up, open_down, open_left, open_right attributes
    """
    class Cell:
        __slots__ = ("open_up", "open_down", "open_left", "open_right", "visited")
        def __init__(self):
            self.open_up = self.open_down = self.open_left = self.open_right = False
            self.visited = False

    grid = [[Cell() for _ in range(cols)] for _ in range(rows)]

    def neighbors(cx, cy):
        dirs = []
        if cy > 0:          dirs.append((cx, cy - 1, "U", verticality_bias))
        if cy < rows - 1:   dirs.append((cx, cy + 1, "D", verticality_bias))
        if cx > 0:          dirs.append((cx - 1, cy, "L", 1.0 - verticality_bias))
        if cx < cols - 1:   dirs.append((cx + 1, cy, "R", 1.0 - verticality_bias))
        total = sum(w for *_, w in dirs) or 1.0
        weighted = []
        for item in dirs:
            w = item[3] / total
            weighted.append((w, item))
        rng.shuffle(weighted)
        weighted.sort(key=lambda x: rng.random() * (1.0 / max(1e-6, x[0])))
        return [item for _, item in weighted]

    def open_between(x, y, nx, ny, d):
        a = grid[y][x]; b = grid[ny][nx]
        if d == "U": a.open_up = True; b.open_down = True
        if d == "D": a.open_down = True; b.open_up = True
        if d == "L": a.open_left = True; b.open_right = True
        if d == "R": a.open_right = True; b.open_left = True

    sx, sy = 0, rows - 1
    stack = [(sx, sy)]
    grid[sy][sx].visited = True

    while stack:
        x, y = stack[-1]
        nxt = None
        for nx, ny, d, _ in neighbors(x, y):
            if not grid[ny][nx].visited:
                nxt = (nx, ny, d)
                break
        if not nxt:
            stack.pop()
            continue
        nx, ny, d = nxt
        grid[ny][nx].visited = True
        open_between(x, y, nx, ny, d)
        stack.append((nx, ny))

        if rng.random() < branchiness:
            for tx, ty, td, _ in neighbors(x, y):
                if (tx, ty) != (nx, ny):
                    open_between(x, y, tx, ty, td)
                    break

    return [[Room(
        rx=x,
        ry=y,
        open_up=grid[y][x].open_up,
        open_down=grid[y][x].open_down,
        open_left=grid[y][x].open_left,
        open_right=grid[y][x].open_right
    ) for x in range(cols)] for y in range(rows)]


def find_room_path(rooms, start, goal, room_cols, room_rows):
    """Find path from start to goal room using BFS.

    Args:
        rooms: 2D list of room objects with open_* attributes
        start: Tuple of (x, y) starting room coordinates
        goal: Tuple of (x, y) goal room coordinates
        room_cols: Number of columns in the room grid
        room_rows: Number of rows in the room grid

    Returns:
        List of (x, y) tuples representing the path from start to goal,
        or None if no path exists
    """
    sx, sy = start
    gx, gy = goal
    q = deque([(sx, sy)])
    prev = {(sx, sy): None}

    while q:
        x, y = q.popleft()
        if (x, y) == (gx, gy): break
        r = rooms[y][x]
        for nx, ny, ok in (
            (x + 1, y, r.open_right),
            (x - 1, y, r.open_left),
            (x, y - 1, r.open_up),
            (x, y + 1, r.open_down),
        ):
            if ok and (nx, ny) not in prev and 0 <= nx < room_cols and 0 <= ny < room_rows:
                prev[(nx, ny)] = (x, y)
                q.append((nx, ny))

    if (gx, gy) not in prev: return None

    path = []
    cur = (gx, gy)
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path


def verify_maze_connectivity(rooms, room_cols, room_rows):
    """Verify that all rooms in the maze are reachable from the start.

    Args:
        rooms: 2D list of room objects with open_* attributes
        room_cols: Number of columns in the room grid
        room_rows: Number of rows in the room grid

    Returns:
        Tuple of (is_connected, reachable_count, total_count)
    """
    visited = set()
    start = (0, room_rows - 1)  # Bottom-left corner
    queue = deque([start])
    visited.add(start)

    while queue:
        x, y = queue.popleft()
        r = rooms[y][x]

        for nx, ny, ok in (
            (x + 1, y, r.open_right),
            (x - 1, y, r.open_left),
            (x, y - 1, r.open_up),
            (x, y + 1, r.open_down),
        ):
            if ok and (nx, ny) not in visited and 0 <= nx < room_cols and 0 <= ny < room_rows:
                visited.add((nx, ny))
                queue.append((nx, ny))

    total_rooms = room_cols * room_rows
    reachable = len(visited)

    return (reachable == total_rooms, reachable, total_rooms)
