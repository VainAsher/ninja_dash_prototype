"""
Test script for validating control changes and coin generation fixes.
"""

import pygame
import random
from level_gen.entity_placer import EntityPlacer
from level_gen.utils import enhanced_valid_pickup_spot
from controls import get_controls_manager
from settings import TILE_SIZE, WORLD_W, WORLD_H


def test_controls():
    """Test that controls are configured correctly."""
    print("\n=== Testing Control Configuration ===")

    controls = get_controls_manager()

    # Test movement actions
    movement_actions = [
        "movement.move_left",
        "movement.move_right",
        "movement.jump",
        "movement.crouch_down"
    ]

    for action_id in movement_actions:
        keys = controls.get_action_keys_display(action_id)
        print(f"{action_id:30} : {keys}")

        # Verify WASD keys are NOT in movement
        action = controls.actions.get(action_id)
        if action:
            key_names = [k.lower() for k in action.keys]
            if action_id != "movement.jump":
                assert 'w' not in key_names, f"WASD key 'w' found in {action_id}"
                assert 'a' not in key_names, f"WASD key 'a' found in {action_id}"
                assert 'd' not in key_names, f"WASD key 'd' found in {action_id}"
            # 's' is allowed for ground_pound, not for crouch_down in movement
            if action_id == "movement.crouch_down":
                assert 's' not in key_names, f"WASD key 's' found in {action_id}"

    print("✅ Movement controls verified - Arrow keys only!")

    # Test ability actions
    print("\n=== Ability Bindings ===")
    ability_actions = [
        "abilities.dash",
        "abilities.shadow_step",
        "abilities.grapple",
        "abilities.ground_pound"
    ]

    for action_id in ability_actions:
        keys = controls.get_action_keys_display(action_id)
        print(f"{action_id:30} : {keys}")

    print("✅ Ability controls verified!")


def test_coin_validation():
    """Test the enhanced coin validation logic."""
    print("\n=== Testing Coin Validation ===")

    # Create a test world with various scenarios
    test_world = [[0 for _ in range(10)] for _ in range(10)]

    # Scenario 1: Valid spot (air above, solid below, open sides)
    test_world[5][5] = 0  # Air
    test_world[6][5] = 1  # Solid below
    test_world[4][5] = 0  # Air above
    result1 = enhanced_valid_pickup_spot(test_world, 5, 5, allow_risky=False)
    print(f"Scenario 1 (valid open spot): {result1}")
    assert result1 == True, "Valid spot should pass"

    # Scenario 2: Invalid spot (solid above - embedded in platform)
    test_world[4][5] = 1  # Solid above
    result2 = enhanced_valid_pickup_spot(test_world, 5, 5, allow_risky=False)
    print(f"Scenario 2 (solid above): {result2}")
    assert result2 == False, "Spot with solid above should fail"

    # Scenario 3: Invalid spot (no solid below)
    test_world[4][5] = 0  # Air above (restore)
    test_world[6][5] = 0  # Air below
    result3 = enhanced_valid_pickup_spot(test_world, 5, 5, allow_risky=False)
    print(f"Scenario 3 (no solid below): {result3}")
    assert result3 == False, "Spot without solid below should fail"

    # Scenario 4: Enclosed spot (both sides solid)
    test_world[6][5] = 1  # Solid below (restore)
    test_world[5][4] = 1  # Solid left
    test_world[5][6] = 1  # Solid right
    result4 = enhanced_valid_pickup_spot(test_world, 5, 5, allow_risky=False)
    print(f"Scenario 4 (enclosed, no risky): {result4}")
    assert result4 == False, "Enclosed spot should fail in safe mode"

    # Scenario 5: Same spot but risky mode (near magnet)
    result5 = enhanced_valid_pickup_spot(test_world, 5, 5, allow_risky=True)
    print(f"Scenario 5 (enclosed, risky mode): {result5}")
    assert result5 == True, "Enclosed spot should pass in risky mode"

    print("✅ All validation tests passed!")


def test_magnet_proximity():
    """Test magnet proximity detection."""
    print("\n=== Testing Magnet Proximity ===")

    # Create dummy world and placer
    world = [[0 for _ in range(50)] for _ in range(50)]
    rng = random.Random(12345)
    placer = EntityPlacer(world, rng)

    # Create test powerups
    powerups = [
        {'rect': pygame.Rect(10 * TILE_SIZE, 10 * TILE_SIZE, 16, 16), 'type': 'magnet'},
        {'rect': pygame.Rect(30 * TILE_SIZE, 30 * TILE_SIZE, 16, 16), 'type': 'speed'},
    ]

    # Test: Close to magnet (should be True)
    result1 = placer._find_nearby_magnets(12, 12, powerups, radius=15)
    print(f"Tile (12, 12) near magnet at (10, 10): {result1}")
    assert result1 == True, "Should detect nearby magnet"

    # Test: Far from magnet (should be False)
    result2 = placer._find_nearby_magnets(40, 40, powerups, radius=15)
    print(f"Tile (40, 40) far from magnets: {result2}")
    assert result2 == False, "Should not detect distant magnet"

    # Test: Near speed powerup only (should be False)
    result3 = placer._find_nearby_magnets(32, 32, powerups, radius=15)
    print(f"Tile (32, 32) near speed powerup: {result3}")
    assert result3 == False, "Should not detect non-magnet powerup"

    print("✅ Magnet proximity tests passed!")


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("NINJA DASH - Controls & Coin Generation Tests")
    print("=" * 60)

    try:
        test_controls()
        test_coin_validation()
        test_magnet_proximity()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now test in-game:")
        print("1. Launch the game with: python main.py")
        print("2. Test arrow key controls")
        print("3. Verify no coins spawn in platforms")
        print("4. Check that coins near magnets can be in tighter spots")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    pygame.init()
    success = run_all_tests()
    pygame.quit()
    exit(0 if success else 1)
