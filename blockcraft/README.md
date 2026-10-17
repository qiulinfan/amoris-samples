# Blockcraft

A Minecraft-like voxel island. `gen_world.py` writes `scene.json` from a seeded heightmap (seed,
size and sea level are its constants): bedrock, stone with coal and iron, dirt, grass, sand, snow,
oak trees, a water plane and drifting clouds. Only blocks with an exposed face become entities
(about 12,200 cubes, 36 trees); a grass block is a dirt cube with a thin green cap.

## Playing

From the engine's repository root:

```sh
cargo run --release -p amoris-app --bin amoris -- play ../amoris-samples/blockcraft --walk
```

Click to capture the mouse; WASD moves, Shift runs, Space jumps (one block), R respawns, Escape
releases the mouse and Escape again exits.

- Walking uses the engine's native collision camera: blocks are solid; water and clouds are
  blended Models (alpha below 1), which it does not collide with, so a player wades down to the
  seabed. Past the island's 72-block square there is no floor, and the walk camera respawns a
  player who falls below -30 m.
- `scripts/main.ts` drifts the clouds east (`Cloud.speed`) and wraps them at the island's edge.
- Blocks cannot be broken or placed yet: the walk camera is presenter state, and scripts neither
  receive pointer input nor spawn `Model` entities.

## Changing the world

Edit `gen_world.py` and regenerate `scene.json`:

```sh
python3 blockcraft/gen_world.py
```
