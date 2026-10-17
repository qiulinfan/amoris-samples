#!/usr/bin/env python3
"""Generates blockcraft/scene.json: a seeded voxel island of one-metre blocks.

Only blocks with an exposed face become entities. A grass block is a dirt cube with a thin
green cap, so its sides read as dirt. Water and clouds are blended (alpha below 1), which the
walk camera does not collide with. Run: python3 blockcraft/gen_world.py
"""

import json
import math
import random
from pathlib import Path

SEED = 8
SIZE = 72          # blocks along x and z
SEA = 9            # water surface sits at the top of block y = SEA
CLOUD_Y = 60
CAP = 0.125        # grass cap thickness

AIR, STONE, DIRT, GRASS, SAND, SNOW, LOG, LEAVES, COAL, IRON, BEDROCK = range(11)

# Linear RGB base colors.
COLORS = {
    STONE: (0.32, 0.32, 0.33),
    DIRT: (0.30, 0.17, 0.08),
    GRASS: (0.16, 0.42, 0.07),
    SAND: (0.80, 0.70, 0.42),
    SNOW: (0.88, 0.90, 0.94),
    LOG: (0.20, 0.12, 0.05),
    LEAVES: (0.07, 0.26, 0.04),
    COAL: (0.06, 0.06, 0.06),
    IRON: (0.62, 0.44, 0.32),
    BEDROCK: (0.08, 0.08, 0.09),
}
ROUGHNESS = {SNOW: 0.6, SAND: 0.9, STONE: 0.85, IRON: 0.5}


class ValueNoise:
    def __init__(self, rng, cell):
        self.cell = cell
        self.rng = rng
        self.grid = {}

    def corner(self, i, j):
        if (i, j) not in self.grid:
            self.grid[i, j] = self.rng.random()
        return self.grid[i, j]

    def __call__(self, x, z):
        fx, fz = x / self.cell, z / self.cell
        i, j = math.floor(fx), math.floor(fz)
        u, v = fx - i, fz - j
        u, v = u * u * (3 - 2 * u), v * v * (3 - 2 * v)
        a = self.corner(i, j) + (self.corner(i + 1, j) - self.corner(i, j)) * u
        b = self.corner(i, j + 1) + (self.corner(i + 1, j + 1) - self.corner(i, j + 1)) * u
        return a + (b - a) * v


def heightmap(rng):
    octaves = [(ValueNoise(rng, 24), 1.0), (ValueNoise(rng, 11), 0.45), (ValueNoise(rng, 5), 0.18)]
    total = sum(w for _, w in octaves)
    raw = {(x, z): sum(f(x, z) * w for f, w in octaves) / total
           for x in range(SIZE) for z in range(SIZE)}
    lo, hi = min(raw.values()), max(raw.values())
    heights = {}
    for (x, z), r in raw.items():
        n = (r - lo) / (hi - lo)
        # An island: fall off toward the edges.
        dx, dz = (x - SIZE / 2) / (SIZE / 2), (z - SIZE / 2) / (SIZE / 2)
        falloff = max(0.0, 1.0 - (dx * dx + dz * dz) ** 1.4)
        h = SEA + 7 + (n - 0.45) * 36 - (1 - falloff) * 16
        heights[x, z] = min(40, max(1, int(h)))
    return heights


def build(rng):
    heights = heightmap(rng)
    blocks = {}
    for (x, z), h in heights.items():
        blocks[x, 0, z] = BEDROCK
        for y in range(1, h + 1):
            depth = h - y
            if depth == 0:
                kind = SAND if h <= SEA + 1 else SNOW if h >= 24 else GRASS
            elif depth < 3 and h < 22:
                kind = SAND if h <= SEA + 1 else DIRT
            else:
                r = rng.random()
                kind = COAL if r < 0.05 else IRON if r < 0.075 else STONE
            blocks[x, y, z] = kind
    trees = 0
    for (x, z), h in sorted(heights.items()):
        if not (3 <= x < SIZE - 3 and 3 <= z < SIZE - 3):
            continue
        if blocks.get((x, h, z)) != GRASS or rng.random() > 0.04:
            continue
        if any(blocks.get((x + dx, y, z + dz)) in (LOG, LEAVES)
               for dx in range(-3, 4) for dz in range(-3, 4) for y in range(h, h + 9)):
            continue
        trunk = rng.randint(4, 6)
        top = h + trunk
        for dy in range(-2, 2):
            radius = 2 if dy < 0 else 1
            for dx in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    corner = abs(dx) == radius and abs(dz) == radius
                    if corner and (dy == 1 or rng.random() < 0.5):
                        continue
                    blocks.setdefault((x + dx, top + dy, z + dz), LEAVES)
        blocks[x, top + 1, z] = LEAVES
        for y in range(h + 1, top + 1):
            blocks[x, y, z] = LOG
        trees += 1
    return heights, blocks, trees


def exposed(blocks, x, y, z):
    for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        if (x + dx, y + dy, z + dz) not in blocks and y + dy >= 0:
            return True
    return False


def round3(v):
    return [round(c, 3) for c in v]


def model(kind, rng, scale=(1, 1, 1)):
    shade = 1 + rng.uniform(-0.07, 0.07)
    color = [min(1.0, c * shade) for c in COLORS[kind]] + [1]
    m = {"mesh": "cube", "color": round3(color), "roughness": ROUGHNESS.get(kind, 0.95)}
    if scale != (1, 1, 1):
        m["scale"] = list(scale)
    return m


def entities(heights, blocks, rng):
    half = SIZE / 2
    out = []
    for (x, y, z), kind in sorted(blocks.items()):
        if not exposed(blocks, x, y, z):
            continue
        px, pz = x - half + 0.5, z - half + 0.5
        if kind == GRASS:
            out.append({"components": {
                "Transform": {"position": round3([px, y + (1 - CAP) / 2, pz])},
                "Model": model(DIRT, rng, (1, 1 - CAP, 1)),
            }})
            out.append({"components": {
                "Transform": {"position": round3([px, y + 1 - CAP / 2, pz])},
                "Model": model(GRASS, rng, (1, CAP, 1)),
            }})
        else:
            out.append({"components": {
                "Transform": {"position": round3([px, y + 0.5, pz])},
                "Model": model(kind, rng),
            }})
    return out


def clouds(rng):
    out = []
    for i in range(14):
        x = rng.uniform(-SIZE * 0.8, SIZE * 0.8)
        z = rng.uniform(-SIZE * 0.8, SIZE * 0.8)
        out.append({"name": f"Cloud{i + 1}", "components": {
            "Transform": {"position": round3([x, CLOUD_Y + rng.uniform(-1, 1), z])},
            "Model": {"mesh": "cube", "scale": [rng.randint(6, 16), 1.5, rng.randint(5, 12)],
                      "color": [1, 1, 1, 0.85], "roughness": 1, "cast_shadows": False},
            "Cloud": {"speed": round(rng.uniform(0.6, 1.4), 3)},
        }})
    return out


def spawn(heights, blocks):
    """A low open grass column near the shore, 16 to 24 blocks out, facing the centre."""
    c = SIZE / 2
    ring = [(x, z) for (x, z), h in heights.items()
            if 16 <= math.hypot(x - c, z - c) <= 24 and blocks[x, h, z] == GRASS
            and not any((x, y, z) in blocks for y in range(h + 1, h + 5))]
    x, z = min(ring, key=lambda p: (heights[p], p))
    yaw = math.atan2(-(c - x), -(c - z))  # the camera looks along -z
    position = [x - c + 0.5, heights[x, z] + 1 + 1.65, z - c + 0.5]
    return position, [0, math.sin(yaw / 2), 0, math.cos(yaw / 2)]


def main():
    rng = random.Random(SEED)
    heights, blocks, trees = build(rng)
    world = entities(heights, blocks, rng)
    position, rotation = spawn(heights, blocks)
    sun = [-0.42, -0.30, -0.11, 0.85]
    norm = math.sqrt(sum(c * c for c in sun))
    scene = {"format": "amoris-scene", "version": 1, "entities": [
        {"name": "Camera", "components": {
            "Transform": {"position": round3(position), "rotation": round3(rotation)},
            "Camera": {"fov_deg": 75}}},
        {"name": "Sun", "components": {
            "Transform": {"rotation": round3([c / norm for c in sun])},
            "Light": {"kind": "directional", "intensity": 10, "shadows": True, "color": [1, 0.95, 0.86]}}},
        {"name": "Environment", "components": {"Environment": {
            "ambient": 0.9, "exposure_ev": 0.6, "bloom": 0.04,
            "fog_density": 0.004, "fog_color": [0.62, 0.74, 0.9]}}},
        {"name": "Water", "components": {
            "Transform": {"position": [0, SEA + 0.85, 0]},
            "Model": {"mesh": "plane", "scale": [SIZE * 3, 1, SIZE * 3],
                      "color": [0.02, 0.1, 0.35, 0.82], "roughness": 0.08, "cast_shadows": False}}},
        {"name": "Title", "components": {"UiText": {
            "text": "Blockcraft", "anchor": "top_left", "offset": [24, 24], "size": 24,
            "color": [1, 1, 1, 1]}}},
        {"name": "Controls", "components": {"UiText": {
            "text": "Click to capture  |  WASD move  |  Shift run  |  Space jump  |  R respawn",
            "anchor": "bottom_left", "offset": [24, 52], "size": 15, "color": [1, 1, 1, 0.9]}}},
        *clouds(rng),
        *world,
    ]}
    path = Path(__file__).with_name("scene.json")
    path.write_text(json.dumps(scene, separators=(",", ":")) + "\n")
    print(f"{len(blocks)} blocks, {len(world)} block entities, {trees} trees -> {path}")


if __name__ == "__main__":
    main()
