from __future__ import annotations

import pygame

from pixelworld.grid import PixelGrid
from pixelworld.materials import MATERIALS, Material


class PygameRenderer:
    def __init__(self, screen: pygame.Surface, scale: int) -> None:
        self.screen = screen
        self.scale = scale
        self.buffer = bytearray()

    def draw(self, grid: PixelGrid, *, entities: list[object], selected: Material, brush_radius: int) -> None:
        needed = grid.size * 3
        if len(self.buffer) != needed:
            self.buffer = bytearray(needed)

        out = self.buffer
        for idx, mat_id in enumerate(grid.material):
            color = self._cell_color(Material(mat_id), grid.life[idx], idx)
            offset = idx * 3
            out[offset] = color[0]
            out[offset + 1] = color[1]
            out[offset + 2] = color[2]

        surface = pygame.image.frombuffer(bytes(out), (grid.width, grid.height), "RGB")
        scaled = pygame.transform.scale(
            surface,
            (grid.width * self.scale, grid.height * self.scale),
        )
        self.screen.blit(scaled, (0, 0))

        for entity in entities:
            self._draw_entity(entity)

        self._draw_brush_preview(selected, brush_radius)
        pygame.display.flip()

    def _cell_color(self, material: Material, life: int, idx: int) -> tuple[int, int, int]:
        if material == Material.FIRE:
            flicker = (idx * 17 + life * 9) & 31
            return (255, 80 + flicker, 16)
        if material == Material.SMOKE:
            shade = max(28, min(96, 38 + life // 3))
            return (shade, shade, shade + 2)
        return MATERIALS[material].color

    def _draw_entity(self, entity: object) -> None:
        x = int(getattr(entity, "x") * self.scale)
        y = int(getattr(entity, "y") * self.scale)
        radius = max(2, int(getattr(entity, "radius") * self.scale))
        color = getattr(entity, "color", (120, 230, 220))
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, (16, 24, 28), (x, y), radius, width=1)

    def _draw_brush_preview(self, selected: Material, brush_radius: int) -> None:
        pos = pygame.mouse.get_pos()
        color = MATERIALS[selected].color
        radius = max(2, brush_radius * self.scale)
        pygame.draw.circle(self.screen, color, pos, radius, width=1)

