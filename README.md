# Amoris samples

Small games built with the [Amoris](https://github.com/qiulinfan/amoris) engine, one folder per
game. Each is a complete Amoris project: `project.toml`, `scene.json` and TypeScript scripts under
`scripts/`.

| Game | What it is |
|---|---|
| [blockcraft](blockcraft/README.md) | A voxel sandbox island in pixel-art blocks, to walk and climb |

## Running

The games run on an Amoris checkout beside this repository (`~/Desktop/amoris` for
`~/Desktop/amoris-samples`). From the engine's root:

```sh
cargo run --release -p amoris-app --bin amoris -- play ../amoris-samples/<game>
```

Each game's README gives its own flags and controls. `amoris check ../amoris-samples/<game> --only
types` type-checks a game's scripts; how scripts are written is the engine's `docs/sdk.md`.
