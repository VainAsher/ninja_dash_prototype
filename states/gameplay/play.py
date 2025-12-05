
# states/play.py - core gameplay loop using entity-based collectibles

from __future__ import annotations

import pygame

from settings import DIFFICULTY_CONFIG
from ..base import GameState


class PlayState(GameState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.notification_timer = 0.0
        self.notification_text = ""
        self.unlock_notification_timer = 0.0
        self.unlock_notification_text = ""
        self.show_controls_overlay = False

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("pause")
            # F1: Toggle controls quick reference
            elif event.key == pygame.K_F1:
                self.show_controls_overlay = not self.show_controls_overlay
                print(f"[INFO] Controls Overlay: {'ON' if self.show_controls_overlay else 'OFF'}")
            # F3: Toggle debug overlay
            elif event.key == pygame.K_F3:
                if hasattr(self.game, 'debug_overlay'):
                    visible = self.game.debug_overlay.toggle()
                    print(f"[DEBUG] Debug Overlay: {'ON' if visible else 'OFF'}")
                if hasattr(self.game, 'modifiers'):
                    self.game.modifiers.toggle_debug_overlay()
            # F4: Toggle hitboxes
            elif event.key == pygame.K_F4:
                if hasattr(self.game, 'modifiers'):
                    show = self.game.modifiers.toggle_hitboxes()
                    print(f"[DEBUG] Hitboxes: {'ON' if show else 'OFF'}")
            # F5: Reload level
            elif event.key == pygame.K_F5:
                print("[DEBUG] Reloading level...")
                self.game.restart_level()
            # Tab: Toggle debug overlay mode (minimal/full)
            elif event.key == pygame.K_TAB:
                if hasattr(self.game, 'debug_overlay') and self.game.debug_overlay.visible:
                    mode = self.game.debug_overlay.toggle_mode()
                    print(f"[DEBUG] Overlay Mode: {mode}")

    def update(self, dt: float) -> None:
        player = self.game.player
        if not player:
            return

        # Advance run timer
        self.game.game_time += dt

        # Update notification timers
        if self.notification_timer > 0:
            self.notification_timer -= dt
        if self.unlock_notification_timer > 0:
            self.unlock_notification_timer -= dt

        # Check for ability orb collection notification
        if hasattr(self.game, 'ability_orb_collected') and self.game.ability_orb_collected:
            self.notification_text = "Ability Orb +1!"
            self.notification_timer = 2.0
            self.game.ability_orb_collected = False

        # Check for ability unlock notification
        if hasattr(self.game, 'ability_unlocked') and self.game.ability_unlocked:
            from unlocks import ABILITY_INFO
            ability_name = ABILITY_INFO.get(self.game.ability_unlocked, {}).get('name', self.game.ability_unlocked)
            self.unlock_notification_text = f"New Ability Unlocked: {ability_name}!"
            self.unlock_notification_timer = 3.0
            self.game.ability_unlocked = None

        # Get modifiers if available
        modifiers = getattr(self.game, 'modifiers', None)

        # --- Player movement & input (via controller when available) ---
        if getattr(self.game, "player_controller", None) is not None:
            # Preferred path: centralised control logic
            self.game.player_controller.update(dt, self.game)
        else:
            # Fallback: legacy direct control
            keys = pygame.key.get_pressed()
            player.update(
                keys,
                self.game.tiles,
                dt,
                self.game.phaseable_walls,
                self.game.abilities,
                modifiers,
            )
            # Coin magnet logic still uses the underlying coin rects via entities
            player.apply_magnet_to_coins([c.rect for c in self.game.coins], dt)

        # Update damage numbers
        if hasattr(self.game, 'damage_numbers'):
            self.game.damage_numbers.update(dt)

        # Update enemies
        if hasattr(self.game, 'enemy_manager'):
            self.game.enemy_manager.update(dt, self.game.world, player, self.game)
            self.game.enemy_manager.remove_dead()

            # Check if player died from enemy damage
            if player.health <= 0:
                self.game.lives -= 1
                if self.game.lives <= 0:
                    self.game.on_game_over()
                else:
                    self.game.restart_level()
                return

        cfg = DIFFICULTY_CONFIG[self.game.difficulty]
        multiplier = cfg.get("multiplier", 1.0)
        coin_value = int(10 * multiplier)  # kept for future scaling if needed

        # Coins (entity-based)
        for coin in self.game.coins[:]:
            # Coin entity already adds its base value & notifies the exit gate.
            if coin.try_collect(player.rect, self.game):
                self.game.coins.remove(coin)

        # Health pickups
        for hp in self.game.health_pickups[:]:
            if hp.try_collect(player, self.game):
                self.game.health_pickups.remove(hp)

        # Life pickups
        for life in self.game.life_pickups[:]:
            if life.try_collect(player, self.game):
                self.game.life_pickups.remove(life)

        # Powerups
        for pup in self.game.powerups[:]:
            if pup.try_collect(player, self.game):
                self.game.powerups.remove(pup)

        # Ability Orbs (update animations and check collection)
        for orb in self.game.ability_orbs[:]:
            orb.update(dt)
            if orb.try_collect(player.rect, self.game):
                self.game.ability_orbs.remove(orb)

        # Hazards (still rect-based in current build)
        # Check if hazards are disabled
        hazards_disabled = modifiers and modifiers.disable_hazards
        if not hazards_disabled:
            for h in self.game.hazards:
                if player.rect.colliderect(h):
                    # Import combat system for knockback
                    from core.combat_system import calculate_knockback

                    # Take damage
                    damage_dealt = player.take_damage(1)

                    if damage_dealt:
                        # Apply knockback from hazard
                        hazard_center = (h.centerx, h.centery)
                        player_center = (player.rect.centerx, player.rect.centery)
                        kb_vx, kb_vy = calculate_knockback(
                            hazard_center,
                            player_center,
                            180  # Reduced knockback force for gentle arc (was 250)
                        )
                        player.vx = kb_vx
                        player.vy = kb_vy

                        if player.health <= 0:
                            self.game.lives -= 1
                            if self.game.lives <= 0:
                                self.game.on_game_over()
                            else:
                                self.game.restart_level()
                            return

        # Exit gate
        gate = self.game.exit_gate
        if gate and gate.can_finish(player.rect):
            self.game.on_level_clear()

    def draw(self, surface: pygame.Surface) -> None:
        self.game.draw_world_and_player()

        # Draw debug overlay if available
        if hasattr(self.game, 'debug_overlay') and self.game.player:
            modifiers = getattr(self.game, 'modifiers', None)
            seed = getattr(self.game, 'seed', None)
            self.game.debug_overlay.render(surface, self.game.player, modifiers, seed)

        # Draw notifications
        self._draw_notifications(surface)

        # Draw controls overlay if enabled
        if self.show_controls_overlay:
            self._draw_controls_overlay(surface)

    def _draw_notifications(self, surface: pygame.Surface) -> None:
        """Draw collection and unlock notifications."""
        from settings import LOGICAL_W, LOGICAL_H, FONT_BIG, FONT

        y_offset = 200  # Below the HUD

        # Draw ability orb collection notification
        if self.notification_timer > 0:
            # Fade in/out effect
            alpha = min(255, int(255 * min(self.notification_timer, 1.0)))
            color = (200, 150, 255, alpha)  # Purple like orbs

            text = FONT_BIG.render(self.notification_text, True, color[:3])
            text_rect = text.get_rect(center=(LOGICAL_W // 2, y_offset))

            # Draw background for better visibility
            bg_rect = text_rect.inflate(40, 20)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, min(180, alpha)))
            surface.blit(bg_surface, bg_rect.topleft)

            # Draw text
            surface.blit(text, text_rect)

        # Draw ability unlock notification (below orb notification)
        if self.unlock_notification_timer > 0:
            y_offset += 80

            # Fade in/out effect
            alpha = min(255, int(255 * min(self.unlock_notification_timer, 1.0)))
            color = (255, 220, 100, alpha)  # Gold for unlocks

            text = FONT_BIG.render(self.unlock_notification_text, True, color[:3])
            text_rect = text.get_rect(center=(LOGICAL_W // 2, y_offset))

            # Draw background for better visibility
            bg_rect = text_rect.inflate(40, 20)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, min(180, alpha)))
            surface.blit(bg_surface, bg_rect.topleft)

            # Draw text
            surface.blit(text, text_rect)

            # Draw smaller subtitle
            subtitle = FONT.render("Check your abilities!", True, (220, 220, 220))
            subtitle_rect = subtitle.get_rect(center=(LOGICAL_W // 2, y_offset + 35))
            surface.blit(subtitle, subtitle_rect)

    def _draw_controls_overlay(self, surface: pygame.Surface) -> None:
        """Draw quick controls reference overlay (F1)."""
        from settings import LOGICAL_W, LOGICAL_H, FONT, FONT_SMALL, FONT_BIG

        # Semi-transparent background
        overlay = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Control panel dimensions
        panel_w = 600
        panel_h = 500
        panel_x = (LOGICAL_W - panel_w) // 2
        panel_y = (LOGICAL_H - panel_h) // 2

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(surface, (25, 25, 40), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (100, 120, 180), panel_rect, 3, border_radius=12)

        # Title
        title = FONT_BIG.render("CONTROLS", True, (200, 220, 255))
        title_rect = title.get_rect(center=(LOGICAL_W // 2, panel_y + 30))
        surface.blit(title, title_rect)

        # Get controls manager for dynamic key display
        from controls import get_controls_manager
        controls = get_controls_manager()

        # Define control groups
        control_groups = [
            ("MOVEMENT", [
                ("Jump", "movement.jump"),
                ("Move Left/Right", "movement.move_left"),
                ("Crouch/Slide", "movement.crouch_down"),
            ]),
            ("ABILITIES", [
                ("Dash", "abilities.dash"),
                ("Wall Jump", "abilities.wall_jump"),
                ("Double Jump", "abilities.double_jump"),
                ("Air Dodge", "abilities.air_dodge"),
            ]),
            ("GAME", [
                ("Pause", "ui.pause"),
                ("Quick Controls", "Press F1"),
                ("Debug", "Press F3"),
            ])
        ]

        # Draw controls
        y_offset = panel_y + 70
        x_left = panel_x + 30
        x_right = panel_x + panel_w - 180

        for group_name, controls_list in control_groups:
            # Group header
            group_header = FONT.render(group_name, True, (150, 200, 255))
            surface.blit(group_header, (x_left, y_offset))
            y_offset += 28

            # Draw each control
            for action_name, action_id in controls_list:
                # Action name
                action_text = FONT_SMALL.render(action_name, True, (200, 200, 220))
                surface.blit(action_text, (x_left + 10, y_offset))

                # Key binding
                if action_id.startswith("Press "):
                    # Special case for non-action keys
                    key_text = action_id.replace("Press ", "")
                else:
                    key_text = controls.get_action_keys_display(action_id)

                key_surf = FONT_SMALL.render(key_text, True, (255, 230, 120))
                surface.blit(key_surf, (x_right, y_offset))

                y_offset += 24

            y_offset += 12  # Extra space between groups

        # Footer hint
        hint = FONT_SMALL.render("Press F1 again to close", True, (180, 180, 200))
        hint_rect = hint.get_rect(center=(LOGICAL_W // 2, panel_y + panel_h - 25))
        surface.blit(hint, hint_rect)
