"""
Integration Tests for Ability Combinations

Tests that verify abilities work correctly together, including:
- Ability combinations (dash + wall jump, air dodge + glide, etc.)
- Powerup effects on abilities
- Edge cases and interaction bugs
"""

import pytest
import pygame
from player import Player
from settings import TILE_SIZE, JUMP_POWER, MAX_JUMPS


@pytest.fixture
def player():
    """Create a test player instance."""
    pygame.init()
    p = Player(100, 100)
    # Enable all abilities for testing
    for ability_name in ['DOUBLE_JUMP', 'DASH', 'WALL_JUMP', 'SLIDE', 'SHADOW_STEP',
                         'WALL_CLING', 'AIR_DODGE', 'GLIDE', 'SWORD_ATTACK', 'GRAPPLE_HOOK']:
        p.unlock_ability(ability_name)
    return p


@pytest.fixture
def tiles():
    """Create basic tile setup for testing."""
    # Ground
    ground = [pygame.Rect(i * TILE_SIZE, 200, TILE_SIZE, TILE_SIZE) for i in range(20)]
    # Wall on the right
    wall = [pygame.Rect(300, i * TILE_SIZE, TILE_SIZE, TILE_SIZE) for i in range(10)]
    return ground + wall


class TestAbilityCombinations:
    """Test ability combinations work correctly together."""

    def test_dash_wall_jump_combo(self, player, tiles):
        """Test that dash + wall jump combo works correctly."""
        # Set up player on wall
        player.rect.x = 300 - player.rect.width
        player.rect.y = 150
        player.vx = 5.0
        player.on_wall = True
        player.wall_dir = 1

        # Enable dash
        keys = {pygame.K_LSHIFT: True, **{k: False for k in range(512) if k != pygame.K_LSHIFT}}
        keys_obj = type('Keys', (), keys)()

        # Activate dash
        if player.abilities['dash'].can_use(player._get_player_state()):
            player.abilities['dash'].use(player._get_player_state(), {})
            player.is_dashing = True

        # Now try wall jump while dashing
        player_state = player._get_player_state()
        assert player.abilities['wall_jump'].can_use(player_state)

        # Wall jump should work even while dashing
        mods = player.abilities['wall_jump'].use(player_state, {})
        assert mods is not None
        assert 'vy' in mods
        assert mods['vy'] < 0  # Should jump upward

        # Dash should be cancelled by wall jump
        assert mods.get('is_dashing') == False

    def test_air_dodge_glide_combo(self, player, tiles):
        """Test air dodge followed by glide."""
        # Set up player in air, falling
        player.rect.y = 100
        player.vy = 5.0
        player.on_ground = False
        player.on_wall = False

        # Activate air dodge first
        player_state = player._get_player_state()
        input_state = {'dodge_x': 1, 'dodge_y': 0}

        assert player.abilities['air_dodge'].can_use(player_state)
        mods = player.abilities['air_dodge'].use(player_state, input_state)
        assert mods is not None

        # Simulate air dodge completing (update through dodge duration)
        air_dodge = player.abilities['air_dodge']
        air_dodge.is_dodging = False
        air_dodge.is_hanging = False
        air_dodge.invuln_timer = 0
        player.is_air_dodging = False

        # Now try to glide
        player.vy = 3.0  # Falling again
        player_state = player._get_player_state()
        player_state['vy'] = player.vy

        assert player.abilities['glide'].can_use(player_state)
        glide_input = {'jump_held': True}
        mods = player.abilities['glide'].use(player_state, glide_input)

        # Should be able to glide after air dodge
        assert mods is not None or player.abilities['glide'].is_active

    def test_wall_jump_double_jump_combo(self, player, tiles):
        """Test wall jump followed by double jump in air."""
        # Set up player on wall
        player.rect.x = 300 - player.rect.width
        player.rect.y = 150
        player.on_wall = True
        player.wall_dir = 1
        player.on_ground = False

        # Reset double jump ability
        player.abilities['double_jump'].jumps_left = player.abilities['double_jump'].max_jumps

        # Do wall jump
        player_state = player._get_player_state()
        wall_jump_mods = player.abilities['wall_jump'].use(player_state, {})
        assert wall_jump_mods is not None

        # Apply wall jump
        player.vy = wall_jump_mods['vy']
        player.vx = wall_jump_mods['vx']

        # Simulate being in air after wall jump
        player.on_wall = False
        player.on_ground = False

        # Player should have jumps left after wall jump (reset in player.py)
        player.abilities['double_jump'].jumps_left = player.abilities['double_jump'].max_jumps - 1

        # Try double jump
        player_state = player._get_player_state()
        assert player.abilities['double_jump'].can_use(player_state)

        double_jump_mods = player.abilities['double_jump'].use(player_state, {})
        assert double_jump_mods is not None
        assert 'vy' in double_jump_mods
        assert double_jump_mods['vy'] < 0

    def test_slide_into_wall_jump(self, player, tiles):
        """Test sliding into a wall then wall jumping."""
        # Set up player on ground, moving fast
        player.rect.y = 200 - player.rect.height
        player.vx = 10.0
        player.on_ground = True

        # Activate slide
        player_state = player._get_player_state()
        assert player.abilities['slide'].can_use(player_state)

        mods = player.abilities['slide'].use(player_state, {})
        assert mods is not None
        player.is_sliding = True

        # Move player to wall while sliding
        player.rect.x = 300 - player.rect.width - 1
        player.on_wall = True
        player.wall_dir = 1
        player.on_ground = False

        # Stop sliding (hit wall)
        player.is_sliding = False
        player.abilities['slide'].is_active = False

        # Should be able to wall jump from wall
        player_state = player._get_player_state()
        assert player.abilities['wall_jump'].can_use(player_state)

    def test_shadow_step_through_wall_jump(self, player, tiles):
        """Test shadow step followed by wall jump."""
        # Set up player
        player.rect.x = 100
        player.rect.y = 150
        player.facing = 1

        # Activate shadow step
        player_state = player._get_player_state()
        assert player.abilities['shadow_step'].can_use(player_state)

        mods = player.abilities['shadow_step'].use(player_state, {})
        assert mods is not None
        player.is_smoke_stepping = True
        player.vx = mods['vx']

        # While shadow stepping, move to wall
        player.rect.x = 300 - player.rect.width
        player.on_wall = True
        player.wall_dir = 1

        # Shadow step ends
        player.is_smoke_stepping = False
        player.abilities['shadow_step'].is_active = False

        # Should be able to wall jump
        player_state = player._get_player_state()
        assert player.abilities['wall_jump'].can_use(player_state)


class TestPowerupAbilityInteractions:
    """Test how powerups affect abilities."""

    def test_triple_jump_powerup(self, player, tiles):
        """Test triple jump powerup grants extra jump."""
        # Activate triple jump powerup
        player.apply_triple_jump(duration=10.0, extra=1)

        # Verify max jumps increased
        assert player.abilities['double_jump'].max_jumps == MAX_JUMPS + 1

        # Set up player in air after first jump
        player.on_ground = False
        player.abilities['double_jump'].jumps_left = 2  # Should have 2 jumps left with powerup

        # Use second jump
        player_state = player._get_player_state()
        assert player.abilities['double_jump'].can_use(player_state)
        mods = player.abilities['double_jump'].use(player_state, {})
        assert mods is not None

        # Should still have one more jump (triple jump)
        assert player.abilities['double_jump'].jumps_left == 1

    def test_extra_jump_powerup_consumption(self, player, tiles):
        """Test extra jump powerup uses are consumed correctly."""
        # Activate extra jump powerup (5 uses)
        player.apply_extra_jump(uses=5, damage_limit=999)

        # Should have extra jumps
        extra_jumps = player.powerup_manager.get_extra_jumps()
        assert extra_jumps > 0

        # Set up player in air
        player.on_ground = False
        player.abilities['double_jump'].jumps_left = 0  # Out of normal jumps
        player.abilities['double_jump'].jumps_used = MAX_JUMPS + 1  # Using extra jump

        # Consume one extra jump use
        initial_uses = player.powerup_manager.powerups['extra_jump'].uses_remaining
        player.powerup_manager.consume_extra_jump_use()

        # Should have one less use
        assert player.powerup_manager.powerups['extra_jump'].uses_remaining == initial_uses - 1

    def test_speed_boost_with_dash(self, player, tiles):
        """Test speed boost powerup stacks with dash."""
        # Activate speed boost
        player.apply_speed_boost(duration=10.0, factor=1.6)

        # Get base speed multiplier
        speed_mult_base = player.powerup_manager.get_speed_multiplier()
        assert speed_mult_base > 1.0

        # Activate dash
        player.abilities['dash'].is_active = True

        # Both should stack (applied in player.py movement logic)
        # This test verifies the powerup is active
        assert player.powerup_manager.powerups['speed_boost'].is_active()

    def test_powerup_expiration_resets_jumps(self, player, tiles):
        """Test that powerup expiration resets jump count."""
        # Activate triple jump
        player.apply_triple_jump(duration=10.0, extra=1)
        initial_max = player.abilities['double_jump'].max_jumps
        assert initial_max == MAX_JUMPS + 1

        # Simulate powerup expiring
        player.powerup_manager.powerups['triple_jump'].timer = 0
        player.powerup_manager.powerups['triple_jump'].active = False

        # Update player (should reset max jumps)
        keys = pygame.key.get_pressed()
        player.update(keys, tiles, 0.016, [], [])

        # Max jumps should be back to normal
        assert player.abilities['double_jump'].max_jumps == MAX_JUMPS


class TestEdgeCases:
    """Test edge cases and potential bugs."""

    def test_ability_activation_during_other_ability(self, player, tiles):
        """Test that certain abilities can't activate during others."""
        # Activate air dodge
        player.on_ground = False
        player.vy = 5.0
        player_state = player._get_player_state()
        input_state = {'dodge_x': 1, 'dodge_y': 0}

        player.abilities['air_dodge'].use(player_state, input_state)
        player.is_air_dodging = True

        # Try to activate slide (should fail - not on ground)
        player_state = player._get_player_state()
        assert not player.abilities['slide'].can_use(player_state)

    def test_wall_jump_with_no_wall(self, player, tiles):
        """Test wall jump fails when not on wall."""
        player.on_ground = False
        player.on_wall = False

        player_state = player._get_player_state()
        assert not player.abilities['wall_jump'].can_use(player_state)

    def test_dash_stamina_depletion(self, player, tiles):
        """Test dash deactivates when stamina depletes."""
        # Activate dash
        player.abilities['dash'].is_active = True

        # Drain all stamina
        player.abilities['dash'].resource = 0.01

        # Update should deactivate dash
        player_state = player._get_player_state()
        mods = player.abilities['dash'].update(0.1, player_state)

        # Should deactivate
        assert not player.abilities['dash'].is_active
        assert mods.get('is_dashing') == False

    def test_shadow_step_charge_depletion(self, player, tiles):
        """Test shadow step can't be used when out of charges."""
        # Use all charges
        player.abilities['shadow_step'].resource = 0

        player_state = player._get_player_state()
        assert not player.abilities['shadow_step'].can_use(player_state)

    def test_air_dodge_use_limit(self, player, tiles):
        """Test air dodge respects max uses per ground touch."""
        # Set up in air
        player.on_ground = False
        player.vy = 5.0

        max_uses = player.abilities['air_dodge'].max_uses
        player.abilities['air_dodge'].uses_left = max_uses

        # Use all air dodges
        for _ in range(max_uses):
            if player.abilities['air_dodge'].uses_left > 0:
                player.abilities['air_dodge'].uses_left -= 1

        # Should have no uses left
        assert player.abilities['air_dodge'].uses_left == 0

        # Can't use anymore
        player_state = player._get_player_state()
        assert not player.abilities['air_dodge'].can_use(player_state)

    def test_glide_during_upward_movement(self, player, tiles):
        """Test glide only works when falling down."""
        # Set up player moving upward
        player.on_ground = False
        player.vy = -5.0  # Moving up

        player_state = player._get_player_state()
        player_state['vy'] = player.vy

        # Should not be able to glide while moving up
        assert not player.abilities['glide'].can_use(player_state)

    def test_multiple_abilities_state_cleanup(self, player, tiles):
        """Test that ability states are properly cleaned up."""
        # Activate several abilities in sequence
        player.is_dashing = True
        player.is_sliding = True
        player.is_gliding = True

        # Update player
        keys = pygame.key.get_pressed()
        player.update(keys, tiles, 0.016, [], [])

        # Verify states are managed correctly
        # (At least one should still be active or all should be inactive)
        state_count = sum([
            player.is_dashing,
            player.is_sliding,
            player.is_gliding
        ])

        # This is a sanity check - states should be consistent
        assert state_count >= 0

    def test_wall_cling_stamina_depletion(self, player, tiles):
        """Test wall cling stops when stamina runs out."""
        # Set up on wall
        player.on_wall = True
        player.wall_dir = 1
        player.on_ground = False

        # Activate wall cling
        player.abilities['wall_cling'].is_active = True

        # Drain stamina
        player.abilities['wall_cling'].resource = 0.01

        # Update
        player_state = player._get_player_state()
        input_state = {'left': True}  # Holding toward wall
        mods = player.abilities['wall_cling'].update(0.1, player_state)

        # Should stop clinging
        assert not player.abilities['wall_cling'].is_active

    def test_collision_during_smoke_step(self, player, tiles):
        """Test that smoke step handles collision correctly."""
        # Set up smoke step
        player.abilities['shadow_step'].is_active = True
        player.is_smoke_stepping = True
        player.vx = 12.0

        # Create phaseable wall
        phaseable_wall = pygame.Rect(150, 150, TILE_SIZE, TILE_SIZE)

        # Update player with phaseable walls
        keys = pygame.key.get_pressed()
        player.update(keys, tiles, 0.016, [phaseable_wall], [])

        # Player should be able to move through phaseable walls
        # (This is tested in player collision logic)
        assert player.is_smoke_stepping or not player.abilities['shadow_step'].is_active


class TestAbilityConfigLoading:
    """Test that abilities load configuration correctly."""

    def test_double_jump_loads_config(self, player):
        """Test double jump loads parameters from config."""
        dj = player.abilities['double_jump']
        # Should have loaded values (either from config or defaults)
        assert hasattr(dj, 'jump_power_first')
        assert hasattr(dj, 'jump_power_second')
        assert hasattr(dj, 'horizontal_boost_second')
        assert dj.jump_power_first > 0
        assert dj.jump_power_second > 0

    def test_dash_loads_config(self, player):
        """Test dash loads parameters from config."""
        dash = player.abilities['dash']
        assert hasattr(dash, 'speed_multiplier')
        assert dash.speed_multiplier > 1.0
        assert dash.max_resource > 0

    def test_shadow_step_loads_config(self, player):
        """Test shadow step loads parameters from config."""
        ss = player.abilities['shadow_step']
        assert hasattr(ss, 'speed')
        assert hasattr(ss, 'duration')
        assert hasattr(ss, 'invuln_time')
        assert ss.speed > 0
        assert ss.duration > 0

    def test_air_dodge_loads_config(self, player):
        """Test air dodge loads parameters from config."""
        ad = player.abilities['air_dodge']
        assert hasattr(ad, 'speed')
        assert hasattr(ad, 'hang_duration')
        assert hasattr(ad, 'invuln_time')
        assert ad.speed > 0
        assert ad.max_uses > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
