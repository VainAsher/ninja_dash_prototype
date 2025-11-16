"""Test script for low priority refinements

Tests:
1. Ability input buffering system
2. Cooldown modifiers
3. Performance optimization utilities
4. Unlock system with prerequisites
"""

import sys


def test_ability_buffer():
    """Test the ability input buffering system."""
    print("Testing ability input buffer...")
    from input.ability_buffer import AbilityInputBuffer, AbilityType

    buffer = AbilityInputBuffer()

    # Test buffering
    buffer.buffer_input(AbilityType.DASH)
    assert buffer.has_buffered_input(AbilityType.DASH), "Dash should be buffered"

    # Test consumption
    data = buffer.consume_buffered_input(AbilityType.DASH)
    assert not buffer.has_buffered_input(AbilityType.DASH), "Dash should be consumed"

    # Test expiration
    buffer.buffer_input(AbilityType.JUMP)
    buffer.update(1.0)  # Update past buffer time
    assert not buffer.has_buffered_input(AbilityType.JUMP), "Jump should have expired"

    print("✓ Ability buffer tests passed")


def test_cooldown_modifiers():
    """Test the cooldown modifier system."""
    print("\nTesting cooldown modifiers...")
    from abilities.modifiers import (
        AbilityModifierManager, ModifierType, ModifierSource,
        create_cooldown_modifier, StackingType
    )

    mgr = AbilityModifierManager()

    # Test single modifier
    mod = create_cooldown_modifier(
        "test_mod",
        20.0,  # 20% reduction
        ModifierSource.EQUIPMENT
    )
    mgr.add_modifier(mod)

    modified = mgr.apply_modifiers(2.0, ModifierType.COOLDOWN)
    expected = 2.0 * 0.8  # 20% reduction
    assert abs(modified - expected) < 0.01, f"Expected {expected}, got {modified}"

    # Test stacking modifiers
    mod2 = create_cooldown_modifier(
        "test_mod2",
        30.0,  # 30% reduction
        ModifierSource.POWERUP
    )
    mgr.add_modifier(mod2)

    modified = mgr.apply_modifiers(2.0, ModifierType.COOLDOWN)
    expected = 2.0 * 0.8 * 0.7  # Both modifiers multiply
    assert abs(modified - expected) < 0.01, f"Expected {expected}, got {modified}"

    print("✓ Cooldown modifier tests passed")


def test_performance_optimization():
    """Test performance optimization utilities."""
    print("\nTesting performance optimization...")
    from abilities.performance import PlayerStateCache, AbilityUpdateOptimizer

    # Test state cache
    cache = PlayerStateCache()
    test_state = {
        'on_ground': True,
        'vx': 5.0,
        'vy': -2.0,
        'facing': 1
    }

    cache.update(test_state, 0.0)
    assert cache.on_ground == True, "Cache should store on_ground"
    assert cache.vx == 5.0, "Cache should store vx"

    # Test optimizer
    optimizer = AbilityUpdateOptimizer()

    # Mock ability
    class MockAbility:
        def __init__(self):
            self.enabled = True
            self.cooldown_timer = 0.5
            self.name = "MOCK"

        def is_active(self):
            return False

        def update(self, dt, player_state):
            return {}

    ability = MockAbility()
    should_update = optimizer.should_update_ability(ability, test_state)
    assert should_update, "Ability with active timer should update"

    ability.cooldown_timer = 0.0
    ability.enabled = False
    should_update = optimizer.should_update_ability(ability, test_state)
    assert not should_update, "Disabled ability with no timers should skip"

    print("✓ Performance optimization tests passed")


def test_unlock_prerequisites():
    """Test unlock system with prerequisites."""
    print("\nTesting unlock prerequisites...")
    from unlocks import ABILITY_PREREQUISITES, ABILITY_ORDER

    # Verify prerequisite structure
    assert "DOUBLE_DASH" in ABILITY_PREREQUISITES, "DOUBLE_DASH should have prerequisite"
    assert ABILITY_PREREQUISITES["DOUBLE_DASH"] == "DASH", "DOUBLE_DASH requires DASH"

    # Test basic abilities have no prerequisites
    assert ABILITY_PREREQUISITES["DOUBLE_JUMP"] is None, "DOUBLE_JUMP should be starter"
    assert ABILITY_PREREQUISITES["DASH"] is None, "DASH should be starter"

    # Test upgrade paths
    assert ABILITY_PREREQUISITES["SLIDE"] == "DASH", "SLIDE requires DASH"
    assert ABILITY_PREREQUISITES["SHADOW_STEP"] == "DASH", "SHADOW_STEP requires DASH"

    print("✓ Unlock prerequisite tests passed")


def test_ability_buffering_integration():
    """Test that abilities have buffering methods."""
    print("\nTesting ability buffering integration...")
    from abilities.movement import Dash, Slide
    from abilities.advanced import AirDodge, ShadowStep

    # Test Dash
    dash = Dash()
    assert hasattr(dash, 'request_dash'), "Dash should have request_dash method"
    assert hasattr(dash, 'has_buffered_dash'), "Dash should have has_buffered_dash method"
    dash.request_dash()
    assert dash.has_buffered_dash(), "Dash should be buffered"

    # Test Slide
    slide = Slide()
    assert hasattr(slide, 'request_slide'), "Slide should have request_slide method"
    assert hasattr(slide, 'has_buffered_slide'), "Slide should have has_buffered_slide method"

    # Test AirDodge
    air_dodge = AirDodge()
    assert hasattr(air_dodge, 'request_air_dodge'), "AirDodge should have request_air_dodge method"
    assert hasattr(air_dodge, 'has_buffered_air_dodge'), "AirDodge should have has_buffered_air_dodge method"

    # Test ShadowStep
    shadow_step = ShadowStep()
    assert hasattr(shadow_step, 'request_shadow_step'), "ShadowStep should have request_shadow_step method"
    assert hasattr(shadow_step, 'has_buffered_shadow_step'), "ShadowStep should have has_buffered_shadow_step method"

    print("✓ Ability buffering integration tests passed")


def test_modifier_integration():
    """Test that abilities integrate with modifier system."""
    print("\nTesting modifier integration...")
    from abilities.movement import Slide
    from abilities.modifiers import (
        get_modifier_manager, create_cooldown_modifier,
        ModifierSource
    )

    mgr = get_modifier_manager()
    mgr.add_modifier(create_cooldown_modifier(
        "test_slide_reduction",
        50.0,  # 50% cooldown reduction
        ModifierSource.EQUIPMENT,
        ability_filter={"SLIDE"}
    ))

    slide = Slide()
    base_cooldown = slide.base_cooldown_duration
    modified_cooldown = slide.get_modified_cooldown()

    # Should be 50% of base
    expected = base_cooldown * 0.5
    assert abs(modified_cooldown - expected) < 0.01, \
        f"Expected {expected}s cooldown, got {modified_cooldown}s"

    print("✓ Modifier integration tests passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Low Priority Refinements")
    print("=" * 60)

    try:
        test_ability_buffer()
        test_cooldown_modifiers()
        test_performance_optimization()
        test_unlock_prerequisites()
        test_ability_buffering_integration()
        test_modifier_integration()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
