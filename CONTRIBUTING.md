# Contributing

Keep the benchmark platform small, typed, and modular.

## Ground Rules

- Preserve clean architecture boundaries.
- Keep canonical JSON and code in `snake_case`.
- Treat `benchmark/tasks/legacy/raw/` and `benchmark/ground_truth/legacy/raw/` as migration inputs, not primary definitions.
- Write benchmark execution artifacts only under `runs/`.
- Do not add provider-specific or Galaxy-specific logic to the domain layer.

## Development Workflow

- Add or update tests with every behavioral change.
- Prefer extending ports and use cases over adding ad hoc scripts.
- Keep prompt generation deterministic unless nondeterminism is the explicit experiment.
- Preserve immutable run artifacts and append-only trace behavior.
