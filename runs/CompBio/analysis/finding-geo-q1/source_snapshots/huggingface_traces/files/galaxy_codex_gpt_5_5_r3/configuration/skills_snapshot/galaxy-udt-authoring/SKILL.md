---
name: galaxy-udt-authoring
description: Use when implementing or debugging a fresh Galaxy UDT. Covers GalaxyUserTool representation, input and output binding, command rendering, container discovery and selection, resources, optional runtime probes, and execution failures. Read the bundled implementation reference for concrete templates and failure diagnosis.
---

# Galaxy UDT Authoring

Use this skill for UDT execution mechanics. It does not prescribe what a UDT
should compute or how its outputs should be interpreted.

## Workflow

1. Map the program or command to its Galaxy inputs, output files, runtime, and
   resource needs.
2. Find and verify a live pinned runtime that contains the required
   implementation.
3. Author a clear `GalaxyUserTool` representation for the intended program.
   Combine stages only when no intermediate result can change, reject, or
   invalidate a downstream stage. Otherwise run the diagnostic or prerequisite
   first, or make the command stop before downstream work when that check fails.
4. Check representation syntax, command rendering, imports, bindings,
   resources, and output paths before submission.
5. After execution, verify mechanically that the expected inputs were bound and
   the declared files were produced and are readable.
6. Repair representation, command, dependency, container, resource, or output
   failures at the layer where they occur.

## Representation

Use a `GalaxyUserTool` representation with:

- unique `id`, `name`, and `version` values;
- a pinned container tag;
- at least one typed input and one or more typed outputs;
- input paths rendered as `$(inputs.<name>.path)`;
- `from_work_dir` for every produced output; and
- resource requirements only when non-default CPU or RAM is needed.

Declare each file the command is expected to produce and bind it with the
corresponding `from_work_dir` path.

The current UDT execution interface requires a non-empty `inputs` list. For a
runtime-only probe, bind an existing small history dataset as an otherwise
unused input.

## Command Rendering

- Invoke the installed binary or module directly when practical.
- Do not assume Bash. Use POSIX `set -eu`, and avoid pipelines that can hide an
  upstream failure.
- Read `GALAXY_SLOTS` when the selected software supports threads.
- Avoid nested quoting in `python -c`. For a nontrivial generated script, use
  the staged-script pattern in
  [references/templates.md](references/templates.md) and bind it with
  `workspace_inputs` in `run_galaxy_udt_and_wait`.
- Use a tested heredoc or base64-argument pattern only for short glue code or
  when staging is unavailable. A heredoc terminator must begin at column 1 and
  have no trailing whitespace.
- If Galaxy creates no rendered `command_line`, fix the representation or
  template syntax before changing command logic.

## Container Selection And Resources

Resolve and verify the complete container tag before authoring or submitting
the UDT. For a single package, use a current BioContainers or Quay catalog or
registry interface. Verify the full active tag, including its build suffix and
worker architecture; do not infer a tag from the package version.

For an exact combination of primary packages, search a current official Galaxy
or BioContainers catalog. The combinations catalog is also available at:

```text
https://raw.githubusercontent.com/BioContainers/multi-package-containers/master/combinations/hash.tsv
```

Verify the required package tuple, versions, exact `mulled-v2-*` image, active
tag, and architecture. Do not calculate or guess a container hash from an
approximate package set.

The UDT `container` value must use the bare `registry/repository:tag` form. For
example:

```text
correct: quay.io/biocontainers/samtools:<verified-build-tag>
correct: docker.io/tensorflow/tensorflow:2.5.1
wrong:   tensorflow/tensorflow:2.5.1
wrong:   docker://quay.io/biocontainers/samtools:<verified-build-tag>
wrong:   quay.io/biocontainers/samtools:<verified-build-tag>@sha256:<digest>
```

"Bare" means that the value has neither a transport prefix such as `docker://`
nor a digest suffix, and it still includes the registry host. Galaxy adds the
transport, and the execution MCP records the registry digest resolved from the
tag at submission. Confirm that a non-BioContainers tag actually exists before
using it.

Use this runtime order:

1. a verified pinned BioContainer for the required package or exact package
   combination;
2. a tested pinned project image that contains the required runtime; or
3. a compatible BioContainer plus one small pinned job-local package whose
   runtime dependencies are already present.

The following pinned project images are available when their contents match the
required runtime:

- `quay.io/chiujunhao24/udt:borzoi-pytorch-0.5.1-torch2.2.2-cpu`
- `quay.io/chiujunhao24/udt:tensorflow-bio-2.15.1-cpu`
- `quay.io/chiujunhao24/udt:caduceus-cpu-torch2.2.0-mamba1.2.0post1-r2`
- `quay.io/chiujunhao24/udt:rds-sparse-r4.5.3-matrix1.7.5-r1` ([RDS/S4 example](references/examples.md#rds-and-s4-inspection))
- `quay.io/chiujunhao24/udt:sequence-toolbox-python3.11-hts1.24-bedtools2.31.1-r1`
- `quay.io/chiujunhao24/udt:donor-deconvolution-cellsnp1.2.3-vireo0.5.9-samtools1.24-cpu`
- `quay.io/chiujunhao24/udt:hic-matrix-hicstraw1.3.1-cooler0.10.4-r1`
- `quay.io/chiujunhao24/udt:encode-atac-2.2.3-official`

For one small pinned package whose runtime dependencies already exist, install
into the writable job directory and expose it explicitly. Never use
`pip --user` in a Galaxy job: the job may have a non-writable home, disable the
Python user site, or omit its package and executable directories from
`PYTHONPATH` and `PATH`.

```sh
set -eu
python -m pip install --no-deps --target "$PWD/.deps" 'package==1.2.3'
PYTHONPATH="$PWD/.deps${PYTHONPATH:+:$PYTHONPATH}" python -c \
  'import package; assert package.__version__ == "1.2.3"'
PYTHONPATH="$PWD/.deps${PYTHONPATH:+:$PYTHONPATH}" python analysis.py
```

Do not assemble a large environment in the job or use package installation to
repair an incompatible base runtime. Galaxy's UDT registration step does not
build or modify the container image; commands and any small installation run
later in the unprivileged job.

Request realistic CPU and RAM on the first submission. Resource routing changes
compute allocation, not installed software. Extra cores help only when the
selected program uses them.

Before specifying RAM, read [Resource Fields](references/templates.md#resource-fields):
RAM values are in MiB, so 8 GiB is `ram_min: 8192`, not `8`.

Before authoring or debugging a UDT, read the relevant sections of
[references/templates.md](references/templates.md). Start with the minimal or
staged-script representation, and consult the execution-failure table when a
job fails.

## Before And After Submission

Before submission, check:

- representation syntax and unique names;
- every input reference and output `from_work_dir` path;
- fragile quoting and the rendered command shape;
- the exact active container tag and worker architecture;
- required imports or binary versions; and
- realistic CPU and RAM requests.

Do not submit a separate mechanical Galaxy preflight by default. Use one only
when a cheap probe resolves a concrete uncertainty about the selected container,
import, command rendering, binding, or output creation before a substantially
more expensive job. Within the current task, do not repeat the probe when its
runtime and mechanics are unchanged.

## Execution Failures

After a terminal job, inspect the resolved input bindings, command, state,
stdout and stderr, and declared output datasets. Classify a failure as
representation, binding, command, dependency, container, resource, or output
creation before retrying, then use the matching row in
[references/templates.md](references/templates.md#execution-failures) before
editing the program or changing the container. Use complete inline output or
`peek_galaxy_dataset` only to confirm that an output has the expected mechanical
structure.
