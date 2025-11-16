"""
Unit tests for ability system

Tests cover:
- Cooldown logic
- State transitions
- Resource consumption (charges, stamina)
- Ability activation conditions
"""

import unittest
from abilities.movement import DoubleJump, Dash, WallJump, Slide
from abilities.advanced import ShadowStep, WallCling, AirDodge, Glide
from powerups import SpeedBoost, TripleJump, CoinMagnet, PowerupManager


class TestDoubleJump(unittest.TestCase):
    """Test double jump ability."""

    def setUp(self):
        self.ability = DoubleJump()
        self.ability.enabled = True

    def test_initialization(self):
        """Test ability initializes with correct values."""
        self.assertEqual(self.ability.jumps_left, self.ability.max_jumps)
        self.assertEqual(self.ability.coyote_timer, 0.0)
        self.assertEqual(self.ability.jump_buffer_timer, 0.0)

    def test_ground_jump(self):
        """Test jumping from ground."""
        player_state = {'on_ground': True, 'crouching': False, 'jump_power': 12.0}
        input_state = {}

        self.assertTrue(self.ability.can_use(player_state))
        result = self.ability.use(player_state, input_state)

        self.assertIsNotNone(result)
        self.assertIn('vy', result)
        self.assertLess(result['vy'], 0)  # Negative = upward
        self.assertEqual(self.ability.jumps_left, self.ability.max_jumps - 1)

    def test_coyote_time(self):
        """Test coyote time allows jump after leaving ground."""
        # Update while on ground
        player_state = {'on_ground': True}
        self.ability.update(0.016, player_state)
        self.assertGreater(self.ability.coyote_timer, 0)

        # Leave ground
        player_state = {'on_ground': False}
        self.ability.update(0.016, player_state)

        # Should still be able to jump in coyote time
        self.assertTrue(self.ability.can_use(player_state))

    def test_air_jump(self):
        """Test double jump in air."""
        # Use ground jump first
        player_state = {'on_ground': True, 'crouching': False, 'jump_power': 12.0}
        self.ability.use(player_state, {})

        # Now in air
        player_state = {'on_ground': False, 'crouching': False, 'jump_power': 12.0}
        self.ability.coyote_timer = 0.0  # Expired

        self.assertTrue(self.ability.can_use(player_state))
        result = self.ability.use(player_state, {})

        self.assertIsNotNone(result)
        self.assertEqual(self.ability.jumps_left, 0)

    def test_no_jumps_left(self):
        """Test can't jump when out of jumps."""
        self.ability.jumps_left = 0
        self.ability.coyote_timer = 0.0

        player_state = {'on_ground': False}
        self.assertFalse(self.ability.can_use(player_state))

    def test_jump_reset_on_ground(self):
        """Test jumps reset when landing."""
        self.ability.jumps_left = 0

        player_state = {'on_ground': True}
        self.ability.update(0.016, player_state)

        self.assertEqual(self.ability.jumps_left, self.ability.max_jumps)

    def test_max_jumps_modification(self):
        """Test modifying max jumps (for powerups)."""
        self.ability.set_max_jumps(3)
        self.assertEqual(self.ability.max_jumps, 3)
        self.assertEqual(self.ability.jumps_left, 3)


class TestDash(unittest.TestCase):
    """Test dash ability."""

    def setUp(self):
        self.ability = Dash()
        self.ability.enabled = True

    def test_initialization(self):
        """Test ability initializes correctly."""
        self.assertFalse(self.ability.is_active)
        self.assertEqual(self.ability.cooldown_timer, 0.0)

    def test_can_dash(self):
        """Test dash activation conditions."""
        player_state = {'facing': 1}
        self.assertTrue(self.ability.can_use(player_state))

    def test_dash_activation(self):
        """Test activating dash."""
        player_state = {'facing': 1}
        result = self.ability.use(player_state, {})

        self.assertIsNotNone(result)
        self.assertIn('vx', result)
        self.assertTrue(self.ability.is_active)
        self.assertGreater(self.ability.dash_timer, 0)

    def test_dash_cooldown(self):
        """Test dash cooldown prevents immediate reuse."""
        player_state = {'facing': 1}

        # Use dash
        self.ability.use(player_state, {})
        self.assertTrue(self.ability.is_active)

        # Update until dash expires
        while self.ability.is_active:
            self.ability.update(0.016, player_state)

        # Should be on cooldown
        self.assertTrue(self.ability.is_on_cooldown())
        self.assertFalse(self.ability.can_use(player_state))

        # Update until cooldown expires
        while self.ability.is_on_cooldown():
            self.ability.update(0.016, player_state)

        # Should be usable again
        self.assertTrue(self.ability.can_use(player_state))

    def test_dash_duration(self):
        """Test dash lasts correct duration."""
        player_state = {'facing': 1}
        self.ability.use(player_state, {})

        elapsed = 0.0
        dt = 0.016
        while self.ability.is_active:
            self.ability.update(dt, player_state)
            elapsed += dt

        # Should be approximately the dash duration
        self.assertAlmostEqual(elapsed, self.ability.duration, delta=dt * 2)


class TestShadowStep(unittest.TestCase):
    """Test shadow step ability."""

    def setUp(self):
        self.ability = ShadowStep()
        self.ability.enabled = True

    def test_initialization(self):
        """Test ability initializes with charges."""
        self.assertEqual(self.ability.resource, self.ability.max_resource)
        self.assertGreater(self.ability.resource, 0)

    def test_consume_charge(self):
        """Test using shadow step consumes a charge."""
        initial_charges = self.ability.resource
        player_state = {'facing': 1}

        self.ability.use(player_state, {})
        self.assertEqual(self.ability.resource, initial_charges - 1)

    def test_no_charges_prevents_use(self):
        """Test can't use without charges."""
        self.ability.resource = 0
        player_state = {'facing': 1}

        self.assertFalse(self.ability.can_use(player_state))

    def test_invulnerability(self):
        """Test shadow step grants invulnerability."""
        player_state = {'facing': 1}
        self.ability.use(player_state, {})

        self.assertTrue(self.ability.is_invulnerable())
        self.assertTrue(self.ability.is_active)

    def test_invulnerability_persists(self):
        """Test invulnerability persists after shadow step ends."""
        player_state = {'facing': 1}
        self.ability.use(player_state, {})

        # Update until shadow step ends
        while self.ability.is_active:
            self.ability.update(0.016, player_state)

        # Should still be invulnerable briefly
        self.assertTrue(self.ability.is_invulnerable())
        self.assertGreater(self.ability.invuln_timer, 0)

    def test_reset_charges(self):
        """Test resetting charges to maximum."""
        self.ability.resource = 0
        self.ability.reset()
        self.assertEqual(self.ability.resource, self.ability.max_resource)


class TestWallCling(unittest.TestCase):
    """Test wall cling ability."""

    def setUp(self):
        self.ability = WallCling()
        self.ability.enabled = True

    def test_initialization(self):
        """Test ability initializes with full stamina."""
        self.assertEqual(self.ability.resource, self.ability.max_resource)

    def test_can_cling_on_wall(self):
        """Test can cling when on wall."""
        player_state = {'on_wall': True, 'on_ground': False, 'wall_dir': 1}
        self.assertTrue(self.ability.can_use(player_state))

    def test_cannot_cling_on_ground(self):
        """Test can't cling when on ground."""
        player_state = {'on_wall': True, 'on_ground': True, 'wall_dir': 1}
        self.assertFalse(self.ability.can_use(player_state))

    def test_stamina_drain(self):
        """Test stamina drains while clinging."""
        player_state = {'on_wall': True, 'on_ground': False, 'wall_dir': 1, 'vy': 5}
        input_state = {'left': False, 'right': True}

        initial_stamina = self.ability.resource
        self.ability.use(player_state, input_state)

        # Update several times
        for _ in range(10):
            self.ability.update(0.1, player_state)

        self.assertLess(self.ability.resource, initial_stamina)

    def test_stamina_regeneration(self):
        """Test stamina regenerates when not clinging."""
        # Drain stamina
        self.ability.resource = 0.5
        self.ability.is_active = False

        player_state = {'on_wall': False, 'on_ground': True}

        # Update several times
        for _ in range(10):
            self.ability.update(0.1, player_state)

        # Stamina should have regenerated
        self.assertGreater(self.ability.resource, 0.5)

    def test_cling_ends_when_stamina_depleted(self):
        """Test clinging stops when out of stamina."""
        player_state = {'on_wall': True, 'on_ground': False, 'wall_dir': 1, 'vy': 5}
        input_state = {'left': False, 'right': True}

        self.ability.use(player_state, input_state)
        self.ability.resource = 0.01  # Almost depleted

        self.ability.update(0.1, player_state)
        self.assertFalse(self.ability.is_active)


class TestAirDodge(unittest.TestCase):
    """Test air dodge ability."""

    def setUp(self):
        self.ability = AirDodge()
        self.ability.enabled = True

    def test_initialization(self):
        """Test ability initializes correctly."""
        self.assertEqual(self.ability.uses_left, self.ability.max_uses)
        self.assertFalse(self.ability.is_active)

    def test_can_dodge_in_air(self):
        """Test can dodge when in air."""
        player_state = {'on_ground': False}
        self.assertTrue(self.ability.can_use(player_state))

    def test_cannot_dodge_on_ground(self):
        """Test can't dodge on ground."""
        player_state = {'on_ground': True}
        self.assertFalse(self.ability.can_use(player_state))

    def test_consume_use(self):
        """Test dodging consumes a use."""
        initial_uses = self.ability.uses_left
        player_state = {'on_ground': False, 'facing': 1}
        input_state = {'dodge_x': 1, 'dodge_y': 0}

        self.ability.use(player_state, input_state)
        self.assertEqual(self.ability.uses_left, initial_uses - 1)

    def test_uses_reset_on_ground(self):
        """Test uses reset when landing."""
        self.ability.uses_left = 0

        player_state = {'on_ground': True}
        self.ability.update(0.016, player_state)

        self.assertEqual(self.ability.uses_left, self.ability.max_uses)

    def test_invulnerability_during_dodge(self):
        """Test dodge grants invulnerability."""
        player_state = {'on_ground': False, 'facing': 1}
        input_state = {'dodge_x': 1, 'dodge_y': 0}

        self.ability.use(player_state, input_state)
        self.assertTrue(self.ability.is_invulnerable())

    def test_directional_dodge(self):
        """Test dodge moves in specified direction."""
        player_state = {'on_ground': False, 'facing': 1}
        input_state = {'dodge_x': 1, 'dodge_y': -1}

        result = self.ability.use(player_state, input_state)

        self.assertIn('vx', result)
        self.assertIn('vy', result)
        # Both should be non-zero for diagonal dodge
        self.assertNotEqual(result['vx'], 0)
        self.assertNotEqual(result['vy'], 0)


class TestGlide(unittest.TestCase):
    """Test glide ability."""

    def setUp(self):
        self.ability = Glide()
        self.ability.enabled = True

    def test_can_glide_while_falling(self):
        """Test can glide when falling."""
        player_state = {'on_ground': False, 'vy': 5}  # Positive = falling
        self.assertTrue(self.ability.can_use(player_state))

    def test_cannot_glide_while_rising(self):
        """Test can't glide while moving upward."""
        player_state = {'on_ground': False, 'vy': -5}  # Negative = rising
        self.assertFalse(self.ability.can_use(player_state))

    def test_glide_activation(self):
        """Test activating glide."""
        player_state = {'on_ground': False, 'vy': 5, 'vx': 3}
        input_state = {'jump_held': True}

        result = self.ability.use(player_state, input_state)
        self.assertIn('is_gliding', result)
        self.assertTrue(result['is_gliding'])

    def test_glide_deactivates_without_input(self):
        """Test glide stops when jump is released."""
        player_state = {'on_ground': False, 'vy': 5, 'vx': 3}
        input_state = {'jump_held': False}

        result = self.ability.use(player_state, input_state)
        self.assertFalse(result.get('is_gliding', False))


class TestPowerups(unittest.TestCase):
    """Test powerup system."""

    def test_speed_boost_activation(self):
        """Test speed boost activates correctly."""
        powerup = SpeedBoost()
        self.assertFalse(powerup.is_active())

        powerup.activate()
        self.assertTrue(powerup.is_active())
        self.assertGreater(powerup.get_speed_multiplier(), 1.0)

    def test_speed_boost_expiration(self):
        """Test speed boost expires after duration."""
        powerup = SpeedBoost(duration=0.1)
        powerup.activate()

        # Update past duration
        powerup.update(0.2)
        self.assertFalse(powerup.is_active())
        self.assertEqual(powerup.get_speed_multiplier(), 1.0)

    def test_triple_jump_extra_jumps(self):
        """Test triple jump grants extra jumps."""
        powerup = TripleJump()
        self.assertEqual(powerup.get_extra_jumps(), 0)

        powerup.activate()
        self.assertGreater(powerup.get_extra_jumps(), 0)

    def test_coin_magnet_radius(self):
        """Test coin magnet has correct radius."""
        powerup = CoinMagnet()
        self.assertEqual(powerup.get_radius(), 0.0)

        powerup.activate()
        self.assertGreater(powerup.get_radius(), 0.0)

    def test_powerup_timer(self):
        """Test powerup timer counts down."""
        powerup = SpeedBoost(duration=1.0)
        powerup.activate()

        initial_time = powerup.get_time_remaining()
        powerup.update(0.1)

        self.assertLess(powerup.get_time_remaining(), initial_time)

    def test_powerup_manager(self):
        """Test powerup manager handles multiple powerups."""
        manager = PowerupManager()

        manager.activate_speed_boost()
        manager.activate_triple_jump()

        active = manager.get_active_powerups()
        self.assertIn('speed_boost', active)
        self.assertIn('triple_jump', active)

        # Update all
        manager.update(0.016)

        # All should still be active
        self.assertGreater(manager.get_speed_multiplier(), 1.0)
        self.assertGreater(manager.get_extra_jumps(), 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
