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
        self.bg_color = (25, 25, 40, 200)  # Semi-transparent, slightly lighter
        self.border_color = (80, 80, 110)

    def draw_background(self, surf):
        """Draw section background with rounded corners"""
        bg_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, self.bg_color, bg_surf.get_rect(), border_radius=10)
        pygame.draw.rect(bg_surf, self.border_color, bg_surf.get_rect(), 3, border_radius=10)
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

    # Border - thicker and brighter for better visibility
    pygame.draw.rect(surf, (140, 140, 160), (x, y, width, height), 3, border_radius=6)


def draw_heart(surf, x, y, size, filled=True):
    """Draw a heart icon (simplified as rounded square)"""
    rect = pygame.Rect(x, y, size, size)

    if filled:
        color = (255, 90, 90)
        border_color = (255, 150, 150)
        pygame.draw.rect(surf, color, rect, border_radius=5)
        pygame.draw.rect(surf, border_color, rect, 3, border_radius=5)
    else:
        color = (70, 35, 35)
        border_color = (120, 60, 60)
        pygame.draw.rect(surf, color, rect, border_radius=5)
        pygame.draw.rect(surf, border_color, rect, 3, border_radius=5)


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

        x, y = self.rect.x + 14, self.rect.y + 10

        # Label - larger and bolder
        label = FONT.render("SCORE", True, (220, 220, 240))
        surf.blit(label, (x, y - 4))

        # Score with larger font
        score_text = FONT_BIG.render(f"{game_data['score']:,}", True, (255, 230, 80))
        surf.blit(score_text, (x, y + 18))

        # Coin progress
        y += 54
        coins_collected = game_data.get('coins_collected', 0)
        coins_required = game_data.get('coins_required', 0)

        # Progress bar - taller for better visibility
        bar_width = self.rect.w - 28
        bar_height = 16
        bar_x, bar_y = x, y

        # Draw bar
        if coins_required > 0:
            ratio = min(1.0, coins_collected / coins_required)
            color = (100, 255, 140) if ratio >= 1.0 else (255, 230, 80)
        else:
            ratio = 1.0
            color = (100, 255, 140)

        draw_progress_bar(surf, bar_x, bar_y, bar_width, bar_height, ratio, color)

        # Text overlay - centered and larger
        coin_text = FONT.render(
            f"{coins_collected}/{coins_required}",
            True, (255, 255, 255)
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

        x, y = self.rect.x + 14, self.rect.y + 10

        # HP label - larger
        hp_label = FONT.render("HP", True, (220, 220, 240))
        surf.blit(hp_label, (x, y - 4))

        # Health hearts - larger and more visible
        health = game_data.get('health', 3)
        max_health = PLAYER_MAX_HEALTH

        segment_size = 24
        segment_gap = 6

        y += 20

        # Draw hearts
        for i in range(max_health):
            seg_x = x + i * (segment_size + segment_gap)
            draw_heart(surf, seg_x, y, segment_size, filled=(i < health))

        # Lives display
        y += 34
        lives = game_data.get('lives', 3)

        # Lives icon (simple square) - larger
        icon_rect = pygame.Rect(x, y, 20, 20)
        pygame.draw.rect(surf, (255, 140, 255), icon_rect, border_radius=4)
        pygame.draw.rect(surf, (255, 180, 255), icon_rect, 3, border_radius=4)

        # Lives count - larger
        lives_text = FONT.render(f"x{lives}", True, (255, 160, 255))
        surf.blit(lives_text, (x + 28, y - 2))

        # Stamina bar (if dash ability is unlocked)
        player = game_data.get('player')
        if player and hasattr(player, 'abilities') and 'dash' in player.abilities:
            dash = player.abilities['dash']
            if hasattr(dash, 'resource') and hasattr(dash, 'max_resource'):
                y += 28

                # Stamina bar - taller and more visible
                bar_w = self.rect.w - 28
                bar_h = 10
                ratio = dash.resource / dash.max_resource if dash.max_resource > 0 else 0

                # Color based on stamina level
                if ratio > 0.5:
                    color = (120, 220, 255)  # Cyan when full
                elif ratio > 0.25:
                    color = (255, 220, 120)  # Orange when medium
                else:
                    color = (255, 120, 120)  # Red when low

                draw_progress_bar(surf, x, y, bar_w, bar_h, ratio, color)


# ============================================================================
# SECTION 3: LEVEL INFO
# ============================================================================

class LevelInfoSection(HUDSection):
    """Level and difficulty information"""

    def draw(self, surf, game_data):
        self.draw_background(surf)

        x, y = self.rect.x + 14, self.rect.y + 10

        # Level label - larger
        label = FONT.render("LEVEL", True, (220, 220, 240))
        surf.blit(label, (x, y - 4))

        # Level number (large)
        level = game_data.get('level', 1)
        level_text = FONT_BIG.render(f"{level}", True, (120, 220, 255))
        surf.blit(level_text, (x, y + 18))

        # Difficulty badge
        y += 54
        difficulty = game_data.get('difficulty', 'medium')

        # Color by difficulty - brighter
        diff_colors = {
            'easy': (120, 255, 120),
            'medium': (255, 220, 80),
            'hard': (255, 120, 120),
            'expert': (220, 80, 255)
        }
        color = diff_colors.get(difficulty, (150, 150, 150))

        badge_width = self.rect.w - 28
        badge_rect = pygame.Rect(x, y, badge_width, 24)
        pygame.draw.rect(surf, color, badge_rect, border_radius=5)
        pygame.draw.rect(surf, (255, 255, 255), badge_rect, 3, border_radius=5)

        diff_text = FONT.render(difficulty.upper(), True, (20, 20, 30))
        text_rect = diff_text.get_rect(center=badge_rect.center)
        surf.blit(diff_text, text_rect)


# ============================================================================
# SECTION 4: TIME & ABILITIES
# ============================================================================

class TimeAbilitiesSection(HUDSection):
    """Timer and abilities section"""

    def draw(self, surf, game_data):
        self.draw_background(surf)

        x, y = self.rect.x + 14, self.rect.y + 10

        # Time label - larger
        label = FONT.render("TIME", True, (220, 220, 240))
        surf.blit(label, (x, y - 4))

        # Time display - larger and more visible
        time = game_data.get('time', 0.0)
        time_text = FONT_BIG.render(format_time(time), True, (160, 255, 220))
        surf.blit(time_text, (x, y + 18))

        # Ability indicators
        y += 54
        abilities = game_data.get('abilities', [])

        # Draw ability chips - larger
        chip_w, chip_h = 38, 28
        chip_gap = 5

        from unlocks import ABILITY_INFO

        for i, ability in enumerate(abilities[:5]):  # Show max 5
            chip_x = x + i * (chip_w + chip_gap)
            chip_rect = pygame.Rect(chip_x, y, chip_w, chip_h)

            info = ABILITY_INFO.get(ability, {})
            short = info.get("short", "??")
            color = info.get("color", (150, 150, 150))

            pygame.draw.rect(surf, color, chip_rect, border_radius=5)
            pygame.draw.rect(surf, (255, 255, 255), chip_rect, 2, border_radius=5)

            txt = FONT.render(short, True, (255, 255, 255))
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

        x, y = self.rect.x + 14, self.rect.y + 10

        # Get unlock manager data
        unlock_mgr = game_data.get('unlock_mgr')
        if not unlock_mgr:
            # No unlock manager, show placeholder
            label = FONT.render("PROGRESS", True, (220, 220, 240))
            surf.blit(label, (x, y))
            return

        # Get unlock info
        next_unlock = unlock_mgr.get_next_unlock()
        available_orbs = unlock_mgr.get_ability_orbs_available()

        # Section label - larger
        label = FONT.render("NEXT", True, (220, 220, 240))
        surf.blit(label, (x, y - 4))

        y += 18

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

            # Ability preview box - larger
            preview_w = self.rect.w - 28
            preview_h = 28
            preview_rect = pygame.Rect(x, y, preview_w, preview_h)

            # Draw preview background
            pygame.draw.rect(surf, (30, 30, 40), preview_rect, border_radius=5)
            pygame.draw.rect(surf, color, preview_rect, 3, border_radius=5)

            # Ability icon (chip style) - larger
            icon_size = 24
            icon_x = x + 4
            icon_y = y + 2
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            pygame.draw.rect(surf, color, icon_rect, border_radius=4)

            # Short name in icon
            icon_text = FONT.render(short, True, (255, 255, 255))
            icon_text_rect = icon_text.get_rect(center=icon_rect.center)
            surf.blit(icon_text, icon_text_rect)

            # Ability name
            name_text = FONT.render(ability_name[:8], True, COLOR_TEXT)
            surf.blit(name_text, (icon_x + icon_size + 6, y + 6))

            # Progress info
            y += 34

            # Current/needed text - larger
            progress_text = FONT.render(
                f"{available_orbs}/{cost}",
                True, (200, 200, 220)
            )
            surf.blit(progress_text, (x, y))

            y += 20

            # Progress bar - taller
            bar_width = self.rect.w - 28
            bar_height = 12
            bar_x = x
            bar_y = y

            # Color based on progress
            if progress >= 1.0:
                bar_color = (100, 255, 140)  # Green when ready
            elif progress >= 0.5:
                bar_color = (255, 220, 80)  # Yellow when halfway
            else:
                bar_color = color  # Ability color

            draw_progress_bar(surf, bar_x, bar_y, bar_width, bar_height, progress, bar_color)

        else:
            # All abilities unlocked!
            all_text = FONT_BIG.render("MAXED!", True, (100, 255, 140))
            surf.blit(all_text, (x, y))

            y += 38
            congrats = FONT.render("Master!", True, (255, 230, 80))
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

        bar_w, bar_h = 180, 26
        gap = 6
        offset_y = 0

        pm = player.powerup_manager
        powerups = []

        # Collect active powerups
        if hasattr(pm, 'speed_boost') and pm.speed_boost.is_active():
            powerups.append({
                'name': 'SPEED',
                'time': pm.speed_boost.get_time_remaining(),
                'duration': pm.speed_boost.duration,
                'color': (255, 220, 80)
            })

        if hasattr(pm, 'triple_jump') and pm.triple_jump.is_active():
            powerups.append({
                'name': 'TRIPLE',
                'time': pm.triple_jump.get_time_remaining(),
                'duration': pm.triple_jump.duration,
                'color': (120, 255, 220)
            })

        if hasattr(pm, 'coin_magnet') and pm.coin_magnet.is_active():
            powerups.append({
                'name': 'MAGNET',
                'time': pm.coin_magnet.get_time_remaining(),
                'duration': pm.coin_magnet.duration,
                'color': (255, 230, 80)
            })

        # Draw each powerup
        for pup in powerups:
            ratio = pup['time'] / pup['duration'] if pup['duration'] > 0 else 0

            # Background with transparency - darker for better contrast
            bg_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (20, 20, 30, 220), bg_surf.get_rect(), border_radius=6)
            surf.blit(bg_surf, (x, y + offset_y))

            # Fill
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(surf, pup['color'], (x, y + offset_y, fill_w, bar_h), border_radius=6)

            # Border - thicker and brighter
            pygame.draw.rect(surf, pup['color'], (x, y + offset_y, bar_w, bar_h), 3, border_radius=6)

            # Label and time - larger font
            label = FONT.render(pup['name'], True, (255, 255, 255))
            time_text = FONT.render(f"{pup['time']:.1f}s", True, (255, 255, 255))

            surf.blit(label, (x + 8, y + offset_y + 4))
            surf.blit(time_text, (x + bar_w - time_text.get_width() - 8, y + offset_y + 4))

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

        bar_w, bar_h = 120, 14
        gap = 6
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
                    'color': (200, 120, 255),
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
                    'color': (255, 170, 120),
                    'discrete': True
                })

        # Note: Dash stamina is NOT shown here - it's in the Vitals section

        # Draw each resource
        for res in resources:
            ratio = res['value'] / res['max'] if res['max'] > 0 else 0

            # Label (to the left) - larger font
            label_text = res['name']
            if res.get('discrete'):
                # Show discrete count for charge-based abilities
                label_text = f"{res['name']} ({int(res['value'])})"

            label = FONT.render(label_text, True, (220, 220, 240))
            surf.blit(label, (x - label.get_width() - 8, y + offset_y))

            # Background - darker for better contrast
            pygame.draw.rect(surf, (30, 30, 40), (x, y + offset_y, bar_w, bar_h), border_radius=4)

            # Fill
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(surf, res['color'], (x, y + offset_y, fill_w, bar_h), border_radius=4)

            # Border - thicker and brighter
            pygame.draw.rect(surf, res['color'], (x, y + offset_y, bar_w, bar_h), 3, border_radius=4)

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
