"""Official terminology for all figures, legends, tables and supplementary files (single source of truth).

Status: 'Original' = adopted as supplied by the authors; 'Sharpened' = supplied entry made more precise for this study;
'New' = concept the paper uses that the supplied glossary did not define. 'Replaces' lists retired wording.
Run from the repository root to write glossary/Glossary.md, .xlsx and .docx:  python manuscript_material/scripts/glossary.py
"""
import os

GROUPS = [
    ('Study structure', [
        ('Benchmark', 'New', 'A published collection of tasks with its own evaluator and endpoint. The three benchmarks are analysed separately and never pooled.',
         'BixBench-Verified-50 (50 tasks); CompBioBench (100 tasks); IWC (10 tasks)', ''),
        ('Platform-neutral benchmark', 'New', 'A benchmark whose tasks prescribe neither a workbench nor an analytical route.',
         'BixBench-Verified-50; CompBioBench', 'platform-neutral tasks or questions'),
        ('Workflow-derived benchmark', 'New', 'A benchmark whose tasks are derived from curated, published Galaxy workflows and are therefore aligned with installed Galaxy tools by design.',
         'IWC (Intergalactic Workflow Commission) benchmark', 'workflow-derived tasks'),
        ('Task', 'Original', 'One independently evaluated analytical problem within a benchmark, comprising the question or objective and the inputs needed for the analysis.',
         'One BixBench question; one CompBioBench problem; one IWC workflow-derived task', ''),
        ('Model configuration', 'Sharpened', 'The evaluated AI setup: the underlying model plus its agent harness and, where relevant, its reasoning setting. '
         'Always name the full configuration: the agent harness differs between configurations in this study, so "model" is never used as shorthand.',
         'GPT-5.5; GPT-5.6 Sol; GPT-5.6 Luna; DeepSeek V4 Pro (Codex); DeepSeek V4 Pro (Claude Code, superseded; BixBench only)', 'configuration; model; agent configuration'),
        ('Agent harness', 'New', 'The software that runs a model as an agent: it issues tool calls, executes commands and manages the conversation.',
         'Codex (four model configurations); Claude Code (the superseded DeepSeek V4 Pro configuration)', 'harness'),
        ('Execution condition', 'Sharpened', 'The experimental arm defining how the agent may perform the computational analysis. The open-ended code condition is the reference condition '
         'and is shown first in every figure and table.', 'Galaxy condition; open-ended code condition', 'environment; track; arm'),
        ('Galaxy condition', 'Original', 'The arm in which the agent performs the analysis through the Galaxy workbench, using its programmatic interface and Galaxy analytical resources. '
         'Formal first-use name: Galaxy-mediated execution. The label records condition assignment; it does not certify that every operation ran inside Galaxy.',
         'GPT-5.6 Sol solving a CompBioBench task through Galaxy', 'Galaxy environment; Galaxy track'),
        ('Open-ended code condition', 'Original', 'The arm in which the agent freely writes and executes code and invokes command-line tools, packages and other resources, '
         'without being restricted to Galaxy. Formal first-use name: open-ended code execution.', 'Agent using Python, R, shell commands or installed packages',
         'code environment; code track; custom code'),
        ('Run', 'Original', 'One complete execution of one task by one model configuration under one execution condition in one replicate run. This is the atomic experimental observation.',
         'GPT-5.6 Sol × bix-30-q3 × Galaxy condition × replicate run 2', ''),
        ('Replicate run', 'Original', 'One repetition of the same task × model configuration × execution condition. Replicate labels are not matched random seeds. '
         'CompBioBench replicates are final campaign selections and may include continuations.', 'Replicate run 1, 2 or 3', 'replicate; r1, r2, r3'),
        ('Replicate set', 'Sharpened', 'The replicate runs for one task × model configuration × execution condition (up to three runs). Classified by outcome repeatability as '
         'unanimous or split. Called the "cell" of the data table only once, in Methods.', 'The three Galaxy runs of GPT-5.6 Sol on bix-30-q3', 'triplicate; cell'),
        ('Split replicate set', 'New', 'A replicate set whose replicate runs disagree in outcome: 1–2 of 3 scored correct (BixBench); 1–2 of 3 matching the consensus answer '
         '(CompBioBench, consensus proxy); or a within-set range of output agreement above 0.05 (IWC). A unanimous set has 3/3 or 0/3.',
         '28 split Galaxy replicate sets versus 33 open-ended code sets in BixBench', 'mixed cell; non-unanimous triplicate'),
        ('Model–condition set', 'Original', 'All runs for one model configuration under one execution condition within a benchmark; tasks and replicate runs vary.',
         'All GPT-5.6 Sol Galaxy runs across the 50 BixBench tasks', ''),
        ('Task–condition set', 'Original', 'All runs for one task under one execution condition; model configurations and replicate runs vary.', 'All Galaxy runs for bix-30-q3', ''),
        ('Condition-level summary', 'Original', 'A result summarized across the evaluated model configurations, tasks and replicate runs for one execution condition within a benchmark.',
         'Galaxy-condition accuracy on BixBench', ''),
        ('Run population', 'Original', 'The exact collection of runs included in a reported statistic, identifiable from benchmark, model configurations, conditions, tasks and replicate runs.',
         '50 tasks × 4 model configurations × 3 replicate runs = 600 runs per condition', ''),
    ]),
    ('Outcomes and comparisons', [
        ('Accuracy', 'Sharpened', 'The proportion of runs in a stated run population that the benchmark evaluator scored correct. Used only for BixBench, the one benchmark '
         'with binary evaluator verdicts. Runs that submitted no answer count as scored incorrect.', '134 of 150 GPT-5.5 Galaxy runs scored correct on BixBench (89.3%)',
         'acceptance; accepted answers; success rate'),
        ('Scored-correct run; scored-incorrect run', 'New', 'A run whose final answer the benchmark evaluator accepted (scored correct) or rejected (scored incorrect). '
         '"Rejected" describes the evaluator\'s action; the run itself is "scored incorrect".', '246 scored-incorrect BixBench runs (111 Galaxy, 135 open-ended code)',
         'rejected run; failed run; failure (for runs)'),
        ('Output agreement', 'Original', 'A continuous measure (0–1) of agreement between a run\'s output and the reference output, used when the benchmark endpoint is continuous. '
         'Never converted to accuracy.', 'IWC output agreement for one run', 'agreement; score (for IWC)'),
        ('Mean output agreement', 'Original', 'The mean output agreement across a stated run population.',
         'Mean IWC output agreement of 0.980 in the Galaxy condition (nine matched tasks)', 'mean agreement'),
        ('Reported benchmark score', 'Original', 'An aggregate score taken from archived answer vectors that cannot be reconstructed per run. It is neither accuracy nor output agreement.',
         'CompBioBench, GPT-5.6 Sol Galaxy replicate run 1: 93/100 (labelled official)', 'aggregate score; vector score; answer-vector score'),
        ('Consensus proxy', 'New', 'For CompBioBench only: the most common answer across the 25 runs of a task, used to flag probable failures because per-run grades are not archived. '
         'Applied only to the 82 tasks where at least 20 of 25 runs agree, and always labelled as a proxy.',
         'Reproduces reported benchmark scores with a mean absolute error of 2.6 of 100', 'modal answer'),
        ('Performance', 'Sharpened', 'Umbrella term for benchmark outcomes. Use it only when a statement holds for every endpoint involved; otherwise name the metric. '
         'Never use accuracy as the umbrella term.', '"Performance was similar between execution conditions in all three benchmarks."', 'accuracy (as umbrella term)'),
        ('Score conflict', 'Original', 'A run whose evaluator score differs from its run-record score, or where one of the two is missing.', '17 of 240 IWC records',
         'scoring artefact'),
        ('Condition difference', 'Original', 'Galaxy condition minus open-ended code condition, holding the run population constant. The sign convention is always Galaxy − open-ended code.',
         '+1.33 percentage points in accuracy on BixBench', 'environment difference; Galaxy − code'),
        ('Model difference', 'Original', 'A comparison between model configurations under a specified execution condition and benchmark, always against a named reference model configuration.',
         'GPT-5.6 Sol versus GPT-5.5 in the Galaxy condition: −0.67 percentage points', ''),
        ('Task-level condition difference', 'Original', 'A condition difference for one task, across a stated set of model configurations and replicate runs.',
         'bix-45-q1: Galaxy 0/15 versus open-ended code 8/15 scored correct', ''),
        ('Outcome repeatability', 'Original', 'Consistency of outcomes (evaluator verdicts or output agreement) across the replicate runs of one replicate set.',
         'Within-set range of IWC output agreement', 'replicate dispersion'),
        ('Repeatability category', 'Original', 'The categorical form of outcome repeatability for binary endpoints: 3/3, 1–2/3 or 0/3 replicate runs scored correct.',
         '44 of 50 GPT-5.5 Galaxy replicate sets at 3/3 on BixBench', ''),
        ('Answer consistency', 'Original', 'Identical submitted answer text across replicate runs, with no implication of correctness. Used where evaluator verdicts are unavailable.',
         '62 of 100 CompBioBench tasks with one distinct answer across all 12 Galaxy runs', ''),
        ('Estimand', 'Original', 'The specific quantity being summarized or compared. Used mainly in Methods.', 'Condition difference in accuracy', ''),
    ]),
    ('Analysis process and Galaxy records', [
        ('Analysis trajectory', 'Original', 'The sequence of analytical actions an agent takes during a run to reach, or attempt to reach, its final answer. It does not imply the answer was scored correct.',
         'Inspect data → filter → run DESeq2 → inspect output → submit answer', 'solution path; path'),
        ('Execution trace', 'Original', 'The recorded evidence documenting an analysis trajectory: agent messages, commands, tool calls, Galaxy jobs and outputs.',
         'Codex trace plus Galaxy history', 'agent trace; transcript'),
        ('Analytical operation', 'Original', 'A scientifically meaningful computational action within an analysis trajectory.', 'Alignment, filtering, differential expression, enrichment', ''),
        ('Tool-set fingerprint', 'Original', 'An unordered set of tool identifiers (Galaxy) or command names (open-ended code) used in a run. It does not encode operation order, parameters or biological decisions.',
         'Set of version-stripped Galaxy tool IDs used in one run', 'recorded path'),
        ('Tool-set similarity', 'Original', 'Overlap between tool-set fingerprints across the replicate runs of a replicate set, measured as mean pairwise Jaccard similarity.',
         'Mean Galaxy tool-set similarity of 0.616 (IWC) versus 0.134 (CompBioBench)', 'path agreement; Jaccard index'),
        ('Declared route', 'Original', 'The analytical method an agent states it used. It is not independently verified and is distinct from the tool-set fingerprint.',
         'DESeq2 versus edgeR for IWC RNA-seq differential expression', ''),
        ('Galaxy interface call', 'New', 'One call from the agent to Galaxy through the programmatic interface of the Galaxy condition (a Model Context Protocol server), '
         'such as a tool search, tool inspection or job submission.', '69,812 Galaxy interface calls, of which 7,389 returned a failure status', 'MCP call'),
        ('Direct Galaxy API call', 'New', 'A shell command that calls Galaxy\'s web API or the BioBlend library directly, outside the Galaxy interface.',
         'Copying the provided analysis history in 537 of 600 Codex BixBench Galaxy runs', 'BioBlend or raw REST bypass'),
        ('Analysis history', 'New', 'The Galaxy record (history) of the datasets, jobs, tools and parameters produced during a run.',
         '714 of 750 BixBench Galaxy runs have a detailed analysis-history snapshot', 'history (unqualified)'),
        ('Galaxy analysis job', 'New', 'A Galaxy job other than a data-fetch (upload) job, counted once per server and job identifier.',
         '23,080 Galaxy analysis jobs (5,042 BixBench; 16,686 CompBioBench; 1,352 IWC)', 'non-fetch job'),
        ('Installed Galaxy tool', 'Original', 'A Tool Shed wrapper available on the Galaxy server. Subdivided into domain tools and utility tools.', 'Any wrapper in the server\'s tool panel',
         'installed wrapper'),
        ('Domain tool', 'Original', 'An installed Galaxy tool implementing a domain-specific analytical method.', 'fastp, DADA2, PepQuery, Bowtie2',
         'domain-analysis tool; non-utility Tool Shed job'),
        ('Utility tool', 'Original', 'An installed Galaxy tool for generic data handling.', 'Cut, Filter, xlsx2tsv, Datamash', 'file or table utility'),
        ('User-defined tool (UDT)', 'Original', 'A custom tool written by the agent and executed through Galaxy\'s interface.', 'Custom wrapper for PhyKIT treeness in bix-11-q1', ''),
        ('Probe tool', 'New', 'A throwaway user-defined tool written only to find out why jobs fail, because Galaxy offers no trial run.',
         '1,859 probe-tool calls in 517 of 808 CompBioBench runs that used user-defined tools', 'probe UDT'),
        ('Parameter substitution', 'New', 'A difference between the parameter values an agent requested in a Galaxy tool-run call and the tool state Galaxy resolved from them '
         '(a value replaced, or a requested value dropped). It is either blocked before submission by the benchmark\'s check or executed.',
         '4,352 tool-run calls, 916 executed (for example, Datamash max → count)', 'parameter mismatch; requested-versus-resolved difference'),
        ('Operational error', 'Original', 'A failed computational operation during a run. It does not by itself imply that the final answer was scored incorrect. '
         'Always reported through one of its two instrument-specific subtypes.', 'Galaxy job error; nonzero shell exit', 'failure (for operations)'),
        ('Galaxy job error', 'Sharpened', 'A Galaxy analysis job that ends in error state. Not comparable with nonzero shell exits.',
         '552 of 5,042 BixBench Galaxy analysis jobs', 'error job; failed job'),
        ('Nonzero shell exit', 'Original', 'A shell command that returns a nonzero exit code. It can reflect probes or searches rather than analytical failure.',
         'Failed package check or empty search result', 'failed shell command'),
        ('Candidate recovery', 'Original', 'An operational error followed by a later successful related action, not yet manually adjudicated. This is the default term.',
         '93 candidate recoveries in BixBench', 'recovery (unqualified)'),
        ('Verified recovery', 'Original', 'A candidate recovery that manual review confirms: the agent overcame the failure while keeping the same analytical objective.',
         'String columns cast to numeric before a repeated calculation (bedtools-chromhmm-q1)', ''),
        ('Input-token usage', 'Original', 'Input tokens consumed by a run or run population, according to archived usage records (cached input included; output and reasoning tokens not added).',
         'Median of 1.19 million input tokens per GPT-5.5 Galaxy run on BixBench', 'input tokens; token burden'),
        ('Input-token ratio', 'Original', 'Median Galaxy input-token usage divided by median open-ended code input-token usage, for the same task and model configuration.',
         'Median ratio of 4.74 on BixBench', 'token overhead; token multiplier'),
    ]),
    ('Adjudication', [
        ('Primary cause; secondary cause', 'New', 'The main reason, and at most one contributing reason, for a scored-incorrect run (or an IWC run with output agreement below 0.5), '
         'assigned by trace-level adjudication from seven categories: task under-specified or reference ambiguous; statistical or reasoning error; evaluator rejected a correct answer; '
         'missing domain knowledge; platform or tool defect; no answer submitted; output format violated.',
         'Galaxy platform or tool defect: primary in 4 and secondary in 18 of 111 scored-incorrect Galaxy runs', 'root cause'),
        ('Adjudication confidence', 'New', 'How firmly the decisive step of a scored-incorrect run was established: high, moderate, mixed or unresolved (Supplementary Note 6).',
         '159 high, 55 moderate, 20 mixed and 12 unresolved of 246 BixBench adjudications', ''),
        ('Divergence mechanism', 'New', 'What separated a scored-incorrect replicate run from its scored-correct sibling(s) in a split replicate set. Distinct from its primary cause.',
         'Hand-written method or software-version difference: 30 of 45 open-ended code runs versus 5 of 36 Galaxy runs', ''),
        ('Verifier mode', 'New', 'The rule the BixBench evaluator uses to compare a numeric answer with the reference: tolerance (within a stated margin) or rounded-numeric (after rounding).',
         'bix-43-q2: 5.831005… scored correct under the tolerance verifier and incorrect under the rounded-numeric verifier', ''),
    ]),
]


def rows():
    return [(g, *r) for g, rr in GROUPS for r in rr]


def write_all(outdir):
    import pandas as pd
    from docx import Document
    from docx.shared import Pt
    os.makedirs(outdir, exist_ok=True)
    head = ['Group', 'Official term', 'Status', 'Definition', 'Example in this study', 'Replaces (do not use)']
    df = pd.DataFrame(rows(), columns=head)
    df.to_excel(os.path.join(outdir, 'Glossary.xlsx'), index=False)
    md = ['# Glossary of official terms', '',
          'Applies to all figures, legends, Supplementary Information, Supplementary Tables and Supplementary Data. Status: Original = adopted as supplied; '
          'Sharpened = supplied entry made more precise; New = term the paper needs that the supplied glossary did not define.', '']
    for g, rr in GROUPS:
        md += [f'## {g}', '', '| Official term | Status | Definition | Example in this study | Replaces (do not use) |', '|---|---|---|---|---|']
        md += [f'| {t} | {s} | {d} | {e} | {r} |' for t, s, d, e, r in rr]
        md.append('')
    open(os.path.join(outdir, 'Glossary.md'), 'w').write('\n'.join(md))
    doc = Document()
    doc.styles['Normal'].font.name, doc.styles['Normal'].font.size = 'Arial', Pt(8)
    doc.add_heading('Glossary of official terms', 1)
    for g, rr in GROUPS:
        doc.add_heading(g, 2)
        t = doc.add_table(rows=1, cols=5)
        t.style = 'Light Grid Accent 1'
        for c, h in zip(t.rows[0].cells, head[1:]):
            c.text = h
        for r in rr:
            for c, v in zip(t.add_row().cells, r):
                c.text = v
    doc.save(os.path.join(outdir, 'Glossary.docx'))
    return df


if __name__ == '__main__':
    df = write_all(os.path.join(os.path.dirname(__file__), '..', 'glossary'))
    print(df['Status'].value_counts().to_dict(), len(df), 'terms')
