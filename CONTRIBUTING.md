# Contributing

Keep the benchmark platform small, typed, and modular.

## Ground Rules

- Preserve clean architecture boundaries.
- Keep canonical JSON and code in `snake_case`.
- Keep checked-in benchmark content in the flat canonical paths under `benchmark/tasks/` and `benchmark/ground_truth/`.
- Write benchmark execution artifacts only under `runs/`.
- Do not add provider-specific or Galaxy-specific logic to the domain layer.

## Development Workflow

- Add or update tests with every behavioral change.
- Prefer extending ports and use cases over adding ad hoc scripts.
- Keep prompt generation deterministic unless nondeterminism is the explicit experiment.
- Preserve immutable run artifacts and append-only trace behavior.
