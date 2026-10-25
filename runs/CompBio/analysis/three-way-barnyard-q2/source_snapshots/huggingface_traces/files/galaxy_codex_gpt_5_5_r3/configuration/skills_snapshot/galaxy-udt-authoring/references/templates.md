# Galaxy UDT Implementation Reference

Read only the section needed for the current implementation or failure.

- [Minimal UDT](#minimal-udt)
- [Staged generated script](#staged-generated-script)
- [Short base64 fallback](#short-base64-fallback)
- [Resource fields](#resource-fields)
- [Execution failures](#execution-failures)

The YAML blocks are authoring examples. The API representation may be serialized
as JSON.

## Minimal UDT

Replace the container placeholder with a verified pinned tag. Use a bare tagged
reference without `docker://` or a digest.

```yaml
class: GalaxyUserTool
id: analysis-v1
name: Analysis
version: 0.1.0
container: quay.io/biocontainers/<package>:<pinned-tag>

shell_command: |
  set -eu
  application-command \
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

## Staged Generated Script

Pass a nontrivial workspace script through the `workspace_inputs` argument of
`run_galaxy_udt_and_wait`. The MCP operation stages it, binds it as `script`,
submits the UDT, and waits in one call.

```yaml
class: GalaxyUserTool
id: scripted-analysis-v1
name: Scripted Analysis
version: 0.1.0
container: quay.io/biocontainers/<package>:<pinned-tag>

shell_command: |
  set -eu
  python "$(inputs.script.path)" \
    "$(inputs.input.path)" \
    result.tsv

inputs:
  - name: script
    type: data
    format: [txt]
  - name: input
    type: data
    format: [tabular]

outputs:
  - name: result
    type: data
    format: tabular
    from_work_dir: result.tsv
```

Bind an existing input and the workspace script in the same call:

```json
{
  "tool_inputs": {
    "input": {"src": "hda", "id": "<input-dataset-id>"}
  },
  "workspace_inputs": {
    "script": {
      "path": "analysis.py",
      "name": "analysis.py",
      "file_type": "txt"
    }
  }
}
```

Use `stage_workspace_file` separately only when more than one Galaxy job will
reuse the staged dataset.

## Short Base64 Fallback

Use this only for short glue code when staging is unavailable. The encoded
script travels inside the UDT representation.

```bash
SCRIPT_B64='BASE64_WITHOUT_NEWLINES'
python -c 'import base64, pathlib, sys; pathlib.Path("job.py").write_bytes(base64.b64decode(sys.argv[1]))' "$SCRIPT_B64"
python job.py "$(inputs.input.path)"
```

For longer scripts, use the staged-script pattern. With a heredoc, put the
terminator at column 1 with no trailing whitespace.

## Resource Fields

`ram_min` and `ram_max` are in MiB, not GiB. For 8 GiB, specify `8192`, not
`8`. [TPV #205](https://github.com/galaxyproject/total-perspective-vortex/pull/205)
fixed the old missing MiB-to-GiB conversion; usegalaxy.org job metrics on
2026-09-30 confirm the corrected behavior. Do not copy the small RAM values
from runs that relied on the old conversion bug. Omit the whole resource
block when server defaults suffice; a resource block with only CPU fields
can introduce Galaxy's small default RAM request. Do not assume `tmpdir_min`
is enforced unless the current server configuration says so.

```yaml
requirements:
  - type: resource
    cores_min: 4
    ram_min: 8192
    ram_max: 8192
```

After a resource-related failure, inspect the exact job's `/api/jobs/{id}/metrics`
and compare `galaxy_memory_mb` with the intended request. A request intended as
8 GiB but allocated 8 MiB is a unit mismatch, not evidence that the program
needs a different method or local execution. Correct the request before
retrying; do not blindly multiply a value that is already in MiB. Check stderr
and output completeness even when Galaxy reports `ok`: an OOM-killed process
can be hidden by a wrapper's successful exit.

## Execution Failures

| Symptom | Likely layer | Required action |
|---|---|---|
| Failure before a rendered `command_line` exists | Representation or template rendering | Check input and output names and escape template-sensitive shell forms before retrying. |
| Heredoc terminator appears as program text | Command rendering | Put the terminator at column 1 with no trailing whitespace, or stage the script. |
| Encoded script is parsed as source or a variable name | Nested quoting | Pass the encoded value through `sys.argv` and decode it inside the program. |
| Galaxy binds fewer inputs than the UDT declares | Payload binding | Inspect the live schema and resolved job inputs, then correct the payload. |
| Container URI becomes `docker://docker://...` | Invalid container field | Use the bare `registry/repository:tag`. |
| Digest-qualified container is rejected | Invalid container field | Use the bare pinned tag; submission records the resolved registry digest. |
| Job never starts with a new BioContainer | Tag, architecture, conversion, or cache | Verify the exact live tag and architecture before retrying. |
| Import or binary is missing | Incompatible runtime | Select a compatible image or add one small pinned package when eligible. |
| Job is killed after starting | Resource allocation or destination policy | Inspect job evidence and request realistic CPU or RAM for the same computation. |
| Expected output dataset is absent | Command or `from_work_dir` mismatch | Inspect stdout, stderr, exit status, and actual work-directory filenames. |
