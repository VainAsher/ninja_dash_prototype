"""
Player Module - Enhanced character controller with ability and power-up systems

This refactored version separates player physics from ability implementations.
Abilities are self-contained in the abilities/ package, and powerups are
managed through the powerups module.
"""

import pygame
import math
from settings import (
    TILE_SIZE,
    MAX_RUN_SPEED, RUN_ACCEL_GROUND, RUN_DECEL_GROUND,
    RUN_ACCEL_AIR, RUN_DECEL_AIR,
    GRAVITY, JUMP_POWER, MAX_JUMPS,
    FALL_GRAVITY_MULT, JUMP_CUT_MULT,
    WALL_SLIDE_SPEED, FAST_FALL_MULT, MAX_FALL_SPEED,
    CROUCH_SPEED_MULT,
    PLAYER_MAX_HEALTH, INVINCIBILITY_TIME,
    FEATURES,
)

# Import ability classes
from abilities.movement import DoubleJump, Dash, WallJump, Slide
from abilities.advanced import ShadowStep, WallCling, AirDodge, Glide
from abilities.combat import SwordAttack, GrappleHook
from powerups import PowerupManager

# Import physics and state management
from physics.player_collider import PlayerCollider

# Import combo system
from abilities.combos import ComboTracker

# Import animation events (for future animation system)
from abilities.animation_events import (
    emit_ability_start,
    emit_ability_end,
    emit_impact,
    emit_particle_burst
)


class Player:
    """
    Player character with physics-based movement and modular ability system.

    The player now uses a composition-based approach where abilities are
    separate objects that handle their own state and logic.
    """

    def __init__(self, x, y):
        # Physical properties
        self.normal_height = int(TILE_SIZE * 1.5)
        self.crouch_height = self.normal_height // 2
        self.width = TILE_SIZE - 8
        self.rect = pygame.Rect(x, y, self.width, self.normal_height)

        # Movement state
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1

        # Collision state
        self.on_ground = False
        self.on_wall = False
        self.wall_dir = 0

        # Crouch state
        self._down_prev = False
        self.crouching = False

        # Health system
        self.health = PLAYER_MAX_HEALTH
        self.inv_timer = 0.0

        # User overrides (from settings)
        self.user_max_speed = None
        self.user_gravity = None
        self.user_jump_power = None

        # === PHYSICS & COLLISION ===
        self.collider = PlayerCollider()

        # === COMBO SYSTEM ===
        self.combo_tracker = ComboTracker()

        # === ABILITY SYSTEM ===
        # Movement abilities
        self.abilities = {
            'double_jump': DoubleJump(),
            'dash': Dash(),
            'wall_jump': WallJump(),
            'slide': Slide(),
            # Advanced abilities
            'shadow_step': ShadowStep(),
            'wall_cling': WallCling(),
            'air_dodge': AirDodge(),
            'glide': Glide(),
            # Combat abilities
            'sword_attack': SwordAttack(),
            'grapple_hook': GrappleHook(),
        }

        # Track which abilities are unlocked
        self.unlocked_abilities = set()

        # === POWERUP SYSTEM ===
        self.powerup_manager = PowerupManager()

        # Input tracking (for edge detection)
        self._jump_held = False
        self._dash_held = False
        self._shadow_step_held = False
        self._slide_key_held = False
        self._air_dodge_held = False
        self._sword_key_held = False
        self._grapple_key_held = False

        # Active state flags (for rendering and external queries)
        self.is_dashing = False
        self.is_smoke_stepping = False  # Renamed from shadow_stepping
        self.is_sliding = False
        self.is_air_dodging = False
        self.is_air_dodge_hanging = False  # NEW: hang time state
        self.is_gliding = False
        self.is_wall_clinging = False
        self.is_attacking = False  # NEW: sword attack
        self.is_blocking = False   # NEW: sword block
        self.is_grappling = False  # NEW: grapple hook

    def apply_user_overrides(self, overrides):
        """Apply runtime physics overrides from user settings."""
        self.user_max_speed = overrides.get('MAX_RUN_SPEED')
        self.user_gravity = overrides.get('GRAVITY')
        self.user_jump_power = overrides.get('JUMP_POWER')

    def unlock_ability(self, ability_name):
        """
        Unlock an ability for use.

        Args:
            ability_name: Name of ability to unlock (e.g., "SHADOW_STEP")
        """
        self.unlocked_abilities.add(ability_name)
        # Map ability names to ability keys
        ability_map = {
            'DOUBLE_JUMP': 'double_jump',
            'DASH': 'dash',
            'WALL_JUMP': 'wall_jump',
            'SLIDE': 'slide',
            'SHADOW_STEP': 'shadow_step',
            'WALL_CLING': 'wall_cling',
            'AIR_DODGE': 'air_dodge',
            'GLIDE': 'glide',
            'SWORD_ATTACK': 'sword_attack',
            'GRAPPLE_HOOK': 'grapple_hook',
        }
        ability_key = ability_map.get(ability_name)
        if ability_key and ability_key in self.abilities:
            self.abilities[ability_key].enabled = True

    def update(self, keys, tiles, dt, phaseable_walls=None, abilities=None):
        """
        Update player state based on input and physics.

        Args:
            keys: Pygame key state
            tiles: List of tile rectangles for collision
            dt: Delta time since last frame
            phaseable_walls: Optional list of walls that can be phased through
            abilities: Optional list of unlocked ability names
        """
        if phaseable_walls is None:
            phaseable_walls = []
        if abilities is None:
            abilities = []

        # Unlock abilities from list
        for ability_name in abilities:
            self.unlock_ability(ability_name)

        # Update timers and powerups
        self._update_timers(dt)
        self.powerup_manager.update(dt)

        # Update combo tracker
        combo_effects = self.combo_tracker.update(dt)

        # Update all abilities (with combo effects applied)
        self._update_abilities(dt, combo_effects)

        # Handle input
        self._handle_input(keys, tiles)

        # Apply gravity
        self._apply_gravity(keys)

        # Move and resolve collisions
        self._move_and_collide(tiles, phaseable_walls)

        # Apply wall slide or wall cling if on wall
        if self.on_wall and not self.on_ground:
            if self.is_wall_clinging:
                # Wall cling handled by ability
                pass
            elif self.vy > WALL_SLIDE_SPEED:
                # Regular wall slide
                self.vy = WALL_SLIDE_SPEED

    def take_damage(self, amount):
        """Apply damage to player if not invincible."""
        # Check all sources of invincibility
        if self.is_invulnerable():
            return False

        # Apply block damage reduction if blocking
        if self.is_blocking:
            amount *= 0.5  # 50% damage reduction

        self.health -= max(1, int(amount))
        self.inv_timer = INVINCIBILITY_TIME

        # Register damage with powerups (for extra jump expiration)
        self.powerup_manager.register_damage(max(1, int(amount)))

        return True

    def heal(self, amount):
        """Restore health to player."""
        self.health = min(PLAYER_MAX_HEALTH, self.health + max(1, int(amount)))

    def is_invulnerable(self):
        """Check if player is currently invulnerable from any source."""
        # Regular invincibility timer
        if self.inv_timer > 0.0:
            return True
        # Shadow step invulnerability
        if self.abilities['shadow_step'].is_invulnerable():
            return True
        # Air dodge invulnerability
        if self.abilities['air_dodge'].is_invulnerable():
            return True
        return False

    def reset_shadow_step_charges(self):
        """Reset Shadow Step charges for new level."""
        self.abilities['shadow_step'].reset()

    # ===== POWER-UP INTERFACE =====

    def apply_speed_boost(self, duration=None, factor=None):
        """Activate speed boost power-up."""
        self.powerup_manager.activate_speed_boost(duration, factor)

    def apply_triple_jump(self, duration=None, extra=None):
        """Activate triple jump power-up."""
        self.powerup_manager.activate_triple_jump(duration, extra)
        # Update double jump ability with extra jumps
        extra_jumps = self.powerup_manager.get_extra_jumps()
        self.abilities['double_jump'].set_max_jumps(MAX_JUMPS + extra_jumps)

    def apply_extra_jump(self, uses=None, damage_limit=None):
        """Activate extra jump power-up (use/damage-based)."""
        self.powerup_manager.activate_extra_jump(uses, damage_limit)
        # Update double jump ability with extra jumps
        extra_jumps = self.powerup_manager.get_extra_jumps()
        self.abilities['double_jump'].set_max_jumps(MAX_JUMPS + extra_jumps)

    def activate_magnet(self, duration=None, radius=None):
        """Activate coin magnet power-up."""
        self.powerup_manager.activate_coin_magnet(duration, radius)

    def apply_magnet_to_coins(self, coins, dt):
        """Pull coins toward player if magnet is active."""
        player_center = self.rect.center
        self.powerup_manager.apply_magnet_to_coins(player_center, coins, dt)

    # ===== INTERNAL METHODS =====

    def _update_timers(self, dt):
        """Update basic timers."""
        if self.inv_timer > 0.0:
            self.inv_timer = max(0.0, self.inv_timer - dt)

    def _update_abilities(self, dt, combo_effects=None):
        """Update all ability states with combo effects applied."""
        if combo_effects is None:
            combo_effects = {}

        # Build player state for abilities
        player_state = self._get_player_state()

        # Update each ability and apply state modifications
        for ability in self.abilities.values():
            if ability.enabled or ability.name == "DOUBLE_JUMP":  # Double jump always enabled
                modifications = ability.update(dt, player_state)
                self._apply_ability_modifications(modifications)

        # Update active state flags from abilities
        self.is_dashing = self.abilities['dash'].is_active
        self.is_smoke_stepping = self.abilities['shadow_step'].is_active  # Renamed
        self.is_sliding = self.abilities['slide'].is_active
        air_dodge = self.abilities['air_dodge']
        self.is_air_dodging = air_dodge.is_dodging if hasattr(air_dodge, 'is_dodging') else air_dodge.is_active
        self.is_air_dodge_hanging = air_dodge.is_hanging if hasattr(air_dodge, 'is_hanging') else False
        self.is_gliding = self.abilities['glide'].is_active
        self.is_wall_clinging = self.abilities['wall_cling'].is_active
        self.is_attacking = self.abilities['sword_attack'].is_attacking if hasattr(self.abilities['sword_attack'], 'is_attacking') else False
        self.is_blocking = self.abilities['sword_attack'].is_blocking if hasattr(self.abilities['sword_attack'], 'is_blocking') else False
        self.is_grappling = self.abilities['grapple_hook'].is_active if hasattr(self.abilities['grapple_hook'], 'is_active') else False

        # Update triple jump max jumps from powerup
        extra_jumps = self.powerup_manager.get_extra_jumps()
        if extra_jumps > 0:
            self.abilities['double_jump'].set_max_jumps(MAX_JUMPS + extra_jumps)
        elif self.abilities['double_jump'].max_jumps != MAX_JUMPS:
            # Powerup expired, reset to base
            self.abilities['double_jump'].set_max_jumps(MAX_JUMPS)

    def _get_player_state(self):
        """Build a state dictionary for ability use."""
        return {
            'on_ground': self.on_ground,
            'on_wall': self.on_wall,
            'wall_dir': self.wall_dir,
            'vx': self.vx,
            'vy': self.vy,
            'facing': self.facing,
            'crouching': self.crouching,
            'jump_power': self.user_jump_power or JUMP_POWER,
        }

    def _apply_ability_modifications(self, modifications):
        """Apply state modifications returned by abilities."""
        if not modifications:
            return

        # NEW: Apply multipliers before direct sets
        if 'vx_mult' in modifications:
            self.vx *= modifications['vx_mult']

        if 'vx' in modifications:
            self.vx = modifications['vx']
        if 'vy' in modifications:
            self.vy = modifications['vy']
        if 'facing' in modifications:
            self.facing = modifications['facing']
        if 'on_ground' in modifications:
            self.on_ground = modifications['on_ground']
        if 'is_dashing' in modifications:
            self.is_dashing = modifications['is_dashing']
        # NEW: Handle renamed smoke stepping
        if 'is_smoke_stepping' in modifications:
            self.is_smoke_stepping = modifications['is_smoke_stepping']
        if 'is_shadow_stepping' in modifications:  # Legacy support
            self.is_smoke_stepping = modifications['is_shadow_stepping']
        if 'is_sliding' in modifications:
            self.is_sliding = modifications['is_sliding']
        if 'is_air_dodging' in modifications:
            self.is_air_dodging = modifications['is_air_dodging']
        # NEW: Air dodge hang time
        if 'is_air_dodge_hanging' in modifications:
            self.is_air_dodge_hanging = modifications['is_air_dodge_hanging']
        if 'is_gliding' in modifications:
            self.is_gliding = modifications['is_gliding']
        if 'is_wall_clinging' in modifications:
            self.is_wall_clinging = modifications['is_wall_clinging']
        # NEW: Sword combat
        if 'is_attacking' in modifications:
            self.is_attacking = modifications['is_attacking']
        if 'is_blocking' in modifications:
            self.is_blocking = modifications['is_blocking']
        # NEW: Grapple hook
        if 'is_grappling' in modifications:
            self.is_grappling = modifications['is_grappling']
        if 'crouching' in modifications:
            if modifications['crouching'] and not self.crouching:
                self._enter_crouch()

    def _handle_input(self, keys, tiles):
        """Process player input and trigger abilities."""
        # Get input state
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        down_now = keys[pygame.K_s] or keys[pygame.K_DOWN]
        jump_down = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

        # DEBUG: F-key controls for ability testing
        if keys[pygame.K_F1] and not getattr(self, '_f1_held', False):
            self.abilities['double_jump'].enabled = not self.abilities['double_jump'].enabled
            print(f"[DEBUG] Double Jump: {'ENABLED' if self.abilities['double_jump'].enabled else 'DISABLED'}")
        self._f1_held = keys[pygame.K_F1]

        if keys[pygame.K_F2] and not getattr(self, '_f2_held', False):
            self.abilities['dash'].enabled = not self.abilities['dash'].enabled
            print(f"[DEBUG] Dash: {'ENABLED' if self.abilities['dash'].enabled else 'DISABLED'}")
        self._f2_held = keys[pygame.K_F2]

        if keys[pygame.K_F3] and not getattr(self, '_f3_held', False):
            self.abilities['slide'].enabled = not self.abilities['slide'].enabled
            print(f"[DEBUG] Slide: {'ENABLED' if self.abilities['slide'].enabled else 'DISABLED'}")
        self._f3_held = keys[pygame.K_F3]

        if keys[pygame.K_F4] and not getattr(self, '_f4_held', False):
            self.abilities['shadow_step'].enabled = not self.abilities['shadow_step'].enabled
            print(f"[DEBUG] Shadow Step: {'ENABLED' if self.abilities['shadow_step'].enabled else 'DISABLED'}")
        self._f4_held = keys[pygame.K_F4]

        if keys[pygame.K_F5] and not getattr(self, '_f5_held', False):
            self.abilities['wall_cling'].enabled = not self.abilities['wall_cling'].enabled
            print(f"[DEBUG] Wall Cling: {'ENABLED' if self.abilities['wall_cling'].enabled else 'DISABLED'}")
        self._f5_held = keys[pygame.K_F5]

        if keys[pygame.K_F6] and not getattr(self, '_f6_held', False):
            self.abilities['air_dodge'].enabled = not self.abilities['air_dodge'].enabled
            print(f"[DEBUG] Air Dodge: {'ENABLED' if self.abilities['air_dodge'].enabled else 'DISABLED'}")
        self._f6_held = keys[pygame.K_F6]

        if keys[pygame.K_F7] and not getattr(self, '_f7_held', False):
            self.abilities['glide'].enabled = not self.abilities['glide'].enabled
            print(f"[DEBUG] Glide: {'ENABLED' if self.abilities['glide'].enabled else 'DISABLED'}")
        self._f7_held = keys[pygame.K_F7]

        if keys[pygame.K_F8] and not getattr(self, '_f8_held', False):
            self.abilities['sword_attack'].enabled = not self.abilities['sword_attack'].enabled
            print(f"[DEBUG] Sword Attack: {'ENABLED' if self.abilities['sword_attack'].enabled else 'DISABLED'}")
        self._f8_held = keys[pygame.K_F8]

        if keys[pygame.K_F9] and not getattr(self, '_f9_held', False):
            self.abilities['grapple_hook'].enabled = not self.abilities['grapple_hook'].enabled
            print(f"[DEBUG] Grapple Hook: {'ENABLED' if self.abilities['grapple_hook'].enabled else 'DISABLED'}")
        self._f9_held = keys[pygame.K_F9]

        # Wall jump can lock horizontal input
        if self.abilities['wall_jump'].is_input_locked():
            left = False
            right = False

        # Handle crouch toggle
        if FEATURES.get("crouch", True):
            if down_now and not self._down_prev and self.on_ground:
                if not self.crouching:
                    self._enter_crouch()
                else:
                    self._try_exit_crouch(tiles)
        self._down_prev = down_now

        # Build input state for abilities
        input_state = {
            'left': left,
            'right': right,
            'down': down_now,
            'jump': jump_down,
        }

        # Get player state
        player_state = self._get_player_state()

        # === ABILITY ACTIVATION ===

        # Shadow Step (Q key)
        shadow_step_pressed = keys[pygame.K_q]
        if shadow_step_pressed and not self._shadow_step_held:
            ability = self.abilities['shadow_step']
            if ability.enabled and ability.can_use(player_state):
                modifications = ability.use(player_state, input_state)
                self._apply_ability_modifications(modifications)
                # Record for combo tracking
                self.combo_tracker.record_ability_use("SHADOW_STEP")
                emit_ability_start("SHADOW_STEP")
        self._shadow_step_held = shadow_step_pressed

        # Dash (Shift) - NEW: Hold to activate, release to deactivate
        dash_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if FEATURES.get("dash", True):
            ability = self.abilities['dash']
            if dash_pressed:
                # Holding dash - activate or maintain
                if ability.can_use(player_state):
                    was_active = ability.is_active
                    modifications = ability.use(player_state, input_state)
                    self._apply_ability_modifications(modifications)
                    # Record for combo tracking (only on first activation)
                    if not was_active and ability.is_active:
                        self.combo_tracker.record_ability_use("DASH")
                        emit_ability_start("DASH")
            else:
                # Released dash - deactivate
                if self._dash_held:  # Was holding, now released
                    ability.deactivate_dash()
                    self.is_dashing = False
        self._dash_held = dash_pressed

        # Slide (C key)
        slide_key = keys[pygame.K_c]
        if slide_key and not self._slide_key_held:
            ability = self.abilities['slide']
            if ability.enabled and ability.can_use(player_state):
                modifications = ability.use(player_state, input_state)
                self._apply_ability_modifications(modifications)
                # Record for combo tracking
                self.combo_tracker.record_ability_use("SLIDE")
                emit_ability_start("SLIDE")
        self._slide_key_held = slide_key

        # Wall Cling (hold toward wall)
        ability = self.abilities['wall_cling']
        if ability.enabled:
            was_active = ability.is_active
            modifications = ability.use(player_state, input_state)
            self._apply_ability_modifications(modifications)
            # Record for combo tracking (only on first activation)
            if not was_active and ability.is_active:
                self.combo_tracker.record_ability_use("WALL_CLING")
                emit_ability_start("WALL_CLING")

        # Air Dodge (X key) - NEW: Hang time support
        air_dodge_key = keys[pygame.K_x]
        ability = self.abilities['air_dodge']
        if air_dodge_key and not self._air_dodge_held:
            if ability.enabled and ability.can_use(player_state):
                # Build dodge direction from input
                dodge_x = (-1 if left else 0) + (1 if right else 0)
                dodge_y = (-1 if jump_down else 0) + (1 if down_now else 0)
                input_state['dodge_x'] = dodge_x
                input_state['dodge_y'] = dodge_y
                modifications = ability.use(player_state, input_state)
                self._apply_ability_modifications(modifications)
                # Record for combo tracking
                self.combo_tracker.record_ability_use("AIR_DODGE")
                emit_ability_start("AIR_DODGE")

        # NEW: Update direction during hang time
        if ability.enabled and hasattr(ability, 'is_hanging') and ability.is_hanging:
            dodge_x = (-1 if left else 0) + (1 if right else 0)
            dodge_y = (-1 if jump_down else 0) + (1 if down_now else 0)
            input_state['dodge_x'] = dodge_x
            input_state['dodge_y'] = dodge_y
            ability.update_direction(input_state, player_state)

        self._air_dodge_held = air_dodge_key

        # Glide (hold jump while falling)
        ability = self.abilities['glide']
        if ability.enabled:
            was_active = ability.is_active
            input_state['jump_held'] = jump_down
            modifications = ability.use(player_state, input_state)
            self._apply_ability_modifications(modifications)
            # Record for combo tracking (only on first activation)
            if not was_active and ability.is_active:
                self.combo_tracker.record_ability_use("GLIDE")
                emit_ability_start("GLIDE")

        # === HORIZONTAL MOVEMENT ===
        # Only apply manual movement if no ability is controlling velocity
        if not (self.is_smoke_stepping or self.is_air_dodging or self.is_sliding):
            target_dir = (-1 if left else 0) + (1 if right else 0)
            if target_dir != 0:
                self.facing = target_dir

            on_ground = self.on_ground

            # NEW: Apply glide air control multipliers
            accel = RUN_ACCEL_GROUND if on_ground else RUN_ACCEL_AIR
            decel = RUN_DECEL_GROUND if on_ground else RUN_DECEL_AIR
            if self.is_gliding:
                # Enhanced air control while gliding
                accel *= 1.5  # From GLIDE_HORIZONTAL_ACCEL
                decel *= 1.5

            if target_dir != 0:
                if (self.vx == 0) or (self.vx * target_dir > 0):
                    self.vx += target_dir * accel
                else:
                    self.vx += target_dir * decel
            else:
                if abs(self.vx) <= decel:
                    self.vx = 0.0
                else:
                    self.vx -= decel * (1 if self.vx > 0 else -1)

            if self.crouching:
                self.vx *= CROUCH_SPEED_MULT

            # Apply speed limits (with power-up and ability modifiers)
            effective_max_speed = self.user_max_speed or MAX_RUN_SPEED

            # NEW: Apply dash speed multiplier
            if self.is_dashing:
                dash_ability = self.abilities['dash']
                effective_max_speed *= dash_ability.speed_multiplier

            # Power-up speed multiplier
            speed_mult = self.powerup_manager.get_speed_multiplier()
            effective_max_speed *= speed_mult

            # NEW: Apply glide horizontal enhancement
            if self.is_gliding:
                effective_max_speed *= 1.3  # From GLIDE_HORIZONTAL_MULT

            # CAP: Maximum combined speed to prevent extreme velocities
            # This prevents dash + powerup + glide from stacking too much
            absolute_max_speed = MAX_RUN_SPEED * 2.5  # Never exceed 2.5x base speed
            effective_max_speed = min(effective_max_speed, absolute_max_speed)

            if abs(self.vx) > effective_max_speed:
                self.vx = effective_max_speed * (1 if self.vx > 0 else -1)

        # === JUMPING ===
        if jump_down and not self._jump_held:
            self.abilities['double_jump'].request_jump()
        self._jump_held = jump_down

        # Try to execute jump
        double_jump = self.abilities['double_jump']
        if double_jump.has_buffered_jump():
            # Try ground/coyote jump first
            if double_jump.can_use(player_state):
                modifications = double_jump.use(player_state, input_state)
                if modifications:
                    self._apply_ability_modifications(modifications)
                    # Record for combo tracking (ground jump doesn't combo, only air jumps)
                    return

            # Try wall jump
            if FEATURES.get("wall_jump", True):
                wall_jump = self.abilities['wall_jump']
                if wall_jump.enabled and wall_jump.can_use(player_state):
                    modifications = wall_jump.use(player_state, input_state)
                    if modifications:
                        self._apply_ability_modifications(modifications)
                        # Reset jump count after wall jump
                        double_jump.jumps_left = double_jump.max_jumps - 1
                        double_jump.jump_buffer_timer = 0.0
                        # Record for combo tracking
                        self.combo_tracker.record_ability_use("WALL_JUMP")
                        emit_ability_start("WALL_JUMP")
                        emit_impact("WALL_JUMP")
                        return

            # Try double jump
            if FEATURES.get("double_jump", True) and double_jump.can_use(player_state):
                modifications = double_jump.use(player_state, input_state)
                if modifications:
                    self._apply_ability_modifications(modifications)
                    # Record for combo tracking
                    self.combo_tracker.record_ability_use("DOUBLE_JUMP")
                    emit_ability_start("DOUBLE_JUMP")
                    emit_particle_burst("DOUBLE_JUMP")

                    # NEW: Consume extra jump powerup use if using extra jump
                    extra_jumps = self.powerup_manager.get_extra_jumps()
                    if extra_jumps > 0:
                        # Check if this was an extra jump from the powerup
                        # (jumps_used > MAX_JUMPS means using powerup jump)
                        if double_jump.jumps_used > MAX_JUMPS:
                            self.powerup_manager.consume_extra_jump_use()

    def _apply_gravity(self, keys):
        """Apply gravity and vertical movement modifiers."""
        down = keys[pygame.K_s] or keys[pygame.K_DOWN]
        jump_held = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

        # Air Dodge (dodging phase) and Glide handle their own vertical movement
        if self.is_air_dodging or self.is_gliding:
            return

        # Use override gravity if set
        effective_gravity = self.user_gravity or GRAVITY

        # NEW: Apply hang time gravity reduction
        if self.is_air_dodge_hanging:
            effective_gravity *= 0.1  # Hang time has 10% gravity

        self.vy += effective_gravity

        # Jump cut: release jump early = faster fall (not during hang time)
        if self.vy < 0 and not jump_held and not self.is_air_dodge_hanging:
            self.vy += effective_gravity * (JUMP_CUT_MULT - 1)

        # Falling gravity multiplier (not during hang time)
        if self.vy > 0 and not self.is_air_dodge_hanging:
            self.vy += effective_gravity * (FALL_GRAVITY_MULT - 1)

        # Fast fall (not during hang time)
        if FEATURES.get("fast_fall", True) and self.vy > 0 and down and not self.on_ground and not self.is_air_dodge_hanging:
            self.vy += effective_gravity * (FAST_FALL_MULT - 1)

        # Terminal velocity
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

    def _move_and_collide(self, tiles, phaseable_walls=None):
        """Move player and resolve collisions with tiles."""
        if phaseable_walls is None:
            phaseable_walls = []

        # Use the PlayerCollider to handle all collision logic
        self.vx, self.vy, self.on_ground, self.on_wall, self.wall_dir = \
            self.collider.move_and_collide(
                self.rect,
                self.vx,
                self.vy,
                tiles,
                phaseable_walls,
                self.is_smoke_stepping,
                self.is_sliding
            )

    def _enter_crouch(self):
        """Enter crouch state."""
        if self.crouching:
            return

        diff = self.normal_height - self.crouch_height
        self.rect.y += diff
        self.rect.height = self.crouch_height
        self.crouching = True

    def _try_exit_crouch(self, tiles):
        """Try to exit crouch state if space is available."""
        if not self.crouching:
            return

        if self.collider.check_can_uncrouch(self.rect, self.width, self.normal_height, tiles):
            diff = self.normal_height - self.crouch_height
            self.rect.y -= diff
            self.rect.height = self.normal_height
            self.crouching = False

    # ===== BACKWARD COMPATIBILITY PROPERTIES =====

    @property
    def jumps_left(self):
        """Backward compatibility: get jumps left from double jump ability."""
        return self.abilities['double_jump'].jumps_left

    @jumps_left.setter
    def jumps_left(self, value):
        """Backward compatibility: set jumps left on double jump ability."""
        self.abilities['double_jump'].jumps_left = value

    @property
    def base_max_jumps(self):
        """Backward compatibility: get max jumps from double jump ability."""
        return self.abilities['double_jump'].max_jumps

    @base_max_jumps.setter
    def base_max_jumps(self, value):
        """Backward compatibility: set max jumps on double jump ability."""
        self.abilities['double_jump'].max_jumps = value

    @property
    def shadow_step_charges(self):
        """Backward compatibility: get shadow step/smoke step charges."""
        return self.abilities['shadow_step'].resource

    @shadow_step_charges.setter
    def shadow_step_charges(self, value):
        """Backward compatibility: set shadow step/smoke step charges."""
        self.abilities['shadow_step'].resource = value

    @property
    def shadow_step_max_charges(self):
        """Backward compatibility: get shadow step/smoke step max charges."""
        return self.abilities['shadow_step'].max_resource

    @property
    def is_shadow_stepping(self):
        """Backward compatibility: renamed to is_smoke_stepping."""
        return self.is_smoke_stepping

    @is_shadow_stepping.setter
    def is_shadow_stepping(self, value):
        """Backward compatibility: renamed to is_smoke_stepping."""
        self.is_smoke_stepping = value

    # Powerup timers (for external queries)
    @property
    def speed_boost_timer(self):
        """Get remaining speed boost time."""
        return self.powerup_manager.powerups['speed_boost'].get_time_remaining()

    @property
    def triple_jump_timer(self):
        """Get remaining triple jump time."""
        return self.powerup_manager.powerups['triple_jump'].get_time_remaining()

    @property
    def extra_jump_uses(self):
        """Get remaining extra jump uses."""
        powerup = self.powerup_manager.powerups.get('extra_jump')
        return powerup.uses_remaining if powerup and powerup.is_active() else 0

    @property
    def magnet_timer(self):
        """Get remaining magnet time."""
        return self.powerup_manager.powerups['coin_magnet'].get_time_remaining()

    @property
    def magnet_radius(self):
        """Get current magnet radius."""
        return self.powerup_manager.get_magnet_radius()
