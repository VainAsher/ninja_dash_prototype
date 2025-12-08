"""
Zone-Based World Generation Demo

Demonstrates the new zone-based room generation system with:
- 5x5 zone grid per room
- Data-driven room customization
- Auto-tiling support
- Minimap rendering
- Console logging

Run this file to see a simple demo of the zone generation system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
import random
from typing import Dict, Tuple

from level_gen.zone_generator import (
    RoomNode, assign_zone_roles_for_room,
    ROOM_START, ROOM_COMBAT, ROOM_TREASURE, ROOM_SHOP, ROOM_EXIT,
    ZONES_W, ZONES_H
)
from level_gen.zone_integration import (
    generate_room_from_zones,
    log_generation_start,
    log_room_generation,
    log_generation_complete
)
from level_gen.tileset import TileSet, draw_tiles, validate_tiles
from ui.minimap import Minimap, print_world

from settings import TILE_SIZE, ROOM_W, ROOM_H


def create_demo_world(seed: int) -> Dict[Tuple[int, int], RoomNode]:
    """
    Create a small demo world with a few rooms.
    """
    rng = random.Random(seed)

    # Create a simple 3-room path: Start -> Combat -> Exit
    rooms = {
        (0, 0): RoomNode(0, 0, ROOM_START, rng.randrange(10**9)),
        (1, 0): RoomNode(1, 0, ROOM_COMBAT, rng.randrange(10**9)),
        (2, 0): RoomNode(2, 0, ROOM_TREASURE, rng.randrange(10**9)),
        (2, 1): RoomNode(2, 1, ROOM_SHOP, rng.randrange(10**9)),
        (2, 2): RoomNode(2, 2, ROOM_EXIT, rng.randrange(10**9)),
    }

    # Set up connections
    rooms[(0, 0)].neighbors = {(1, 0)}
    rooms[(1, 0)].neighbors = {(0, 0), (2, 0)}
    rooms[(2, 0)].neighbors = {(1, 0), (2, 1)}
    rooms[(2, 1)].neighbors = {(2, 0), (2, 2)}
    rooms[(2, 2)].neighbors = {(2, 1)}

    # Set up neighbor directions
    rooms[(0, 0)].neighbor_dirs = {"right": (1, 0)}
    rooms[(1, 0)].neighbor_dirs = {"left": (0, 0), "right": (2, 0)}
    rooms[(2, 0)].neighbor_dirs = {"left": (1, 0), "down": (2, 1)}
    rooms[(2, 1)].neighbor_dirs = {"up": (2, 0), "down": (2, 2)}
    rooms[(2, 2)].neighbor_dirs = {"up": (2, 1)}

    # Generate zone roles and tilemaps for each room
    for rc, room in rooms.items():
        room_rng = random.Random(room.seed)

        # Assign zone roles
        room.zone_roles = assign_zone_roles_for_room(room, room_rng)

        # Generate tilemap from zones
        room.tilemap, room.anchor_candidates = generate_room_from_zones(
            room, room.zone_roles, room_rng, ROOM_W, ROOM_H
        )

        # Log progress
        log_room_generation(rc, room.type, list(rooms.keys()).index(rc) + 1, len(rooms))

    return rooms


def main():
    """Run the zone generation demo."""
    pygame.init()

    # Settings
    SCREEN_W, SCREEN_H = 960, 540
    seed = 42

    # Create window
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Zone Generation Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    # Load tileset (will use placeholders if assets don't exist)
    assets_root = Path(__file__).parent.parent / "assets" / "tiles"
    tileset = TileSet("lantern", TILE_SIZE, assets_root)
    validate_tiles(tileset)

    # Generate world
    log_generation_start(seed, "demo")
    rooms = create_demo_world(seed)
    log_generation_complete(len(rooms))

    # Print ASCII world map
    print_world(rooms, (0, 0), (2, 2), (3, 3), "demo", "ZONE DEMO WORLD")

    # Build mega tilemap (all rooms stitched together)
    coords = list(rooms.keys())
    minx = min(x for x, _ in coords)
    miny = min(y for _, y in coords)
    maxx = max(x for x, _ in coords)
    maxy = max(y for _, y in coords)

    world_w = (maxx - minx + 1) * ROOM_W
    world_h = (maxy - miny + 1) * ROOM_H

    mega = [[0] * world_w for _ in range(world_h)]

    for (rx, ry), room in rooms.items():
        if room.tilemap is None:
            continue

        ox = (rx - minx) * ROOM_W
        oy = (ry - miny) * ROOM_H

        for y in range(ROOM_H):
            for x in range(ROOM_W):
                mega[oy + y][ox + x] = room.tilemap[y][x]

    # Create minimap
    minimap = Minimap(cell_size=10)

    # Camera and player
    room_px_w = ROOM_W * TILE_SIZE
    room_px_h = ROOM_H * TILE_SIZE

    cam = pygame.Vector2(0, 0)
    player_rect = pygame.Rect(100, 100, 20, 30)
    current_room = (0, 0)

    # Controls
    move_speed = 5.0
    show_minimap = True

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    show_minimap = not show_minimap
                elif event.key == pygame.K_g:
                    # Regenerate with new seed
                    seed += 1
                    log_generation_start(seed, "demo")
                    rooms = create_demo_world(seed)
                    log_generation_complete(len(rooms))

                    # Rebuild mega tilemap
                    for (rx, ry), room in rooms.items():
                        if room.tilemap is None:
                            continue
                        ox = (rx - minx) * ROOM_W
                        oy = (ry - miny) * ROOM_H
                        for y in range(ROOM_H):
                            for x in range(ROOM_W):
                                mega[oy + y][ox + x] = room.tilemap[y][x]

                    player_rect.center = (100, 100)
                    current_room = (0, 0)

        # Movement
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += move_speed

        player_rect.x += dx
        player_rect.y += dy

        # Update current room
        gx = int(player_rect.centerx // room_px_w) + minx
        gy = int(player_rect.centery // room_px_h) + miny
        if (gx, gy) in rooms:
            current_room = (gx, gy)

        # Camera follows player
        cam.x = player_rect.centerx - SCREEN_W // 2
        cam.y = player_rect.centery - SCREEN_H // 2

        # Render
        screen.fill((10, 10, 15))

        # Draw tiles
        draw_tiles(screen, mega, cam, tileset, seed, debug_grid=False)

        # Draw player
        pr = player_rect.copy()
        pr.x -= cam.x
        pr.y -= cam.y
        pygame.draw.rect(screen, (240, 235, 245), pr, border_radius=6)
        pygame.draw.circle(screen, (20, 20, 24), (pr.centerx + 4, pr.centery - 4), 2)

        # Draw minimap
        if show_minimap:
            minimap.draw(screen, rooms, current_room, player_rect,
                        room_px_w, room_px_h, minx, miny)

        # HUD
        info_lines = [
            f"Seed: {seed} | Room: {current_room} | Type: {rooms[current_room].type}",
            "Controls: WASD/Arrows=Move | M=Toggle Minimap | G=Regenerate | Esc=Quit",
        ]

        for i, line in enumerate(info_lines):
            surf = font.render(line, True, (220, 220, 230))
            screen.blit(surf, (10, 10 + i * 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
