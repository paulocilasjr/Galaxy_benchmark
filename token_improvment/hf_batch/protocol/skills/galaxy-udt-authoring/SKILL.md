---
name: galaxy-udt-authoring
description: Use only after targeted live discovery and inspection found no faithful ordinary Galaxy tool, when the task explicitly requires a fresh UDT, or when debugging an already-selected UDT route. Covers GalaxyUserTool representation, command rendering, public containers, resource requirements, preflight, and output validation. Read the bundled reference only for concrete YAML, BioBlend fallback, resource fields, or failure diagnosis.
---

# Galaxy UDT Authoring

Create a fresh UDT for the current task. Glue code may adapt Galaxy inputs and
outputs, but the scientific computation should call the selected published
package, binary, model, or named library function.

## Entry Condition

Do not choose this route from memory or convenience. Complete the policy's
targeted live ordinary-tool search first and inspect any plausible candidate,
unless the task explicitly requires a UDT.

## Representation

Use a `GalaxyUserTool` representation with:

- unique `id`, `name`, `version`, and a pinned BioContainer;
- typed `inputs` and `outputs`;
- `shell_command` paths rendered as `$(inputs.<name>.path)`;
- `from_work_dir` for each produced output; and
- resource requirements only when non-default CPU, RAM, temporary space, or GPU
  is needed.

Declare only outputs required by the analysis. Add diagnostics only to investigate
a concrete command, dependency, resource, or model-loading failure.

## Command Rendering

- Prefer a short command that invokes an installed binary or module.
- Do not assume Bash. Use POSIX `set -eu`; avoid pipelines that can hide an
  upstream failure.
- Read `GALAXY_SLOTS` when the selected software supports threads.
- Avoid nested quoting in `python -c`. For generated scripts, use one tested
  heredoc or base64-argument pattern.
- Heredoc terminators must begin at column 1 without trailing whitespace.
- If no rendered `command_line` exists, fix representation or quoting before
  changing scientific code.

## Containers And Resources

For usegalaxy.org, use a pinned image under `quay.io/biocontainers`. These
images are available through Galaxy's shared container cache; arbitrary public
images may require slow or unreliable compute-node pull and conversion. The
UDT `container` value must be the bare tagged image reference, such as
`quay.io/biocontainers/<image>:<tag>`. Never prefix it with `docker://`, and do
not put a digest in this field. Galaxy adds the transport internally and the
UDT validator expects a tag.

Choose package requirements from the scientific method first. Then perform one
bounded live BioContainers lookup for the likely package repositories and
print only the few relevant tags. Do not browse unrelated registries or dump
complete tag lists. If no single BioContainer contains every dependency,
prefer one of these while preserving the requested method and data semantics:

1. use the exact primary-package BioContainer and install one small, pinned,
   compatible secondary package into a job-local target; or
2. split the computation across exact BioContainer UDTs and pass intermediate
   datasets through Galaxy.

Do not install a large environment during the job. Verify the installed package
version and imports before running the analysis. Do not replace a named method,
database, universe, or output definition merely to fit an available image.

Galaxy's UDT build step validates and registers the tool definition; it does
not build or modify the container image. Any package installation in
`shell_command` happens later as the unprivileged Galaxy job. Install only into
the writable job directory, not the container filesystem, and do not assume
root access or system-package installation.

Resource routing does not add software to an image. Request realistic resources
on the first submission and ensure a GPU request uses a GPU-capable image.

## Preflight And Validation

Before submission, validate representation syntax, names, BioContainer tag,
fragile command rendering, and declared outputs. A tiny synthetic preflight may
test imports or quoting but must not compute the task answer.

Before accepting a result, inspect the actual output dataset and verify its
method, parameters, row/key/sample scope, and expected structure. Repair the
representation, command, container, or resources when those checks fail; do not
change the scientific method solely to make the UDT execute.

Read [references/templates.md](references/templates.md) only when a concrete
template, direct BioBlend call, resource block, or failure pattern is needed.
