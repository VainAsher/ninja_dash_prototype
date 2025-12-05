
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
from level_gen.config import ACT_GEOMETRY
from core.campaign import get_base_abilities_for_act
from player import Player
from camera import get_camera_rect
from highscores import get_highscores, add_highscore, qualifies_for_highscore
from unlocks import get_unlock_manager, get_enabled_abilities, ABILITY_INFO, ABILITY_ORDER
from user_settings import get_user_settings

from entities.exit_gate import ExitGate
from entities.collectibles import Coin, HealthPickup, LifePickup, Powerup
from entities.ability_orb import AbilityOrb
from entities.enemy_manager import EnemyManager
from core.combat_system import DamageNumberManager
from entities.player_entity import PlayerController

from core.campaign import CampaignState

from states.base import GameState
from states.gameplay.play import PlayState
from states.gameplay.pause import PauseState
from states.gameplay.gameover import GameOverState
from states.menus.menu import MenuState
from states.menus.options_state import OptionsState
from states.menus.debug_menu import DebugMenuState
from states.menus.help_state import HelpState
from states.menus.controls_viewer import ControlsViewerState
from states.meta.highscores import HighscoresState
from states.meta.unlocks import UnlocksState
from states.meta.name_entry import NameEntryState
from states.meta.seed_entry import SeedEntryState
from states.campaign import LanternHub, HollowHub, EmberHub, SkyHub

from ui.hud_components import (
    ScoreSection,
    VitalsSection,
    LevelInfoSection,
    TimeAbilitiesSection,
    AbilityProgressSection,
    PowerupIndicators,
    AbilityResourceBars,
    ExitGateIndicator
)
from ui.debug_overlay import DebugOverlay

from gameplay_modifiers import get_modifiers


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
    biome: str = "lantern",
) -> None:
    """Draw game world with all entities."""
    if not debug:
        # Biome-specific background colors
        bg_colors = {
            "lantern": (10, 10, 20),      # Dark blue-black (current default)
            "hollow": (5, 5, 15),          # Very dark purple-black
            "ember": (20, 10, 5),          # Dark reddish-brown
            "sky": (15, 25, 40),           # Dark blue-gray
        }
        play_surf.fill(bg_colors.get(biome, COLOR_BG))

        # Biome-specific tile colors
        tile_colors = {
            "lantern": (200, 180, 120),    # Warm golden stone
            "hollow": (40, 40, 70),        # Deep purple-gray
            "ember": (150, 80, 40),        # Burnt orange-brown
            "sky": (180, 220, 255),        # Light sky blue
        }
        ground_color = tile_colors.get(biome, COLOR_TILE)

        # Tiles / phaseable walls
        for t in tiles:
            if cam.colliderect(t):
                color = COLOR_PHASEABLE_WALL if t in phaseable_walls else ground_color
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

        # Exit gate (biome-aware colors)
        if exit_gate and exit_gate.rect and cam.colliderect(exit_gate.rect):
            er = exit_gate.rect

            # Biome-specific exit colors
            if exit_gate.unlocked:
                exit_colors = {
                    "lantern": (255, 220, 120),    # Golden
                    "hollow": (120, 0, 150),       # Purple
                    "ember": (255, 150, 80),       # Orange-red
                    "sky": (200, 255, 255),        # Cyan-white
                }
                color = exit_colors.get(biome, COLOR_EXIT)
            else:
                color = COLOR_EXIT_LOCKED

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
    player: Any = None,
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

    # Stamina bar for dash ability
    if player and hasattr(player, 'abilities') and 'dash' in player.abilities:
        dash_ability = player.abilities['dash']
        if hasattr(dash_ability, 'resource') and hasattr(dash_ability, 'max_resource'):
            stamina_ratio = dash_ability.resource / dash_ability.max_resource

            # Draw stamina bar below HP
            bar_x = 480
            bar_y = 12
            bar_width = 60
            bar_height = 8

            # Background (empty bar)
            pygame.draw.rect(hud_surf, (40, 40, 60), (bar_x, bar_y, bar_width, bar_height))

            # Filled portion (stamina)
            filled_width = int(bar_width * stamina_ratio)
            if filled_width > 0:
                # Color changes based on stamina level
                if stamina_ratio > 0.5:
                    stamina_color = (100, 200, 255)  # Cyan when full
                elif stamina_ratio > 0.25:
                    stamina_color = (255, 200, 100)  # Orange when medium
                else:
                    stamina_color = (255, 100, 100)  # Red when low

                pygame.draw.rect(hud_surf, stamina_color, (bar_x, bar_y, filled_width, bar_height))

            # Border
            pygame.draw.rect(hud_surf, (120, 120, 140), (bar_x, bar_y, bar_width, bar_height), 1)

            # Label
            stamina_label = FONT_SMALL.render("STAM", True, (180, 180, 200))
            hud_surf.blit(stamina_label, (bar_x - 38, bar_y - 2))

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


def draw_hud_new(
    hud_surf: pygame.Surface,
    score: int,
    lives: int,
    health: int,
    level_index: int,
    difficulty: str,
    abilities: List[str],
    game_time: float,
    exit_gate: Any = None,
    player: Any = None,
    unlock_mgr: Any = None,
) -> None:
    """Draw enhanced modular HUD with ability progress."""
    # Darker background for better contrast
    hud_surf.fill((15, 15, 25))

    # Calculate section dimensions with more spacing
    section_height = HUD_HEIGHT - 16
    section_gap = 8
    available_width = hud_surf.get_width() - (6 * section_gap)

    # Section widths (adjusted for 5 sections)
    score_w = int(available_width * 0.20)
    vitals_w = int(available_width * 0.19)
    level_w = int(available_width * 0.15)
    time_w = int(available_width * 0.26)
    progress_w = int(available_width * 0.20)

    # Create sections with spacing from top
    x = section_gap
    y_offset = 8
    sections = []

    # Score & Progress
    sections.append(ScoreSection(x, y_offset, score_w, section_height))
    x += score_w + section_gap

    # Player Vitals
    sections.append(VitalsSection(x, y_offset, vitals_w, section_height))
    x += vitals_w + section_gap

    # Level Info
    sections.append(LevelInfoSection(x, y_offset, level_w, section_height))
    x += level_w + section_gap

    # Time & Abilities
    sections.append(TimeAbilitiesSection(x, y_offset, time_w, section_height))
    x += time_w + section_gap

    # Ability Progress
    sections.append(AbilityProgressSection(x, y_offset, progress_w, section_height))

    # Prepare game data
    coins_collected = exit_gate.coins_collected if exit_gate else 0
    coins_required = exit_gate.required_coins if exit_gate else 0

    game_data = {
        'score': score,
        'coins_collected': coins_collected,
        'coins_required': coins_required,
        'health': health,
        'lives': lives,
        'level': level_index,
        'difficulty': difficulty,
        'time': game_time,
        'abilities': abilities,
        'unlock_mgr': unlock_mgr,
        'player': player,
    }

    # Draw all sections
    for section in sections:
        section.draw(hud_surf, game_data)


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

        # Campaign mode
        self.campaign_mode: bool = False
        self.campaign_state: CampaignState = CampaignState()
        self.current_biome: str = "lantern"  # Current biome for rendering

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

        # Combat system
        self.damage_numbers = DamageNumberManager()
        self.enemy_manager = EnemyManager()

        # Meta systems
        self.user_settings = get_user_settings()
        self.unlock_mgr = get_unlock_manager()
        self._sync_features_with_unlocks()

        # Gameplay modifiers and debug overlay
        self.modifiers = get_modifiers()
        self.debug_overlay = DebugOverlay()

        # State machine
        self.states: Dict[str, GameState] = {}
        self.current_state: GameState | None = None
        self.previous_state_name: str | None = None
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
            "options": OptionsState(self),
            "debug": DebugMenuState(self),
            "help": HelpState(self),
            "name_entry": NameEntryState(self),
            "seed_entry": SeedEntryState(self),
            "controls": ControlsViewerState(self),
            # Campaign hubs
            "lantern_hub": LanternHub(self),
            "hollow_hub": HollowHub(self),
            "ember_hub": EmberHub(self),
            "sky_hub": SkyHub(self),
        }

    def change_state(self, name: str) -> None:
        # Track previous state for navigation
        if self.current_state:
            # Get the current state name by finding it in the states dict
            for state_name, state_obj in self.states.items():
                if state_obj == self.current_state:
                    self.previous_state_name = state_name
                    break
            self.current_state.exit()
        self.current_state = self.states[name]
        self.current_state.enter()

    # ---------------- Core operations ----------------

    def quit(self) -> None:
        # Save game state before quitting (unless already game over)
        if self.lives > 0:
            self.unlock_mgr.save_game_state(
                self.level_index,
                self.lives,
                self.total_score,
                self.game_time
            )
        self.running = False

    def _sync_features_with_unlocks(self) -> None:
        FEATURES["double_jump"] = self.unlock_mgr.is_enabled("DOUBLE_JUMP")
        FEATURES["dash"] = self.unlock_mgr.is_enabled("DASH")
        FEATURES["wall_jump"] = self.unlock_mgr.is_enabled("WALL_JUMP")

    def build_level(self) -> None:
        # Generate actual seed if not set (for display in debug overlay)
        if self.seed is None:
            import time
            self.seed = int(time.time() * 1000) % 1000000  # Use timestamp-based seed

        # Determine configuration based on mode
        if self.campaign_mode:
            # Campaign mode: use act-specific config
            config_key = (self.campaign_state.act, self.campaign_state.mission_index)
            config = ACT_GEOMETRY.get(
                config_key,
                ACT_GEOMETRY.get((self.campaign_state.act, 0))  # Fallback to first mission of act
            )

            # Get abilities from campaign state
            base_abilities = get_base_abilities_for_act(self.campaign_state)
            self.abilities = list(base_abilities | self.campaign_state.abilities_unlocked)

            # Set current biome
            self.current_biome = config.biome

            # Generate level with campaign config
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
                enemy_positions,
            ) = generate_level(
                seed=self.seed,
                config=config,
                abilities=self.abilities,
            )

            # Get multiplier from campaign config
            base_multiplier = config.multiplier
        else:
            # Arcade mode: use difficulty config
            cfg = DIFFICULTY_CONFIG[self.difficulty].copy()
            cfg.update(self.user_settings.get_generation_overrides())

            self.abilities = get_enabled_abilities()
            self.current_biome = "lantern"  # Default biome for arcade

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
                enemy_positions,
            ) = generate_level(
                seed=self.seed,
                diff_cfg=cfg,
                abilities=self.abilities,
            )

            # Get multiplier from difficulty config
            cfg_for_diff = DIFFICULTY_CONFIG[self.difficulty]
            base_multiplier = cfg_for_diff.get("multiplier", 1.0)

        self.world = world
        self.tiles = tiles
        self.phaseable_walls = phaseable_walls
        self.hazards = hazards

        # Collectibles as entities
        self.coins = []
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

        # Clear enemies for new level
        self.enemy_manager.clear()

        # Spawn enemies at generated positions
        from entities.patroller import Patroller
        for ex, ey in enemy_positions:
            self.enemy_manager.spawn_enemy(Patroller, ex, ey)

        # Exit gate entity (coin-gated)
        coin_total = len(self.coins)
        if self.campaign_mode:
            coin_ratio = config.coin_ratio
        else:
            coin_ratio = DIFFICULTY_CONFIG[self.difficulty].get("coin_ratio", 0.0)
        required_coins = max(0, math.ceil(coin_total * coin_ratio))
        self.exit_gate = ExitGate(exit_rect, coin_total, required_coins)

        # Player spawn
        sx, sy = spawn
        self.player = Player(sx, sy)
        self.player_controller = PlayerController(self.player)

        # Reset run timer for this level
        self.game_time = 0.0

    def start_new_run(self) -> None:
        """Start a completely new run (legacy method - use start_new_game() or continue_game())."""
        self.level_index = 1
        self.total_score = 0
        self.lives = PLAYER_LIVES
        self.game_time = 0.0
        self.build_level()
        self.change_state("play")

    def start_new_game(self) -> None:
        """Start a new game from scratch (deletes save)."""
        # Delete save file and reset unlock manager
        self.unlock_mgr.delete_save()
        self.unlock_mgr.reset_to_defaults()
        self._sync_features_with_unlocks()

        # Reset game state
        self.level_index = 1
        self.total_score = 0
        self.lives = PLAYER_LIVES
        self.game_time = 0.0
        self.seed = None

        # Start playing
        self.build_level()
        self.change_state("play")
        print("🆕 New Game started!")

    def continue_game(self) -> None:
        """Continue from last save."""
        if not self.unlock_mgr.has_save():
            print("⚠️  No save file found, starting new game")
            self.start_new_game()
            return

        # Load saved game state
        saved_state = self.unlock_mgr.load_game_state()
        self._sync_features_with_unlocks()

        self.level_index = saved_state["level_index"]
        self.lives = saved_state["lives"]
        self.total_score = saved_state["total_score"]
        self.game_time = saved_state["game_time"]
        self.seed = None  # Will generate new level seed

        # Build level and start playing
        self.build_level()
        self.change_state("play")
        print(f"📂 Game loaded: Level {self.level_index}, {self.lives} lives, {self.total_score} score")

    def start_campaign(self) -> None:
        """Start a new campaign playthrough (Hollowed Ninja story mode)."""
        # Enable campaign mode
        self.campaign_mode = True
        self.campaign_state = CampaignState()

        # Reset game state
        self.level_index = 1
        self.total_score = 0
        self.lives = PLAYER_LIVES
        self.game_time = 0.0
        self.seed = None

        # Start in Lantern Hub (Act 0)
        self.campaign_state.act = 0
        self.campaign_state.mission_index = 0

        # Go to Lantern Hub instead of directly to play
        self.change_state("lantern_hub")
        print("🎮 Campaign started: Lantern Heights Hub")

    def set_campaign_act(self, act: int, mission: int = 0) -> None:
        """
        DEBUG: Set campaign to specific act/mission for testing.

        Args:
            act: Act number (0-4)
            mission: Mission index (default: 0)
        """
        if not self.campaign_mode:
            print("⚠️  Campaign mode not active. Use start_campaign() first.")
            return

        self.campaign_state.act = act
        self.campaign_state.mission_index = mission

        # Reset seed for variety
        self.seed = None

        # Rebuild level with new act config
        self.build_level()

        act_names = {
            0: "Lantern Heights",
            1: "Veil Maiden Arena",
            2: "Hollow Depths",
            3: "Ember Monastery",
            4: "Skyroad Summit"
        }
        print(f"🎮 Campaign set to: Act {act} - {act_names.get(act, 'Unknown')} (Mission {mission})")
        print(f"   Biome: {self.current_biome}")
        print(f"   Base abilities: {get_base_abilities_for_act(self.campaign_state)}")

    def get_hub_for_act(self, act: int) -> str:
        """Get the hub state name for a given act."""
        hub_map = {
            0: "lantern_hub",
            1: "lantern_hub",  # Veil Maiden leads back to Lantern before hollowing
            2: "hollow_hub",
            3: "ember_hub",
            4: "sky_hub",
        }
        return hub_map.get(act, "lantern_hub")

    def return_to_hub(self) -> None:
        """Return to the appropriate hub for the current act."""
        if not self.campaign_mode:
            return

        hub_state = self.get_hub_for_act(self.campaign_state.act)
        self.change_state(hub_state)
        print(f"🏛️  Returned to hub: {hub_state}")

    def restart_level(self) -> None:
        self.build_level()
        self.change_state("play")

    def next_level(self) -> None:
        self.level_index += 1
        unlocked_id = self.unlock_mgr.unlock_next()
        if unlocked_id:
            self._sync_features_with_unlocks()
        # Reset seed to None so each level gets a new random seed
        self.seed = None
        self.build_level()
        self.change_state("play")

    def on_level_clear(self) -> None:
        cfg = DIFFICULTY_CONFIG[self.difficulty]
        clear_bonus = int(1000 * cfg.get("multiplier", 1.0))
        self.total_score += clear_bonus

        # Auto-save on level completion (checkpoint)
        self.unlock_mgr.save_game_state(
            self.level_index,
            self.lives,
            self.total_score,
            self.game_time
        )

        if self.campaign_mode:
            # Campaign mode: Advance mission and return to hub
            self.campaign_state.mission_index += 1
            self.return_to_hub()
        else:
            # Arcade mode: Continue to next level
            self.next_level()

    def on_game_over(self) -> None:
        if self.campaign_mode:
            # Campaign mode: Return to hub on death (keep campaign progress)
            # Reset mission progress but keep abilities and scrolls
            self.campaign_state.mission_index = 0
            self.lives = PLAYER_LIVES  # Restore lives at hub
            print("💀 Mission failed. Returning to hub...")
            self.return_to_hub()
        else:
            # Arcade mode: Game over screen and highscore
            # Delete save file on game over (death consequences)
            self.unlock_mgr.delete_save()

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
            self.current_biome,
        )

        # Render Ability Orbs (with animations)
        for orb in self.ability_orbs:
            orb.draw(self.play_area, cam)

        # Render enemies
        self.enemy_manager.draw(self.play_area, (cam.x, cam.y))

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

        # Draw player facing direction indicator (similar to enemies)
        player_screen_rect = self.player.rect.move(-cam.x, -cam.y)
        if self.player.facing == 1:
            # Right facing triangle
            points = [
                (player_screen_rect.right - 5, player_screen_rect.top + 5),
                (player_screen_rect.right - 5, player_screen_rect.top + 15),
                (player_screen_rect.right - 2, player_screen_rect.top + 10)
            ]
        else:
            # Left facing triangle
            points = [
                (player_screen_rect.left + 5, player_screen_rect.top + 5),
                (player_screen_rect.left + 5, player_screen_rect.top + 15),
                (player_screen_rect.left + 2, player_screen_rect.top + 10)
            ]
        pygame.draw.polygon(self.play_area, (255, 255, 255), points)

        # Draw sword on player
        # Sword is a small rectangle extending from player's side
        sword_length = 8
        sword_width = 3
        if self.player.facing == 1:
            # Right facing sword
            sword_rect = pygame.Rect(
                player_screen_rect.right,
                player_screen_rect.centery - sword_width // 2,
                sword_length,
                sword_width
            )
        else:
            # Left facing sword
            sword_rect = pygame.Rect(
                player_screen_rect.left - sword_length,
                player_screen_rect.centery - sword_width // 2,
                sword_length,
                sword_width
            )
        pygame.draw.rect(self.play_area, (200, 200, 200), sword_rect)  # Silver sword

        # Draw sword arc animation during attack
        if self.player.is_attacking:
            attack_hitbox = self.player.get_attack_hitbox()
            if attack_hitbox:
                # Draw arc to show attack range
                attack_screen = attack_hitbox.move(-cam.x, -cam.y)
                # Draw semi-transparent arc
                arc_surface = pygame.Surface((attack_screen.width, attack_screen.height), pygame.SRCALPHA)

                if self.player.facing == 1:
                    # Right facing arc
                    pygame.draw.arc(
                        arc_surface,
                        (255, 200, 100, 180),  # Orange-yellow with alpha
                        arc_surface.get_rect(),
                        -math.pi/3,  # Start angle
                        math.pi/3,   # End angle
                        3
                    )
                else:
                    # Left facing arc
                    pygame.draw.arc(
                        arc_surface,
                        (255, 200, 100, 180),  # Orange-yellow with alpha
                        arc_surface.get_rect(),
                        2*math.pi/3,  # Start angle
                        4*math.pi/3,  # End angle
                        3
                    )

                self.play_area.blit(arc_surface, (attack_screen.x, attack_screen.y))

        # Draw attack hitbox if attacking
        if self.modifiers.show_hitboxes and hasattr(self.player, 'get_attack_hitbox'):
            attack_hitbox = self.player.get_attack_hitbox()
            if attack_hitbox:
                pygame.draw.rect(
                    self.play_area,
                    (255, 100, 0),  # Orange for attack hitbox
                    attack_hitbox.move(-cam.x, -cam.y),
                    2,
                )

        # Draw damage numbers
        self.damage_numbers.draw(self.play_area, (cam.x, cam.y))

        # Draw hitboxes if enabled
        if self.modifiers.show_hitboxes:
            # Player hitbox (bright green)
            pygame.draw.rect(
                self.play_area,
                (0, 255, 0),
                self.player.rect.move(-cam.x, -cam.y),
                2,
            )

            # Tile hitboxes (white)
            for t in self.tiles:
                if cam.colliderect(t):
                    pygame.draw.rect(
                        self.play_area,
                        (255, 255, 255),
                        (t.x - cam.x, t.y - cam.y, t.w, t.h),
                        1,
                    )

            # Phaseable wall hitboxes (purple)
            for pw in self.phaseable_walls:
                if cam.colliderect(pw):
                    pygame.draw.rect(
                        self.play_area,
                        (255, 0, 255),
                        (pw.x - cam.x, pw.y - cam.y, pw.w, pw.h),
                        2,
                    )

            # Hazard hitboxes (red)
            for h in self.hazards:
                if cam.colliderect(h):
                    pygame.draw.rect(
                        self.play_area,
                        (255, 0, 0),
                        (h.x - cam.x, h.y - cam.y, h.w, h.h),
                        2,
                    )

            # Coin hitboxes (yellow)
            for coin in self.coins:
                if cam.colliderect(coin.rect):
                    pygame.draw.rect(
                        self.play_area,
                        (255, 255, 0),
                        (coin.rect.x - cam.x, coin.rect.y - cam.y, coin.rect.w, coin.rect.h),
                        1,
                    )

            # Pickup hitboxes (cyan)
            for hp in self.health_pickups:
                if cam.colliderect(hp.rect):
                    pygame.draw.rect(
                        self.play_area,
                        (0, 255, 255),
                        (hp.rect.x - cam.x, hp.rect.y - cam.y, hp.rect.w, hp.rect.h),
                        1,
                    )

            for life in self.life_pickups:
                if cam.colliderect(life.rect):
                    pygame.draw.rect(
                        self.play_area,
                        (0, 255, 255),
                        (life.rect.x - cam.x, life.rect.y - cam.y, life.rect.w, life.rect.h),
                        1,
                    )

            # Powerup hitboxes (magenta)
            for pup in self.powerups:
                if cam.colliderect(pup.rect):
                    pygame.draw.rect(
                        self.play_area,
                        (255, 0, 200),
                        (pup.rect.x - cam.x, pup.rect.y - cam.y, pup.rect.w, pup.rect.h),
                        1,
                    )

            # Exit gate hitbox (bright cyan)
            if self.exit_gate and self.exit_gate.rect and cam.colliderect(self.exit_gate.rect):
                pygame.draw.rect(
                    self.play_area,
                    (0, 255, 255),
                    (self.exit_gate.rect.x - cam.x, self.exit_gate.rect.y - cam.y,
                     self.exit_gate.rect.w, self.exit_gate.rect.h),
                    2,
                )

        # Draw new modular HUD at the top
        draw_hud_new(
            self.hud_area,
            self.total_score,
            self.lives,
            self.player.health,
            self.level_index,
            self.difficulty,
            self.abilities,
            self.game_time,
            self.exit_gate,
            self.player,
            self.unlock_mgr,
        )

        # Draw overlays on play area - larger and more visible
        PowerupIndicators.draw(self.play_area, self.player, LOGICAL_W - 200, 20)
        AbilityResourceBars.draw(self.play_area, self.player, LOGICAL_W - 20, 140)

        # Blit HUD at top, play area below
        self.logical.blit(self.hud_area, (0, 0))
        self.logical.blit(self.play_area, (0, HUD_HEIGHT))
