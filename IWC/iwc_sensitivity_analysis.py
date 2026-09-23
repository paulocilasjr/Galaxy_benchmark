#!/usr/bin/env python3
"""Sensitivity and distribution analyses for the IWC output-agreement endpoint.

Auditor-derived. Reads only ``iwc_scientific_audit.json`` (itself produced by
``audit_iwc_results.py``); executes no archived agent code, contacts no Galaxy
server and opens no hidden reference. Writes ``iwc_sensitivity_results.json``.

Motivation. The primary environment contrast is a mean of task-level
differences over 9 or 10 task units. With so few units, a mean difference and a
percentile bootstrap interval cannot by themselves show whether a contrast
reflects a broad shift or one task. These analyses answer three questions a
reader should ask of any such contrast:

  1. Shape.       Is the endpoint distributed such that a mean is informative?
  2. Influence.   Does any single task carry the contrast (leave-one-task-out)?
  3. Mechanism.   Do a few catastrophic runs account for the contrast?

Units follow the report: a run is one task x model configuration x execution
environment x replicate; an analysis cell is the three replicates of one task,
model configuration and environment.
"""

import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.join(HERE, "iwc_scientific_audit.json")
DEST = os.path.join(HERE, "iwc_sensitivity_results.json")

MODELS = ["GPT-5.5", "GPT-5.6 Sol", "GPT-5.6 Luna", "Codex + DeepSeek V4 Pro"]
HOST_REMOVAL = "wf_003_host_contamination_removal"
ENVIRONMENTS = ["galaxy", "open_ended_code"]


def load_runs():
    with open(AUDIT) as fh:
        return json.load(fh)["runs"]


def cell_scores(runs, task, model, environment):
    """Numeric scores of the three replicates in one analysis cell."""
    return [
        r["score"]
        for r in runs
        if r["task"] == task
        and r["model"] == model
        and r["condition"] == environment
        and r["score"] is not None
    ]


def task_difference(runs, task, model):
    """Galaxy minus open-ended-code mean agreement for one task and configuration.

    Returns None unless both environments contribute three numeric replicates,
    which is the same completeness rule the primary comparison uses.
    """
    g = cell_scores(runs, task, model, "galaxy")
    c = cell_scores(runs, task, model, "open_ended_code")
    if len(g) != 3 or len(c) != 3:
        return None
    return statistics.mean(g) - statistics.mean(c)


def contrast(runs, model, tasks):
    diffs = [d for d in (task_difference(runs, t, model) for t in tasks) if d is not None]
    return (statistics.mean(diffs) if diffs else None), diffs


def endpoint_shape(runs):
    scores = [r["score"] for r in runs if r["score"] is not None]
    edges = [(0.0, 0.001), (0.001, 0.5), (0.5, 0.9), (0.9, 0.99), (0.99, 0.999), (0.999, 1.0001)]
    labels = ["<0.001", "0.001-0.5", "0.5-0.9", "0.9-0.99", "0.99-0.999", ">=0.999"]
    return dict(
        n=len(scores),
        median=statistics.median(scores),
        mean=statistics.mean(scores),
        bins={lab: sum(1 for s in scores if lo <= s < hi) for (lo, hi), lab in zip(edges, labels)},
        runs_below_0_5=sorted(
            (
                dict(id=r["id"], environment=r["condition"], task=r["task"], model=r["model"],
                     replicate=r["replicate"], score=r["score"],
                     score_conflict=r.get("score_conflict_gt_1e_9", False))
                for r in runs
                if r["score"] is not None and r["score"] < 0.5
            ),
            key=lambda x: (x["environment"], x["task"]),
        ),
    )


def cell_reliability(runs, tasks):
    out = {}
    for env in ENVIRONMENTS:
        cells = []
        for t in tasks:
            for m in MODELS:
                v = cell_scores(runs, t, m, env)
                if len(v) == 3:
                    cells.append(v)
        ranges = sorted(max(v) - min(v) for v in cells)
        out[env] = dict(
            evaluable_cells=len(cells),
            all_three_at_least_0_99=sum(1 for v in cells if min(v) >= 0.99),
            any_replicate_below_0_5=sum(1 for v in cells if min(v) < 0.5),
            replicate_range_median=statistics.median(ranges),
            replicate_range_q3=statistics.quantiles(ranges, n=4, method="inclusive")[2],
            replicate_range_max=max(ranges),
            cells_with_identical_replicates=sum(1 for x in ranges if x == 0.0),
        )
    return out


def jackknife(runs, tasks):
    out = {}
    for m in MODELS:
        full, _ = contrast(runs, m, tasks)
        loo = {}
        for dropped in tasks:
            est, _ = contrast(runs, m, [t for t in tasks if t != dropped])
            if est is not None:
                loo[dropped] = est
        most = max(loo, key=lambda t: abs(loo[t] - full))
        out[m] = dict(
            full_estimate=full,
            leave_one_out=loo,
            minimum=min(loo.values()),
            maximum=max(loo.values()),
            most_influential_task=most,
            swing_when_most_influential_dropped=abs(loo[most] - full),
            sign_stable=len({v > 0 for v in loo.values()}) == 1,
        )
    return out


def zero_run_sensitivity(runs, tasks):
    out = {}
    for m in MODELS:
        tasks_with_zero = {r["task"] for r in runs if r["model"] == m and r["score"] == 0.0}
        kept = [t for t in tasks if t not in tasks_with_zero]
        full, _ = contrast(runs, m, tasks)
        reduced, _ = contrast(runs, m, kept)
        out[m] = dict(
            full_estimate=full,
            tasks_containing_a_zero_scored_run=sorted(tasks_with_zero & set(tasks)),
            estimate_excluding_those_tasks=reduced,
            tasks_remaining=len(kept),
        )
    return out


def per_task_differences(runs, tasks):
    out = {}
    for m in MODELS:
        out[m] = {t: task_difference(runs, t, m) for t in tasks}
    return out


def main():
    runs = load_runs()
    tasks = sorted({r["task"] for r in runs})
    common_nine = [t for t in tasks if t != HOST_REMOVAL]
    results = dict(
        provenance=dict(
            source="iwc_scientific_audit.json",
            runs=len(runs),
            tasks=len(tasks),
            common_nine_tasks=common_nine,
            note=(
                "Auditor-derived sensitivity analyses. No archived code executed, no "
                "Galaxy API call, no hidden reference opened, no score regraded."
            ),
        ),
        endpoint_shape=endpoint_shape(runs),
        cell_reliability_all_ten_tasks=cell_reliability(runs, tasks),
        jackknife_common_nine=jackknife(runs, common_nine),
        zero_run_sensitivity_common_nine=zero_run_sensitivity(runs, common_nine),
        per_task_differences_common_nine=per_task_differences(runs, common_nine),
    )
    with open(DEST, "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=False)
    print(f"runs={len(runs)} tasks={len(tasks)} -> wrote {DEST}")
    for m in MODELS:
        j = results["jackknife_common_nine"][m]
        z = results["zero_run_sensitivity_common_nine"][m]
        print(
            f"  {m:26} full {j['full_estimate']:+.4f} | LOO [{j['minimum']:+.4f},{j['maximum']:+.4f}]"
            f" | sign stable {str(j['sign_stable']):5} | excl. zero-tasks {z['estimate_excluding_those_tasks']:+.4f}"
        )


if __name__ == "__main__":
    main()
