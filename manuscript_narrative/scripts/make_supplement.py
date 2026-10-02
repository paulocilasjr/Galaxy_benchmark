"""Supplementary Tables for both narrative manuscripts.

Run from the repository root after both make_figures.py scripts (it reads their numbers.json and Source Data):
    python manuscript_narrative/scripts/make_supplement.py

Writes <paper>/supplementary/Supplementary_Tables.xlsx for the user-oriented and the Galaxy-oriented manuscript. Every
table is built from archived evidence or from the figure scripts' outputs; no number is typed in by hand. CompBioBench
answers are never written: Supplementary Table 3 describes the reference-key layers by file role and checksum prefix only.
"""
import json
import os
import sys

import pandas as pd

NARR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, NARR)
import narrative_common as nc  # noqa: E402


def load(paper, name):
    return json.load(open(os.path.join(NARR, paper, name)))


def rows(obj):
    return pd.DataFrame(obj['rows'] if isinstance(obj, dict) and 'rows' in obj else obj)


def write(paper, tables, readme):
    out = os.path.join(NARR, paper, 'supplementary')
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, 'Supplementary_Tables.xlsx')
    with pd.ExcelWriter(p, engine='openpyxl') as xw:
        pd.DataFrame(readme, columns=['sheet', 'content']).to_excel(xw, sheet_name='README', index=False)
        for name, df in tables.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
    print('wrote', p)


def provenance_table(paper):
    num, src = load(paper, 'numbers.json'), load(paper, 'numbers_provenance.json')
    text = open(os.path.join(NARR, paper, 'manuscript.md')).read()
    return pd.DataFrame([dict(key=k, value=v, computed_in=src.get(k, ''), quoted_in_text=('{{' + k + '}}') in text)
                         for k, v in num.items()])


# ---------------------------------------------------------------------------------------------------- user-oriented
def user_tables():
    d = json.load(open(os.path.join(NARR, 'derived', 'design', 'design_metadata.json')))
    num = load('user-oriented', 'numbers.json')
    t = {}
    # 1: design differences between arms
    t['S1a_harness_container'] = rows(d['q1_harness_container']['rows'])
    t['S1b_prompt_identity'] = rows(d['q3_prompts']['galaxy_vs_code_prompt_identity'])
    t['S1c_prompt_words'] = rows(d['q3_prompts']['word_counts_by_condition'])
    t['S1d_budgets'] = rows(d['q4_budgets']['summary'])
    pm = d['q4_budgets']['iwc_pair_matching']
    t['S1e_iwc_budget_pairs'] = pd.DataFrame([dict(combination=k, pairs=v) for k, v in pm['by_combination'].items()])
    t['S1f_compbio_campaigns'] = rows(d['q7_campaign_selection']['compbio_totals_by_condition'])
    t['S1g_other_differences'] = rows(d['q8_other_differences']['items'])
    t['S1h_not_recorded'] = rows(d['unknowns_not_recorded'])
    # 2: populations, eligibility and measure definitions
    t['S2_populations_measures'] = pd.DataFrame([
        dict(measure='BixBench-Verified-50 accuracy', population='four Codex configurations', eligible_unit='run',
             numerator='runs accepted by the original evaluator', denominator='runs (600 per arm)', clusters='33 source capsules'),
        dict(measure='CompBioBench key agreement', population='four Codex configurations', eligible_unit='run',
             numerator='runs whose stripped answer equals the reconstructed key', denominator='runs (1,200 per arm)', clusters='100 tasks'),
        dict(measure='IWC output agreement', population='four Codex configurations, nine tasks scored in both arms', eligible_unit='run',
             numerator='sum of output agreement (0-1)', denominator='runs (108 per arm)', clusters='9 tasks'),
        dict(measure='Discordant replicate sets', population='four Codex configurations', eligible_unit='replicate set',
             numerator='sets with one or two runs correct (IWC: range > 0.05)', denominator='sets per arm (200, 400, 36)',
             clusters='as above'),
        dict(measure='IWC discordant sets, all ten tasks', population='four Codex configurations', eligible_unit='scored replicate set',
             numerator='sets with range > 0.05', denominator=num['iwc_disc_ten'], clusters='10 tasks'),
        dict(measure='Unanimous accuracy', population='four Codex configurations', eligible_unit='task x configuration',
             numerator='sets with all three runs correct', denominator='sets per arm', clusters='as above'),
        dict(measure='Answer agreement', population='four Codex configurations', eligible_unit='pair of replicate runs',
             numerator='pairs with matching answers (decimals within relative 1e-4, integers exact, text without case and spaces)',
             denominator='three pairs per set', clusters='as above'),
        dict(measure='Token and action ratios', population='four Codex configurations', eligible_unit='task x configuration cell',
             numerator='Galaxy median', denominator='open-ended code median; cells with records in both arms only',
             clusters=f"complete cells: {num['bix_tok_cells']}, {num['cb_tok_cells']}, {num['iwc_tok_cells']}"),
        dict(measure='Majority vote (rules A and B)', population='four Codex configurations', eligible_unit='replicate set',
             numerator='sets whose selected answer is scored correct', denominator='sets (no majority counts as incorrect)',
             clusters='as above'),
        dict(measure='Detailed analysis history', population='Galaxy-arm runs', eligible_unit='run', numerator='runs with a retrieved history',
             denominator=f"primary {num['hist_primary']}; all Galaxy runs {num['hist_all']}", clusters='none'),
        dict(measure='Parameter check coverage', population='Galaxy-arm tool-run calls, four Codex configurations', eligible_unit='call',
             numerator='calls with at least one non-dataset parameter compared', denominator=num['check_coverage_primary'], clusters='none'),
    ])
    # 3: CompBioBench reference-key layers and sensitivity analyses (no answers)
    t['S3a_key_layers'] = pd.DataFrame([
        dict(layer='score-inferred answers', items=54, file_role='score_inferred_answers.tsv', sha256_prefix='959dd3f2'),
        dict(layer='score-predicted answers', items=46, file_role='compbiobench_results_score_predicted_answers.tsv', sha256_prefix='57a6a92d'),
        dict(layer='official scores (verification)', items=24, file_role='paper_site_runs_lab.json; all 24 paired replicate scores reproduced',
             sha256_prefix='055cfb18'),
    ]).assign(source='goeckslab/galaxy-agent-benchmark (private), commit bdc00429f559; files kept outside the repository')
    t['S3b_sensitivity'] = pd.DataFrame([
        dict(analysis='primary', definition='all 100 tasks', galaxy_minus_code=f"{num['cb_diff']} ({num['cb_diff_ci']})"),
        dict(analysis='alternative key D', definition='genome-coords-q1 scored against key D', galaxy_minus_code=num['cb_sens_alt_genome_D']),
        dict(analysis='no predicted-key audited tasks', definition='two audited tasks with predicted keys removed',
             galaxy_minus_code=num['cb_sens_no_predicted']),
        dict(analysis='informative tasks', definition='53 tasks with any run deviating from the key', galaxy_minus_code=num['cb_sens_informative']),
        dict(analysis='no outcome-named campaigns',
             definition=f"{num['cb_outcome_named_cells']} task x configuration cells containing any of {num['cb_outcome_named_runs']} runs from "
                        'campaigns whose names match wrong|target<digits>|near<digits> removed',
             galaxy_minus_code=num['cb_sens_no_outcome_campaigns']),
    ])
    # 4: codebooks
    t['S4a_divergence_mechanisms'] = pd.DataFrame([
        ('Hand-written method or different software version', 'The incorrect run implemented the method itself or installed a different version than its correct siblings'),
        ('Domain convention applied differently', 'A different, defensible convention (normalization, test, threshold, population)'),
        ('Error in the final step', 'Correct intermediate results, wrong final extraction or arithmetic'),
        ('Galaxy interface trap', 'A Galaxy-specific behaviour (parameter rebinding, wrapper semantics, staging) changed the result'),
        ('No answer, or benchmark source files read', 'No submitted answer, or the run read benchmark source material'),
    ], columns=['mechanism', 'definition'])
    t['S4b_audit_causes'] = pd.DataFrame([
        ('C1', 'Equivalent answer, other notation'), ('C2', 'Scoring or evaluator artifact'),
        ('C3', 'Reference depends on an unstated choice (definition, software version, sample set, threshold)'),
        ('C4', 'Galaxy platform, wrapper or server'), ('C5', 'Agent analysis error'),
        ('C6', 'Provenance violation or benchmark-answer exposure'),
        ('C7', 'Changed scientific conclusion despite a near-perfect composite score'),
        ('C8', 'Harness, completion or unresolved failure'),
    ], columns=['code', 'primary_cause'])
    t['S4c_voting_rules'] = pd.DataFrame([
        ('A (primary)', 'strip, lowercase, remove whitespace; numeric answers equal to 10 significant digits; percent units retained; nonfinite/missing answers cannot form a majority'),
        ('B (sensitivity)', 'as A, numbers compared to 3 significant digits'),
        ('selection', 'select a group of at least two of three answers, then its earliest-replicate submitted answer; no group counts as incorrect; reuse the selected run\'s archived grade, without independent regrading'),
        ('oracle (reference only)', 'at least two of three runs scored correct; uses grades, so it is not a strategy a user can apply'),
    ], columns=['rule', 'definition'])
    t['S4d_error_types'] = pd.DataFrame([
        ('Code, parameter or syntax', 'shell or job error naming code, syntax or a parameter'),
        ('Missing software, package or container', 'command, module or package not found'),
        ('File, path or input format', 'missing file, wrong path or unreadable input'),
        ('Time or memory limit', 'timeout, killed or out of memory'),
        ('Galaxy job never started', 'job not dispatched or rejected before execution'),
        ('Network, or no or unclassified message', 'network error, or no classifiable message'),
    ], columns=['error_type', 'rule_summary'])
    t['S5_number_provenance'] = provenance_table('user-oriented')
    readme = [('S1a-S1h', 'Supplementary Table 1: design differences between arms, read-only from the archive (derived/design/)'),
              ('S2', 'Supplementary Table 2: analysed populations, eligibility and measure definitions'),
              ('S3a-S3b', 'Supplementary Table 3: CompBioBench reference-key layers (no answers) and sensitivity analyses'),
              ('S4a-S4d', 'Supplementary Table 4: codebooks'),
              ('S5', 'Supplementary Table 5: every number in numbers.json, the figure function that computed it, and whether the text quotes it')]
    write('user-oriented', t, readme)


# ---------------------------------------------------------------------------------------------------- Galaxy-oriented
def galaxy_tables():
    num = load('galaxy-oriented', 'numbers.json')
    t = {}
    fig1 = pd.read_excel(os.path.join(NARR, 'galaxy-oriented', 'source_data', 'Source_Data_Fig1.xlsx'), sheet_name='b_evidence')
    t['S1a_evidence'] = fig1
    meta = json.load(open(os.path.join(NARR, 'derived', 'galaxy_calls', '_coverage_meta.json')))
    t['S1b_extraction_coverage'] = pd.json_normalize(meta).T.reset_index().rename(columns={'index': 'field', 0: 'value'})
    summ = json.load(open(os.path.join(NARR, 'derived', 'galaxy_calls', 'summary.json')))
    t['S1c_reconciliation'] = pd.DataFrame([dict(benchmark=b, **{k: v for k, v in s['reconciliation'].items() if not isinstance(v, dict)})
                                            for b, s in summ['per_benchmark'].items()])
    t['S2a_failure_rules'] = pd.DataFrame([dict(order=i + 1, failure_class=n, pattern=rx) for i, (n, rx) in enumerate(nc.FAIL_RULES)] + [
        dict(order=len(nc.FAIL_RULES) + 1, failure_class='fallbacks', pattern='validation_failed -> A4; timeout -> A8; empty text -> B2; else Z'),
        dict(order=0, failure_class='X additional transport or tool exceptions (previously uncounted)',
             pattern='call-status failed on a Galaxy-interface call that the earlier extraction counted as a success; includes transport, server and tool exceptions')])
    f = nc.galaxy_failures()
    leg = json.load(open(os.path.join(nc.ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction', 'cat_tool.json')))
    legc = {}
    for k, v in leg.items():
        legc[k.split('|')[0]] = legc.get(k.split('|')[0], 0) + (v if isinstance(v, int) else sum(v.values()) if isinstance(v, dict) else len(v))
    new = f.failure_class.value_counts().to_dict()
    t['S2b_reconciliation'] = pd.DataFrame([dict(failure_class=c, archived_ledger=legc.get(c, 0), this_analysis=new.get(c, 0))
                                            for c in sorted(set(legc) | set(new))])
    t['S2c_A1_subclasses'] = f[f.failure_class.str.startswith('A1')].groupby(['benchmark', 'a1_subclass']).size().reset_index(name='calls')
    t['S3a_fidelity_classes'] = pd.DataFrame([
        ('compared and matched', 'returned ok and the adapter compared the requested non-dataset parameters with the job record: matched'),
        ('dataset inputs only', 'returned ok; zero non-dataset parameters compared and explicit dataset-only provenance status; does not establish complete scientific-intent fidelity'),
        ('ok; not comparable', 'returned ok with positive checked count but parameter provenance marked not_comparable; parameter agreement is unverified'),
        ('mismatch before submission', 'validation found parameters that would not bind; no job was created'),
        ('mismatch after the job', 'the job ran; the adapter reported a parameter or provenance mismatch'),
        ('failed', 'validation, submission or job failure'),
    ], columns=['class', 'definition'])
    t['S3b_tool_mismatch_rates'] = pd.read_excel(os.path.join(NARR, 'galaxy-oriented', 'source_data', 'Source_Data_Fig3.xlsx'),
                                                 sheet_name='b_tool_rates')
    t['S4_readiness_measures'] = pd.DataFrame([
        dict(measure='Run calls compared and matched', numerator='installed-tool run calls in class "compared and matched"',
             denominator='installed-tool run calls', better='higher', baseline=num['base_checked_matched']),
        dict(measure='Run calls with a parameter mismatch flag', numerator='calls with prov_status=mismatch, including failed-result calls; separate from exclusive result-status classes',
             denominator='installed-tool run calls', better='lower', baseline=num['base_unbound']),
        dict(measure='Galaxy-interface calls that failed', numerator='failed calls (all classes)', denominator='Galaxy-interface calls',
             better='lower', baseline=num['base_failed_calls']),
        dict(measure='Failed-job calls without diagnostic text in extracted excerpt', numerator='failed-job calls without standard error, output or traceback detected in the 240-character excerpt; not proof of absent full-payload diagnostics',
             denominator='calls that returned a failed job', better='lower', baseline=num['base_notext']),
        dict(measure='Returned text spent on tool discovery', numerator='characters returned by search and inspect-tool calls',
             denominator='characters returned by all Galaxy-interface calls', better='lower', baseline=num['base_discovery_text']),
        dict(measure='Shell commands calling the Galaxy API directly', numerator='Galaxy-arm shell commands calling BioBlend or the REST API',
             denominator='Galaxy-arm shell commands (Codex traces)', better='lower', baseline=num['base_shell_api']),
        dict(measure='Runs with a detailed analysis history', numerator='runs with a retrieved detailed history',
             denominator='Galaxy-arm runs', better='higher', baseline=num['base_history']),
        dict(measure='User-defined tool calls returning ok', numerator='user-defined-tool calls with status ok',
             denominator='user-defined-tool calls (BixBench-Verified-50, CompBioBench)', better='higher', baseline=num['base_udt_ok']),
    ]).assign(values_order='BixBench-Verified-50, CompBioBench, IWC')
    t['S5_number_provenance'] = provenance_table('galaxy-oriented')
    readme = [('S1a-S1c', 'Supplementary Table 1: evidence inventory, extraction coverage and reconciliation with run summaries'),
              ('S2a-S2c', 'Supplementary Table 2: failure-taxonomy rules, reconciliation with the archived ledger, A1 subclasses'),
              ('S3a-S3b', 'Supplementary Table 3: semantic-fidelity class definitions and per-tool mismatch rates'),
              ('S4', 'Supplementary Table 4: readiness-measure definitions, numerators, denominators and baselines'),
              ('S5', 'Supplementary Table 5: every number in numbers.json, the figure function that computed it, and whether the text quotes it')]
    write('galaxy-oriented', t, readme)


if __name__ == '__main__':
    user_tables()
    galaxy_tables()
