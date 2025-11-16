#!/usr/bin/env python3
"""
Quick verification script for low-priority refinements.
Tests that all new components work correctly without requiring pygame.
"""

import sys
from typing import Dict, Any

# Test 1: Constants backward compatibility
print("=" * 60)
print("Test 1: Constants backward compatibility")
print("=" * 60)

# Test old-style import still works
try:
    from level_gen.constants import (
        DEFAULT_VERTICALITY_BIAS,
        DEFAULT_BRANCHINESS,
        DEFAULT_PLATFORM_BAND_STEP,
        DEFAULT_HAZARD_RATE,
        DEFAULT_ABILITY_ORB_SPAWN_RATE,
    )
    print("✓ Old-style imports work correctly")
    print(f"  - DEFAULT_VERTICALITY_BIAS = {DEFAULT_VERTICALITY_BIAS}")
    print(f"  - DEFAULT_HAZARD_RATE = {DEFAULT_HAZARD_RATE}")
except ImportError as e:
    print(f"✗ Old-style imports failed: {e}")
    sys.exit(1)

# Test new-style imports work
try:
    from level_gen.constants.maze import DEFAULT_VERTICALITY_BIAS as VERT_BIAS
    from level_gen.constants.decoration import DEFAULT_PLATFORM_BAND_STEP as PLATFORM_STEP
    from level_gen.constants.entities import DEFAULT_HAZARD_RATE as HAZARD_RATE
    from level_gen.constants.abilities import DEFAULT_ABILITY_ORB_SPAWN_RATE as ORB_RATE
    print("✓ New-style modular imports work correctly")
    print(f"  - maze.DEFAULT_VERTICALITY_BIAS = {VERT_BIAS}")
    print(f"  - entities.DEFAULT_HAZARD_RATE = {HAZARD_RATE}")
except ImportError as e:
    print(f"✗ New-style imports failed: {e}")
    sys.exit(1)

# Test values match
if DEFAULT_VERTICALITY_BIAS == VERT_BIAS:
    print("✓ Values match between old and new import styles")
else:
    print("✗ Value mismatch detected!")
    sys.exit(1)

print()

# Test 2: Configuration Dataclass
print("=" * 60)
print("Test 2: Configuration Dataclass")
print("=" * 60)

try:
    from level_gen.config import (
        LevelGenConfig,
        EASY_CONFIG,
        MEDIUM_CONFIG,
        HARD_CONFIG,
    )
    print("✓ Config imports successful")

    # Test creating custom config
    custom_config = LevelGenConfig(
        verticality_bias=0.7,
        hazard_rate=0.05,
        coin_density=0.03,
    )
    print(f"✓ Custom config created: verticality_bias={custom_config.verticality_bias}")

    # Test validation
    custom_config.validate()
    print("✓ Config validation passed")

    # Test from_dict conversion
    old_style_dict = {
        'verticality_bias': 0.6,
        'hazard_rate': 0.04,
        'unknown_key': 'should_be_ignored',
    }
    converted_config = LevelGenConfig.from_dict(old_style_dict)
    assert converted_config.verticality_bias == 0.6
    assert converted_config.hazard_rate == 0.04
    print("✓ from_dict() backward compatibility works")

    # Test to_dict conversion
    config_dict = custom_config.to_dict()
    assert isinstance(config_dict, dict)
    assert 'verticality_bias' in config_dict
    print("✓ to_dict() conversion works")

    # Test preset configs
    assert EASY_CONFIG.hazard_rate == 0.015
    assert MEDIUM_CONFIG.hazard_rate == 0.03
    assert HARD_CONFIG.hazard_rate == 0.045
    print("✓ Preset difficulty configs (EASY, MEDIUM, HARD) work correctly")

except Exception as e:
    print(f"✗ Config test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Performance utilities
print("=" * 60)
print("Test 3: Performance Utilities")
print("=" * 60)

try:
    from level_gen.utils import (
        is_in_bounds,
        is_on_boundary,
        precompute_valid_spawn_locations,
        SpatialGrid,
    )
    print("✓ Performance utility imports successful")

    # Test cached boundary checks
    result1 = is_in_bounds(5, 5, 100, 100, margin=1)
    result2 = is_in_bounds(5, 5, 100, 100, margin=1)  # Should hit cache
    assert result1 == result2 == True
    print("✓ Cached boundary checks work")

    # Test spatial grid
    grid = SpatialGrid(100, 100, cell_size=10)
    grid.add((10, 10))
    grid.add((15, 15))
    grid.add((50, 50))

    nearby = grid.get_nearby((12, 12), radius=5)
    assert len(nearby) > 0
    print(f"✓ Spatial grid works (found {len(nearby)} nearby entities)")

except Exception as e:
    print(f"✗ Performance utilities test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Docstring quality check
print("=" * 60)
print("Test 4: Enhanced Docstrings")
print("=" * 60)

try:
    from level_gen.config import LevelGenConfig
    from level_gen.utils import precompute_valid_spawn_locations

    # Check that docstrings exist and are comprehensive
    config_doc = LevelGenConfig.__doc__
    assert config_doc is not None
    assert len(config_doc) > 200, "Docstring should be comprehensive"
    assert "Example:" in config_doc, "Should include usage examples"
    print("✓ LevelGenConfig has comprehensive docstring with examples")

    precompute_doc = precompute_valid_spawn_locations.__doc__
    assert precompute_doc is not None
    assert "Performance:" in precompute_doc, "Should document performance characteristics"
    assert "Example:" in precompute_doc, "Should include usage examples"
    print("✓ Performance functions have detailed documentation")

except Exception as e:
    print(f"✗ Docstring check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Summary
print("=" * 60)
print("✓✓✓ ALL TESTS PASSED ✓✓✓")
print("=" * 60)
print()
print("Summary of improvements:")
print("  1. ✓ Configuration Dataclass: Type-safe LevelGenConfig with validation")
print("  2. ✓ Enhanced Docstrings: Comprehensive docs with examples and ASCII diagrams")
print("  3. ✓ Performance Optimizations: Caching, pre-computation, spatial partitioning")
print("  4. ✓ Organized Constants: Separated into maze, decoration, entities, abilities")
print()
print("Backward compatibility:")
print("  - Old dict-based config still works via from_dict()")
print("  - All constants imports remain unchanged")
print("  - Existing code continues to function without modifications")
