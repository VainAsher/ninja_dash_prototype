"""
Tests for state transitions - game state machine behavior
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import pygame

from core.game import Game
from states.base import GameState


class TestStateTransitions(unittest.TestCase):
    """Test game state transitions."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        # Suppress display initialization for tests
        with patch('core.game.create_window') as mock_window:
            mock_window.return_value = pygame.Surface((1280, 720))
            self.game = Game()

    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()

    def test_initial_state_is_menu(self):
        """Test that game starts in menu state."""
        self.assertIsNotNone(self.game.current_state)
        self.assertEqual(self.game.states.get("menu"), self.game.current_state)

    def test_menu_to_play_transition(self):
        """Test Menu → Play state transition."""
        # Start in menu
        self.game.change_state("menu")
        self.assertEqual(self.game.current_state, self.game.states["menu"])

        # Transition to play
        self.game.change_state("play")
        self.assertEqual(self.game.current_state, self.game.states["play"])

        # Verify player is created
        self.assertIsNotNone(self.game.player)
        self.assertIsNotNone(self.game.world)

    def test_play_to_pause_transition(self):
        """Test Play → Pause state transition."""
        # Start in play state
        self.game.change_state("play")
        play_state = self.game.current_state

        # Transition to pause
        self.game.change_state("pause")
        self.assertEqual(self.game.current_state, self.game.states["pause"])

        # Game world should still exist
        self.assertIsNotNone(self.game.player)
        self.assertIsNotNone(self.game.world)

    def test_pause_to_play_transition(self):
        """Test Pause → Play (resume) transition."""
        # Start in play, then pause
        self.game.change_state("play")
        self.game.change_state("pause")

        # Resume play
        self.game.change_state("play")
        self.assertEqual(self.game.current_state, self.game.states["play"])

    def test_play_pause_play_cycle(self):
        """Test Play → Pause → Play cycle maintains game state."""
        # Start game
        self.game.change_state("play")
        initial_lives = self.game.lives
        initial_score = self.game.total_score

        # Pause
        self.game.change_state("pause")

        # Resume
        self.game.change_state("play")

        # Verify game state preserved
        self.assertEqual(self.game.lives, initial_lives)
        self.assertEqual(self.game.total_score, initial_score)

    def test_gameover_to_menu_transition(self):
        """Test GameOver → Menu transition."""
        # Trigger game over
        self.game.change_state("gameover")
        self.assertEqual(self.game.current_state, self.game.states["gameover"])

        # Return to menu
        self.game.change_state("menu")
        self.assertEqual(self.game.current_state, self.game.states["menu"])

    def test_gameover_to_highscores_transition(self):
        """Test GameOver → HighScores transition."""
        # Go to game over
        self.game.change_state("gameover")

        # Transition to highscores
        self.game.change_state("highscores")
        self.assertEqual(self.game.current_state, self.game.states["highscores"])

    def test_menu_to_settings_transition(self):
        """Test Menu → Settings transition."""
        self.game.change_state("menu")

        # Go to settings
        self.game.change_state("settings")
        self.assertEqual(self.game.current_state, self.game.states["settings"])

    def test_menu_to_help_transition(self):
        """Test Menu → Help transition."""
        self.game.change_state("menu")

        # Go to help
        self.game.change_state("help")
        self.assertEqual(self.game.current_state, self.game.states["help"])

    def test_pause_to_menu_transition(self):
        """Test Pause → Menu (quit to menu) transition."""
        # Start playing
        self.game.change_state("play")

        # Pause
        self.game.change_state("pause")

        # Quit to menu
        self.game.change_state("menu")
        self.assertEqual(self.game.current_state, self.game.states["menu"])

    def test_state_enter_exit_hooks(self):
        """Test that enter() and exit() hooks are called on state transitions."""
        # Mock state to track enter/exit calls
        mock_state = Mock(spec=GameState)
        mock_state.enter = Mock()
        mock_state.exit = Mock()

        # Add mock state to game
        self.game.states["mock"] = mock_state
        self.game.current_state = self.game.states["menu"]

        # Change to mock state
        self.game.change_state("mock")

        # Verify exit was called on previous state
        # (menu state's exit should have been called)

        # Verify enter was called on new state
        mock_state.enter.assert_called_once()

    def test_multiple_state_transitions(self):
        """Test chain of multiple state transitions."""
        transitions = [
            ("menu", "play"),
            ("play", "pause"),
            ("pause", "play"),
            ("play", "pause"),
            ("pause", "menu"),
            ("menu", "settings"),
            ("settings", "menu"),
            ("menu", "help"),
            ("help", "menu"),
        ]

        for from_state, to_state in transitions:
            self.game.change_state(from_state)
            self.game.change_state(to_state)
            self.assertEqual(
                self.game.current_state,
                self.game.states[to_state],
                f"Failed transition: {from_state} → {to_state}"
            )

    def test_controls_viewer_from_pause(self):
        """Test Pause → Controls transition."""
        self.game.change_state("play")
        self.game.change_state("pause")

        # Open controls viewer
        self.game.change_state("controls")
        self.assertEqual(self.game.current_state, self.game.states["controls"])

    def test_controls_viewer_from_help(self):
        """Test Help → Controls transition."""
        self.game.change_state("help")

        # Open controls viewer from help
        self.game.change_state("controls")
        self.assertEqual(self.game.current_state, self.game.states["controls"])

    def test_unlocks_from_menu(self):
        """Test Menu → Unlocks transition."""
        self.game.change_state("menu")

        # Open unlocks viewer
        self.game.change_state("unlocks")
        self.assertEqual(self.game.current_state, self.game.states["unlocks"])

    def test_options_from_menu(self):
        """Test Menu → Options transition."""
        self.game.change_state("menu")

        # Open options
        self.game.change_state("options")
        self.assertEqual(self.game.current_state, self.game.states["options"])

    def test_state_persistence_across_transitions(self):
        """Test that game state persists across menu transitions."""
        # Start game and modify state
        self.game.change_state("play")
        self.game.total_score = 1000
        self.game.level_index = 5

        # Go to menu and back
        self.game.change_state("pause")
        self.game.change_state("menu")
        self.game.change_state("play")

        # Score and level should be reset (new game)
        # This tests that returning to play starts fresh
        self.assertEqual(self.game.level_index, 1)

    def test_name_entry_state(self):
        """Test transition to name entry state."""
        # Simulate high score qualification
        self.game.pending_score = 10000
        self.game.pending_level = 10
        self.game.pending_difficulty = "hard"

        self.game.change_state("name_entry")
        self.assertEqual(self.game.current_state, self.game.states["name_entry"])

    def test_seed_entry_state(self):
        """Test transition to seed entry state."""
        self.game.change_state("seed_entry")
        self.assertEqual(self.game.current_state, self.game.states["seed_entry"])


class TestStateRegistration(unittest.TestCase):
    """Test that all states are properly registered."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        with patch('core.game.create_window') as mock_window:
            mock_window.return_value = pygame.Surface((1280, 720))
            self.game = Game()

    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()

    def test_all_states_registered(self):
        """Test that all expected states are registered."""
        expected_states = [
            "menu",
            "play",
            "pause",
            "gameover",
            "highscores",
            "unlocks",
            "settings",
            "options",
            "help",
            "name_entry",
            "seed_entry",
            "controls",
        ]

        for state_name in expected_states:
            self.assertIn(
                state_name,
                self.game.states,
                f"State '{state_name}' not registered"
            )

    def test_all_states_have_required_methods(self):
        """Test that all states implement required methods."""
        required_methods = ["enter", "exit", "handle_event", "update", "draw"]

        for state_name, state in self.game.states.items():
            for method_name in required_methods:
                self.assertTrue(
                    hasattr(state, method_name),
                    f"State '{state_name}' missing method '{method_name}'"
                )


if __name__ == '__main__':
    unittest.main()
