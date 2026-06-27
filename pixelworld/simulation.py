from __future__ import annotations

import math
import random

from pixelworld.grid import PixelGrid
from pixelworld.materials import MATERIALS, Material


class PixelSimulator:
    def __init__(self, grid: PixelGrid, seed: int | None = None) -> None:
        self.grid = grid
        self.rng = random.Random(seed)
        self.frame = 0

    def update(self, substeps: int = 1) -> None:
        for _ in range(substeps):
            self.frame += 1
            self._update_once()

    def set_cell(self, x: int, y: int, material: Material | int) -> None:
        if not self.grid.in_bounds(x, y):
            return
        self.set_idx(self.grid.index(x, y), material)

    def set_idx(self, idx: int, material: Material | int) -> None:
        mat = Material(material)
        material_def = MATERIALS[mat]
        life = 0
        if material_def.life_range != (0, 0):
            life = self.rng.randint(*material_def.life_range)
        heat = 255 if mat == Material.FIRE else 0
        self.grid.set_idx(idx, mat, life=life, heat=heat)

    def paint_disc(self, cx: int, cy: int, radius: int, material: Material | int) -> None:
        for idx, _x, _y, _dist_sq in self.grid.iter_disc(cx, cy, radius):
            self.set_idx(idx, material)
            self.grid.moved[idx] = self.frame

    def explode(self, cx: int, cy: int, radius: int) -> None:
        radius_sq = radius * radius
        for idx, _x, _y, dist_sq in self.grid.iter_disc(cx, cy, radius):
            dist = math.sqrt(dist_sq)
            force = 1.0 - dist / max(1, radius)
            mat = Material(self.grid.material[idx])

            if mat == Material.EMPTY:
                if self.rng.random() < force * 0.18:
                    self.set_idx(idx, Material.SMOKE)
                continue

            if mat == Material.STONE and force < 0.56 and self.rng.random() > force:
                continue

            if mat == Material.WATER:
                self.set_idx(idx, Material.SMOKE)
            elif MATERIALS[mat].flammable and self.rng.random() < 0.72:
                self.set_idx(idx, Material.FIRE)
            elif self.rng.random() < 0.18 + force * 0.55:
                self.set_idx(idx, Material.FIRE if self.rng.random() < force * 0.35 else Material.EMPTY)

            self.grid.moved[idx] = self.frame

        for idx, _x, _y, dist_sq in self.grid.iter_disc(cx, cy, radius + 4):
            if dist_sq <= radius_sq:
                continue
            mat = Material(self.grid.material[idx])
            if MATERIALS[mat].flammable and self.rng.random() < 0.25:
                self.set_idx(idx, Material.FIRE)
                self.grid.moved[idx] = self.frame

    def _update_once(self) -> None:
        y_range = range(self.grid.height - 1, -1, -1)

        for y in y_range:
            if (y + self.frame) & 1:
                x_range = range(self.grid.width - 1, -1, -1)
            else:
                x_range = range(self.grid.width)

            for x in x_range:
                idx = self.grid.index(x, y)
                if self.grid.moved[idx] == self.frame:
                    continue

                mat = Material(self.grid.material[idx])
                if mat == Material.SAND:
                    self._update_sand(x, y, idx)
                elif mat == Material.WATER:
                    self._update_water(x, y, idx)
                elif mat == Material.FIRE:
                    self._update_fire(x, y, idx)
                elif mat == Material.SMOKE:
                    self._update_smoke(x, y, idx)
                elif mat == Material.WOOD:
                    self._update_wood(x, y, idx)

    def _can_displace(self, moving: Material, target: Material) -> bool:
        if target == Material.EMPTY:
            return True
        if target in (Material.FIRE, Material.SMOKE) and moving in (Material.SAND, Material.WATER):
            return True
        return MATERIALS[moving].density > MATERIALS[target].density and target != Material.STONE

    def _try_move(self, x: int, y: int, nx: int, ny: int, moving: Material) -> bool:
        if not self.grid.in_bounds(nx, ny):
            return False

        src = self.grid.index(x, y)
        dst = self.grid.index(nx, ny)
        target = Material(self.grid.material[dst])
        if not self._can_displace(moving, target):
            return False

        self.grid.swap_idx(src, dst)
        self.grid.moved[src] = self.frame
        self.grid.moved[dst] = self.frame
        return True

    def _try_move_empty(self, x: int, y: int, nx: int, ny: int) -> bool:
        if not self.grid.in_bounds(nx, ny):
            return False
        dst = self.grid.index(nx, ny)
        if self.grid.material[dst] != int(Material.EMPTY):
            return False
        src = self.grid.index(x, y)
        self.grid.swap_idx(src, dst)
        self.grid.moved[src] = self.frame
        self.grid.moved[dst] = self.frame
        return True

    def _update_sand(self, x: int, y: int, idx: int) -> None:
        if self._try_move(x, y, x, y + 1, Material.SAND):
            return

        dirs = [-1, 1]
        self.rng.shuffle(dirs)
        for dx in dirs:
            if self._try_move(x, y, x + dx, y + 1, Material.SAND):
                return

        self.grid.moved[idx] = self.frame

    def _update_water(self, x: int, y: int, idx: int) -> None:
        if self._try_move(x, y, x, y + 1, Material.WATER):
            return

        dirs = [-1, 1]
        self.rng.shuffle(dirs)
        for dx in dirs:
            if self._try_move(x, y, x + dx, y + 1, Material.WATER):
                return

        for dx in dirs:
            if self._try_water_slide(x, y, dx):
                return

        self.grid.moved[idx] = self.frame

    def _try_water_slide(self, x: int, y: int, dx: int) -> bool:
        src = self.grid.index(x, y)
        target_idx = None

        for step in range(1, 5):
            nx = x + dx * step
            if not self.grid.in_bounds(nx, y):
                break

            idx = self.grid.index(nx, y)
            target = Material(self.grid.material[idx])
            if not self._can_displace(Material.WATER, target):
                break
            target_idx = idx
            if target == Material.EMPTY:
                break

        if target_idx is None:
            return False

        self.grid.swap_idx(src, target_idx)
        self.grid.moved[src] = self.frame
        self.grid.moved[target_idx] = self.frame
        return True

    def _update_fire(self, x: int, y: int, idx: int) -> None:
        self.grid.life[idx] -= 1
        if self.grid.life[idx] <= 0:
            self.set_idx(idx, Material.SMOKE if self.rng.random() < 0.55 else Material.EMPTY)
            self.grid.moved[idx] = self.frame
            return

        for nidx in self._neighbor_indices(x, y):
            neighbor = Material(self.grid.material[nidx])
            if neighbor == Material.WATER:
                self.set_idx(idx, Material.SMOKE)
                self.grid.moved[idx] = self.frame
                return
            if MATERIALS[neighbor].flammable and self.rng.random() < 0.13:
                self.set_idx(nidx, Material.FIRE)
                self.grid.moved[nidx] = self.frame

        dirs = [-1, 0, 1]
        self.rng.shuffle(dirs)
        for dx in dirs:
            if self._try_move_empty(x, y, x + dx, y - 1):
                return

        self.grid.moved[idx] = self.frame

    def _update_smoke(self, x: int, y: int, idx: int) -> None:
        self.grid.life[idx] -= 1
        if self.grid.life[idx] <= 0:
            self.set_idx(idx, Material.EMPTY)
            self.grid.moved[idx] = self.frame
            return

        dirs = [0, -1, 1]
        self.rng.shuffle(dirs)
        for dx in dirs:
            if self._try_move_empty(x, y, x + dx, y - 1):
                return

        if self.rng.random() < 0.35:
            dirs = [-1, 1]
            self.rng.shuffle(dirs)
            for dx in dirs:
                if self._try_move_empty(x, y, x + dx, y):
                    return

        self.grid.moved[idx] = self.frame

    def _update_wood(self, x: int, y: int, idx: int) -> None:
        for nidx in self._neighbor_indices(x, y):
            if self.grid.material[nidx] == int(Material.FIRE) and self.rng.random() < 0.045:
                self.set_idx(idx, Material.FIRE)
                self.grid.moved[idx] = self.frame
                return

    def _neighbor_indices(self, x: int, y: int):
        for ny in range(y - 1, y + 2):
            for nx in range(x - 1, x + 2):
                if nx == x and ny == y:
                    continue
                if self.grid.in_bounds(nx, ny):
                    yield self.grid.index(nx, ny)

