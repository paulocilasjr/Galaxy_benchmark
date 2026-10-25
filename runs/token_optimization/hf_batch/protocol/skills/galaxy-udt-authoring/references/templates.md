# Galaxy UDT Templates And Troubleshooting

Read only the section needed for the current UDT.

## Minimal UDT

Replace the container placeholder with a pinned BioContainer found through one
bounded live BioContainers lookup. Use a bare tagged reference without
`docker://` or a digest.

```yaml
class: GalaxyUserTool
id: analysis-v1
name: Analysis
version: 0.1.0
container: quay.io/biocontainers/<package>:<pinned-tag>

shell_command: |
  set -eu
  selected-command \
    --input "$(inputs.input.path)" \
    --output result.tsv

inputs:
  - name: input
    type: data
    format: [tabular]

outputs:
  - name: result
    type: data
    format: tabular
    from_work_dir: result.tsv
```

For generated glue scripts, avoid nested `python -c` quoting. A base64 argument
keeps the script as one shell token:

```bash
SCRIPT_B64='BASE64_WITHOUT_NEWLINES'
python -c 'import base64, pathlib, sys; pathlib.Path("job.py").write_bytes(base64.b64decode(sys.argv[1]))' "$SCRIPT_B64"
python job.py "$(inputs.input.path)"
```

With a heredoc, put the terminator at column 1 with no trailing whitespace.

## Resource Fields

`ram_min` and `tmpdir_min` are GB values on usegalaxy.org.

```yaml
requirements:
  - type: resource
    cores_min: 4
    ram_min: 8
    tmpdir_min: 16
```

For GPU routing, add only the fields required by the server configuration, for
example `gpu_memory_min` and `cuda_device_count_min`, and use a public image that
already contains the matching CUDA-capable library. Resource fields cannot turn
a CPU-only image into a GPU image.

## Direct BioBlend Fallback

Use this only when the available UDT execution tool does not support the needed
operation. The installed BioBlend build must expose `unprivileged_tools`.

```python
from bioblend.galaxy import GalaxyInstance

gi = GalaxyInstance(url=galaxy_url, key=api_key)
if not hasattr(gi, "unprivileged_tools"):
    raise RuntimeError("BioBlend UDT interface is unavailable")

created = gi.unprivileged_tools.create_user_tool(representation)
submitted = gi.tools.run_tool(
    history_id=history_id,
    tool_uuid=created["uuid"],
    tool_inputs=tool_inputs,
)
for job in submitted.get("jobs", []):
    gi.jobs.wait_for_job(job["id"])
```

Pass the bare `GalaxyUserTool` representation to `create_user_tool`; BioBlend
adds the transport envelope. Submit with `tool_uuid`. Keep create, submit,
blocking wait, and needed output downloads in one program so job waiting does
not require repeated model turns.

## Failure Patterns

| Symptom | Likely cause | First correction |
|---|---|---|
| Failure before `command_line` exists | Representation or command-template rendering | Check names and remove unescaped shell-template forms. |
| Heredoc terminator appears as program text | Indentation or trailing whitespace | Put the terminator at column 1 or use the base64 pattern. |
| Encoded script is parsed as source text | Nested quoting broke argument boundaries | Pass it through `sys.argv` as shown above. |
| Job has fewer inputs than requested | Repeat or conditional payload shape | Inspect the live schema and resolved job inputs. |
| GPU resource is assigned but unused | CPU-only image or incompatible runtime | Use a compatible GPU image and verify imports. |
| Container conversion or pull fails | Non-BioContainer image, tag, architecture, or cache problem | Use a pinned `quay.io/biocontainers` tag and verify the architecture. |
| No single BioContainer has every package | Dependencies span published environments | Use the exact primary BioContainer plus one small pinned job-local install, or split the work across exact BioContainer UDTs without changing method semantics. |
| Thread count ignores allocation | Hardcoded threads | Read `GALAXY_SLOTS`. |
