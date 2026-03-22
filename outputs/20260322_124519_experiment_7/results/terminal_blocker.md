# Terminal Blocker Summary

## Decision

Stop experiment_7 after attempt 4. The workflow fails repeatedly in the same Galaxy MMseqs2 taxonomy step on `usegalaxy.org`, and two progressively deeper resource-mitigation retries did not clear the failure.

## Repeated Failure Signature

- Failing tool: `toolshed.g2.bx.psu.edu/repos/iuc/mmseqs2_taxonomy_assignment/mmseqs2_taxonomy_assignment/17-b804f+galaxy0`
- Repeated failed outputs: `MMseqs2 Taxonomy Tabular`, `MMseqs2 Taxonomy Kraken`
- Repeated paused descendants: `Krakentools: Convert kraken report file on dataset 72`, `MMseqs2 Taxonomy Krona`, `MultiQC Report`, `MultiQC ... Stats`
- Galaxy instance: `https://usegalaxy.org`
- Available taxonomy DB used in all retries: `UniRef50-17-b804f-07112025`

## Attempt Evidence

### Attempt 2

- Run directory: `outputs/20260321_015411_experiment_7`
- History ID: `bbd44e69cb8906b584a975a958b696c8`
- Invocation ID: `b181a579e1f49985`
- Failing job ID: `bbd44e69cb8906b5effa49b74ce6ca1c`
- MMseqs2 prefilter settings in failing command: `split=0`, `split_mode=2`, `max_seqs=300`, `sensitivity=2.0`
- Low-level failure evidence:
  - `job_stderr`: `slurmstepd: error: Detected 1 oom-kill event(s) in StepId=4515340.batch. Some of your processes may have been killed by the cgroup out-of-memory handler.`
  - `tool_stderr`: `... Killed ... mmseqs prefilter ...`

### Attempt 3

- Run directory: `outputs/20260322_122457_experiment_7`
- History ID: `bbd44e69cb8906b5e846915d85d2122a`
- Invocation ID: `00442068f186904a`
- Failing job ID: `bbd44e69cb8906b56c93a782294c33cc`
- MMseqs2 prefilter settings in failing command: `split=16`, `split_mode=2`, `max_seqs=300`, `sensitivity=2.0`
- Failure pattern:
  - same two MMseqs2 taxonomy outputs entered `error`
  - same taxonomy/Krona/MultiQC descendants entered `paused`
  - Galaxy did not expose stderr text for this retry, but the failing tool and downstream failure pattern were unchanged

### Attempt 4

- Run directory: `outputs/20260322_124519_experiment_7`
- History ID: `bbd44e69cb8906b582d0ebb67128de77`
- Invocation ID: `981feee01bae6710`
- Failing job ID: `bbd44e69cb8906b55478a1a8e55af5cd`
- MMseqs2 prefilter settings in failing command: `split=64`, `split_mode=0`, `max_seqs=100`, `sensitivity=1.0`
- Failure pattern:
  - same two MMseqs2 taxonomy outputs entered `error`
  - same taxonomy/Krona/MultiQC descendants entered `paused`
  - Galaxy again did not expose stderr text

## Why This Is A Terminal Stop

The failure stayed pinned to the same MMseqs2 taxonomy stage across three attempts, including two signature-specific retries that materially reduced prefilter memory pressure. The benchmark policy forbids blind retries after the same signature persists without a justified mechanism change. The remaining options would require a materially different execution environment or resource allocation, such as:

- a different Galaxy instance with a valid API key and higher memory for this tool
- administrative changes to `usegalaxy.org` job resources
- a workflow/tool change that would no longer be the same benchmark execution path

## Metadata-Derived Fields

These values were identified from the pinned workflow definition and saved workflow metadata, but they were not emitted as `result.json` because the end-to-end Galaxy execution did not succeed:

- `tool_name_1`: `eggNOG Mapper`
- `total__steps`: `34`
- `tool_name_2`: `MEGAHIT`
