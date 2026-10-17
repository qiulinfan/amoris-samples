# amoris-samples guidance

- One top-level folder per game, each a complete Amoris project with its own README. A new game
  gets a new folder; games do not share files.
- The engine lives in a separate checkout, `../amoris`. Run its commands from the engine's root
  with `../amoris-samples/<game>`. Engine gaps a game finds are fixed in the engine repository; game
  code only uses the engine.
- The engine's own `samples/` stay there: its tests, checks and benchmarks read them.
- A generated `scene.json` is committed together with the generator that writes it; regenerate it
  rather than editing it by hand.
- Run output, captures and logs go to the engine's ignored `out/`, never into this repository.
- This repository is public: commit only original or compatibly licensed assets, with their
  license and source next to them.
