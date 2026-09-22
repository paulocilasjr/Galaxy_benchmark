"""Render a cautious, task-scoped Results draft from validated evidence."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

def _fmt(value, digits=3):
    if value is None:
        return "unavailable"
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def render(output: Path, evidence: dict) -> None:
    task = evidence["task"]
    prompt = (task.get("prompt") or "**unavailable in the retrieved metadata**").strip()
    prompt_sentence = prompt if prompt.endswith((".", "?", "!")) else prompt + "."
    runs = evidence["runs"]
    comparisons = evidence["comparisons"]
    scored = [r for r in runs if r["outcome"]["original_evaluator_score"] is not None]
    unique_histories = {a["history_id"] for r in runs for a in r["artifacts"] if a.get("history_id")}
    jobs = {(a["history_id"], e["native_job_id"]): e for r in runs for e in r["events"]
            for a in r["artifacts"] if a.get("history_id") and e["execution_location"] == "galaxy_job"
            and e["event_type"] == "analysis"}
    failed_jobs = [e for e in jobs.values() if e.get("status") in {"error", "failed"}]
    failed_label = "failed job" if len(failed_jobs) == 1 else "failed jobs"
    by_model = defaultdict(dict)
    for c in comparisons:
        prefix = "score_" if c["comparison_id"].startswith("score_") else "input_tokens_"
        by_model[c["comparison_id"].removeprefix(prefix)][prefix[:-1]] = c
    lines = [f"# {task['benchmark']} {task['task_id']}: retrospective execution-history analysis", "",
             "## 1. Task, design, evidence, and matching", "",
             f"The supplied task prompt is: {prompt_sentence} This audit includes **{len(runs)} workbook rows** for one selected task. The workbook is the observed-link inventory; an independent protocol manifest was not supplied, so expected coverage and replicate matching are unknown. Conditions are kept as Galaxy and open-ended code, with original labels in `run_manifest.json`. Runtime model IDs are reported only when a retrieved invocation file verifies them. Replicate numbers do not establish matched seeds.", "",
             f"Original traces were retrieved for **{sum(r['evidence_completeness']['agent_transcript']=='retrieved' for r in runs)}/{len(runs)}** rows. Public Galaxy contents were retrieved for **{len(unique_histories)} distinct histories represented by dataset records**; history metadata-only and unavailable records remain in the source manifests. This is retrospective: no agent code or Galaxy analysis was rerun, and hidden reference files were not opened.", "",
             "## 2. Main outcomes", "",
             f"The original evaluator supplied a numeric score for **{len(scored)}/{len(runs)}** runs. These are original run evaluations, separate from saved outputs and the auditor's interpretation. The scoring field and mode are retained per run; scores from different benchmarks must not be pooled. The retrieved public histories expose **{len(jobs)} distinct analytical creating jobs**, including **{len(failed_jobs)} {failed_label}**. Native shell and MCP calls are separate from those jobs and are not equated with scientific attempts.", "",
             "| Model slug | Galaxy score mean | Code score mean | Difference (original metric unit) | Galaxy/code median input-token ratio |", "|---|---:|---:|---:|---:|"]
    for model, c in sorted(by_model.items()):
        s, t = c.get("score", {}), c.get("input_tokens", {})
        estimate_unit = s.get("estimate_unit") or ""
        difference = _fmt(s.get('estimate')) + (" pp" if estimate_unit.startswith("percentage points") else "")
        lines.append(f"| {model} | {_fmt(s.get('galaxy_mean'))} | {_fmt(s.get('code_mean'))} | {difference} | {_fmt(t.get('estimate'))} |")
    lines += ["", "These are descriptive within-task comparisons. A score difference is shown only when both conditions contain the same numeric original evaluator field. A token ratio divides the two condition medians; it is not the median of paired replicate ratios. No task-level confidence interval or equivalence conclusion is calculated from this one task.", "",
              "## 3. Results questions", "",
              "### Accuracy and output agreement by execution condition", "",
              f"Among the {len(scored)} runs with an original numeric evaluator score, the score field and answer bytes are preserved in `history_analysis_evidence.json` and the trace snapshots. For BixBench, an original `accuracy.score` evaluates a fixed submitted answer; for other benchmarks, the original evaluation definition must be checked before calling a score answer accuracy or output agreement. Public Galaxy outputs are execution artifacts and are not substitutes for submitted answers. Missing scores remain missing rather than zero.", "",
              "### Analysis execution, failures, and recovery", "",
              f"The retrieved public histories contain {len(jobs)} distinct analytical creating jobs after excluding data-fetch jobs and deduplicating multi-output jobs and shared histories. {len(failed_jobs)} have a failed/error state. The per-run job ledgers retain tool IDs, parameters, native IDs, status, available error text, and source links. A later successful Galaxy job with the same tool and input HDA IDs is flagged as an operational recovery **candidate** for case review. Nonzero shell exits and failed Galaxy jobs are platform-specific observations; the pipeline does not manufacture a cross-condition scientific-attempt count or infer scientific recovery from a later successful command alone.", "",
              "### Solution-route variability across models and replicates", "",
              "The route table below catalogues observed tool families and command indicators. It does not assert that different wrappers implement different biological methods, or that two similar commands are scientifically equivalent. Each recovered command or Galaxy Python payload is an archival copy; none was executed in this audit. Difficulty is unclassified unless an independent source supplies it.", "",
              "### Token cost, provenance, and human readability", "",
              "Provider usage totals are retained with their original accounting categories. Cached input can be included in input, and reasoning output can be included in output; these fields are not summed. A median-ratio comparison is available only for models with reported input totals in both conditions. No per-call usage, dated prices, compute/storage costs, or blinded human readability assessment is inferred. Structured source manifests and job ledgers support provenance inspection, not measured faster review.", "",
              "## 4. Per-condition, model, and replicate routes", "",
              "| Run | Runtime model ID | Score field/value | Answer | Route indicators | Galaxy analytical jobs / failed | Nonzero shell calls |", "|---|---|---|---|---|---:|---:|"]
    for r in runs:
        out = r["outcome"]
        route = (r["solution_route"].get("classification") or "unclassified").replace("|", "\\|")
        answer = (out.get("submitted_answer") or "unavailable").replace("|", "\\|").replace("\n", " ")[:90]
        jobs_count = r["derived_metrics"].get("analytical_job_count")
        failed = r["derived_metrics"].get("total_failed_jobs")
        lines.append(f"| `{r['run_id']}` | {_fmt(r['model']['verified_runtime_id'])} | {_fmt(out['original_evaluator_score_field'])} / {_fmt(out['original_evaluator_score'])} | {answer} | {route} | {_fmt(jobs_count)} / {_fmt(failed)} | {r['derived_metrics']['nonzero_exit_shell_calls']} |")
    lines += ["", "The table preserves run-level labels. A public history linked to multiple rows is counted once in the distinct-job total. The exact sequence and any same-goal correction require inspection of the retained events; no generic event-count rule establishes scientific recovery.", "",
              "## 5. Inputs, external computation, and reproducibility", "",
              "`input_manifest.json` compares names and original run-reported SHA-256 values from staged-input manifests. It does not claim the auditor rehashed large source inputs. Galaxy dataset association IDs, underlying dataset IDs, creating jobs, and accessible selected output bytes are retained where returned. Copied associations are not treated as fresh independent uploads. Remote input retrieval is separate from external analytical computation; execution location is recorded per event. Current public histories can include inherited or later state, so the original transcript is preferred for chronology.", "",
              "## 6. Methods and safeguards", "",
              "The XLSX parser reads displayed cell text and hyperlink targets without executing formulas or workbook code. Source collection is read-only. Hugging Face files above the configured byte cap are linked; retained text and gzip traces are scanned for credential and account-path patterns, with original and derivative hashes recorded. The repository Galaxy credential gate is checked before Galaxy API access. Source manifests record whether TLS certificates were verified; if not, retained-byte hashes do not authenticate the remote server. Creating jobs are deduplicated by server and native job ID; trace calls are counted separately. Exact original evaluator fields are kept rather than replaced with current scoring rules. JSON Schema 2.0, reference checks, retained hashes, and report counts are validated by `validate.py`.", "",
              "## 7. Claim-to-evidence map", "",
              "| Bounded claim | Finding ID | Evidence |", "|---|---|---|",
              "| Original evaluator score coverage for supplied rows | `finding_accuracy` | Per-run evaluator artifacts and original `evaluation.json` |",
              "| Distinct public Galaxy analytical jobs and recorded failures | `finding_execution` | Galaxy job snapshots and ledgers; one native job counted once |",
              "| Observed route families vary across run records | `finding_variability` | Trace events, tool IDs, recovered-code manifest |",
              "| Input-token ratios where usage exists; readability unmeasured | `finding_cost_readability` | Per-run `usage.json` and comparison records |", "",
              "## 8. Missing evidence and additional data", "",
              "An independent experiment manifest is needed to establish expected coverage, seeds, stopping rules, and compatible pairing. Missing or partial trace/history records are listed in source manifests. Scientific interpretation of domain-specific outputs, a common cross-condition scientific-attempt codebook, per-call token attribution, prices, and blinded reviewer outcomes require separate evidence. No missing value is encoded as an observed zero.", "",
              "### Abstract-ready paragraph", "",
              f"For one selected {task['benchmark']} task, {len(runs)} supplied runs yielded {len(scored)} original numeric evaluator scores. Retrieved public Galaxy records exposed {len(jobs)} distinct analytical creating jobs, including {len(failed_jobs)} {failed_label}. These case-study counts describe the supplied links and do not establish benchmark-wide condition effects or human readability gains.", "",
              "### Results draft", "",
              f"We audited {len(runs)} workbook-listed runs for {task['task_id']}, retaining original agent traces, evaluator records, usage totals, and read-only Galaxy history snapshots where accessible. The original evaluator returned a numeric score for {len(scored)} runs. We kept those scores separate from saved Galaxy outputs and did not regrade answers. Distinct public Galaxy histories exposed {len(jobs)} analytical creating jobs, of which {len(failed_jobs)} had failed/error status. Within-model score and input-token comparisons were calculated only where both conditions supplied compatible original fields; they are descriptive ratios or differences for a single task. Replicate seeds, complete protocol coverage, stage-attributed tokens, and blinded readability outcomes were unavailable, limiting causal and benchmark-wide inference.", ""]
    report = output / "history_analysis.md"
    report.write_text("\n".join(lines))
    readme = [f"# {task['task_id']} retrospective audit", "", "Start with [history_analysis.md](history_analysis.md).",
              "The [evidence JSON](history_analysis_evidence.json) is validated against [Schema 2.0](history_analysis_evidence.schema.json).",
              "[Run inventory](run_manifest.json), [input manifest](input_manifest.json), [recovered-code manifest](recovered_code/manifest.json),",
              "source snapshots, selected outputs, and per-run job ledgers preserve the audit trail.", "",
              "This pipeline did not execute agent code, submit Galaxy jobs, or open hidden references.", ""]
    (output / "README.md").write_text("\n".join(readme))
