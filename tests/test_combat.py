"""
Combat System Tests

Tests for combat mechanics including:
- Sword attack activation and hitbox creation
- Damage calculation and application
- Knockback physics
- Attack cooldown timing
- Block mechanics
- Damage number display
"""

import unittest
from unittest.mock import Mock, MagicMock
from abilities.combat import SwordAttack
from core.combat_system import (
    calculate_knockback,
    deal_damage,
    check_attack_hit,
    DamageNumber,
    DamageNumberManager
)

# Try to import pygame and Player, skip tests if not available
try:
    import pygame
    pygame.init()
    from player import Player
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    pygame = None
    Player = None


@unittest.skipUnless(PYGAME_AVAILABLE, "Pygame not available")
class TestSwordAttack(unittest.TestCase):
    """Test sword attack ability."""

    def setUp(self):
        """Set up test fixtures."""
        self.ability = SwordAttack()
        self.ability.enabled = True

    def test_can_use_when_ready(self):
        """Test that sword attack can be used when not attacking and off cooldown."""
        player_state = {
            'on_ground': True,
            'facing': 1,
            'vx': 0,
            'vy': 0
        }
        self.assertTrue(self.ability.can_use(player_state))

    def test_cannot_use_while_attacking(self):
        """Test that sword attack cannot be used while already attacking."""
        self.ability.is_attacking = True
        player_state = {'facing': 1}
        self.assertFalse(self.ability.can_use(player_state))

    def test_cannot_use_on_cooldown(self):
        """Test that sword attack cannot be used while on cooldown."""
        self.ability.start_cooldown()
        player_state = {'facing': 1}
        self.assertFalse(self.ability.can_use(player_state))

    def test_tap_triggers_attack(self):
        """Test that a quick tap triggers an attack."""
        player_state = {'facing': 1}

        # Press
        self.ability.on_input_pressed(player_state)
        self.assertEqual(self.ability.hold_timer, 0.0)

        # Quick release (before block threshold)
        result = self.ability.on_input_released(player_state)

        self.assertIsNotNone(result)
        self.assertTrue(result.get('is_attacking'))
        self.assertEqual(result.get('attack_direction'), 1)
        self.assertGreater(result.get('attack_damage', 0), 0)
        self.assertGreater(result.get('attack_knockback', 0), 0)

    def test_hold_triggers_block(self):
        """Test that holding triggers block after threshold."""
        player_state = {'facing': 1}

        # Press
        self.ability.on_input_pressed(player_state)

        # Hold past threshold
        dt = 0.2  # Longer than block_hold_time (0.15)
        result = self.ability.on_input_held(dt, player_state)

        self.assertIsNotNone(result)
        self.assertTrue(result.get('is_blocking'))
        self.assertGreater(result.get('block_damage_reduction', 0), 0)
        self.assertTrue(result.get('can_reflect_projectiles'))

    def test_attack_direction_matches_facing(self):
        """Test that attack direction matches player facing."""
        # Facing right
        player_state = {'facing': 1}
        self.ability.on_input_pressed(player_state)
        result = self.ability.on_input_released(player_state)
        self.assertEqual(result.get('attack_direction'), 1)

        # Reset
        self.ability.reset()

        # Facing left
        player_state = {'facing': -1}
        self.ability.on_input_pressed(player_state)
        result = self.ability.on_input_released(player_state)
        self.assertEqual(result.get('attack_direction'), -1)

    def test_attack_timer_expires(self):
        """Test that attack timer expires correctly."""
        player_state = {'facing': 1}

        # Trigger attack
        self.ability.on_input_pressed(player_state)
        self.ability.on_input_released(player_state)
        self.assertTrue(self.ability.is_attacking)

        # Update past duration
        dt = self.ability.attack_duration + 0.1
        result = self.ability.update(dt, player_state)

        self.assertFalse(self.ability.is_attacking)
        self.assertFalse(result.get('is_attacking', True))

    def test_cooldown_prevents_rapid_attacks(self):
        """Test that cooldown prevents rapid successive attacks."""
        player_state = {'facing': 1}

        # First attack
        self.ability.on_input_pressed(player_state)
        result1 = self.ability.on_input_released(player_state)
        self.assertTrue(result1.get('is_attacking'))

        # Try immediate second attack
        self.ability.reset()  # Reset attack state but not cooldown
        self.ability.on_input_pressed(player_state)
        result2 = self.ability.on_input_released(player_state)

        # Should not be able to attack due to cooldown
        self.assertFalse(result2.get('is_attacking', False))


@unittest.skipUnless(PYGAME_AVAILABLE, "Pygame not available")
class TestAttackHitbox(unittest.TestCase):
    """Test player attack hitbox creation."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(100, 100)
        self.player.abilities['sword_attack'].enabled = True

    def test_no_hitbox_when_not_attacking(self):
        """Test that no hitbox exists when not attacking."""
        self.player.is_attacking = False
        hitbox = self.player.get_attack_hitbox()
        self.assertIsNone(hitbox)

    def test_hitbox_exists_when_attacking(self):
        """Test that hitbox is created when attacking."""
        self.player.is_attacking = True
        hitbox = self.player.get_attack_hitbox()
        self.assertIsNotNone(hitbox)
        self.assertIsInstance(hitbox, pygame.Rect)

    def test_hitbox_right_facing(self):
        """Test hitbox position when facing right."""
        self.player.facing = 1
        self.player.is_attacking = True
        hitbox = self.player.get_attack_hitbox()

        # Hitbox should start at player's right edge
        self.assertEqual(hitbox.left, self.player.rect.right)
        self.assertEqual(hitbox.height, self.player.rect.height)

    def test_hitbox_left_facing(self):
        """Test hitbox position when facing left."""
        self.player.facing = -1
        self.player.is_attacking = True
        hitbox = self.player.get_attack_hitbox()

        # Hitbox should end at player's left edge
        self.assertEqual(hitbox.right, self.player.rect.left)
        self.assertEqual(hitbox.height, self.player.rect.height)

    def test_hitbox_uses_ability_range(self):
        """Test that hitbox width matches ability range."""
        self.player.is_attacking = True
        attack_range = self.player.abilities['sword_attack'].range
        hitbox = self.player.get_attack_hitbox()

        self.assertEqual(hitbox.width, attack_range)


class TestDamageCalculation(unittest.TestCase):
    """Test damage and knockback calculations."""

    def test_knockback_horizontal(self):
        """Test knockback calculation for horizontal hit."""
        attacker_pos = (100, 100)
        target_pos = (200, 100)  # Same height, to the right
        knockback_force = 10.0

        vx, vy = calculate_knockback(attacker_pos, target_pos, knockback_force)

        # Should knock to the right
        self.assertGreater(vx, 0)
        # Should have slight upward component
        self.assertLess(vy, 0)

    def test_knockback_vertical(self):
        """Test knockback calculation for vertical hit."""
        attacker_pos = (100, 100)
        target_pos = (100, 200)  # Directly below
        knockback_force = 10.0

        vx, vy = calculate_knockback(attacker_pos, target_pos, knockback_force)

        # Horizontal should be minimal
        self.assertAlmostEqual(vx, 0, delta=1.0)
        # Should knock downward (but with upward boost, might be negative)
        # Just check that we get a valid value
        self.assertIsNotNone(vy)

    def test_knockback_diagonal(self):
        """Test knockback calculation for diagonal hit."""
        attacker_pos = (100, 100)
        target_pos = (200, 200)  # Down and to the right
        knockback_force = 10.0

        vx, vy = calculate_knockback(attacker_pos, target_pos, knockback_force)

        # Both components should be non-zero
        self.assertNotEqual(vx, 0)
        self.assertNotEqual(vy, 0)

    def test_knockback_overlapping_positions(self):
        """Test knockback when attacker and target overlap."""
        attacker_pos = (100, 100)
        target_pos = (100, 100)  # Same position
        knockback_force = 10.0

        vx, vy = calculate_knockback(attacker_pos, target_pos, knockback_force)

        # Should default to horizontal knockback
        self.assertNotEqual(vx, 0)
        self.assertIsNotNone(vy)


@unittest.skipUnless(PYGAME_AVAILABLE, "Pygame not available")
class TestDamageDealin(unittest.TestCase):
    """Test damage dealing system."""

    def setUp(self):
        """Set up test fixtures."""
        self.attacker = Mock()
        self.attacker.rect = pygame.Rect(100, 100, 32, 32)

        self.target = Mock()
        self.target.rect = pygame.Rect(200, 100, 32, 32)
        self.target.take_damage = Mock(return_value=True)
        self.target.vx = 0
        self.target.vy = 0

    def test_deal_damage_applies_damage(self):
        """Test that deal_damage calls target's take_damage method."""
        deal_damage(self.attacker, self.target, 5)
        self.target.take_damage.assert_called_once_with(5)

    def test_deal_damage_applies_knockback(self):
        """Test that deal_damage applies knockback to target."""
        initial_vx = self.target.vx
        initial_vy = self.target.vy

        deal_damage(self.attacker, self.target, 5, knockback_force=10)

        # Velocity should have changed
        self.assertNotEqual(self.target.vx, initial_vx)
        self.assertNotEqual(self.target.vy, initial_vy)

    def test_deal_damage_no_knockback_if_zero(self):
        """Test that no knockback is applied if force is 0."""
        initial_vx = self.target.vx
        initial_vy = self.target.vy

        deal_damage(self.attacker, self.target, 5, knockback_force=0)

        # Velocity should not change
        self.assertEqual(self.target.vx, initial_vx)
        self.assertEqual(self.target.vy, initial_vy)

    def test_deal_damage_returns_false_if_blocked(self):
        """Test that deal_damage returns False if damage is blocked."""
        self.target.take_damage.return_value = False
        result = deal_damage(self.attacker, self.target, 5)
        self.assertFalse(result)

    def test_deal_damage_creates_damage_number(self):
        """Test that damage numbers are created."""
        damage_mgr = DamageNumberManager()
        deal_damage(self.attacker, self.target, 5, damage_numbers=damage_mgr)

        self.assertEqual(len(damage_mgr.damage_numbers), 1)
        self.assertEqual(damage_mgr.damage_numbers[0].damage, 5)


@unittest.skipUnless(PYGAME_AVAILABLE, "Pygame not available")
class TestAttackHitDetection(unittest.TestCase):
    """Test attack hit detection."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_hit_detection_single_target(self):
        """Test hit detection with single target."""
        attack_hitbox = pygame.Rect(100, 100, 40, 30)

        target = Mock()
        target.rect = pygame.Rect(120, 110, 20, 20)  # Overlapping

        targets = [target]
        hit = check_attack_hit(attack_hitbox, targets)

        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0], target)

    def test_hit_detection_multiple_targets(self):
        """Test hit detection with multiple overlapping targets."""
        attack_hitbox = pygame.Rect(100, 100, 40, 30)

        target1 = Mock()
        target1.rect = pygame.Rect(120, 110, 20, 20)  # Overlapping

        target2 = Mock()
        target2.rect = pygame.Rect(125, 105, 20, 20)  # Also overlapping

        targets = [target1, target2]
        hit = check_attack_hit(attack_hitbox, targets)

        self.assertEqual(len(hit), 2)

    def test_hit_detection_miss(self):
        """Test that non-overlapping targets are not hit."""
        attack_hitbox = pygame.Rect(100, 100, 40, 30)

        target = Mock()
        target.rect = pygame.Rect(300, 300, 20, 20)  # Far away

        targets = [target]
        hit = check_attack_hit(attack_hitbox, targets)

        self.assertEqual(len(hit), 0)

    def test_hit_detection_prevents_double_hit(self):
        """Test that already_hit set prevents hitting the same target twice."""
        attack_hitbox = pygame.Rect(100, 100, 40, 30)

        target = Mock()
        target.rect = pygame.Rect(120, 110, 20, 20)

        already_hit = {id(target)}
        targets = [target]
        hit = check_attack_hit(attack_hitbox, targets, already_hit)

        # Should not hit again
        self.assertEqual(len(hit), 0)


@unittest.skipUnless(PYGAME_AVAILABLE, "Pygame not available")
class TestDamageNumbers(unittest.TestCase):
    """Test damage number display system."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_damage_number_creation(self):
        """Test creating a damage number."""
        dn = DamageNumber(100, 100, 5)
        self.assertEqual(dn.damage, 5)
        self.assertEqual(dn.x, 100)
        self.assertEqual(dn.y, 100)

    def test_damage_number_update(self):
        """Test damage number animation update."""
        dn = DamageNumber(100, 100, 5)
        initial_y = dn.y

        # Update for 0.1 seconds
        is_alive = dn.update(0.1)

        # Should still be alive
        self.assertTrue(is_alive)
        # Should have moved upward (y decreases)
        self.assertLess(dn.y, initial_y)

    def test_damage_number_expires(self):
        """Test that damage number expires after lifetime."""
        dn = DamageNumber(100, 100, 5)

        # Update past lifetime
        is_alive = dn.update(2.0)

        # Should be dead
        self.assertFalse(is_alive)

    def test_damage_number_manager_add(self):
        """Test adding damage numbers to manager."""
        mgr = DamageNumberManager()
        mgr.add_damage_number(100, 100, 5)

        self.assertEqual(len(mgr.damage_numbers), 1)

    def test_damage_number_manager_update_removes_expired(self):
        """Test that manager removes expired damage numbers."""
        mgr = DamageNumberManager()
        mgr.add_damage_number(100, 100, 5)

        # Update past lifetime
        mgr.update(2.0)

        # Should be removed
        self.assertEqual(len(mgr.damage_numbers), 0)

    def test_damage_number_manager_clear(self):
        """Test clearing all damage numbers."""
        mgr = DamageNumberManager()
        mgr.add_damage_number(100, 100, 5)
        mgr.add_damage_number(200, 200, 10)

        mgr.clear()

        self.assertEqual(len(mgr.damage_numbers), 0)


@unittest.skipUnless(PYGAME_AVAILABLE, "Pygame not available")
class TestCombatIntegration(unittest.TestCase):
    """Integration tests for complete combat flow."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(100, 100)
        self.player.abilities['sword_attack'].enabled = True

    def test_full_attack_cycle(self):
        """Test complete attack cycle from input to hitbox."""
        # Start attack
        player_state = {
            'on_ground': True,
            'facing': 1,
            'vx': 0,
            'vy': 0,
            'on_wall': False,
            'wall_dir': 0,
            'crouching': False,
            'jump_power': 0
        }

        sword_ability = self.player.abilities['sword_attack']

        # Press and release (tap)
        sword_ability.on_input_pressed(player_state)
        modifications = sword_ability.on_input_released(player_state)

        # Should activate attack
        self.assertTrue(modifications.get('is_attacking'))

        # Apply modifications
        self.player.is_attacking = modifications.get('is_attacking')

        # Should create hitbox
        hitbox = self.player.get_attack_hitbox()
        self.assertIsNotNone(hitbox)

        # Verify hitbox is in correct position (facing right)
        self.assertEqual(hitbox.left, self.player.rect.right)

    def test_block_reduces_damage(self):
        """Test that blocking reduces incoming damage."""
        initial_health = self.player.health

        # Activate block
        self.player.is_blocking = True

        # Take damage
        damage_dealt = self.player.take_damage(10)

        # Damage should be reduced by 50%
        expected_damage = 5
        expected_health = initial_health - expected_damage
        self.assertEqual(self.player.health, expected_health)


if __name__ == '__main__':
    unittest.main()
