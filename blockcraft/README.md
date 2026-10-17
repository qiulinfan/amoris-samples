# Blockcraft

A voxel sandbox island in the style of the original block game: a 128 x 128 seeded island of
one-metre blocks in an open ocean, with grass, dirt, stone, coal, iron and gold ore, sand, gravel,
snow-capped peaks, oak and birch trees, tall grass, poppies, dandelions and flat blocky clouds.

The textures are original 16 x 16 pixel art drawn by `textures.py`; no game's assets are copied.

## Playing

From the engine's repository root:

```sh
cargo run --release -p amoris-app --bin amoris -- play ../amoris-samples/blockcraft --walk
```

Click to capture the mouse; WASD moves, Shift runs, Space jumps (one block), R respawns, Escape
releases the mouse and Escape again exits.

- Walking uses the engine's native collision camera. Blocks and leaves are solid; tall grass,
  flowers (cut-out) and water (blended) are not, so a player wades down to the seabed. The
  ocean floor continues past the island.
- `scripts/main.ts` drifts the clouds east (`Cloud.speed`) and wraps them every 400 m.
- Blocks cannot be broken or placed yet: the walk camera is presenter state, and scripts neither
  receive pointer input nor change the world's geometry.

## How the world is built

`gen_world.py` writes everything the scene loads:

- `textures/`: one PNG per block face, drawn at 16 x 16 and written upscaled by nearest neighbour
  to 1024 x 1024, the size the engine resamples every texture to, so the pixels stay sharp.
- `world.gltf` and `world.bin`: the terrain meshed per 16 x 16 chunk with every hidden face
  culled, one primitive per texture; plants are two crossed quads; the water and the ocean floor
  are planes reaching 1 km out.
- `clouds/`: six cloud shapes of 12 x 12 x 4 m cells, which the scene's 22 clouds reuse.
- `scene.json`: the camera, placed where it sees farthest across open land, the sun, the
  environment, the world model and the clouds.

Edit the generator (its constants set the seed, size, sea level and cloud height) and run:

```sh
python3 blockcraft/gen_world.py
```
