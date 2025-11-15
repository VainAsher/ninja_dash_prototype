
# states/play.py - core gameplay loop using entity-based collectibles

from __future__ import annotations

import pygame

from settings import DIFFICULTY_CONFIG
from .base import GameState


class PlayState(GameState):
    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("pause")

    def update(self, dt: float) -> None:
        player = self.game.player
        if not player:
            return

        # Advance run timer
        self.game.game_time += dt

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
            )
            # Coin magnet logic still uses the underlying coin rects via entities
            player.apply_magnet_to_coins([c.rect for c in self.game.coins], dt)

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

        # Hazards (still rect-based in current build)
        for h in self.game.hazards:
            if player.rect.colliderect(h):
                if player.take_damage(1):
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
