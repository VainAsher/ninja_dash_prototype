"""
UI Module - Enhanced user interface components for Ninja Dash
Includes Button, TextInput, Toggle, Slider, HUD, and debug overlays.
"""

import pygame
from settings import (
    FONT, FONT_BIG, FONT_SMALL,
    COLOR_TEXT, COLOR_BTN_BG, COLOR_BTN_BG_HOVER,
    COLOR_HUD_BG, HUD_HEIGHT
)


class Button:
    """Interactive button UI element with enhanced visual feedback."""
    
    def __init__(self, label, on_click):
        self.label = label
        self.on_click = on_click
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hover = False
        self.enabled = True
        self.click_started = False

    def layout(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def handle_event(self, event):
        if not self.enabled:
            return
            
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.click_started = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.click_started and self.rect.collidepoint(event.pos):
                self.on_click()
            self.click_started = False

    def draw(self, surf):
        # Enhanced visual feedback
        if not self.enabled:
            bg = (30, 30, 40)
            border = (50, 50, 60)
            text_color = (100, 100, 120)
        elif self.click_started and self.hover:
            bg = (50, 80, 120)  # Pressed state
            border = (100, 150, 200)
            text_color = (255, 255, 255)
        elif self.hover:
            bg = (70, 90, 130)  # Hover state
            border = (120, 180, 240)
            text_color = (255, 255, 255)
        else:
            bg = COLOR_BTN_BG  # Normal state
            border = (60, 60, 90)
            text_color = COLOR_TEXT
        
        # Draw button with border
        pygame.draw.rect(surf, bg, self.rect, border_radius=8)
        pygame.draw.rect(surf, border, self.rect, 2, border_radius=8)
        
        # Draw text
        txt = FONT.render(self.label, True, text_color)
        tr = txt.get_rect(center=self.rect.center)
        surf.blit(txt, tr)


class Toggle:
    """Toggle switch UI element."""
    
    def __init__(self, label, initial_value, on_change):
        self.label = label
        self.value = initial_value
        self.on_change = on_change
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.switch_rect = pygame.Rect(0, 0, 0, 0)
        self.hover = False

    def layout(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        # Switch is on the right side
        switch_w = 60
        switch_h = 30
        self.switch_rect = pygame.Rect(
            x + w - switch_w - 10,
            y + (h - switch_h) // 2,
            switch_w,
            switch_h
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.switch_rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.switch_rect.collidepoint(event.pos):
                self.value = not self.value
                self.on_change(self.value)

    def draw(self, surf):
        # Draw label
        txt = FONT.render(self.label, True, COLOR_TEXT)
        surf.blit(txt, (self.rect.x + 10, self.rect.y + (self.rect.h - txt.get_height()) // 2))
        
        # Draw switch background
        bg_color = (80, 200, 120) if self.value else (60, 60, 80)
        if self.hover:
            bg_color = tuple(min(255, c + 20) for c in bg_color)
        
        pygame.draw.rect(surf, bg_color, self.switch_rect, border_radius=15)
        
        # Draw switch knob
        knob_radius = 12
        knob_x = self.switch_rect.right - 18 if self.value else self.switch_rect.left + 18
        knob_y = self.switch_rect.centery
        pygame.draw.circle(surf, COLOR_TEXT, (knob_x, knob_y), knob_radius)


class Slider:
    """Slider UI element for numeric values."""
    
    def __init__(self, label, min_val, max_val, initial_value, on_change, format_str="{:.2f}"):
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_value
        self.on_change = on_change
        self.format_str = format_str
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.slider_rect = pygame.Rect(0, 0, 0, 0)
        self.dragging = False
        self.hover = False

    def layout(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        # Slider track is on the right side
        slider_w = 200
        slider_h = 8
        self.slider_rect = pygame.Rect(
            x + w - slider_w - 80,
            y + (h - slider_h) // 2,
            slider_w,
            slider_h
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.slider_rect.collidepoint(event.pos) or self._get_handle_rect().collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_mouse(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value_from_mouse(event.pos)
            self.hover = self.slider_rect.collidepoint(event.pos) or self._get_handle_rect().collidepoint(event.pos)

    def _update_value_from_mouse(self, pos):
        # Calculate value from mouse position
        rel_x = pos[0] - self.slider_rect.x
        ratio = max(0.0, min(1.0, rel_x / self.slider_rect.width))
        old_value = self.value
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        
        if abs(self.value - old_value) > 0.001:  # Avoid spam
            self.on_change(self.value)

    def _get_handle_rect(self):
        # Calculate handle position
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.slider_rect.x + int(ratio * self.slider_rect.width)
        handle_y = self.slider_rect.centery
        handle_size = 16
        return pygame.Rect(handle_x - handle_size // 2, handle_y - handle_size // 2, handle_size, handle_size)

    def draw(self, surf):
        # Draw label
        txt = FONT.render(self.label, True, COLOR_TEXT)
        surf.blit(txt, (self.rect.x + 10, self.rect.y + (self.rect.h - txt.get_height()) // 2))
        
        # Draw slider track
        track_color = (80, 80, 100) if not self.hover else (100, 100, 120)
        pygame.draw.rect(surf, track_color, self.slider_rect, border_radius=4)
        
        # Draw filled portion
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        filled_w = int(ratio * self.slider_rect.width)
        if filled_w > 0:
            filled_rect = pygame.Rect(self.slider_rect.x, self.slider_rect.y, filled_w, self.slider_rect.height)
            pygame.draw.rect(surf, (100, 150, 200), filled_rect, border_radius=4)
        
        # Draw handle
        handle_rect = self._get_handle_rect()
        handle_color = (200, 200, 220) if not self.hover else COLOR_TEXT
        pygame.draw.circle(surf, handle_color, handle_rect.center, handle_rect.width // 2)
        
        # Draw value
        value_txt = FONT_SMALL.render(self.format_str.format(self.value), True, COLOR_TEXT)
        value_x = self.slider_rect.right + 10
        value_y = self.rect.y + (self.rect.h - value_txt.get_height()) // 2
        surf.blit(value_txt, (value_x, value_y))


class TextInput:
    """Text input field for entering strings."""
    
    def __init__(self, prompt, initial=""):
        self.prompt = prompt
        self.text = str(initial)
        self.active = True
        self.cursor_timer = 0
        self.cursor_visible = True

    def handle_event(self, event):
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.active = False
            elif event.key == pygame.K_ESCAPE:
                self.text = ""
                self.active = False
            else:
                ch = event.unicode
                if ch.isprintable():
                    self.text += ch

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surf, rect):
        pygame.draw.rect(surf, (30, 30, 50), rect, border_radius=10)
        border_color = (120, 120, 180) if self.active else (90, 90, 140)
        pygame.draw.rect(surf, border_color, rect, 2, border_radius=10)
        
        p = FONT.render(self.prompt, True, COLOR_TEXT)
        surf.blit(p, (rect.x + 16, rect.y + 12))
        
        display_text = self.text
        if self.active and self.cursor_visible:
            display_text += "_"
        
        t = FONT_BIG.render(display_text or " ", True, COLOR_TEXT)
        surf.blit(t, (rect.x + 16, rect.y + 12 + p.get_height() + 8))


def draw_hud(surf, text_left, text_right):
    """Draw the HUD banner at the top of the screen."""
    bar = pygame.Rect(0, 0, surf.get_width(), HUD_HEIGHT)
    pygame.draw.rect(surf, COLOR_HUD_BG, bar)
    pygame.draw.line(surf, (60, 60, 80), (0, HUD_HEIGHT - 1), (surf.get_width(), HUD_HEIGHT - 1), 1)
    
    l = FONT.render(text_left, True, COLOR_TEXT)
    surf.blit(l, (12, (HUD_HEIGHT - l.get_height()) // 2))
    
    r = FONT.render(text_right, True, COLOR_TEXT)
    rr = r.get_rect(topright=(surf.get_width() - 12, (HUD_HEIGHT - r.get_height()) // 2))
    surf.blit(r, rr)


def draw_ability_chips(surf, enabled_abilities, x, y):
    """Draw small chips showing enabled abilities."""
    from unlocks import ABILITY_INFO
    
    chip_w, chip_h = 40, 24
    gap = 6
    
    for i, ability in enumerate(enabled_abilities):
        info = ABILITY_INFO.get(ability, {})
        short = info.get("short", "??")
        color = info.get("color", (150, 150, 150))
        
        chip_x = x + i * (chip_w + gap)
        chip_rect = pygame.Rect(chip_x, y, chip_w, chip_h)
        
        # Draw chip background
        pygame.draw.rect(surf, color, chip_rect, border_radius=4)
        pygame.draw.rect(surf, (255, 255, 255), chip_rect, 1, border_radius=4)
        
        # Draw short name
        txt = FONT_SMALL.render(short, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=chip_rect.center)
        surf.blit(txt, txt_rect)


def draw_powerup_timers(surf, player, x, y):
    """Draw active power-up timer bars."""
    bar_w, bar_h = 60, 16
    gap = 4
    offset_y = 0
    
    # Speed boost
    if player.speed_boost_timer > 0:
        ratio = player.speed_boost_timer / player.speed_boost_duration
        _draw_timer_bar(surf, x, y + offset_y, bar_w, bar_h, ratio, "SPD", (255, 200, 50))
        offset_y += bar_h + gap
    
    # Triple jump
    if player.triple_jump_timer > 0:
        ratio = player.triple_jump_timer / player.triple_jump_duration
        _draw_timer_bar(surf, x, y + offset_y, bar_w, bar_h, ratio, "TRP", (100, 255, 200))
        offset_y += bar_h + gap
    
    # Magnet
    if player.magnet_timer > 0:
        ratio = player.magnet_timer / player.magnet_duration
        _draw_timer_bar(surf, x, y + offset_y, bar_w, bar_h, ratio, "MAG", (255, 215, 0))
        offset_y += bar_h + gap


def _draw_timer_bar(surf, x, y, w, h, ratio, label, color):
    """Helper to draw a single timer bar."""
    # Background
    pygame.draw.rect(surf, (30, 30, 30), (x, y, w, h), border_radius=3)
    
    # Filled portion
    filled_w = int(w * ratio)
    if filled_w > 0:
        pygame.draw.rect(surf, color, (x, y, filled_w, h), border_radius=3)
    
    # Border
    pygame.draw.rect(surf, color, (x, y, w, h), 1, border_radius=3)
    
    # Label
    txt = FONT_SMALL.render(label, True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(x + w // 2, y + h // 2))
    surf.blit(txt, txt_rect)
