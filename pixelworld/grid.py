from __future__ import annotations

from pixelworld.materials import Material


class PixelGrid:
    """Dense, row-major pixel grid.

    This intentionally mirrors the memory model we will want in C++ later:
    separate arrays for material, life, heat, and per-frame movement stamps.
    """

    __slots__ = ("width", "height", "size", "material", "life", "heat", "moved")

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.size = width * height
        self.material = [int(Material.EMPTY)] * self.size
        self.life = [0] * self.size
        self.heat = [0] * self.size
        self.moved = [0] * self.size

    def clear(self) -> None:
        self.material[:] = [int(Material.EMPTY)] * self.size
        self.life[:] = [0] * self.size
        self.heat[:] = [0] * self.size
        self.moved[:] = [0] * self.size

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def index(self, x: int, y: int) -> int:
        return y * self.width + x

    def get(self, x: int, y: int) -> int:
        if not self.in_bounds(x, y):
            return int(Material.STONE)
        return self.material[self.index(x, y)]

    def set_idx(self, idx: int, material: Material | int, life: int = 0, heat: int = 0) -> None:
        self.material[idx] = int(material)
        self.life[idx] = life
        self.heat[idx] = heat

    def set_cell(self, x: int, y: int, material: Material | int, life: int = 0, heat: int = 0) -> None:
        if self.in_bounds(x, y):
            self.set_idx(self.index(x, y), material, life, heat)

    def swap_idx(self, a: int, b: int) -> None:
        self.material[a], self.material[b] = self.material[b], self.material[a]
        self.life[a], self.life[b] = self.life[b], self.life[a]
        self.heat[a], self.heat[b] = self.heat[b], self.heat[a]

    def iter_disc(self, cx: int, cy: int, radius: int):
        radius_sq = radius * radius
        y0 = max(0, cy - radius)
        y1 = min(self.height - 1, cy + radius)
        x0 = max(0, cx - radius)
        x1 = min(self.width - 1, cx + radius)

        for y in range(y0, y1 + 1):
            dy = y - cy
            for x in range(x0, x1 + 1):
                dx = x - cx
                dist_sq = dx * dx + dy * dy
                if dist_sq <= radius_sq:
                    yield self.index(x, y), x, y, dist_sq

