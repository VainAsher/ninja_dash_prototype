"""
Camera Module - Viewport management for Ninja Dash
Handles camera positioning and following the player.
"""

import pygame
from settings import LOGICAL_W, LOGICAL_H, HUD_HEIGHT, WORLD_W, WORLD_H, TILE_SIZE


def get_camera_rect(player_rect: pygame.Rect) -> pygame.Rect:
    """
    Calculate camera position centered on player with bounds checking.
    
    The camera follows the player while keeping them centered in the viewport.
    It stops at world boundaries to prevent showing areas outside the world.
    
    Args:
        player_rect: The player's rectangle position
        
    Returns:
        pygame.Rect representing the camera's viewport in world coordinates
    """
    # Calculate viewport size (excluding HUD)
    view_h = LOGICAL_H - HUD_HEIGHT
    
    # Center camera on player
    cam_x = player_rect.centerx - LOGICAL_W // 2
    cam_y = player_rect.centery - view_h // 2

    # Calculate maximum camera positions (prevent showing beyond world)
    max_x = WORLD_W * TILE_SIZE - LOGICAL_W
    max_y = WORLD_H * TILE_SIZE - view_h

    # Clamp camera to world bounds
    cam_x = max(0, min(cam_x, max_x))
    cam_y = max(0, min(cam_y, max_y))

    return pygame.Rect(cam_x, cam_y, LOGICAL_W, view_h)


def smooth_camera_follow(current_cam: pygame.Rect, 
                         target_cam: pygame.Rect, 
                         smoothing: float = 0.1) -> pygame.Rect:
    """
    Smooth camera movement using linear interpolation.
    
    This function can be used for smoother camera movement that lags
    slightly behind the player for a more cinematic feel.
    
    Args:
        current_cam: Current camera position
        target_cam: Target camera position (from get_camera_rect)
        smoothing: Smoothing factor (0-1, lower = smoother)
        
    Returns:
        New camera rect with smoothed position
    """
    new_x = current_cam.x + (target_cam.x - current_cam.x) * smoothing
    new_y = current_cam.y + (target_cam.y - current_cam.y) * smoothing
    
    return pygame.Rect(new_x, new_y, current_cam.width, current_cam.height)


def camera_with_deadzone(player_rect: pygame.Rect, 
                         current_cam: pygame.Rect,
                         deadzone_w: int = 200,
                         deadzone_h: int = 150) -> pygame.Rect:
    """
    Camera with deadzone - only moves when player leaves central area.
    
    This creates a more stable camera that doesn't constantly move with
    small player movements.
    
    Args:
        player_rect: Player position
        current_cam: Current camera position
        deadzone_w: Width of deadzone
        deadzone_h: Height of deadzone
        
    Returns:
        Updated camera rect
    """
    view_h = LOGICAL_H - HUD_HEIGHT
    
    # Calculate deadzone bounds relative to camera
    dead_left = current_cam.x + (LOGICAL_W - deadzone_w) // 2
    dead_right = dead_left + deadzone_w
    dead_top = current_cam.y + (view_h - deadzone_h) // 2
    dead_bottom = dead_top + deadzone_h
    
    # New camera position (start with current)
    new_x = current_cam.x
    new_y = current_cam.y
    
    # Adjust if player is outside deadzone
    if player_rect.centerx < dead_left:
        new_x = player_rect.centerx - (LOGICAL_W - deadzone_w) // 2
    elif player_rect.centerx > dead_right:
        new_x = player_rect.centerx - (LOGICAL_W + deadzone_w) // 2
    
    if player_rect.centery < dead_top:
        new_y = player_rect.centery - (view_h - deadzone_h) // 2
    elif player_rect.centery > dead_bottom:
        new_y = player_rect.centery - (view_h + deadzone_h) // 2
    
    # Clamp to world bounds
    max_x = WORLD_W * TILE_SIZE - LOGICAL_W
    max_y = WORLD_H * TILE_SIZE - view_h
    
    new_x = max(0, min(new_x, max_x))
    new_y = max(0, min(new_y, max_y))
    
    return pygame.Rect(new_x, new_y, LOGICAL_W, view_h)
