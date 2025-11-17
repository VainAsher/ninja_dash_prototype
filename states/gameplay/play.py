
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

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("pause")
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
