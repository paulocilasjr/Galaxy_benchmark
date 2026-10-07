"""Supplementary Table: design and run selection for each benchmark and condition (accompanies Fig. 1).

From the read-only design extraction (manuscript_narrative/derived/design/per_run_design_metadata.csv) and the scored
runs (figures/scored_runs.csv, every run as the public results site shows it; make_scored_runs.py). Writes
figures/supp_table_design.csv and figures/supp_table_design.md.
"""
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DESIGN = os.path.join(ROOT, 'manuscript_narrative', 'derived', 'design', 'per_run_design_metadata.csv')
SCORED = os.path.join(ROOT, 'figures', 'scored_runs.csv')
OUT = os.path.join(ROOT, 'figures')
PRIMARY = {'codex_gpt_5_5', 'codex_gpt_5_6_sol', 'codex_gpt_5_6_luna', 'deepseek_v4_pro_via_codex',
           'codex_deepseek_v4_pro_0813', 'codex_deepseek_v4_pro'}
EXCLUDED = {'deepseek_v4_pro_via_claude_code_superseded': 'DeepSeek V4 Pro through Claude Code (superseded harness)',
            'codex_gpt_6_astra': 'GPT-6 Astra (custom code only)'}
COND = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}
BENCH = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
# Execution setting as recorded in the design extraction (Q1) and stated budgets (Q3/Q4).
WHERE = {('BixBench50', 'open_ended_code'): 'Docker container (bixbench-galaxy-agent image; tag recorded per run)',
         ('BixBench50', 'galaxy'): 'Docker container; analysis as usegalaxy.org jobs through MCP',
         ('CompBio', 'open_ended_code'): 'Host conda environment (no container; environment not exported)',
         ('CompBio', 'galaxy'): 'Docker container (galaxy-eval-agent); analysis as usegalaxy.org jobs through MCP',
         ('IWC', 'open_ended_code'): 'Docker container (image digest recorded)',
         ('IWC', 'galaxy'): 'Docker container (same digest); analysis as usegalaxy.org jobs through MCP'}
TOOLS = {'open_ended_code': 'Software the agent installs', 'galaxy': 'Installed Galaxy tools; UDTs except on IWC'}


def budget(g):
    if g.iwc_wall_clock_timeout_seconds.notna().any():
        hrs = sorted({int(v / 3600) for v in g.iwc_wall_clock_timeout_seconds.dropna()})
        n = g.iwc_wall_clock_timeout_seconds.value_counts()
        return ' or '.join(f'{h} h' for h in hrs) + ' wall clock (' + ', '.join(
            f'{int(n.get(h * 3600, 0))} runs at {h} h' for h in hrs) + ')'
    if g.stated_minutes.notna().any():
        m = g.stated_minutes.value_counts()
        return '; '.join(f'{int(k)} min stated ({int(v)} runs)' for k, v in m.items())
    return 'None stated'


def main():
    d = pd.read_csv(DESIGN, low_memory=False)
    scored = pd.read_csv(SCORED).assign(condition=lambda x: x.env)
    rows = []
    for (bm, cond), g in d.groupby(['benchmark', 'condition']):
        p = g[g.model.isin(PRIMARY)]
        excl = g[~g.model.isin(PRIMARY)].model.map(EXCLUDED).value_counts()
        s = scored[(scored.benchmark == bm) & (scored.condition == cond)]
        rows.append({
            'Benchmark': BENCH[bm], 'Condition': COND[cond], 'Archived runs': len(g),
            'Excluded from the comparison': '; '.join(f'{k} ({v})' for k, v in excl.items()) or 'None',
            'Primary runs': len(p), 'Scored runs': len(s), 'Scored tasks': s.task.nunique(),
            'Where the analysis ran': WHERE[(bm, cond)], 'Tools': TOOLS[cond],
            'Prompt words, median (range)': f'{p.prompt_file_words.median():.0f} ({p.prompt_file_words.min():.0f}–'
                                            f'{p.prompt_file_words.max():.0f})',
            'Distinct prompt files': p.prompt_file_sha256.nunique(),
            'Time budget': budget(p),
            'Selection note': ('Host-read removal scored from run_record.json, the value the results site shows' if bm == 'IWC' else '') +
                              ('Composite campaigns: some replicate vectors combine runs from different campaigns'
                               if bm == 'CompBio' else ''),
        })
    t = pd.DataFrame(rows)
    order = {b: i for i, b in enumerate(BENCH.values())}
    t = t.sort_values(['Benchmark', 'Condition'], key=lambda s: s.map(order) if s.name == 'Benchmark' else s.map(
        {'Custom code': 0, 'Galaxy': 1}))
    t.to_csv(os.path.join(OUT, 'supp_table_design.csv'), index=False)
    with open(os.path.join(OUT, 'supp_table_design.md'), 'w') as f:
        f.write('**Supplementary Table | Design and run selection by benchmark and condition.** '
                'Archived runs are all runs in the archive; primary runs are the four model configurations compared '
                'in the paper; scored runs have a benchmark score. Prompts differ between conditions for every task, '
                'model and replicate (0 identical prompt files of 2,070 pairs), and Galaxy prompts add execution '
                'policy. Values come from the read-only design extraction '
                '(`manuscript_narrative/derived/design/`).\n\n')
        f.write('| ' + ' | '.join(t.columns) + ' |\n|' + '---|' * len(t.columns) + '\n')   # no tabulate dependency
        for row in t.itertuples(index=False):
            f.write('| ' + ' | '.join(str(v) for v in row) + ' |\n')
    print(t.to_string())


if __name__ == '__main__':
    main()
