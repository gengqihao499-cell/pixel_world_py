# PixelWorld Engine

PixelWorld Engine is a small 2D pixel-physics sandbox built as a stepping stone
toward a C++/SFML Noita-like engine. The first version is intentionally written
in Python + pygame so the simulation rules can be explored quickly before being
ported to a faster C++ runtime.

## Stage Plan

1. Python + pygame prototype
   - Sand, water, fire, smoke, explosion.
   - Mouse painting and a tiny player entity.
   - Simple material table and per-pixel simulation loop.

2. C++ + SDL2/Raylib/SFML rewrite
   - Move the same module boundaries into C++.
   - Replace Python lists with contiguous typed buffers.
   - Keep the same material IDs and rule concepts.

3. Chunk system
   - Split the world into fixed-size chunks.
   - Track active/dirty chunks.
   - Update only chunks touched by simulation, entities, explosions, or edits.

4. Expanded material system
   - sand / water / fire / smoke / wood / acid.
   - Reaction rules, temperature, lifetimes, density, and state flags.

5. Game layer
   - Player, wand/spell system, enemies, damage, procedural generation.

## Run Stage 1

```powershell
python -m pip install -r requirements.txt
python main.py
```

Controls:

- Left mouse: paint selected material.
- Right mouse: erase.
- Middle mouse or `X`: explode at cursor.
- `1`: sand
- `2`: water
- `3`: fire
- `4`: wood
- `5`: stone
- `6`: smoke
- `[` / `]`: brush size
- `C`: clear world
- `R`: reset cave test scene
- `A` / `D`: move entity
- `Space`: jump

## Smoke Test

The simulation smoke test does not require pygame:

```powershell
python tests/smoke_simulation.py
```

