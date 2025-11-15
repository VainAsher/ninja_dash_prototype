
# core/game.py - central Game object and shared rendering with entities
from __future__ import annotations

import math
from typing import Any, List, Dict

import pygame

from settings import (
    LOGICAL_W,
    LOGICAL_H,
    HUD_HEIGHT,
    FPS,
    COLOR_BG,
    COLOR_HUD_BG,
    COLOR_TILE,
    COLOR_PHASEABLE_WALL,
    COLOR_HAZARD,
    COLOR_COIN,
    COLOR_HEALTH,
    COLOR_LIFE,
    COLOR_EXIT,
    COLOR_EXIT_LOCKED,
    COLOR_TEXT,
    COLOR_PLAYER,
    COLOR_SHADOW_STEP,
    FONT,
    FONT_SMALL,
    FONT_BIG,
    FEATURES,
    DEBUG_DEFAULT,
    DIFFICULTY,
    DIFFICULTY_CONFIG,
    PLAYER_LIVES,
    DEFAULT_SEED,
    WINDOW_FLAGS,
    VSYNC,
)

from level_gen import generate_level
from player import Player
from camera import get_camera_rect
from highscores import get_highscores, add_highscore, qualifies_for_highscore
from unlocks import get_unlock_manager, get_enabled_abilities, ABILITY_INFO, ABILITY_ORDER
from user_settings import get_user_settings

from entities.exit_gate import ExitGate
from entities.collectibles import Coin, HealthPickup, LifePickup, Powerup
from entities.ability_orb import AbilityOrb
from entities.player_entity import PlayerController

from states.base import GameState
from states.menu import MenuState
from states.play import PlayState
from states.pause import PauseState
from states.gameover import GameOverState
from states.highscores import HighscoresState
from states.unlocks import UnlocksState
from states.settings_state import SettingsState
from states.help_state import HelpState
from states.name_entry import NameEntryState
from states.seed_entry import SeedEntryState
from states.controls_viewer import ControlsViewerState


def create_window() -> pygame.Surface:
    pygame.display.set_caption("Ninja Dash - Refactored Prototype")
    return pygame.display.set_mode((LOGICAL_W, LOGICAL_H), WINDOW_FLAGS, vsync=VSYNC)


def blit_letterboxed(src: pygame.Surface, dst: pygame.Surface) -> None:
    """Scale src to fit dst while preserving aspect ratio and letterboxing."""
    sw, sh = src.get_size()
    dw, dh = dst.get_size()
    scale = min(dw / sw, dh / sh)
    tw, th = int(sw * scale), int(sh * scale)
    temp = pygame.transform.smoothscale(src, (tw, th))
    x = (dw - tw) // 2
    y = (dh - th) // 2
    dst.fill((0, 0, 0))
    dst.blit(temp, (x, y))


def draw_world(
    play_surf: pygame.Surface,
    tiles: List[pygame.Rect],
    phaseable_walls: List[pygame.Rect],
    exit_gate: ExitGate | None,
    coins: List[Coin],
    hazards: List[pygame.Rect],
    health_pickups: List[HealthPickup],
    life_pickups: List[LifePickup],
    powerups: List[Powerup],
    cam: pygame.Rect,
    debug: bool,
) -> None:
    """Draw game world with all entities."""        
    if not debug:
        play_surf.fill(COLOR_BG)

        # Tiles / phaseable walls
        for t in tiles:
            if cam.colliderect(t):
                color = COLOR_PHASEABLE_WALL if t in phaseable_walls else COLOR_TILE
                pygame.draw.rect(
                    play_surf,
                    color,
                    (t.x - cam.x, t.y - cam.y, t.w, t.h),
                )

        # Hazards
        for h in hazards:
            if cam.colliderect(h):
                pygame.draw.polygon(
                    play_surf,
                    COLOR_HAZARD,
                    [
                        (h.x - cam.x, h.bottom - cam.y),
                        (h.centerx - cam.x, h.top - cam.y),
                        (h.right - cam.x, h.bottom - cam.y),
                    ],
                )

        # Coins (from entities)
        for coin in coins:
            r = coin.rect
            if cam.colliderect(r):
                pygame.draw.circle(
                    play_surf,
                    COLOR_COIN,
                    (r.centerx - cam.x, r.centery - cam.y),
                    r.w // 2,
                )

        # Health pickups
        for hp in health_pickups:
            r = hp.rect
            if cam.colliderect(r):
                pygame.draw.rect(
                    play_surf,
                    COLOR_HEALTH,
                    (r.x - cam.x, r.y - cam.y, r.w, r.h),
                    border_radius=4,
                )

        # Life pickups
        for life in life_pickups:
            r = life.rect
            if cam.colliderect(r):
                pygame.draw.rect(
                    play_surf,
                    COLOR_LIFE,
                    (r.x - cam.x, r.y - cam.y, r.w, r.h),
                    border_radius=4,
                )

        # Power-ups
        for pup in powerups:
            r = pup.rect
            if cam.colliderect(r):
                cx = r.centerx - cam.x
                cy = r.centery - cam.y
                # Color by type, fallback to a neutral
                if pup.ptype == "speed":
                    color = (255, 200, 0)
                elif pup.ptype == "triple":
                    color = (0, 200, 255)
                elif pup.ptype == "magnet":
                    color = (255, 0, 200)
                else:
                    color = (200, 200, 255)
                points = [
                    (cx, cy - r.h // 2),
                    (cx + r.w // 2, cy),
                    (cx, cy + r.h // 2),
                    (cx - r.w // 2, cy),
                ]
                pygame.draw.polygon(play_surf, color, points)
                pygame.draw.polygon(play_surf, (255, 255, 255), points, 2)

        # Exit gate
        if exit_gate and exit_gate.rect and cam.colliderect(exit_gate.rect):
            er = exit_gate.rect
            color = COLOR_EXIT if exit_gate.unlocked else COLOR_EXIT_LOCKED
            pygame.draw.rect(
                play_surf,
                color,
                (er.x - cam.x, er.y - cam.y, er.w, er.h),
                border_radius=6,
            )


def draw_hud(
    hud_surf: pygame.Surface,
    score: int,
    lives: int,
    health: int,
    level_index: int,
    difficulty: str,
    abilities: List[str],
    game_time: float,
    unlock_mgr: Any = None,
) -> None:
    """Draw HUD overlay."""
    hud_surf.fill(COLOR_HUD_BG)

    score_txt = FONT.render(f"Score: {score}", True, COLOR_TEXT)
    lives_txt = FONT.render(f"Lives: {lives}", True, COLOR_TEXT)
    hp_txt = FONT.render(f"HP: {health}", True, COLOR_TEXT)
    level_txt = FONT.render(f"Level: {level_index}", True, COLOR_TEXT)
    diff_txt = FONT_SMALL.render(f"Diff: {difficulty}", True, COLOR_TEXT)
    time_txt = FONT_SMALL.render(f"{game_time:6.1f}s", True, COLOR_TEXT)

    hud_surf.blit(score_txt, (16, 8))
    hud_surf.blit(lives_txt, (220, 8))
    hud_surf.blit(hp_txt, (400, 8))
    hud_surf.blit(level_txt, (580, 8))
    hud_surf.blit(diff_txt, (760, 12))
    hud_surf.blit(time_txt, (900, 12))

    # Ability Orbs counter
    if unlock_mgr:
        available_orbs = unlock_mgr.get_ability_orbs_available()
        total_orbs = unlock_mgr.get_ability_orbs_total()
        orb_color = (200, 150, 255)  # Purple/rainbow color for orbs

        # Draw orb icon (small circle)
        orb_icon_x = 1000
        orb_icon_y = 14
        pygame.draw.circle(hud_surf, orb_color, (orb_icon_x, orb_icon_y), 6)
        pygame.draw.circle(hud_surf, (255, 255, 255), (orb_icon_x - 2, orb_icon_y - 2), 2)

        # Draw orb count
        orb_txt = FONT_SMALL.render(f"{available_orbs}/{total_orbs}", True, orb_color)
        hud_surf.blit(orb_txt, (orb_icon_x + 10, orb_icon_y - 8))

    # Ability chips
    x = 1100
    y = 12
    for aid in abilities:
        info = ABILITY_INFO.get(aid, {"short": aid[:3], "color": (200, 200, 200)})
        label = info.get("short", aid[:3])
        color = info.get("color", (200, 200, 200))
        chip = FONT_SMALL.render(label, True, (0, 0, 0))
        rect = chip.get_rect()
        rect.inflate_ip(12, 8)
        rect.topleft = (x, y)
        pygame.draw.rect(hud_surf, color, rect, border_radius=8)
        hud_surf.blit(chip, (rect.x + 6, rect.y + 2))
        x += rect.w + 8


class Game:
    """Central game object managing state, world, and meta systems."""        

    def __init__(self) -> None:
        self.window = create_window()
        self.logical = pygame.Surface((LOGICAL_W, LOGICAL_H))
        self.play_area = pygame.Surface((LOGICAL_W, LOGICAL_H - HUD_HEIGHT))
        self.hud_area = pygame.Surface((LOGICAL_W, HUD_HEIGHT))

        # Run control
        self.running: bool = True

        # Meta / config
        self.debug: bool = DEBUG_DEFAULT
        self.difficulty: str = DIFFICULTY
        self.seed: Any = DEFAULT_SEED

        self.level_index: int = 1
        self.total_score: int = 0
        self.lives: int = PLAYER_LIVES
        self.game_time: float = 0.0
        self.pending_score: int | None = None
        self.pending_level: int | None = None
        self.pending_difficulty: str | None = None


        # World / entities
        self.world: Any = None
        self.tiles: List[pygame.Rect] = []
        self.phaseable_walls: List[pygame.Rect] = []
        self.hazards: List[pygame.Rect] = []

        self.coins: List[Coin] = []
        self.health_pickups: List[HealthPickup] = []
        self.life_pickups: List[LifePickup] = []
        self.powerups: List[Powerup] = []
        self.ability_orbs: List[AbilityOrb] = []
        self.exit_gate: ExitGate | None = None

        self.player: Player | None = None
        self.abilities: list[str] = []
        self.player_controller: PlayerController | None = None

        # UI notifications
        self.ability_orb_collected = False
        self.ability_unlocked = None  # Set to ability name when unlocked



        # Meta systems
        self.user_settings = get_user_settings()
        self.unlock_mgr = get_unlock_manager()
        self._sync_features_with_unlocks()

        # State machine
        self.states: Dict[str, GameState] = {}
        self.current_state: GameState | None = None
        self._register_states()
        self.change_state("menu")

        # Build initial level so world-based states can draw
        self.build_level()

    # ---------------- State machine ----------------

    def _register_states(self) -> None:
        self.states = {
            "menu": MenuState(self),
            "play": PlayState(self),
            "pause": PauseState(self),
            "gameover": GameOverState(self),
            "highscores": HighscoresState(self),
            "unlocks": UnlocksState(self),
            "settings": SettingsState(self),
            "help": HelpState(self),
            "name_entry": NameEntryState(self),
            "seed_entry": SeedEntryState(self),
            "controls": ControlsViewerState(self),
        }

    def change_state(self, name: str) -> None:
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states[name]
        self.current_state.enter()

    # ---------------- Core operations ----------------

    def quit(self) -> None:
        self.running = False

    def _sync_features_with_unlocks(self) -> None:
        FEATURES["double_jump"] = self.unlock_mgr.is_enabled("DOUBLE_JUMP")
        FEATURES["dash"] = self.unlock_mgr.is_enabled("DASH")
        FEATURES["wall_jump"] = self.unlock_mgr.is_enabled("WALL_JUMP")

    def build_level(self) -> None:
        cfg = DIFFICULTY_CONFIG[self.difficulty].copy()
        cfg.update(self.user_settings.get_generation_overrides())

        self.abilities = get_enabled_abilities()

        (
            world,
            tiles,
            exit_rect,
            spawn,
            coin_rects,
            hazards,
            health_rects,
            life_rects,
            powerup_defs,
            phaseable_walls,
            ability_orb_rects,
        ) = generate_level(
            seed=self.seed,
            diff_cfg=cfg,
            abilities=self.abilities,
        )

        self.world = world
        self.tiles = tiles
        self.phaseable_walls = phaseable_walls
        self.hazards = hazards

        # Collectibles as entities
        self.coins = []
        cfg_for_diff = DIFFICULTY_CONFIG[self.difficulty]
        base_multiplier = cfg_for_diff.get("multiplier", 1.0)
        base_coin_value = int(10 * base_multiplier)  # keep consistent with old behaviour

        for r in coin_rects:
            self.coins.append(Coin(r, base_coin_value))

        self.health_pickups = [HealthPickup(r, 1) for r in health_rects]
        self.life_pickups = [LifePickup(r, 1) for r in life_rects]

        self.powerups = []
        for p in powerup_defs:
            rect = p.get("rect")
            ptype = p.get("type", "speed")
            if rect is not None:
                self.powerups.append(Powerup(rect, ptype))

        # Ability Orbs (rare collectibles for unlocking abilities)
        self.ability_orbs = [AbilityOrb(r) for r in ability_orb_rects]

        # Exit gate entity (coin-gated)
        coin_total = len(self.coins)
        coin_ratio = cfg_for_diff.get("coin_ratio", 0.0)
        required_coins = max(0, math.ceil(coin_total * coin_ratio))
        self.exit_gate = ExitGate(exit_rect, coin_total, required_coins)

        # Player spawn
        sx, sy = spawn
        self.player = Player(sx, sy)
        self.player_controller = PlayerController(self.player)

        # Reset run timer for this level
        self.game_time = 0.0

    def start_new_run(self) -> None:
        self.level_index = 1
        self.total_score = 0
        self.lives = PLAYER_LIVES
        self.game_time = 0.0
        self.build_level()
        self.change_state("play")

    def restart_level(self) -> None:
        self.build_level()
        self.change_state("play")

    def next_level(self) -> None:
        self.level_index += 1
        unlocked_id = self.unlock_mgr.unlock_next()
        if unlocked_id:
            self._sync_features_with_unlocks()
        self.build_level()
        self.change_state("play")

    def on_level_clear(self) -> None:
        cfg = DIFFICULTY_CONFIG[self.difficulty]
        clear_bonus = int(1000 * cfg.get("multiplier", 1.0))
        self.total_score += clear_bonus
        self.next_level()

    def on_game_over(self) -> None:
        if qualifies_for_highscore(self.total_score):
            add_highscore("Player", self.total_score, self.level_index, self.difficulty)
        self.change_state("gameover")

    def on_game_over(self) -> None:
        if qualifies_for_highscore(self.total_score):
            self.pending_score = self.total_score
            self.pending_level = self.level_index
            self.pending_difficulty = self.difficulty
            self.change_state("name_entry")
        else:
            self.change_state("gameover")        

    # ---------------- Top-level loop hooks ----------------

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.QUIT:
            self.quit()
            return
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current_state:
            self.current_state.update(dt)

    def draw(self) -> None:
        self.logical.fill((20, 20, 40))
        if self.current_state:
            self.current_state.draw(self.logical)
        blit_letterboxed(self.logical, self.window)
        pygame.display.flip()

    # ---------------- Helpers for world-based states ----------------

    def draw_world_and_player(self) -> None:
        if not self.player:
            return

        cam = get_camera_rect(self.player.rect)
        draw_world(
            self.play_area,
            self.tiles,
            self.phaseable_walls,
            self.exit_gate,
            self.coins,
            self.hazards,
            self.health_pickups,
            self.life_pickups,
            self.powerups,
            cam,
            self.debug,
        )

        # Render Ability Orbs (with animations)
        for orb in self.ability_orbs:
            orb.draw(self.play_area, cam)

        # Player with proper colours
        player_color = COLOR_PLAYER
        if getattr(self.player, "is_shadow_stepping", False):
            player_color = COLOR_SHADOW_STEP
        elif getattr(self.player, "shadow_step_invuln", 0.0) > 0.0:
            if int(self.player.shadow_step_invuln * 10) % 2 == 0:
                player_color = COLOR_SHADOW_STEP

        pygame.draw.rect(
            self.play_area,
            player_color,
            self.player.rect.move(-cam.x, -cam.y),
            border_radius=4,
        )

        draw_hud(
            self.hud_area,
            self.total_score,
            self.lives,
            self.player.health,
            self.level_index,
            self.difficulty,
            self.abilities,
            self.game_time,
            self.unlock_mgr,
        )

        self.logical.blit(self.play_area, (0, 0))
        self.logical.blit(self.hud_area, (0, LOGICAL_H - HUD_HEIGHT))
