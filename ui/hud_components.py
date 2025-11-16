"""
HUD Components - Modular UI elements for game HUD
"""

import pygame
from settings import (
    FONT, FONT_BIG, FONT_SMALL,
    COLOR_TEXT, COLOR_HUD_BG,
    PLAYER_MAX_HEALTH
)


# ============================================================================
# BASE CLASSES AND HELPER FUNCTIONS
# ============================================================================

class HUDSection:
    """Base class for HUD sections with positioning"""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = (20, 20, 30, 180)  # Semi-transparent
        self.border_color = (60, 60, 80)

    def draw_background(self, surf):
        """Draw section background with rounded corners"""
        bg_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, self.bg_color, bg_surf.get_rect(), border_radius=8)
        pygame.draw.rect(bg_surf, self.border_color, bg_surf.get_rect(), 2, border_radius=8)
        surf.blit(bg_surf, self.rect.topleft)

    def draw(self, surf, game_data):
        """Override in subclasses"""
        pass


def draw_progress_bar(surf, x, y, width, height, ratio, color_filled, color_empty=(40, 40, 50)):
    """Draw a progress bar with fill ratio"""
    # Clamp ratio
    ratio = max(0.0, min(1.0, ratio))

    # Background
    pygame.draw.rect(surf, color_empty, (x, y, width, height), border_radius=6)

    # Fill
    fill_width = int(width * ratio)
    if fill_width > 0:
        pygame.draw.rect(surf, color_filled, (x, y, fill_width, height), border_radius=6)

    # Border
    pygame.draw.rect(surf, (100, 100, 120), (x, y, width, height), 2, border_radius=6)


def draw_heart(surf, x, y, size, filled=True):
    """Draw a heart icon (simplified as rounded square)"""
    rect = pygame.Rect(x, y, size, size)

    if filled:
        color = (255, 80, 80)
        border_color = (255, 120, 120)
        pygame.draw.rect(surf, color, rect, border_radius=4)
        pygame.draw.rect(surf, border_color, rect, 2, border_radius=4)
    else:
        color = (60, 30, 30)
        border_color = (100, 50, 50)
        pygame.draw.rect(surf, color, rect, border_radius=4)
        pygame.draw.rect(surf, border_color, rect, 2, border_radius=4)


def format_time(seconds):
    """Format seconds as MM:SS.T"""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


# ============================================================================
# SECTION 1: SCORE & PROGRESS
# ============================================================================

class ScoreSection(HUDSection):
    """Score and collection progress section"""

    def draw(self, surf, game_data):
        self.draw_background(surf)

        x, y = self.rect.x + 12, self.rect.y + 6

        # Score with larger font
        score_text = FONT_BIG.render(f"{game_data['score']:,}", True, (255, 215, 0))
        surf.blit(score_text, (x, y))

        # Label
        label = FONT_SMALL.render("SCORE", True, (180, 180, 200))
        surf.blit(label, (x, y - 14))

        # Coin progress
        y += 32
        coins_collected = game_data.get('coins_collected', 0)
        coins_required = game_data.get('coins_required', 0)

        # Progress bar
        bar_width = self.rect.w - 24
        bar_height = 12
        bar_x, bar_y = x, y

        # Draw bar
        if coins_required > 0:
            ratio = min(1.0, coins_collected / coins_required)
            color = (80, 255, 120) if ratio >= 1.0 else (255, 215, 0)
        else:
            ratio = 1.0
            color = (80, 255, 120)

        draw_progress_bar(surf, bar_x, bar_y, bar_width, bar_height, ratio, color)

        # Text overlay
        coin_text = FONT_SMALL.render(
            f"COINS: {coins_collected}/{coins_required}",
            True, COLOR_TEXT
        )
        text_rect = coin_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        surf.blit(coin_text, text_rect)


# ============================================================================
# SECTION 2: PLAYER VITALS
# ============================================================================

class VitalsSection(HUDSection):
    """Player health, lives, and stamina section"""

    def draw(self, surf, game_data):
        self.draw_background(surf)

        x, y = self.rect.x + 12, self.rect.y + 8

        # Health hearts
        health = game_data.get('health', 3)
        max_health = PLAYER_MAX_HEALTH

        segment_size = 20
        segment_gap = 4

        # HP label
        hp_label = FONT_SMALL.render("HP", True, (180, 180, 200))
        surf.blit(hp_label, (x, y - 14))

        # Draw hearts
        for i in range(max_health):
            seg_x = x + i * (segment_size + segment_gap)
            draw_heart(surf, seg_x, y, segment_size, filled=(i < health))

        # Lives display
        y += 32
        lives = game_data.get('lives', 3)

        # Lives label
        lives_label = FONT_SMALL.render("LIVES", True, (180, 180, 200))
        surf.blit(lives_label, (x, y - 14))

        # Lives icon (simple square)
        icon_rect = pygame.Rect(x, y, 16, 16)
        pygame.draw.rect(surf, (255, 120, 255), icon_rect, border_radius=3)

        # Lives count
        lives_text = FONT.render(f"x{lives}", True, (255, 120, 255))
        surf.blit(lives_text, (x + 24, y))

        # Stamina bar (if dash ability is unlocked)
        player = game_data.get('player')
        if player and hasattr(player, 'abilities') and 'dash' in player.abilities:
            dash = player.abilities['dash']
            if hasattr(dash, 'resource') and hasattr(dash, 'max_resource'):
                y += 28

                # Stamina label
                stam_label = FONT_SMALL.render("STAM", True, (180, 180, 200))
                surf.blit(stam_label, (x, y - 14))

                # Stamina bar
                bar_w = self.rect.w - 24
                bar_h = 8
                ratio = dash.resource / dash.max_resource if dash.max_resource > 0 else 0

                # Color based on stamina level
                if ratio > 0.5:
                    color = (100, 200, 255)  # Cyan when full
                elif ratio > 0.25:
                    color = (255, 200, 100)  # Orange when medium
                else:
                    color = (255, 100, 100)  # Red when low

                draw_progress_bar(surf, x, y, bar_w, bar_h, ratio, color)


# ============================================================================
# SECTION 3: LEVEL INFO
# ============================================================================

class LevelInfoSection(HUDSection):
    """Level and difficulty information"""

    def draw(self, surf, game_data):
        self.draw_background(surf)

        x, y = self.rect.x + 12, self.rect.y + 8

        # Level label
        label = FONT_SMALL.render("LEVEL", True, (180, 180, 200))
        surf.blit(label, (x, y - 14))

        # Level number (large)
        level = game_data.get('level', 1)
        level_text = FONT_BIG.render(f"{level}", True, (100, 200, 255))
        surf.blit(level_text, (x, y))

        # Difficulty badge
        y += 32
        difficulty = game_data.get('difficulty', 'medium')

        # Color by difficulty
        diff_colors = {
            'easy': (100, 255, 100),
            'medium': (255, 200, 50),
            'hard': (255, 100, 100),
            'expert': (200, 50, 255)
        }
        color = diff_colors.get(difficulty, (150, 150, 150))

        badge_width = self.rect.w - 24
        badge_rect = pygame.Rect(x, y, badge_width, 20)
        pygame.draw.rect(surf, color, badge_rect, border_radius=4)

        diff_text = FONT_SMALL.render(difficulty.upper(), True, (0, 0, 0))
        text_rect = diff_text.get_rect(center=badge_rect.center)
        surf.blit(diff_text, text_rect)


# ============================================================================
# SECTION 4: TIME & ABILITIES
# ============================================================================

class TimeAbilitiesSection(HUDSection):
    """Timer and abilities section"""

    def draw(self, surf, game_data):
        self.draw_background(surf)

        x, y = self.rect.x + 12, self.rect.y + 8

        # Time label
        label = FONT_SMALL.render("TIME", True, (180, 180, 200))
        surf.blit(label, (x, y - 14))

        # Time display
        time = game_data.get('time', 0.0)
        time_text = FONT.render(format_time(time), True, (150, 255, 200))
        surf.blit(time_text, (x, y))

        # Ability indicators
        y += 32
        abilities = game_data.get('abilities', [])

        # Draw ability chips
        chip_w, chip_h = 32, 24
        chip_gap = 4

        from unlocks import ABILITY_INFO

        for i, ability in enumerate(abilities[:5]):  # Show max 5
            chip_x = x + i * (chip_w + chip_gap)
            chip_rect = pygame.Rect(chip_x, y, chip_w, chip_h)

            info = ABILITY_INFO.get(ability, {})
            short = info.get("short", "??")
            color = info.get("color", (150, 150, 150))

            pygame.draw.rect(surf, color, chip_rect, border_radius=4)
            pygame.draw.rect(surf, (255, 255, 255), chip_rect, 1, border_radius=4)

            txt = FONT_SMALL.render(short, True, (255, 255, 255))
            txt_rect = txt.get_rect(center=chip_rect.center)
            surf.blit(txt, txt_rect)


# ============================================================================
# SECTION 5: ABILITY PROGRESS
# ============================================================================

class AbilityProgressSection(HUDSection):
    """
    Display ability orb collection progress and next unlock.

    Shows:
    - Current ability orbs available
    - Progress to next ability unlock
    - Preview of next ability (icon + name)
    - Orbs needed for next unlock
    """

    def draw(self, surf, game_data):
        self.draw_background(surf)

        x, y = self.rect.x + 12, self.rect.y + 6

        # Get unlock manager data
        unlock_mgr = game_data.get('unlock_mgr')
        if not unlock_mgr:
            # No unlock manager, show placeholder
            label = FONT_SMALL.render("PROGRESS", True, (180, 180, 200))
            surf.blit(label, (x, y))
            return

        # Get unlock info
        next_unlock = unlock_mgr.get_next_unlock()
        available_orbs = unlock_mgr.get_ability_orbs_available()

        # Section label
        label = FONT_SMALL.render("NEXT ABILITY", True, (180, 180, 200))
        surf.blit(label, (x, y - 14))

        if next_unlock:
            # Next ability preview
            ability_id = next_unlock['ability_id']
            ability_name = next_unlock['name']
            cost = next_unlock['cost']
            orbs_needed = next_unlock['orbs_needed']
            progress = next_unlock['progress']

            from unlocks import ABILITY_INFO
            ability_info = ABILITY_INFO.get(ability_id, {})
            color = ability_info.get('color', (150, 150, 150))
            short = ability_info.get('short', '??')

            # Ability preview box
            preview_w = self.rect.w - 24
            preview_h = 24
            preview_rect = pygame.Rect(x, y, preview_w, preview_h)

            # Draw preview background
            pygame.draw.rect(surf, (30, 30, 40), preview_rect, border_radius=4)
            pygame.draw.rect(surf, color, preview_rect, 2, border_radius=4)

            # Ability icon (chip style)
            icon_size = 20
            icon_x = x + 4
            icon_y = y + 2
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            pygame.draw.rect(surf, color, icon_rect, border_radius=3)

            # Short name in icon
            icon_text = FONT_SMALL.render(short, True, (255, 255, 255))
            icon_text_rect = icon_text.get_rect(center=icon_rect.center)
            surf.blit(icon_text, icon_text_rect)

            # Ability name
            name_text = FONT_SMALL.render(ability_name, True, COLOR_TEXT)
            surf.blit(name_text, (icon_x + icon_size + 6, y + 5))

            # Progress info
            y += 30

            # Current/needed text
            progress_text = FONT_SMALL.render(
                f"ORBS: {available_orbs}/{cost}",
                True, (180, 180, 200)
            )
            surf.blit(progress_text, (x, y))

            y += 16

            # Progress bar
            bar_width = self.rect.w - 24
            bar_height = 8
            bar_x = x
            bar_y = y

            # Color based on progress
            if progress >= 1.0:
                bar_color = (80, 255, 120)  # Green when ready
            elif progress >= 0.5:
                bar_color = (255, 200, 50)  # Yellow when halfway
            else:
                bar_color = color  # Ability color

            draw_progress_bar(surf, bar_x, bar_y, bar_width, bar_height, progress, bar_color)

            # Orbs needed text (if not ready)
            if orbs_needed > 0:
                y += 12
                needed_text = FONT_SMALL.render(
                    f"Need {orbs_needed} more",
                    True, (200, 150, 150)
                )
                surf.blit(needed_text, (x, y))
            else:
                y += 12
                ready_text = FONT_SMALL.render(
                    "READY TO UNLOCK!",
                    True, (80, 255, 120)
                )
                surf.blit(ready_text, (x, y))

        else:
            # All abilities unlocked!
            all_text = FONT.render("ALL UNLOCKED!", True, (80, 255, 120))
            surf.blit(all_text, (x, y))

            y += 24
            congrats = FONT_SMALL.render("Master Ninja!", True, (255, 215, 0))
            surf.blit(congrats, (x, y))


# ============================================================================
# OVERLAY COMPONENTS
# ============================================================================

class PowerupIndicators:
    """Display active powerup timers"""

    @staticmethod
    def draw(surf, player, x, y):
        """Draw powerup timer bars"""
        if not player or not hasattr(player, 'powerup_manager'):
            return

        bar_w, bar_h = 140, 18
        gap = 4
        offset_y = 0

        pm = player.powerup_manager
        powerups = []

        # Collect active powerups
        if hasattr(pm, 'speed_boost') and pm.speed_boost.is_active():
            powerups.append({
                'name': 'SPEED BOOST',
                'time': pm.speed_boost.get_time_remaining(),
                'duration': pm.speed_boost.duration,
                'color': (255, 200, 50)
            })

        if hasattr(pm, 'triple_jump') and pm.triple_jump.is_active():
            powerups.append({
                'name': 'TRIPLE JUMP',
                'time': pm.triple_jump.get_time_remaining(),
                'duration': pm.triple_jump.duration,
                'color': (100, 255, 200)
            })

        if hasattr(pm, 'coin_magnet') and pm.coin_magnet.is_active():
            powerups.append({
                'name': 'MAGNET',
                'time': pm.coin_magnet.get_time_remaining(),
                'duration': pm.coin_magnet.duration,
                'color': (255, 215, 0)
            })

        # Draw each powerup
        for pup in powerups:
            ratio = pup['time'] / pup['duration'] if pup['duration'] > 0 else 0

            # Background with transparency
            bg_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (30, 30, 30, 200), bg_surf.get_rect(), border_radius=4)
            surf.blit(bg_surf, (x, y + offset_y))

            # Fill
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(surf, pup['color'], (x, y + offset_y, fill_w, bar_h), border_radius=4)

            # Border
            pygame.draw.rect(surf, pup['color'], (x, y + offset_y, bar_w, bar_h), 2, border_radius=4)

            # Label and time
            label = FONT_SMALL.render(pup['name'], True, (255, 255, 255))
            time_text = FONT_SMALL.render(f"{pup['time']:.1f}s", True, (255, 255, 255))

            surf.blit(label, (x + 6, y + offset_y + 3))
            surf.blit(time_text, (x + bar_w - time_text.get_width() - 6, y + offset_y + 3))

            offset_y += bar_h + gap


class AbilityResourceBars:
    """Display ability resource bars (charges, cooldowns, etc.)

    Note: Dash stamina is shown in Vitals section, not here.
    This overlay is for other ability resources like Shadow Step charges.
    """

    @staticmethod
    def draw(surf, player, x, y):
        """Draw ability resource indicators (excluding dash stamina)"""
        if not player or not hasattr(player, 'abilities'):
            return

        bar_w, bar_h = 100, 10
        gap = 3
        offset_y = 0

        resources = []

        # Shadow Step charges (not regenerating, discrete charges)
        if 'shadow_step' in player.abilities:
            shadow = player.abilities['shadow_step']
            if hasattr(shadow, 'charges') and hasattr(shadow, 'max_charges'):
                resources.append({
                    'name': 'SMOKE',
                    'value': shadow.charges,
                    'max': shadow.max_charges,
                    'color': (180, 100, 255),
                    'discrete': True  # Show as charges, not continuous bar
                })

        # Air Dodge charges
        if 'air_dodge' in player.abilities:
            dodge = player.abilities['air_dodge']
            if hasattr(dodge, 'uses_remaining') and hasattr(dodge, 'max_uses'):
                resources.append({
                    'name': 'DODGE',
                    'value': dodge.uses_remaining,
                    'max': dodge.max_uses,
                    'color': (255, 150, 100),
                    'discrete': True
                })

        # Note: Dash stamina is NOT shown here - it's in the Vitals section

        # Draw each resource
        for res in resources:
            ratio = res['value'] / res['max'] if res['max'] > 0 else 0

            # Label (to the left)
            label_text = res['name']
            if res.get('discrete'):
                # Show discrete count for charge-based abilities
                label_text = f"{res['name']} ({int(res['value'])})"

            label = FONT_SMALL.render(label_text, True, (180, 180, 200))
            surf.blit(label, (x - label.get_width() - 6, y + offset_y - 1))

            # Background
            pygame.draw.rect(surf, (40, 40, 50), (x, y + offset_y, bar_w, bar_h), border_radius=3)

            # Fill
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(surf, res['color'], (x, y + offset_y, fill_w, bar_h), border_radius=3)

            # Border
            pygame.draw.rect(surf, res['color'], (x, y + offset_y, bar_w, bar_h), 1, border_radius=3)

            offset_y += bar_h + gap


class ExitGateIndicator:
    """Visual indicator for exit gate status"""

    @staticmethod
    def draw(surf, exit_gate, x, y):
        """Draw exit gate status indicator"""
        if not exit_gate:
            return

        size = 32
        icon_rect = pygame.Rect(x, y, size, size)

        # Color based on status
        if exit_gate.unlocked:
            color = (80, 255, 120)
            border_color = (120, 255, 160)
            label = "UNLOCKED"
        else:
            color = (220, 80, 80)
            border_color = (255, 120, 120)
            label = "LOCKED"

        # Draw gate icon
        pygame.draw.rect(surf, color, icon_rect, border_radius=6)
        pygame.draw.rect(surf, border_color, icon_rect, 3, border_radius=6)

        # Draw lock/unlock symbol (simplified)
        center_x, center_y = icon_rect.center
        if exit_gate.unlocked:
            # Open padlock
            pygame.draw.circle(surf, (0, 0, 0), (center_x, center_y + 4), 6)
            pygame.draw.circle(surf, color, (center_x, center_y + 4), 4)
        else:
            # Closed padlock
            pygame.draw.circle(surf, (0, 0, 0), (center_x, center_y), 8, 3)
            pygame.draw.rect(surf, (0, 0, 0), (center_x - 6, center_y, 12, 10), border_radius=2)

        # Label
        label_text = FONT_SMALL.render(label, True, COLOR_TEXT)
        surf.blit(label_text, (x, y + size + 4))
