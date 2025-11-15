"""
Unit tests for maze generation module.
Tests maze connectivity, pathfinding, and generation robustness.
"""

import unittest
import random
from level_gen.maze_generator import (
    generate_macro_maze,
    find_room_path,
    verify_maze_connectivity
)


class TestMazeGeneration(unittest.TestCase):
    """Test maze generation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)  # Fixed seed for reproducibility

    def test_generate_basic_maze(self):
        """Test basic maze generation."""
        rooms = generate_macro_maze(3, 3, self.rng)

        # Check that we get the right dimensions
        self.assertEqual(len(rooms), 3)
        self.assertEqual(len(rooms[0]), 3)

        # Check that rooms have the expected attributes
        for row in rooms:
            for room in row:
                self.assertIsNotNone(room.open_up)
                self.assertIsNotNone(room.open_down)
                self.assertIsNotNone(room.open_left)
                self.assertIsNotNone(room.open_right)

    def test_maze_connectivity(self):
        """Test that all rooms in generated maze are connected."""
        for size in [(3, 3), (5, 5), (7, 7), (10, 8)]:
            cols, rows = size
            rng = random.Random(42)
            rooms = generate_macro_maze(cols, rows, rng)

            is_connected, reachable, total = verify_maze_connectivity(rooms, cols, rows)

            self.assertTrue(
                is_connected,
                f"Maze {cols}x{rows} is not fully connected: {reachable}/{total} rooms reachable"
            )
            self.assertEqual(reachable, total)

    def test_maze_connectivity_with_different_seeds(self):
        """Test maze connectivity across different random seeds."""
        for seed in [1, 42, 100, 999, 12345]:
            rng = random.Random(seed)
            rooms = generate_macro_maze(5, 5, rng)

            is_connected, reachable, total = verify_maze_connectivity(rooms, 5, 5)

            self.assertTrue(
                is_connected,
                f"Maze with seed {seed} is not fully connected: {reachable}/{total} rooms reachable"
            )

    def test_maze_with_different_verticality_bias(self):
        """Test maze generation with different verticality bias values."""
        for bias in [0.0, 0.25, 0.5, 0.75, 1.0]:
            rng = random.Random(42)
            rooms = generate_macro_maze(5, 5, rng, verticality_bias=bias)

            is_connected, reachable, total = verify_maze_connectivity(rooms, 5, 5)

            self.assertTrue(
                is_connected,
                f"Maze with verticality_bias={bias} is not fully connected"
            )

    def test_maze_with_different_branchiness(self):
        """Test maze generation with different branchiness values."""
        for branch in [0.0, 0.1, 0.3, 0.5, 0.8]:
            rng = random.Random(42)
            rooms = generate_macro_maze(5, 5, rng, branchiness=branch)

            is_connected, reachable, total = verify_maze_connectivity(rooms, 5, 5)

            self.assertTrue(
                is_connected,
                f"Maze with branchiness={branch} is not fully connected"
            )

    def test_single_room_maze(self):
        """Test edge case: single room maze."""
        rooms = generate_macro_maze(1, 1, self.rng)

        self.assertEqual(len(rooms), 1)
        self.assertEqual(len(rooms[0]), 1)

        is_connected, reachable, total = verify_maze_connectivity(rooms, 1, 1)
        self.assertTrue(is_connected)
        self.assertEqual(reachable, 1)

    def test_single_row_maze(self):
        """Test edge case: single row maze."""
        rooms = generate_macro_maze(5, 1, self.rng)

        is_connected, reachable, total = verify_maze_connectivity(rooms, 5, 1)
        self.assertTrue(is_connected)

    def test_single_column_maze(self):
        """Test edge case: single column maze."""
        rooms = generate_macro_maze(1, 5, self.rng)

        is_connected, reachable, total = verify_maze_connectivity(rooms, 1, 5)
        self.assertTrue(is_connected)

    def test_large_maze(self):
        """Test generation of larger maze."""
        rooms = generate_macro_maze(20, 20, self.rng)

        is_connected, reachable, total = verify_maze_connectivity(rooms, 20, 20)
        self.assertTrue(is_connected)
        self.assertEqual(total, 400)


class TestPathfinding(unittest.TestCase):
    """Test pathfinding functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)

    def test_find_path_in_simple_maze(self):
        """Test pathfinding in a simple maze."""
        rooms = generate_macro_maze(5, 5, self.rng)

        start = (0, 4)  # Bottom-left
        goal = (4, 0)   # Top-right

        path = find_room_path(rooms, start, goal, 5, 5)

        self.assertIsNotNone(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)

    def test_path_validity(self):
        """Test that generated path only uses valid connections."""
        rooms = generate_macro_maze(7, 7, self.rng)

        start = (0, 6)
        goal = (6, 0)

        path = find_room_path(rooms, start, goal, 7, 7)

        self.assertIsNotNone(path)

        # Verify each step in path is valid (connected rooms)
        for i in range(len(path) - 1):
            x, y = path[i]
            nx, ny = path[i + 1]
            room = rooms[y][x]

            # Check that the move is valid
            if nx == x + 1:  # Moving right
                self.assertTrue(room.open_right, f"Path invalid: room at {x},{y} doesn't connect right to {nx},{ny}")
            elif nx == x - 1:  # Moving left
                self.assertTrue(room.open_left, f"Path invalid: room at {x},{y} doesn't connect left to {nx},{ny}")
            elif ny == y + 1:  # Moving down
                self.assertTrue(room.open_down, f"Path invalid: room at {x},{y} doesn't connect down to {nx},{ny}")
            elif ny == y - 1:  # Moving up
                self.assertTrue(room.open_up, f"Path invalid: room at {x},{y} doesn't connect up to {nx},{ny}")
            else:
                self.fail(f"Path has non-adjacent rooms: {x},{y} to {nx},{ny}")

    def test_find_path_same_start_and_goal(self):
        """Test pathfinding when start equals goal."""
        rooms = generate_macro_maze(5, 5, self.rng)

        start = (2, 2)
        goal = (2, 2)

        path = find_room_path(rooms, start, goal, 5, 5)

        self.assertIsNotNone(path)
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], start)

    def test_find_path_adjacent_rooms(self):
        """Test pathfinding between adjacent rooms."""
        rooms = generate_macro_maze(3, 3, self.rng)

        # Test a few adjacent pairs
        start = (0, 2)
        goal = (1, 2)

        path = find_room_path(rooms, start, goal, 3, 3)

        self.assertIsNotNone(path)
        self.assertLessEqual(len(path), 3)  # Should be short

    def test_pathfinding_in_different_maze_sizes(self):
        """Test pathfinding works across different maze sizes."""
        for size in [(3, 3), (5, 5), (8, 6), (10, 10)]:
            cols, rows = size
            rng = random.Random(42)
            rooms = generate_macro_maze(cols, rows, rng)

            start = (0, rows - 1)
            goal = (cols - 1, 0)

            path = find_room_path(rooms, start, goal, cols, rows)

            self.assertIsNotNone(
                path,
                f"Could not find path in {cols}x{rows} maze from {start} to {goal}"
            )
            self.assertEqual(path[0], start)
            self.assertEqual(path[-1], goal)

    def test_pathfinding_with_high_branchiness(self):
        """Test pathfinding in highly branched mazes."""
        # High branchiness should create many alternative paths
        rng = random.Random(42)
        rooms = generate_macro_maze(6, 6, rng, branchiness=0.8)

        start = (0, 5)
        goal = (5, 0)

        path = find_room_path(rooms, start, goal, 6, 6)

        self.assertIsNotNone(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)


class TestMazeProperties(unittest.TestCase):
    """Test maze structural properties."""

    def test_start_room_is_visited(self):
        """Test that start room is accessible."""
        rng = random.Random(42)
        rooms = generate_macro_maze(5, 5, rng)

        # Start is at (0, 4) - bottom-left
        start_room = rooms[4][0]

        # Should have at least one open connection
        has_connection = (
            start_room.open_up or start_room.open_down or
            start_room.open_left or start_room.open_right
        )

        self.assertTrue(has_connection, "Start room has no connections")

    def test_goal_room_is_reachable(self):
        """Test that goal room can be reached from start."""
        rng = random.Random(42)
        rooms = generate_macro_maze(6, 6, rng)

        start = (0, 5)  # Bottom-left
        goal = (5, 0)   # Top-right

        path = find_room_path(rooms, start, goal, 6, 6)

        self.assertIsNotNone(path, "Goal room is not reachable from start")

    def test_maze_has_no_isolated_rooms(self):
        """Test that no rooms are completely isolated."""
        rng = random.Random(123)
        rooms = generate_macro_maze(5, 5, rng)

        for y in range(5):
            for x in range(5):
                room = rooms[y][x]
                has_connection = (
                    room.open_up or room.open_down or
                    room.open_left or room.open_right
                )
                self.assertTrue(
                    has_connection,
                    f"Room at ({x},{y}) is isolated with no connections"
                )


if __name__ == '__main__':
    unittest.main()
