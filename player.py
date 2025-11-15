"""
Player Module - Enhanced character controller with power-up system
Handles player physics, movement, abilities, and temporary power-up effects.
"""

import pygame
import math
from settings import (
    TILE_SIZE,
    MAX_RUN_SPEED, RUN_ACCEL_GROUND, RUN_DECEL_GROUND,
    RUN_ACCEL_AIR, RUN_DECEL_AIR,
    GRAVITY, JUMP_POWER, MAX_JUMPS, COYOTE_TIME, JUMP_BUFFER_TIME,
    FALL_GRAVITY_MULT, JUMP_CUT_MULT,
    WALL_SLIDE_SPEED, WALL_JUMP_POWER_X, WALL_JUMP_POWER_Y, WALL_JUMP_INPUT_LOCK,
    DASH_SPEED, DASH_DURATION, DASH_COOLDOWN,
    FAST_FALL_MULT, MAX_FALL_SPEED,
    CROUCH_SPEED_MULT, CROUCH_JUMP_MULT,
    PLAYER_MAX_HEALTH, INVINCIBILITY_TIME,
    FEATURES,
    SHADOW_STEP_CHARGES, SHADOW_STEP_DURATION, SHADOW_STEP_INVULN_TIME,
    SHADOW_STEP_SPEED, SHADOW_STEP_COOLDOWN,
    POWERUP_SPEED_DURATION, POWERUP_SPEED_FACTOR,
    POWERUP_TRIPLE_DURATION, POWERUP_TRIPLE_EXTRA_JUMPS,
    POWERUP_MAGNET_DURATION, POWERUP_MAGNET_RADIUS,
    SLIDE_SPEED_MULT, SLIDE_DURATION, SLIDE_MIN_SPEED, SLIDE_COOLDOWN,
    WALL_CLING_SLIDE_SPEED, WALL_CLING_STAMINA, WALL_CLING_STAMINA_REGEN,
    AIR_DODGE_SPEED, AIR_DODGE_DURATION, AIR_DODGE_INVULN_TIME,
    AIR_DODGE_COOLDOWN, AIR_DODGE_MAX_USES,
    GLIDE_FALL_SPEED, GLIDE_HORIZONTAL_MULT, GLIDE_MAX_DURATION,
)


class Player:
    """Player character with advanced platforming and power-up effects."""
    
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

        # Jump state
        self.base_max_jumps = MAX_JUMPS
        self.jumps_left = self.base_max_jumps
        self._jump_held = False

        # Dash state
        self._dash_held = False
        self.is_dashing = False
        self.dash_time = 0.0
        self.dash_cooldown = 0.0

        # Crouch state
        self._down_prev = False
        self.crouching = False

        # Advanced movement timers
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.wall_jump_lock = 0.0

        # Health system
        self.health = PLAYER_MAX_HEALTH
        self.inv_timer = 0.0

        # Power-up effects
        self.speed_boost_timer = 0.0
        self.speed_boost_duration = 0.0
        self.speed_boost_factor = 1.0
        
        self.triple_jump_timer = 0.0
        self.triple_jump_duration = 0.0
        self.triple_jump_extra = 0
        
        self.magnet_timer = 0.0
        self.magnet_duration = 0.0
        self.magnet_radius = 0.0
        
        # Shadow Step ABILITY (not power-up)
        self.shadow_step_charges = SHADOW_STEP_CHARGES
        self.shadow_step_max_charges = SHADOW_STEP_CHARGES
        self.is_shadow_stepping = False
        self.shadow_step_time = 0.0
        self.shadow_step_cooldown_timer = 0.0
        self.shadow_step_invuln = 0.0
        self._shadow_step_held = False

        # NEW ABILITIES
        # Slide
        self.is_sliding = False
        self.slide_time = 0.0
        self.slide_cooldown_timer = 0.0
        self._slide_key_held = False

        # Wall Cling
        self.is_wall_clinging = False
        self.wall_cling_stamina = WALL_CLING_STAMINA

        # Air Dodge
        self.is_air_dodging = False
        self.air_dodge_time = 0.0
        self.air_dodge_cooldown_timer = 0.0
        self.air_dodge_uses_left = AIR_DODGE_MAX_USES
        self.air_dodge_invuln_timer = 0.0
        self._air_dodge_held = False
        self.air_dodge_direction = (0, 0)  # Dodge direction vector

        # Glide
        self.is_gliding = False
        self.glide_time = 0.0

        # User overrides (from settings)
        self.user_max_speed = None
        self.user_gravity = None
        self.user_jump_power = None

    def apply_user_overrides(self, overrides):
        """Apply runtime physics overrides from user settings."""
        self.user_max_speed = overrides.get('MAX_RUN_SPEED')
        self.user_gravity = overrides.get('GRAVITY')
        self.user_jump_power = overrides.get('JUMP_POWER')

    def update(self, keys, tiles, dt, phaseable_walls=None, abilities=None):
        """Update player state based on input and physics."""
        if phaseable_walls is None:
            phaseable_walls = []
        if abilities is None:
            abilities = []
        
        self._update_timers(dt)
        self._update_powerup_timers(dt)
        self._update_dash_state(dt)
        self._update_shadow_step_state(dt)
        self._update_slide_state(dt)
        self._update_air_dodge_state(dt)
        self._update_glide_state(dt)
        self._update_wall_cling_state(dt)
        self._handle_input(keys, tiles, abilities)
        self._apply_gravity(keys)
        self._move_and_collide(tiles, phaseable_walls)

        # Apply wall slide or wall cling if on wall
        if self.on_wall and not self.on_ground:
            if self.is_wall_clinging:
                # Wall cling: very slow slide
                if self.vy > WALL_CLING_SLIDE_SPEED:
                    self.vy = WALL_CLING_SLIDE_SPEED
            elif self.vy > WALL_SLIDE_SPEED:
                # Regular wall slide
                self.vy = WALL_SLIDE_SPEED

    def take_damage(self, amount):
        """Apply damage to player if not invincible."""
        # Check invincibility: regular, shadow step, or air dodge
        if (self.inv_timer > 0.0 or
            self.shadow_step_invuln > 0.0 or
            self.air_dodge_invuln_timer > 0.0):
            return False
            
        self.health -= max(1, int(amount))
        self.inv_timer = INVINCIBILITY_TIME
        return True

    def heal(self, amount):
        """Restore health to player."""
        self.health = min(PLAYER_MAX_HEALTH, self.health + max(1, int(amount)))
    
    def reset_shadow_step_charges(self):
        """Reset Shadow Step charges for new level."""
        self.shadow_step_charges = SHADOW_STEP_CHARGES
        self.shadow_step_max_charges = SHADOW_STEP_CHARGES

    # ===== POWER-UP EFFECTS =====
    
    def apply_speed_boost(self, duration=None, factor=None):
        """Activate speed boost power-up."""
        self.speed_boost_duration = duration or POWERUP_SPEED_DURATION
        self.speed_boost_timer = self.speed_boost_duration
        self.speed_boost_factor = factor or POWERUP_SPEED_FACTOR

    def apply_triple_jump(self, duration=None, extra=None):
        """Activate triple jump power-up."""
        self.triple_jump_duration = duration or POWERUP_TRIPLE_DURATION
        self.triple_jump_timer = self.triple_jump_duration
        self.triple_jump_extra = extra or POWERUP_TRIPLE_EXTRA_JUMPS
        # Update max jumps
        self.base_max_jumps = MAX_JUMPS + self.triple_jump_extra
        self.jumps_left = min(self.jumps_left + self.triple_jump_extra, self.base_max_jumps)

    def activate_magnet(self, duration=None, radius=None):
        """Activate coin magnet power-up."""
        self.magnet_duration = duration or POWERUP_MAGNET_DURATION
        self.magnet_timer = self.magnet_duration
        self.magnet_radius = radius or POWERUP_MAGNET_RADIUS

    def _update_powerup_timers(self, dt):
        """Update power-up effect timers."""
        # Speed boost
        if self.speed_boost_timer > 0:
            self.speed_boost_timer = max(0.0, self.speed_boost_timer - dt)
            if self.speed_boost_timer <= 0:
                self.speed_boost_factor = 1.0
        
        # Triple jump
        if self.triple_jump_timer > 0:
            self.triple_jump_timer = max(0.0, self.triple_jump_timer - dt)
            if self.triple_jump_timer <= 0:
                self.triple_jump_extra = 0
                self.base_max_jumps = MAX_JUMPS
                self.jumps_left = min(self.jumps_left, self.base_max_jumps)
        
        # Magnet
        if self.magnet_timer > 0:
            self.magnet_timer = max(0.0, self.magnet_timer - dt)

    # ===== INTERNAL METHODS =====

    def _update_timers(self, dt):
        """Update various gameplay timers."""
        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)
        
        if self.jump_buffer_timer > 0.0:
            self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)
        
        if self.wall_jump_lock > 0.0:
            self.wall_jump_lock = max(0.0, self.wall_jump_lock - dt)
        
        if self.inv_timer > 0.0:
            self.inv_timer = max(0.0, self.inv_timer - dt)
        
        # Shadow Step invulnerability timer
        if self.shadow_step_invuln > 0.0:
            self.shadow_step_invuln = max(0.0, self.shadow_step_invuln - dt)

        # New ability timers
        # Slide cooldown
        if self.slide_cooldown_timer > 0.0:
            self.slide_cooldown_timer = max(0.0, self.slide_cooldown_timer - dt)

        # Wall cling stamina regen
        if not self.is_wall_clinging and self.wall_cling_stamina < WALL_CLING_STAMINA:
            self.wall_cling_stamina = min(WALL_CLING_STAMINA,
                                         self.wall_cling_stamina + WALL_CLING_STAMINA_REGEN * dt)

        # Air dodge cooldown and invuln
        if self.air_dodge_cooldown_timer > 0.0:
            self.air_dodge_cooldown_timer = max(0.0, self.air_dodge_cooldown_timer - dt)
        if self.air_dodge_invuln_timer > 0.0:
            self.air_dodge_invuln_timer = max(0.0, self.air_dodge_invuln_timer - dt)

        # Reset air dodge uses on ground
        if self.on_ground:
            self.air_dodge_uses_left = AIR_DODGE_MAX_USES

    def _update_dash_state(self, dt):
        """Update dash mechanics."""
        if self.is_dashing:
            self.dash_time -= dt
            if self.dash_time <= 0:
                self.is_dashing = False
                self.dash_cooldown = DASH_COOLDOWN
        elif self.dash_cooldown > 0:
            self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
    
    def _update_shadow_step_state(self, dt):
        """Update Shadow Step ability state."""
        if self.is_shadow_stepping:
            self.shadow_step_time -= dt
            if self.shadow_step_time <= 0:
                self.is_shadow_stepping = False
                self.shadow_step_cooldown_timer = SHADOW_STEP_COOLDOWN
                # Invulnerability persists slightly after shadow step ends
                self.shadow_step_invuln = SHADOW_STEP_INVULN_TIME
        elif self.shadow_step_cooldown_timer > 0:
            self.shadow_step_cooldown_timer = max(0.0, self.shadow_step_cooldown_timer - dt)

    def _update_slide_state(self, dt):
        """Update Slide ability state."""
        if self.is_sliding:
            self.slide_time -= dt
            # End slide if time expires or speed too low
            if self.slide_time <= 0 or abs(self.vx) < SLIDE_MIN_SPEED:
                self.is_sliding = False
                self.slide_cooldown_timer = SLIDE_COOLDOWN
                # Try to stand up
                if self.crouching:
                    self._try_exit_crouch([])  # Will be called with proper tiles later

    def _update_air_dodge_state(self, dt):
        """Update Air Dodge ability state."""
        if self.is_air_dodging:
            self.air_dodge_time -= dt
            if self.air_dodge_time <= 0:
                self.is_air_dodging = False
                self.air_dodge_cooldown_timer = AIR_DODGE_COOLDOWN

    def _update_glide_state(self, dt):
        """Update Glide ability state."""
        if self.is_gliding:
            self.glide_time += dt
            # Optional: limit glide duration
            if self.glide_time >= GLIDE_MAX_DURATION:
                self.is_gliding = False

    def _update_wall_cling_state(self, dt):
        """Update Wall Cling ability state."""
        if self.is_wall_clinging:
            # Drain stamina
            self.wall_cling_stamina -= dt
            if self.wall_cling_stamina <= 0:
                self.is_wall_clinging = False
                self.wall_cling_stamina = 0

    def _handle_input(self, keys, tiles, abilities=None):
        """Process player input and update movement."""
        import pygame
        
        if abilities is None:
            abilities = []
        
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        down_now = keys[pygame.K_s] or keys[pygame.K_DOWN]

        if self.wall_jump_lock > 0.0:
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

        # Shadow Step activation (Q key) - ABILITY
        shadow_step_pressed = keys[pygame.K_q]
        shadow_step_unlocked = "SHADOW_STEP" in abilities if abilities else False
        if shadow_step_unlocked:
            if shadow_step_pressed and not self._shadow_step_held:
                if (self.shadow_step_charges > 0 and not self.is_shadow_stepping 
                    and self.shadow_step_cooldown_timer <= 0.0):
                    self._activate_shadow_step()
        self._shadow_step_held = shadow_step_pressed

        # Handle dash
        dash_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if FEATURES.get("dash", True):
            if dash_pressed and not self._dash_held and not self.is_dashing and self.dash_cooldown <= 0.0:
                if self.facing == 0:
                    self.facing = 1
                self.is_dashing = True
                self.dash_time = DASH_DURATION
        self._dash_held = dash_pressed

        # NEW ABILITIES HANDLING

        # Slide (C key) - activated while crouched and moving
        slide_key = keys[pygame.K_c]
        slide_unlocked = "SLIDE" in abilities if abilities else False
        if slide_unlocked and not self.is_sliding:
            if slide_key and not self._slide_key_held:
                # Can only slide on ground with enough speed
                if (self.on_ground and abs(self.vx) >= SLIDE_MIN_SPEED and
                    self.slide_cooldown_timer <= 0.0):
                    self._activate_slide()
        self._slide_key_held = slide_key

        # Wall Cling - hold toward wall while touching it
        wall_cling_unlocked = "WALL_CLING" in abilities if abilities else False
        if wall_cling_unlocked and self.on_wall and not self.on_ground:
            # Check if holding toward wall
            holding_toward_wall = (
                (left and self.wall_dir == -1) or
                (right and self.wall_dir == 1)
            )
            if holding_toward_wall and self.wall_cling_stamina > 0:
                self.is_wall_clinging = True
            else:
                self.is_wall_clinging = False
        else:
            self.is_wall_clinging = False

        # Air Dodge (X key)
        air_dodge_key = keys[pygame.K_x]
        air_dodge_unlocked = "AIR_DODGE" in abilities if abilities else False
        if air_dodge_unlocked:
            if air_dodge_key and not self._air_dodge_held:
                if (not self.on_ground and not self.is_air_dodging and
                    self.air_dodge_uses_left > 0 and
                    self.air_dodge_cooldown_timer <= 0.0):
                    # Determine dodge direction from input
                    dodge_x = (-1 if left else 0) + (1 if right else 0)
                    dodge_y = (-1 if (keys[pygame.K_w] or keys[pygame.K_UP]) else 0) + \
                             (1 if down_now else 0)
                    if dodge_x == 0 and dodge_y == 0:
                        dodge_x = self.facing  # Default to facing direction
                    self._activate_air_dodge(dodge_x, dodge_y)
        self._air_dodge_held = air_dodge_key

        # Glide - hold jump while falling
        glide_unlocked = "GLIDE" in abilities if abilities else False
        jump_held = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        if glide_unlocked:
            if jump_held and not self.on_ground and self.vy > 0:
                # Can glide while falling
                self.is_gliding = True
            else:
                self.is_gliding = False
                self.glide_time = 0.0
        else:
            self.is_gliding = False

        # Apply horizontal movement
        if self.is_shadow_stepping:
            # Shadow Step has priority and uses high speed
            self.vx = self.facing * SHADOW_STEP_SPEED
        elif self.is_air_dodging:
            # Air Dodge: move in dodge direction
            self.vx = self.air_dodge_direction[0] * AIR_DODGE_SPEED
        elif self.is_dashing:
            self.vx = self.facing * DASH_SPEED
        elif self.is_sliding:
            # Slide: maintain high speed in current direction
            self.vx = self.facing * abs(self.vx) * SLIDE_SPEED_MULT
        else:
            target_dir = (-1 if left else 0) + (1 if right else 0)
            if target_dir != 0:
                self.facing = target_dir
            
            on_ground = self.on_ground
            accel = RUN_ACCEL_GROUND if on_ground else RUN_ACCEL_AIR
            decel = RUN_DECEL_GROUND if on_ground else RUN_DECEL_AIR

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

            # Apply speed limits (with power-up modifier)
            effective_max_speed = self.user_max_speed or MAX_RUN_SPEED
            if self.speed_boost_timer > 0:
                effective_max_speed *= self.speed_boost_factor
            
            if abs(self.vx) > effective_max_speed:
                self.vx = effective_max_speed * (1 if self.vx > 0 else -1)

        # Handle jumping
        jump_down = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        
        if jump_down and not self._jump_held:
            self.jump_buffer_timer = JUMP_BUFFER_TIME
        self._jump_held = jump_down

        if self.jump_buffer_timer > 0.0:
            if self._try_ground_or_coyote_jump():
                return
            if FEATURES.get("wall_jump", True) and self._try_wall_jump():
                return
            if FEATURES.get("double_jump", True) and self._try_double_jump():
                return

    def _try_ground_or_coyote_jump(self):
        """Attempt a ground or coyote jump."""
        if self.on_ground or self.coyote_timer > 0.0:
            jump_power = self.user_jump_power or JUMP_POWER
            power = jump_power * (CROUCH_JUMP_MULT if self.crouching else 1.0)
            self.vy = -power
            self.on_ground = False
            self.coyote_timer = 0.0
            self.jump_buffer_timer = 0.0
            self.jumps_left = self.base_max_jumps - 1
            return True
        return False

    def _try_wall_jump(self):
        """Attempt a wall jump."""
        if self.on_wall:
            self.facing = -self.wall_dir
            jump_power = self.user_jump_power or JUMP_POWER
            self.vy = -WALL_JUMP_POWER_Y * (jump_power / JUMP_POWER)
            self.vx = -self.wall_dir * WALL_JUMP_POWER_X
            self.jump_buffer_timer = 0.0
            self.jumps_left = self.base_max_jumps - 1
            self.is_dashing = False
            self.wall_jump_lock = WALL_JUMP_INPUT_LOCK
            return True
        return False

    def _try_double_jump(self):
        """Attempt a double/air jump."""
        if self.jumps_left > 0:
            jump_power = self.user_jump_power or JUMP_POWER
            self.vy = -jump_power
            self.jumps_left -= 1
            self.jump_buffer_timer = 0.0
            return True
        return False

    def _apply_gravity(self, keys):
        """Apply gravity and vertical movement modifiers."""
        import pygame

        down = keys[pygame.K_s] or keys[pygame.K_DOWN]
        jump_held = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

        # Air Dodge: apply vertical movement
        if self.is_air_dodging:
            self.vy = self.air_dodge_direction[1] * AIR_DODGE_SPEED
            return  # Skip normal gravity during air dodge

        # Glide: reduce fall speed significantly
        if self.is_gliding:
            if self.vy > GLIDE_FALL_SPEED:
                self.vy = GLIDE_FALL_SPEED
            # Reduce horizontal speed while gliding
            self.vx *= GLIDE_HORIZONTAL_MULT
            return  # Skip normal gravity application during glide

        # Use override gravity if set
        effective_gravity = self.user_gravity or GRAVITY

        self.vy += effective_gravity
        
        if self.vy < 0 and not jump_held:
            self.vy += effective_gravity * (JUMP_CUT_MULT - 1)
        
        if self.vy > 0:
            self.vy += effective_gravity * (FALL_GRAVITY_MULT - 1)
        
        if FEATURES.get("fast_fall", True) and self.vy > 0 and down and not self.on_ground:
            self.vy += effective_gravity * (FAST_FALL_MULT - 1)
        
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED


    def _activate_shadow_step(self):
        """Activate Shadow Step ability."""
        if self.facing == 0:
            self.facing = 1

        self.is_shadow_stepping = True
        self.shadow_step_time = SHADOW_STEP_DURATION
        self.shadow_step_charges -= 1
        self.shadow_step_invuln = SHADOW_STEP_INVULN_TIME

        # Cancel regular dash if active
        self.is_dashing = False

    def _activate_slide(self):
        """Activate Slide ability."""
        if not self.crouching:
            self._enter_crouch()
        self.is_sliding = True
        self.slide_time = SLIDE_DURATION
        self.facing = 1 if self.vx > 0 else -1

    def _activate_air_dodge(self, dodge_x, dodge_y):
        """Activate Air Dodge ability."""
        # Normalize direction
        import math
        length = math.sqrt(dodge_x * dodge_x + dodge_y * dodge_y)
        if length > 0:
            self.air_dodge_direction = (dodge_x / length, dodge_y / length)
        else:
            self.air_dodge_direction = (self.facing, 0)

        self.is_air_dodging = True
        self.air_dodge_time = AIR_DODGE_DURATION
        self.air_dodge_uses_left -= 1
        self.air_dodge_invuln_timer = AIR_DODGE_INVULN_TIME

    def _move_and_collide(self, tiles, phaseable_walls=None):
        """Move player and resolve collisions with tiles."""
        if phaseable_walls is None:
            phaseable_walls = []
        
        # During shadow step, ignore phaseable walls
        collision_tiles = tiles
        if self.is_shadow_stepping:
            collision_tiles = [t for t in tiles if t not in phaseable_walls]
        
        # Horizontal movement and collision
        self.rect.x += int(round(self.vx))
        self.on_wall = False
        self.wall_dir = 0
        
        for t in collision_tiles:
            if self.rect.colliderect(t):
                if self.vx > 0:
                    self.rect.right = t.left
                    self.on_wall = True
                    self.wall_dir = 1
                elif self.vx < 0:
                    self.rect.left = t.right
                    self.on_wall = True
                    self.wall_dir = -1
                self.vx = 0.0

        # Vertical movement and collision
        self.rect.y += int(round(self.vy))
        self.on_ground = False
        
        for t in collision_tiles:
            if self.rect.colliderect(t):
                if self.vy > 0:
                    self.rect.bottom = t.top
                    self.vy = 0.0
                    self.on_ground = True
                    self.jumps_left = self.base_max_jumps
                elif self.vy < 0:
                    self.rect.top = t.bottom
                    self.vy = 0.0

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
            
        diff = self.normal_height - self.crouch_height
        test_rect = pygame.Rect(self.rect.x, self.rect.y - diff, 
                                self.width, self.normal_height)
        
        if not any(test_rect.colliderect(t) for t in tiles):
            self.rect = test_rect
            self.crouching = False

    def apply_magnet_to_coins(self, coins, dt):
        """Pull coins toward player if magnet is active."""
        if self.magnet_timer <= 0:
            return
        
        player_center = self.rect.center
        
        for coin in coins:
            coin_center = coin.center
            dx = player_center[0] - coin_center[0]
            dy = player_center[1] - coin_center[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < self.magnet_radius and dist > 1:
                # Lerp coin toward player
                speed = 8.0
                move_x = (dx / dist) * speed
                move_y = (dy / dist) * speed
                coin.x += int(move_x)
                coin.y += int(move_y)
