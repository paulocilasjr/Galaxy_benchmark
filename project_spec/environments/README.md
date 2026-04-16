# Environment Abstraction Spec

Supported environment identifiers:

- `open`
- `galaxy`
- `galaxy_skills`

Interpretation:

- `open` is the standalone BioAgent-style baseline
- `galaxy` is the primary Galaxy Workbench environment
- `galaxy_skills` is an optional procedural-support diagnostic environment

Each environment should implement a unified interface:

- `setup(task, prompt, agent)`
- `run()`
- `collect()`
- `cleanup()`

Required returned data:

- environment id
- status
- outputs
- artifacts
- trace manifest
- timing
- resource usage
- failure modes
- execution context

Galaxy-capable environments should preserve Galaxy-specific identifiers and trace evidence.
