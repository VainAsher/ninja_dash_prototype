"""
Enemy Manager - Manages all enemies in the level

Provides:
- Enemy spawning and tracking
- Bulk enemy updates
- Enemy removal and cleanup
- Integration with combat system
"""

from __future__ import annotations

from typing import List, Any, Optional, Type
import pygame

from .enemy import Enemy


class EnemyManager:
    """
    Manages all active enemies in the current level.

    Handles spawning, updating, rendering, and cleanup of enemies.
    """

    def __init__(self):
        """Initialize empty enemy manager."""
        self.enemies: List[Enemy] = []

    def spawn_enemy(
        self,
        enemy_type: Type[Enemy],
        x: float,
        y: float,
        **kwargs
    ) -> Enemy:
        """
        Spawn a new enemy and add to managed list.

        Args:
            enemy_type: Enemy class to instantiate
            x: X position
            y: Y position
            **kwargs: Additional arguments for enemy constructor

        Returns:
            Enemy: The spawned enemy instance
        """
        enemy = enemy_type(x, y, **kwargs)
        self.enemies.append(enemy)
        return enemy

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add an existing enemy to the manager.

        Args:
            enemy: Enemy instance to add
        """
        if enemy not in self.enemies:
            self.enemies.append(enemy)

    def update(self, dt: float, world: Any, player: Any, game: Any = None) -> None:
        """
        Update all active enemies.

        Args:
            dt: Delta time since last frame
            world: Level tile data
            player: Player entity
            game: Game instance (for damage numbers, scoring, etc.)
        """
        # Update all enemies
        for enemy in self.enemies:
            enemy.update(dt, world, player, game)

        # Check for enemies being attacked by player
        if player and game:
            self._check_player_attacks(player, game)

    def _check_player_attacks(self, player: Any, game: Any) -> None:
        """
        Check if player is attacking any enemies.

        Args:
            player: Player entity
            game: Game instance
        """
        # Check if player has an active attack hitbox
        if not hasattr(player, 'get_attack_hitbox'):
            return

        attack_hitbox = player.get_attack_hitbox()
        if not attack_hitbox:
            return

        # Import combat system
        from core.combat_system import deal_damage

        # Check each enemy
        for enemy in self.enemies:
            if enemy.is_dead:
                continue

            # Check collision with attack
            if attack_hitbox.colliderect(enemy.rect):
                # Check if this enemy was already hit this attack
                # (player's sword attack should track this)
                if hasattr(player, 'abilities') and 'SWORD_ATTACK' in player.abilities:
                    sword = player.abilities['SWORD_ATTACK']
                    if hasattr(sword, 'hit_enemies'):
                        enemy_id = id(enemy)
                        if enemy_id in sword.hit_enemies:
                            continue
                        sword.hit_enemies.add(enemy_id)

                # Deal damage
                damage_amount = 1  # Base sword damage

                # Get damage numbers manager if available
                damage_numbers = getattr(game, 'damage_numbers', None)

                # Deal damage with knockback
                deal_damage(
                    player,
                    enemy,
                    damage_amount,
                    knockback_force=300,
                    damage_numbers=damage_numbers
                )

                # Award points if enemy died
                if enemy.is_dead:
                    game.total_score += enemy.points

                    # Spawn loot
                    self._spawn_loot(enemy, game)

    def _spawn_loot(self, enemy: Enemy, game: Any) -> None:
        """
        Spawn loot drops from a dead enemy.

        Args:
            enemy: Dead enemy entity
            game: Game instance
        """
        if not enemy.loot_table:
            return

        import random

        # Get loot configuration
        coins = enemy.loot_table.get('coins', None)
        health_chance = enemy.loot_table.get('health', 0.0)
        powerup_chance = enemy.loot_table.get('powerup', 0.0)
        orb_chance = enemy.loot_table.get('ability_orb', 0.0)

        # Spawn coins
        if coins:
            if isinstance(coins, tuple) and len(coins) == 2:
                # Range (min, max)
                num_coins = random.randint(coins[0], coins[1])
            else:
                # Fixed amount
                num_coins = coins

            # Create coin drops
            from entities.collectibles import Coin
            for i in range(num_coins):
                # Scatter coins around enemy position
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-20, 20)
                coin_rect = pygame.Rect(
                    enemy.rect.centerx + offset_x - 8,
                    enemy.rect.centery + offset_y - 8,
                    16,
                    16
                )
                coin = Coin(coin_rect, value=10)
                game.coins.append(coin)

        # Spawn health pickup
        if random.random() < health_chance:
            from entities.collectibles import HealthPickup
            health_rect = pygame.Rect(
                enemy.rect.centerx - 12,
                enemy.rect.centery - 12,
                24,
                24
            )
            health_pickup = HealthPickup(health_rect, amount=1)
            game.health_pickups.append(health_pickup)

        # Spawn powerup
        if random.random() < powerup_chance:
            from entities.collectibles import Powerup
            powerup_types = ['speed', 'triple', 'magnet']
            ptype = random.choice(powerup_types)
            powerup_rect = pygame.Rect(
                enemy.rect.centerx - 12,
                enemy.rect.centery - 12,
                24,
                24
            )
            powerup = Powerup(powerup_rect, ptype)
            game.powerups.append(powerup)

        # Spawn ability orb
        if random.random() < orb_chance:
            from entities.ability_orb import AbilityOrb
            orb_rect = pygame.Rect(
                enemy.rect.centerx - 12,
                enemy.rect.centery - 12,
                24,
                24
            )
            orb = AbilityOrb(orb_rect)
            game.ability_orbs.append(orb)

    def remove_dead(self) -> int:
        """
        Remove dead enemies that have finished their death animation.

        Returns:
            int: Number of enemies removed
        """
        initial_count = len(self.enemies)
        self.enemies = [
            enemy for enemy in self.enemies
            if not enemy.can_be_removed()
        ]
        return initial_count - len(self.enemies)

    def draw(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)) -> None:
        """
        Draw all enemies.

        Args:
            screen: Pygame surface to draw on
            camera_offset: (x, y) camera offset for world space
        """
        for enemy in self.enemies:
            enemy.draw(screen, camera_offset)

    def clear(self) -> None:
        """Clear all enemies."""
        self.enemies.clear()

    def get_enemy_count(self) -> int:
        """
        Get count of active (non-dead) enemies.

        Returns:
            int: Number of active enemies
        """
        return sum(1 for enemy in self.enemies if not enemy.is_dead)

    def get_all_enemies(self) -> List[Enemy]:
        """
        Get list of all enemies.

        Returns:
            List[Enemy]: All enemies (including dead ones)
        """
        return self.enemies.copy()

    def get_active_enemies(self) -> List[Enemy]:
        """
        Get list of active (non-dead) enemies.

        Returns:
            List[Enemy]: Active enemies only
        """
        return [enemy for enemy in self.enemies if not enemy.is_dead]

    def get_enemies_in_range(
        self,
        pos: tuple,
        radius: float
    ) -> List[Enemy]:
        """
        Get enemies within a certain range of a position.

        Args:
            pos: (x, y) center position
            radius: Search radius

        Returns:
            List[Enemy]: Enemies within range
        """
        import math
        nearby = []

        for enemy in self.enemies:
            if enemy.is_dead:
                continue

            # Calculate distance
            dx = enemy.rect.centerx - pos[0]
            dy = enemy.rect.centery - pos[1]
            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= radius:
                nearby.append(enemy)

        return nearby
