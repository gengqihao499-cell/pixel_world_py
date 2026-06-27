from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pixelworld.grid import PixelGrid
from pixelworld.materials import Material
from pixelworld.simulation import PixelSimulator


def assert_sand_falls() -> None:
    grid = PixelGrid(16, 16)
    sim = PixelSimulator(grid, seed=1)
    sim.set_cell(8, 1, Material.SAND)

    for _ in range(8):
        sim.update()

    assert grid.get(8, 9) == int(Material.SAND)


def assert_water_spreads() -> None:
    grid = PixelGrid(24, 12)
    sim = PixelSimulator(grid, seed=2)

    for x in range(grid.width):
        sim.set_cell(x, 9, Material.STONE)

    sim.set_cell(12, 8, Material.WATER)
    for _ in range(16):
        sim.update()

    water_count = 0
    for x in range(8, 17):
        water_count += grid.get(x, 8) == int(Material.WATER)

    assert water_count == 1
    assert all(grid.get(x, 9) == int(Material.STONE) for x in range(grid.width))
    assert all(grid.get(x, 10) != int(Material.WATER) for x in range(grid.width))


def assert_explosion_carves_stone() -> None:
    grid = PixelGrid(32, 24)
    sim = PixelSimulator(grid, seed=3)

    sim.paint_disc(16, 12, 8, Material.STONE)
    before = sum(1 for value in grid.material if value == int(Material.STONE))
    sim.explode(16, 12, 6)
    after = sum(1 for value in grid.material if value == int(Material.STONE))

    assert after < before


if __name__ == "__main__":
    assert_sand_falls()
    assert_water_spreads()
    assert_explosion_carves_stone()
    print("simulation smoke tests passed")
