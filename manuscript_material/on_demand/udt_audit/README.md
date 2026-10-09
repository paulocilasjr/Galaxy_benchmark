# UDT error audit (On-demand Fig. 7c)

This is a trace-level audit of every scored-incorrect Galaxy-condition run that requested a user-defined tool (UDT): 22 BixBench-Verified-50 runs and 112 CompBioBench runs, 134 in total (after the reviewed CompBioBench reruns; see below). For each run it records where the decisive error happened relative to the UDT.

| File | Contents |
|---|---|
| `CODEBOOK.md` | The categories, the order they are applied in, the evidence used and the output format. Amendment 1 is at the end (see below). |
| `udt_error_audit.jsonl` | One record per run. |
| `udt_error_audit_pre_rerun_20261005.jsonl` | The audit before the reviewed reruns (130 runs), kept unchanged. |

Each record in `udt_error_audit.jsonl` holds:
- `category`
- `udt_role`
- `answer_source`
- `decisive_error_lines` and `udt_lines` (line numbers in the decompressed execution trace)
- `confidence`
- `rationale`
- `batch` (which reviewer batch the run was in)

## How it was done

1. **Evidence.** `scripts/udt_audit_timelines.py` writes a compact, ordered timeline for each run: UDT jobs with status and failure phase, Galaxy tool jobs, interface calls, shell commands with exit codes, and agent messages, each with its trace line number. It also writes the task-level audit entry from `individual_error_analysis.md`. The timelines contain reference answers and local paths, so they are written outside the repository.
2. **Review.** Six reviewers, each a Claude subagent working read-only on the archived traces, classified the runs in task-grouped batches against the codebook. They started from:
   - the task-level audit;
   - for BixBench-Verified-50, the run-level failure ledger.

   Each record cites the trace lines that show the decisive error. No agent code was rerun and no Galaxy server was contacted.
3. **Amendment 1.** After the first pass, three reviewers independently met the same case: every UDT failed, and a fallback route then repeated the same scientific error that was already in the UDT's own script or inputs. The original codebook did not separate this from a failure that changed the answer. The new category `UDT_FAILED_NOT_DECISIVE` was added and every run with a failed UDT was re-checked:
   - Batches 2, 3, 4 and 6 were re-checked by their own reviewers.
   - For batch 5, the reviewer's re-check stopped on an API rate limit. The lead auditor recoded its 8 affected runs from the reviewer's first-pass evidence and a direct reading of the traces. These records carry an `amended_by` field.

## Reviewed CompBioBench reruns (2026-10-06)

53 CompBioBench Galaxy runs were replaced by the lab's reviewed reruns (`CompBio/reruns_20261005/`). Ten audited runs were among them. Their entries were set aside and are still in `udt_error_audit_pre_rerun_20261005.jsonl`.

The 14 incoming runs that were scored incorrect and requested a UDT were coded with this codebook, including Amendment 1, by two further Claude reviewers working read-only (batches `rerun_20261005_A` and `_B`, seven runs each). Their evidence was timelines from `udt_audit_timelines.py`.

The task entries they started from describe the replaced runs, so each run was judged on its own trace. Two tasks had no task entry (reverse-encode-q1 and perturb-seq-align-q1), and `REFERENCE_OR_EVALUATOR` was not used for them. All other entries are unchanged.

## Results

| Category | BixBench-Verified-50 | CompBioBench |
|---|---:|---:|
| **At the UDT step** | | |
| `UDT_EXECUTION`: the UDT failed to run, and the failure changed the answer | 0 | 14 |
| `UDT_CODE`: the UDT ran, but the agent's code in it computed the wrong quantity | 3 | 44 |
| **Not related to UDT use** | | |
| `BEFORE_UDT` | 0 | 2 |
| `AFTER_UDT` | 0 | 6 |
| `UDT_FAILED_NOT_DECISIVE` | 0 | 19 |
| `NOT_ON_PATH` | 0 | 4 |
| `REFERENCE_OR_EVALUATOR`: the answer is defensible | 19 | 23 |

Confidence ratings: 58 high, 71 moderate and 5 low.

## Limits

- Each run was classified by one reviewer. Inter-rater agreement has not been measured; an independent second review of a random sample would provide it.
- `UDT_EXECUTION` includes 8 encode-atac-pipeline-q1 runs whose UDT ran on Galaxy's extension-less staged file names, which silently disabled adapter trimming. This is a Galaxy staging behaviour inside the UDT. The reviewer noted that `UDT_CODE` is also defensible there, because the agent could have renamed the inputs.
- `REFERENCE_OR_EVALUATOR` follows the task-level audit's judgement that an answer is defensible. For protein-shape-q1 and tissue-fibroblast-q1, that audit also favours the reference, so the call is moderate.
