# Environment Abstraction Spec

Supported environments:
- `open`
- `galaxy`
- `galaxy_skills`

Each environment should implement a unified interface.

Suggested interface:
- `setup(task, prompt, agent)`
- `run()`
- `collect()`
- `cleanup()`

Returned object should include:
- `environment`
- `status`
- `outputs`
- `artifacts`
- `trace`
- `timing`
- `resource_usage`
- `failure_modes`

Purpose:
- `open`: unconstrained baseline
- `galaxy`: constrained scientific workflow environment
- `galaxy_skills`: Galaxy plus explicit procedural support
