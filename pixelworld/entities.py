from __future__ import annotations

from dataclasses import dataclass

from pixelworld.grid import PixelGrid
from pixelworld.materials import blocks_entity


@dataclass(slots=True)
class Player:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 3.2
    color: tuple[int, int, int] = (120, 230, 220)
    on_ground: bool = False

    def update(self, grid: PixelGrid, dt: float, *, left: bool, right: bool, jump: bool) -> None:
        acceleration = 120.0
        gravity = 85.0
        max_speed = 42.0

        if left:
            self.vx -= acceleration * dt
        if right:
            self.vx += acceleration * dt
        if not left and not right:
            self.vx *= max(0.0, 1.0 - 12.0 * dt)

        self.vx = max(-max_speed, min(max_speed, self.vx))

        if jump and self.on_ground:
            self.vy = -48.0
            self.on_ground = False

        self.vy += gravity * dt
        self.vy = min(self.vy, 72.0)

        self._move_axis(grid, self.vx * dt, 0.0)
        self._move_axis(grid, 0.0, self.vy * dt)

    def _move_axis(self, grid: PixelGrid, dx: float, dy: float) -> None:
        if dx == 0.0 and dy == 0.0:
            return

        steps = max(1, int(max(abs(dx), abs(dy)) / 0.35))
        sx = dx / steps
        sy = dy / steps

        for _ in range(steps):
            nx = self.x + sx
            ny = self.y + sy
            if self._collides(grid, nx, ny):
                if dx != 0.0:
                    self.vx = 0.0
                if dy > 0.0:
                    self.on_ground = True
                if dy != 0.0:
                    self.vy = 0.0
                return

            self.x = nx
            self.y = ny
            if dy != 0.0:
                self.on_ground = False

    def _collides(self, grid: PixelGrid, x: float, y: float) -> bool:
        r = self.radius
        probes = (
            (x - r, y),
            (x + r, y),
            (x, y - r),
            (x, y + r),
            (x - r * 0.72, y + r * 0.72),
            (x + r * 0.72, y + r * 0.72),
        )

        for px, py in probes:
            ix = int(px)
            iy = int(py)
            if ix < 0 or ix >= grid.width or iy < 0 or iy >= grid.height:
                return True
            if blocks_entity(grid.get(ix, iy)):
                return True
        return False

