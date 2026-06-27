from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Material(IntEnum):
    EMPTY = 0
    SAND = 1
    WATER = 2
    FIRE = 3
    SMOKE = 4
    STONE = 5
    WOOD = 6


@dataclass(frozen=True, slots=True)
class MaterialDef:
    name: str
    color: tuple[int, int, int]
    density: int
    state: str
    flammable: bool = False
    blocks_entity: bool = False
    life_range: tuple[int, int] = (0, 0)


MATERIALS: dict[Material, MaterialDef] = {
    Material.EMPTY: MaterialDef("empty", (8, 9, 12), density=-100, state="empty"),
    Material.SAND: MaterialDef("sand", (209, 178, 92), density=6, state="powder", blocks_entity=True),
    Material.WATER: MaterialDef("water", (56, 112, 214), density=2, state="liquid"),
    Material.FIRE: MaterialDef("fire", (255, 105, 24), density=-10, state="energy", life_range=(18, 40)),
    Material.SMOKE: MaterialDef("smoke", (86, 88, 92), density=-4, state="gas", life_range=(70, 150)),
    Material.STONE: MaterialDef("stone", (96, 96, 104), density=100, state="solid", blocks_entity=True),
    Material.WOOD: MaterialDef("wood", (122, 79, 38), density=30, state="solid", flammable=True, blocks_entity=True),
}


def blocks_entity(material_id: int) -> bool:
    return MATERIALS[Material(material_id)].blocks_entity

