from __future__ import annotations

import sys

try:
    import pygame
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pygame is not installed. Run: python -m pip install -r requirements.txt"
    ) from exc

from pixelworld.config import SCREEN_SCALE, WORLD_HEIGHT, WORLD_WIDTH
from pixelworld.entities import Player
from pixelworld.grid import PixelGrid
from pixelworld.materials import MATERIALS, Material
from pixelworld.render import PygameRenderer
from pixelworld.simulation import PixelSimulator


KEY_TO_MATERIAL = {
    pygame.K_1: Material.SAND,
    pygame.K_2: Material.WATER,
    pygame.K_3: Material.FIRE,
    pygame.K_4: Material.WOOD,
    pygame.K_5: Material.STONE,
    pygame.K_6: Material.SMOKE,
}


def screen_to_cell(pos: tuple[int, int]) -> tuple[int, int]:
    return pos[0] // SCREEN_SCALE, pos[1] // SCREEN_SCALE


def build_demo_scene(sim: PixelSimulator) -> None:
    grid = sim.grid
    grid.clear()

    for x in range(grid.width):
        sim.set_cell(x, grid.height - 1, Material.STONE)
        sim.set_cell(x, grid.height - 2, Material.STONE)

    for x in range(20, grid.width - 20):
        if x % 7 not in (0, 1):
            sim.set_cell(x, grid.height - 18, Material.STONE)

    sim.paint_disc(42, grid.height - 28, 11, Material.WOOD)
    sim.paint_disc(86, 18, 9, Material.WATER)
    sim.paint_disc(142, 20, 10, Material.SAND)


def update_window_title(selected: Material, brush_radius: int) -> None:
    material_name = MATERIALS[selected].name
    pygame.display.set_caption(
        f"PixelWorld Engine Stage 1 | {material_name} | brush {brush_radius}"
    )


def main() -> int:
    pygame.init()

    screen = pygame.display.set_mode(
        (WORLD_WIDTH * SCREEN_SCALE, WORLD_HEIGHT * SCREEN_SCALE)
    )
    clock = pygame.time.Clock()

    grid = PixelGrid(WORLD_WIDTH, WORLD_HEIGHT)
    sim = PixelSimulator(grid)
    renderer = PygameRenderer(screen, SCREEN_SCALE)
    player = Player(x=36.0, y=20.0)

    selected = Material.SAND
    brush_radius = 4
    build_demo_scene(sim)
    update_window_title(selected, brush_radius)

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 1.0 / 30.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in KEY_TO_MATERIAL:
                    selected = KEY_TO_MATERIAL[event.key]
                    update_window_title(selected, brush_radius)
                elif event.key == pygame.K_LEFTBRACKET:
                    brush_radius = max(1, brush_radius - 1)
                    update_window_title(selected, brush_radius)
                elif event.key == pygame.K_RIGHTBRACKET:
                    brush_radius = min(18, brush_radius + 1)
                    update_window_title(selected, brush_radius)
                elif event.key == pygame.K_c:
                    grid.clear()
                elif event.key == pygame.K_r:
                    build_demo_scene(sim)
                    player.x, player.y = 36.0, 20.0
                    player.vx, player.vy = 0.0, 0.0
                elif event.key == pygame.K_x:
                    sim.explode(*screen_to_cell(pygame.mouse.get_pos()), radius=16)

        mouse_buttons = pygame.mouse.get_pressed(3)
        mouse_cell = screen_to_cell(pygame.mouse.get_pos())
        if mouse_buttons[0]:
            sim.paint_disc(*mouse_cell, brush_radius, selected)
        if mouse_buttons[1]:
            sim.explode(*mouse_cell, radius=max(6, brush_radius * 3))
        if mouse_buttons[2]:
            sim.paint_disc(*mouse_cell, brush_radius, Material.EMPTY)

        keys = pygame.key.get_pressed()
        player.update(grid, dt, left=keys[pygame.K_a], right=keys[pygame.K_d], jump=keys[pygame.K_SPACE])

        sim.update()
        renderer.draw(grid, entities=[player], selected=selected, brush_radius=brush_radius)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())

