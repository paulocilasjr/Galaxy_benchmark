#!/usr/bin/env python3
"""Execution errors of the 24 IWC host-read removal (wf_003) runs, in the schema of On-demand Fig. 5's Source Data.

The archive's error tables (manuscript_material/on_demand/Source_Data_OD_Fig5.xlsx, sheets abc_runs and abc_every_error)
leave out wf_003, which the archive did not score. This script applies the same extraction to those 24 runs: it imports
manuscript_material/scripts/fig_on_demand.py and uses its shell_failures(), galaxy_error_jobs() and classify_error()
unchanged, with the same run checks. A run ends correct at >= 0.99 output agreement (scored_runs.csv), the rule of the
figures.

Writes wf003_abc_runs.csv and wf003_abc_every_error.csv next to this script; make_fig3.py appends them to the sheets.
Run from the repository root after make_scored_runs.py.
"""
import collections
import gzip
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
sys.dont_write_bytecode = True
import fig_on_demand as od  # noqa: E402

TASK = 'wf_003_host_contamination_removal'


def main():
    scored = pd.read_csv(os.path.join(HERE, 'scored_runs.csv'))
    score = {(r.cfg, r.env, r.replicate): r.score for r in scored[scored.task == TASK].itertuples()}
    sums = {(s['benchmark'], s['task'], s['run_id']): s for s in map(json.loads, gzip.open(
        os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt'))}
    gjobs = od.galaxy_error_jobs()
    types = [k for k, _ in od.ERROR_TYPES]
    runs, errs = [], []
    for r in od.A['runs']:
        if r['benchmark'] != 'IWC' or r['task'] != TASK:
            continue
        s = sums[('IWC', TASK, r['run_id'])]
        assert s.get('trace'), r['run_id']
        assert not (r['condition'] == 'galaxy' and r['jobs'] is None), r['run_id']
        cfg = od.MODEL_ALL[r['model']]
        ok = score[(cfg, r['condition'], r['replicate'])] >= 0.99 - 1e-9
        sf = od.shell_failures(s['trace'])
        assert len(sf) <= s['n_shell_nonzero'], r['run_id']
        gj = gjobs.get(('IWC', TASK, r['run_id']), []) if r['condition'] == 'galaxy' else []
        assert len(gj) == ((r['errors'] or 0) if r['condition'] == 'galaxy' else 0), r['run_id']
        kinds = collections.Counter([od.classify_error(m, ec, c) for ec, m, c in sf] + [t for t, _ in gj])
        base = dict(benchmark='IWC', model_configuration=od.ROW[cfg].replace('\n', ' '),
                    execution_condition=od.ENV_LABEL_LONG[r['condition']], task=TASK, replicate=r['replicate'])
        runs.append(dict(**base, failed_shell_commands=len(sf), galaxy_jobs_in_error_state=len(gj), ended_correct=ok,
                         **{dict(od.ERROR_TYPES)[t].replace('\n', ' '): kinds[t] for t in types}))
        for ec, m, c in sf:
            errs.append(dict(**base, channel='shell command', error_type=dict(od.ERROR_TYPES)[od.classify_error(m, ec, c)]
                             .replace('\n', ' '), exit_code=ec, run_ended_correct=ok))
        for t, tool in gj:
            errs.append(dict(**base, channel='Galaxy job', error_type=dict(od.ERROR_TYPES)[t].replace('\n', ' '), tool=tool,
                             run_ended_correct=ok))
    assert len(runs) == 24, len(runs)
    pd.DataFrame(runs).to_csv(os.path.join(HERE, 'wf003_abc_runs.csv'), index=False)
    pd.DataFrame(errs).to_csv(os.path.join(HERE, 'wf003_abc_every_error.csv'), index=False)
    e = pd.DataFrame(errs)
    print(f'wf_003: {len(runs)} runs, {len(errs)} errors'
          + (f' ({e.channel.value_counts().to_dict()})' if len(e) else ''))


if __name__ == '__main__':
    main()
