"""Build summary.json and tool_mismatch_rates.csv from calls.csv.gz (run after extract_calls.py)."""
import collections
import json
import os

import pandas as pd

OUT = os.path.dirname(os.path.abspath(__file__))
from extract_calls import GALAXY_SERVERS, GALAXY_TOOLS, CODEX_BUILTINS  # noqa: E402

df = pd.read_csv(f'{OUT}/calls.csv.gz', low_memory=False)
cov = pd.read_csv(f'{OUT}/run_coverage.csv')
meta = json.load(open(f'{OUT}/_coverage_meta.json'))
salv = pd.read_csv(f'{OUT}/salvaged_calls.csv.gz')


def vc(s):
    return {str(k): int(v) for k, v in s.fillna('null').value_counts().items()}


def failed_mask(d):
    return (d.call_status != 'completed') | d.extract_fail


def mismatch_table(tr, min_calls=20):
    g = tr.groupby('tool_id_base', dropna=False)
    rows = []
    for tid, d in g:
        if len(d) < min_calls:
            continue
        pm = d.prov_status == 'mismatch'
        dm = d.dataset_prov_status == 'mismatch'
        checked = d.prov_status.notna()
        rows.append(dict(tool_id_base=None if pd.isna(tid) else tid, calls=len(d),
                         calls_with_param_prov_check=int(checked.sum()),
                         param_prov_mismatch=int(pm.sum()),
                         validation_stage_mismatch=int((pm & (d.prov_stage == 'validation')).sum()),
                         post_run_mismatch=int((pm & (d.prov_stage == 'post_run')).sum()),
                         dataset_prov_mismatch=int(dm.sum()),
                         any_prov_mismatch=int((pm | dm).sum()),
                         calls_with_substitution=int((d.n_substituted.fillna(0) > 0).sum()),
                         ok_calls=int((d.result_status == 'ok').sum()),
                         rate=round(pm.sum() / len(d), 4),
                         rate_among_checked=round(pm.sum() / checked.sum(), 4) if checked.sum() else None,
                         any_rate=round((pm | dm).sum() / len(d), 4)))
    return sorted(rows, key=lambda r: (-r['calls'], str(r['tool_id_base'])))


summary = dict(
    description='Per-benchmark summary of Galaxy MCP interface activity in Galaxy-condition runs; see README.md.',
    namespaces=dict(
        galaxy_interface_servers=sorted(GALAXY_SERVERS),
        galaxy_interface_tools=sorted(GALAXY_TOOLS),
        codex_builtin_tools_not_galaxy=sorted(CODEX_BUILTINS),
        observed_server_tool_pairs={f'{s}::{t}': int(n) for (s, t), n in
                                    df.groupby(['server', 'tool']).size().sort_values(ascending=False).items()},
        non_galaxy_servers_observed=sorted(set(df.server) - GALAXY_SERVERS),
    ),
    coverage=dict(
        galaxy_condition_runs=meta['n_galaxy_runs'],
        runs_with_trace=meta['n_with_trace'],
        runs_parsed=int(len(cov)),
        runs_with_parse_error=int(cov.parse_error.notna().sum()),
        runs_without_trace=meta['no_trace'],
        runs_by_trace_format=vc(cov.trace_format),
        unparsable_trace_lines=int(cov.get('diag_unparsable_lines', pd.Series(dtype=float)).fillna(0).sum()),
        unparsable_lines_mentioning_mcp=int(cov.get('diag_unparsable_lines_with_mcp', pd.Series(dtype=float)).fillna(0).sum()),
        salvaged_mcp_calls_from_unparsable_lines=int(len(salv)),
        unrecoverable_truncated_mcp_completed_fragments=int(cov.get('diag_truncated_mcp_completed_fragments', pd.Series(dtype=float)).fillna(0).sum()),
        codex_stderr_rejected_mcp_attempts=int(cov.get('diag_stderr_rejected_mcp_attempts', pd.Series(dtype=float)).fillna(0).sum()),
        claude_mcp_calls_without_result=int(cov.get('diag_mcp_calls_without_result', pd.Series(dtype=float)).fillna(0).sum()),
    ),
    expected=dict(galaxy_runs=2070, mcp_calls=69812, by_benchmark=dict(BixBench50=17550, CompBio=48297, IWC=3965),
                  extract_failed_calls=7389),
    per_benchmark={},
)

for b, d in df.groupby('benchmark'):
    cb = cov[cov.benchmark == b]
    tr = d[d.tool == 'run_galaxy_tool_and_wait']
    udt = d[d.udt]
    ok = tr[tr.result_status == 'ok']
    cpc = ok.checked_parameter_count
    fm = failed_mask(d)
    ng = d[~d.galaxy_server]
    ngf = ng[failed_mask(ng)]
    gr = d[d.galaxy_namespace & d.client_rejected]
    udt_failed = udt[(udt.result_status != 'ok') | (udt.call_status != 'completed')]
    pre = udt_failed.job_failure_phases.fillna('').str.contains('pre_execution_or_command_rendering')
    exc = udt_failed.error_excerpt.fillna('').str.contains(
        r'no destinations are available|no execution destination|training_tag_small_rule', case=False, regex=True)
    tr_failed = tr[(tr.result_status != 'ok') | (tr.call_status != 'completed')]
    mm = mismatch_table(tr)
    summary['per_benchmark'][b] = dict(
        runs_parsed=int(len(cb)),
        runs_by_trace_format=vc(cb.trace_format),
        reconciliation=dict(
            mcp_calls_parsed=int(len(d)),
            run_summaries_n_mcp=int(cb.expected_n_mcp.sum()),
            mcp_calls_diff=int(len(d) - cb.expected_n_mcp.sum()),
            extract_failed_calls_parsed=int(d.extract_fail.sum()),
            run_summaries_n_mcp_fail=int(cb.expected_n_mcp_fail.sum()),
            failed_calls_diff=int(d.extract_fail.sum() - cb.expected_n_mcp_fail.sum()),
            runs_with_count_mismatch=int(((cb.n_mcp != cb.expected_n_mcp) |
                                          (cb.n_extract_fail != cb.expected_n_mcp_fail)).sum()),
            transport_failed_calls=int((d.call_status == 'failed').sum()),
            transport_failed_not_counted_by_extract=int(((d.call_status == 'failed') & ~d.extract_fail).sum()),
            failed_calls_union=int(fm.sum()),
            extract_class=vc(d.extract_class),
            salvaged_calls_not_in_table=int((salv.benchmark == b).sum()),
        ),
        galaxy_interface_calls=int(d.galaxy_server.sum()),
        non_galaxy_calls=int((~d.galaxy_server).sum()),
        calls_by_tool=vc(d.tool),
        tool_run_calls=dict(total=int(len(tr)), by_result_status=vc(tr.result_status),
                            by_call_status=vc(tr.call_status)),
        udt_calls=dict(total=int(len(udt)), by_result_status=vc(udt.result_status),
                       by_call_status=vc(udt.call_status)),
        ok_tool_run_checked_parameter_count=dict(
            ok_calls=int(len(ok)), zero=int((cpc == 0).sum()), null=int(cpc.isna().sum()),
            positive=int((cpc > 0).sum()),
            zero_prov_status=vc(ok[cpc == 0].prov_status),
            zero_top_tools=dict(list(vc(ok[cpc == 0].tool_id_base).items())[:10])),
        prov_status=dict(tool_run=vc(tr.prov_status), udt=vc(udt.prov_status),
                         tool_run_dataset_provenance=vc(tr.dataset_prov_status)),
        tool_run_param_mismatch=dict(
            calls_with_mismatch=int((tr.prov_status == 'mismatch').sum()),
            validation_stage=int(((tr.prov_status == 'mismatch') & (tr.prov_stage == 'validation')).sum()),
            post_run=int(((tr.prov_status == 'mismatch') & (tr.prov_stage == 'post_run')).sum()),
            post_run_submitted_and_result_ok=int(((tr.prov_status == 'mismatch') & (tr.prov_stage == 'post_run') &
                                                  (tr.result_status == 'ok')).sum()),
            calls_with_substitution=int((tr.n_substituted.fillna(0) > 0).sum()),
        ),
        non_galaxy_failed_calls=dict(
            n=int(len(ngf)),
            calls=[dict(task=r.task, run_id=r.run_id, model=r.model, line=int(r.line), server=r.server, tool=r.tool,
                        call_status=r.call_status, extract_class=r.extract_class,
                        error_excerpt=None if pd.isna(r.error_excerpt) else r.error_excerpt[:200])
                   for r in ngf.itertuples()],
        ),
        galaxy_namespace_client_rejected_calls=dict(
            n=int(len(gr)), by_tool=vc(gr.tool),
            excerpts=vc(gr.error_excerpt.fillna('').str[:110])),
        failed_udt_outage_signature=dict(
            failed_udt_calls=int(len(udt_failed)),
            excerpt_matches_signature=int(exc.sum()),
            result_text_matches_signature=int(udt_failed.outage_sig_in_result.sum()),
            linked_to_shell_signature_by_job_or_dataset_id=int(udt_failed.outage_sig_linked.fillna(False).astype(bool).sum()),
            in_runs_whose_trace_contains_signature=int(udt_failed.run_outage_sig.sum()),
            pre_execution_phase=int(pre.sum()),
            pre_execution_phase_in_signature_runs=int((pre & udt_failed.run_outage_sig).sum()),
            runs_whose_trace_contains_signature=int(cb.run_outage_sig.sum()),
            failed_tool_run_calls_linked_to_signature=int(tr_failed.outage_sig_linked.fillna(False).astype(bool).sum()),
            failed_wait_calls_linked_to_signature=int(d[(d.tool == 'wait_for_galaxy_jobs') & fm].outage_sig_linked
                                                      .fillna(False).astype(bool).sum()),
        ),
        tool_mismatch_rates_min20=mm,
    )

allfm = failed_mask(df)
summary['totals'] = dict(
    mcp_calls=int(len(df)), run_summaries_n_mcp=int(cov.expected_n_mcp.sum()),
    extract_failed_calls=int(df.extract_fail.sum()), run_summaries_n_mcp_fail=int(cov.expected_n_mcp_fail.sum()),
    transport_failed_calls=int((df.call_status == 'failed').sum()),
    transport_failed_not_counted_by_extract=int(((df.call_status == 'failed') & ~df.extract_fail).sum()),
    failed_calls_union=int(allfm.sum()),
    galaxy_interface_calls=int(df.galaxy_server.sum()), non_galaxy_calls=int((~df.galaxy_server).sum()),
    non_galaxy_failed_calls=int((~df.galaxy_server & allfm).sum()),
    tool_run_calls=int((df.tool == 'run_galaxy_tool_and_wait').sum()), udt_calls=int(df.udt.sum()),
    extract_ok_but_validation_parameter_mismatch=int(((df.result_status == 'validation_parameter_mismatch') &
                                                      ~df.extract_fail).sum()),
)

json.dump(summary, open(f'{OUT}/summary.json', 'w'), indent=1, default=str)
rows = []
for b, v in summary['per_benchmark'].items():
    for r in v['tool_mismatch_rates_min20']:
        rows.append(dict(benchmark=b, **r))
pd.DataFrame(rows).to_csv(f'{OUT}/tool_mismatch_rates.csv', index=False)
print(json.dumps(summary['totals'], indent=1))
