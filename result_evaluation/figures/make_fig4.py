"""Fig. 4: Answer agreement and tool use vary across model configurations.

Panels:
a, what each model ran in Galaxy: the share of its traced Galaxy runs with at least one completed job in each method
   family, by benchmark (the same stage as Fig. 3b: completed jobs); data handling is separated from scientific methods,
   and user-defined tools (UDTs) are one row because their methods have not been annotated. The family codebook is
   written to figures/fig4_tool_family_codebook.csv;
b, the share of replicate sets (three runs of one task by one model in one condition) that gave the same answer in all
   three runs, for BixBench-Verified-50 and CompBioBench, paired by condition; a set with a missing submission does not
   agree. P values test a model effect within each benchmark and condition (model labels permuted within tasks), Holm-
   adjusted over the four tests;
c, tool-set similarity against task accuracy, one facet per benchmark: the mean pairwise Jaccard index of the three
   replicate runs' sets of tools (installed tools by Tool Shed identifier without version, plus one item for any UDT),
   for task-model cells whose three runs all completed a job. It ignores order, repetition, versions and parameters;
d, every replicate set's outcome by held-out task difficulty (the share of the task's other 21 runs that were
   incorrect, so the set's own runs never define its difficulty), one facet per model: all three accepted, mixed,
   all rejected with different answers, the same rejected answer in all three runs, or a missing submission.

Extended Data Fig. 4: a, the 15 installed tools in the most Galaxy runs (completed jobs), per model; b, tool-set
similarity by model and benchmark, with sensitivity analyses; c, answer agreement under three answer-matching rules.

A run is correct when accepted or, for IWC, at >= 0.99 output agreement. Intervals are 95% percentile cluster-bootstrap
intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Writes figures/fig4.{svg,pdf,png},
fig4_source_data.csv, fig4_tool_family_codebook.csv, ed_fig4.{svg,pdf,png} and ed_fig4_source_data.csv.
"""
# result_evaluation copy of figures/make_fig4.py: scores come from scored_runs.csv (make_scored_runs.py; every run matched to
# the public results site, IWC host-read removal included) and every output is written next to this script. The
# manuscript figure set in figures/ is not touched. Changes from the original are marked "result_evaluation:".
import glob
import gzip
import io
import itertools
import json
import os
import re
import sys

import numpy as np
import panel_io  # noqa: E402  (figures/panel_io.py)
import pandas as pd
from scipy.stats import rankdata

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))   # result_evaluation: two levels up
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
import style  # noqa: E402  (sets rcParams on import)
from style import plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})
style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition

AN = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis')
GC = os.path.join(ROOT, 'manuscript_narrative', 'derived', 'galaxy_calls')
EVIDENCE = [os.path.join(ROOT, 'BixBench_50', 'analysis', '*', 'history_analysis_evidence.json'),
            os.path.join(ROOT, 'CompBio', 'analysis', '*', 'history_analysis_evidence.json')]
OUT = os.path.dirname(os.path.abspath(__file__))   # result_evaluation: write here, not to figures/
FIGS = os.path.join(ROOT, 'figures')               # result_evaluation: unchanged inputs from the manuscript figure set
SCORED = os.path.join(OUT, 'scored_runs.csv')      # result_evaluation: per-run scores matched to the results site
B, SEED, B_PERM = 20000, 20261002, 20000
W, MM = 180.0, 1 / 25.4
CFG = style.CONFIGS
ENVS = style.ENVS                                    # custom code first, always
CODE, GAL = ENVS
BENCH = style.BENCH
QA = ['BixBench50', 'CompBio']                       # benchmarks with a submitted answer
BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
BENCH_SHORT = {'BixBench50': 'BixBench', 'CompBio': 'CompBio', 'IWC': 'IWC'}
BENCH_MARK = {'BixBench50': ('^', '#E69F00'), 'CompBio': ('D', '#56B4E9'), 'IWC': ('v', '#FFAABB')}
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
# Model identity (Paul Tol muted green, purple, sand and indigo); every pair differs by >= 25 (OKLab x 100) in normal
# vision and >= 13 under simulated colour-vision deficiencies.
MODEL_COLOR = dict(zip(CFG, ['#117733', '#AA4499', '#DDCC77', '#332288']))
MODEL_SHORT = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'Sol', 'GPT-5.6 Luna': 'Luna', 'DeepSeek V4 Pro': 'DeepSeek'}
TRACE_MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
               'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
               'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}     # the superseded Claude Code harness is excluded
# Panel a: method families of installed Galaxy tools. Ordered rules on the tool identifier (Tool Shed repository and
# tool, or built-in ID); the first match wins. Every tool and its family is written to the codebook.
DATA_FAMILIES = ['Tables and text', 'Format conversion and upload', 'Inspection and quality control',
                 'Data retrieval']
FAMILY_RULES = [
    ('Data retrieval', r'ncbi_datasets|ncbi_acc_download|pysradb|fasterq_dump|sra_tools|seurat_data|snpeff_databases|'
                       r'snpeff_download|ucsc_table_direct|get_online_data|get_pdb|ctb_online'),
    ('Inspection and quality control', r'anndata_inspect|scanpy_inspect|inspect_eset|fastqc|samtools_flagstat|'
                                       r'samtools_idxstats|samtools_stats|fasta_stats|fastq_stats|fastq_info|'
                                       r'seq_composition|fasta_compute_length|gfastats|seqtk_comp|seqtk_fqchk|'
                                       r'bcftools_stats|multiqc|plotqualityprofile|summarize'),
    ('Format conversion and upload', r'^converter_|xlsx2tsv|csv_to_tabular|tabular_to_csv|unzip|^upload1$|__data_fetch__|'
                                     r'rds_to_tabular|anndata_import|anndata_export|sceasy|fasta2tab|tab2fasta|'
                                     r'fasta_to_tabular|fastq_to_tabular|fastq_to_fasta|fastqtofasta|bam_to_sam|'
                                     r'gff2bed|gtftobed12|bigbedtobed|bigwigtowig|wiggle2simple|biom_convert|'
                                     r'maf_to_fasta|lped2pbed|gfa_to_fa|samtools_fastx|bamtofastq|twobittofa|'
                                     r'wigtobigwig|qiime2_core__tools__(import|export)|mcmicro_to_anndata|'
                                     r'mtx_to_10x|read10x|read_10x|seqret|imagemagick|interval2maf|archive|'
                                     r'compress_file|fasta_formatter|interlacer'),
    ('Read processing and alignment', r'fastp|trim|cutadapt|umi_tools|bwa|bowtie|minimap2|hisat2|rna_star|picard|'
                                      r'samtools_view|samtools_sort|samtools_merge|samtools_collate|samtool_filter|'
                                      r'samtools_slice|samtools_phase|sambamba|bamtools|ngsutils|sinto|seqtk|seqkit|'
                                      r'sample_seqs|crossmap|liftover|fastx_|fasta_nucleotide_changer'),
    ('Variant calling and annotation', r'freebayes|bcftools|snpeff|snpsift|samtools_mpileup|lofreq|varscan|gatk|plink|'
                                       r'vcf|ivar_|arriba'),
    ('Expression and differential testing', r'deseq2|edger|limma|featurecounts|salmon|kallisto|alevin|stringtie|'
                                            r'isoformswitch|decoupler|music_|rseqc|gffcompare|htseq|cuffdiff|pizzly'),
    ('Single-cell and spatial analysis', r'scanpy|anndata|seurat|snapatac2|squidpy|scimap|dropletutils|harmony'),
    ('Genomic intervals and sequence features', r'bedtools|bedops|extract genomic dna|gene2exon|flanking|get_flanks|'
                                                r'gtf_filter|gff_filter|extract_features|emboss|orfipy|transdecoder|'
                                                r'fasta_regex|find_subsequences|filter_by_length|filter_by_fasta_ids|'
                                                r'seq_filter_by_id|translate|mosdepth|samtools_depth|'
                                                r'samtools_coverage|samtools_bedcov|deeptools|agat|gffread|splitfasta|'
                                                r'fasta_merge|createinterval|gtf2gene_list|gops_|count_gff|chainswap'),
    ('Phylogenetics', r'phykit|mafft|iqtree|raxml|clustal|muscle'),
    ('Sequence search, taxonomy and assembly', r'blast|kraken|staramr|meme|vsearch|mothur|dada2|qiime2|diamond|hmmer|'
                                               r'mitohifi|flye|hifiasm|trinity|spades|busco|quast|meryl|megahit|weblogo'),
    ('Peak calling and epigenomics', r'macs2|genrich|chipseeker|homer'),
    ('Statistics, machine learning and enrichment', r'correlation|rank_tests|gseapy|kegg|gprofiler|univariate|'
                                                    r'multivariate|transformation|summary_statistics|sklearn|'
                                                    r'model_prediction|scipy|pca|calculate_numeric|annotatemyids|'
                                                    r'scatterplot|ggplot'),
    ('Tables and text', r'^cut1$|^filter1$|^grep1$|^join1$|^sort1$|grouping1|count1|paste1|^comp1$|^cat1$|wc_gnu|'
                        r'remove beginning|show beginning|show tail|convert characters|addvalue|datamash|filter_tabular|'
                        r'column_maker|add_a_column|text_processing|table_compute|query_tabular|regex|changecase|'
                        r'mergecols|random_lines|column_remove|replace_column|split_file|unique|diff|add_line_to_file|'
                        r'collapse|cat_multi|^__|table_pandas|collection_|secure_hash|^tp_|datamash_transpose|melt|'
                        r'subtract_query'),
    ('Other methods', r'.'),
]
METHOD_FAMILIES = [f for f, _ in FAMILY_RULES if f not in DATA_FAMILIES]
FAMILIES = DATA_FAMILIES + METHOD_FAMILIES
TOOL_LABEL = {
    'toolshed.g2.bx.psu.edu/repos/iuc/filter_tabular/filter_tabular': 'Filter tabular', 'Cut1': 'Cut columns',
    'toolshed.g2.bx.psu.edu/repos/iuc/datamash_ops/datamash_ops': 'Datamash',
    'toolshed.g2.bx.psu.edu/repos/devteam/column_maker/Add_a_column1': 'Compute column',
    'toolshed.g2.bx.psu.edu/repos/ufz/xlsx2tsv/xlsx2tsv': 'XLSX to TSV', 'Filter1': 'Filter rows',
    'csv_to_tabular': 'CSV to tabular', 'Grep1': 'Select lines',
    'toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem': 'BWA-MEM',
    'toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_grep_tool': 'Search text (grep)',
    'toolshed.g2.bx.psu.edu/repos/goeckslab/phykit_metrics/phykit_metrics': 'PhyKIT metrics',
    'toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_sort_header_tool': 'Sort with header',
    'toolshed.g2.bx.psu.edu/repos/iuc/anndata_inspect/anndata_inspect': 'Inspect AnnData', 'Grouping1': 'Group',
    'join1': 'Join datasets', 'toolshed.g2.bx.psu.edu/repos/iuc/bedtools/bedtools_intersectbed': 'Bedtools intersect',
    'toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_head_tool': 'Select first lines',
    'CONVERTER_gz_to_uncompressed': 'Uncompress', 'Summary_Statistics1': 'Summary statistics',
    'toolshed.g2.bx.psu.edu/repos/devteam/samtools_idxstats/samtools_idxstats': 'Samtools idxstats',
    'toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2': 'DESeq2',
    'toolshed.g2.bx.psu.edu/repos/iuc/anndata_export/anndata_export': 'Export AnnData',
}
N_TOOLS = 15
# Panel d: held-out difficulty bins (incorrect runs among the task's 21 other runs) and replicate-set outcomes.
DIFF_BINS = [(0, 0, '0'), (1, 2, '1–2'), (3, 10, '3–10'), (11, 21, '11–21')]
OUTCOMES = [('same_rejected', 'Same rejected answer in all three runs', '#CC79A7'),
            ('rejected_differ', 'All rejected, answers differ', '#009E73'),
            ('mixed', 'Mixed: one or two accepted', '#88CCEE'),
            ('missing', 'Missing submission', style.NEUTRAL_DARK),
            ('all_accepted', 'All three accepted', '#E8E8E8')]
MATCH_RULES = [('exact', 'Exact text (trimmed, lower case)'), ('3sig', 'Numbers to 3 significant digits'),
               ('2sig', 'Numbers to 2 significant digits'),
               ('task', 'Task-aware: benchmark tolerance, lists as sets (primary)')]
RUN_SUMMARIES = os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz')
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- statistics
def holm(p):
    p = np.asarray(p, float)
    order, adj, run = np.argsort(p), np.empty(len(p)), 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(1.0, run)
    return adj


def boot_means(frames, group_cols, value):
    point, num, den = None, 0.0, 0.0
    for _, d in frames.groupby('benchmark'):
        s = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='sum').fillna(0)
        n = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='count').fillna(0)
        wts = rng.multinomial(len(s), np.full(len(s), 1 / len(s)), size=B)
        num = num + wts @ s.values
        den = den + wts @ n.values
        point = (s.sum(), n.sum()) if point is None else (point[0] + s.sum(), point[1] + n.sum())
    est = point[0] / point[1]
    return est, pd.DataFrame(num / den, columns=est.index)


def model_effect_p(cells, value='sim'):
    """Permutation test of a model effect: model labels permuted within each task."""
    groups = [g for _, g in cells.groupby('task')]
    vals = [g[value].values for g in groups]
    labs = [np.array([CFG.index(c) for c in g.cfg]) for g in groups]

    def stat(lab_list):
        s, n = np.zeros(len(CFG)), np.zeros(len(CFG))
        for v, l in zip(vals, lab_list):
            np.add.at(s, l, v)
            np.add.at(n, l, 1)
        m, grand = s / np.maximum(n, 1), sum(v.sum() for v in vals) / sum(len(v) for v in vals)
        return float(np.sum(n * (m - grand) ** 2))
    observed = stat(labs)
    hits = sum(stat([rng.permutation(l) for l in labs]) >= observed - 1e-12 for _ in range(B_PERM))
    return observed, (1 + hits) / (B_PERM + 1)


def spearman_perm(x, y, strata):
    """Spearman correlation with a permutation P value, y permuted within strata."""
    x, y, strata = np.asarray(x), np.asarray(y), np.asarray(strata)
    rx = rankdata(x)

    def rho(yy):
        return np.corrcoef(rx, rankdata(yy))[0, 1]
    observed = rho(y)
    idx = [np.where(strata == s)[0] for s in np.unique(strata)]
    hits = 0
    for _ in range(B_PERM):
        yy = y.copy()
        for i in idx:
            yy[i] = y[rng.permutation(i)]
        hits += abs(rho(yy)) >= abs(observed) - 1e-12
    return observed, (1 + hits) / (B_PERM + 1)


# ---------------------------------------------------------------- data
def load_runs():
    r = pd.read_csv(SCORED)
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    return r


def load_calls():
    c = pd.read_csv(os.path.join(GC, 'calls.csv.gz'), low_memory=False,
                    usecols=['benchmark', 'task', 'model', 'replicate', 'tool', 'galaxy_server', 'n_jobs', 'job_states',
                             'tool_id_base', 'tool_id_full', 'run_id', 'line'])
    c = c[c.model.isin(TRACE_MODEL) & c.galaxy_server].assign(cfg=lambda x: x.model.map(TRACE_MODEL))
    c['completed'] = c.job_states.fillna('').str.contains(r'(?:^|;)ok(?=;|$)')
    cov = pd.read_csv(os.path.join(GC, 'run_coverage.csv'))
    cov = cov[cov.model.isin(TRACE_MODEL)].assign(cfg=lambda x: x.model.map(TRACE_MODEL))
    return c, cov[['benchmark', 'task', 'cfg', 'replicate']].drop_duplicates()


def task_tolerance():
    """Absolute numeric tolerance of the BixBench-Verified-50 evaluator for each task that has one."""
    tol = {}
    for line in gzip.open(RUN_SUMMARIES, 'rt'):
        s = json.loads(line)
        if s['benchmark'] == 'BixBench50' and s.get('tolerance') not in (None, 'None', ''):
            tol[s['task']] = float(s['tolerance'])
    return tol


def parse_answer(x):
    """Task-aware form of an answer: a number (thousands separators, % and a trailing unit removed), a set of items
    (lists split on commas, semicolons or spaces; identifier version suffixes removed) or compact text."""
    if x is None:
        return None
    s = str(x).strip().strip('"\'').strip().rstrip('.').lower()
    t = s.replace(',', '') if re.fullmatch(r'[-+]?\d{1,3}(,\d{3})+(\.\d+)?', s) else s
    t = re.sub(r'\s*(%|percent)$', '', t)
    m = re.match(r'^([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[-+]?\d+)?)\s*[a-zµ/]*$', t)
    if m:
        return ('num', float(m.group(1)))
    strip_version = lambda v: re.sub(r'^(ens[a-z]*\d+)\.\d+$', r'\1', v)      # noqa: E731
    items = [v for v in re.split(r'[;,\s]+', s) if v]
    if len(items) > 1:
        return ('set', frozenset(strip_version(v) for v in items))
    return ('text', strip_version(re.sub(r'\s+', '', s)))


def answers_agree(values, tol):
    """All submitted answers of a set agree: numbers within the task tolerance (or 0.1% when the benchmark gives
    none), other answers identical in task-aware form."""
    if any(v is None for v in values):
        return 0
    for a, b in itertools.combinations(values, 2):
        if a[0] == 'num' and b[0] == 'num':
            lim = tol if tol is not None else 1e-3 * max(abs(a[1]), abs(b[1]))
            if abs(a[1] - b[1]) > lim + 1e-12:
                return 0
        elif a != b:
            return 0
    return 1


def normalize_answer(x, rule='3sig'):
    """Answers compared as text after trimming and lower-casing; numbers rounded per rule."""
    if x is None:
        return None
    s = re.sub(r'\s+', ' ', str(x).strip().strip('"\'').lower())
    if rule != 'exact':
        try:
            return f'{float(s):.{3 if rule == "3sig" else 2}g}'
        except ValueError:
            pass
    return s.replace(' ', '')


def load_answers():
    """Submitted answer of every BixBench-Verified-50 and CompBioBench run, normalized three ways (compared here, never
    written out)."""
    rows = []
    for path in sorted(p for pattern in EVIDENCE for p in glob.glob(pattern)):
        d = json.load(open(path))
        bm = 'BixBench50' if os.sep + 'BixBench_50' + os.sep in path else 'CompBio'
        for run in d['runs']:
            model = re.sub(r'_r\d+$', '', re.sub(r'^(galaxy|open_ended_code)_', '', run['run_id']))
            if model in TRACE_MODEL:
                raw = (run.get('outcome') or {}).get('submitted_answer')
                rows.append(dict(benchmark=bm, task=d['task']['task_id'], cfg=TRACE_MODEL[model], env=run['condition'],
                                 replicate=run['replicate_id'], answer_task=parse_answer(raw),
                                 **{f'answer_{k}': normalize_answer(raw, k) for k, _ in MATCH_RULES if k != 'task'}))
    a = pd.DataFrame(rows)
    a['answer'] = a.answer_3sig
    return a


def family(tool):
    t = tool.split('/repos/')[-1].lower() if '/repos/' in tool else tool.lower()
    for name, rx in FAMILY_RULES:
        if re.search(rx, t):
            return name
    return 'Other methods'


# ---------------------------------------------------------------- panels: statistics
def panel_a(calls, traced):
    """Share of traced Galaxy runs with >= 1 completed job in each method family, per benchmark and model."""
    k = ['benchmark', 'task', 'cfg', 'replicate']
    runs = traced.groupby(['benchmark', 'cfg']).size()
    done = calls[calls.completed & calls.tool.isin(['run_galaxy_tool_and_wait', 'run_galaxy_udt_and_wait'])].copy()
    tools = done[done.tool == 'run_galaxy_tool_and_wait'].dropna(subset=['tool_id_base'])
    book = pd.DataFrame({'tool_id': sorted(tools.tool_id_base.unique())})
    book['family'] = book.tool_id.map(family)
    book['kind'] = np.where(book.family.isin(DATA_FAMILIES), 'data handling', 'scientific method')
    used = tools.assign(family=tools.tool_id_base.map(family))[k + ['family']].drop_duplicates()
    udt = done[done.tool == 'run_galaxy_udt_and_wait'][k].drop_duplicates().assign(family='UDT (agent-written code)')
    used = pd.concat([used, udt])
    tab = used.groupby(['family', 'benchmark', 'cfg']).size().unstack(['benchmark', 'cfg'], fill_value=0)
    cols = pd.MultiIndex.from_product([BENCH, CFG])
    tab = tab.reindex(index=FAMILIES + ['UDT (agent-written code)'], columns=cols, fill_value=0)
    pct = tab / runs.reindex(cols).values * 100
    book = book.merge(tools.drop_duplicates(k + ['tool_id_base']).groupby('tool_id_base').size().rename('runs'),
                      left_on='tool_id', right_index=True)
    return pct, tab, runs, book.sort_values(['kind', 'family', 'runs'], ascending=[True, True, False])


def top_tools(calls, traced):
    """Extended Data: the 15 installed tools with completed jobs in the most Galaxy runs, per model."""
    k = ['benchmark', 'task', 'cfg', 'replicate']
    runs = traced.groupby('cfg').size()
    used = calls[calls.completed & (calls.tool == 'run_galaxy_tool_and_wait')].dropna(subset=['tool_id_base'])
    used = used[k + ['tool_id_base']].drop_duplicates()
    overall = used.groupby('tool_id_base').size().sort_values(ascending=False) / runs.sum() * 100
    top = overall.head(N_TOOLS)
    per = (used.groupby(['tool_id_base', 'cfg']).size().unstack(fill_value=0) / runs * 100).reindex(top.index)[CFG]
    return top, per.fillna(0), runs.reindex(CFG)


def route_cells(calls, r, mode='all'):
    """Tool-set similarity of each task x model in the Galaxy condition (three runs, each with a completed job).
    mode 'all': installed tools plus one item for any UDT; 'installed': installed tools only."""
    ran = calls[calls.completed]
    inst = ran[ran.tool == 'run_galaxy_tool_and_wait'].dropna(subset=['tool_id_base']).assign(step=lambda x: x.tool_id_base)
    udt = ran[ran.tool == 'run_galaxy_udt_and_wait'].assign(step='UDT')
    steps = pd.concat([inst, udt] if mode == 'all' else [inst])
    fp = steps.groupby(['benchmark', 'task', 'cfg', 'replicate']).step.agg(frozenset).reset_index()
    rows = []
    for (bm, task, c), g in fp.groupby(['benchmark', 'task', 'cfg']):
        if len(g) == 3:
            f = list(g.step)
            sims = [len(a & b) / len(a | b) for a, b in itertools.combinations(f, 2)]
            route = 'installed only' if all('UDT' not in x for x in f) else (
                'UDT only' if all(x == frozenset({'UDT'}) for x in f) else 'mixed')
            rows.append(dict(benchmark=bm, task=task, cfg=c, sim=float(np.mean(sims)), route=route))
    cells = pd.DataFrame(rows)
    acc = r[r.env == GAL].groupby(['benchmark', 'task', 'cfg']).agg(cluster=('cluster', 'first'), ok=('ok', 'mean'))
    cells = cells.join(acc, on=['benchmark', 'task', 'cfg'])
    return cells[cells.cluster.notna()].reset_index(drop=True)      # scored tasks only (IWC host removal is not)


def _canon(v):
    """Parameter values with dataset references replaced and bookkeeping keys dropped, for comparing settings."""
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except ValueError:
            return v
    if isinstance(v, dict):
        if 'src' in v and ('id' in v or 'values' in v):
            return 'DATA'
        if isinstance(v.get('values'), list) and all(isinstance(x, dict) and 'src' in x for x in v['values']):
            return 'DATA'
        return {k: _canon(x) for k, x in sorted(v.items()) if not k.startswith('__') and k not in ('chromInfo', 'dbkey')}
    if isinstance(v, list):
        return [_canon(x) for x in v]
    return v


def job_steps(calls):
    """Completed analysis jobs of every traced Galaxy run, in order, from the retained Galaxy records: tool without
    version (UDTs as one item), tool with version, and tool with its non-dataset parameters."""
    udt_ids = set(calls[calls.tool == 'run_galaxy_udt_and_wait'].tool_id_full.dropna()) if 'tool_id_full' in calls \
        else set()
    rows = []
    paths = EVIDENCE + [os.path.join(ROOT, 'IWC', 'analysis', '*', 'history_analysis_evidence.json')]
    for path in sorted(p for pattern in paths for p in glob.glob(pattern)):
        d = json.load(open(path))
        bm = 'BixBench50' if os.sep + 'BixBench_50' + os.sep in path else (
            'CompBio' if os.sep + 'CompBio' + os.sep in path else 'IWC')
        for run in d['runs']:
            model = re.sub(r'_r\d+$', '', re.sub(r'^(galaxy|open_ended_code)_', '', run['run_id']))
            model = {'gpt_5_5': 'codex_gpt_5_5', 'gpt_5_6_sol': 'codex_gpt_5_6_sol', 'gpt_5_6_luna': 'codex_gpt_5_6_luna',
                     'deepseek_v4_pro': 'codex_deepseek_v4_pro'}.get(model, model)
            if run['condition'] != 'galaxy' or model not in TRACE_MODEL:
                continue
            evs = [e for e in run['events'] if e['execution_location'] == 'galaxy_job' and e['event_type'] == 'analysis'
                   and e.get('status') == 'ok']
            evs.sort(key=lambda e: int(e.get('sequence') or 0))
            for i, e in enumerate(evs):
                tool = str(e.get('tool') or '')
                udt = tool in udt_ids
                base = 'UDT' if udt else (tool.rsplit('/', 1)[0] if tool.startswith('toolshed') and
                                          len(tool.split('/')) >= 6 else tool)
                full = 'UDT' if udt else tool
                params = e.get('parameters')
                canon = json.dumps(_canon(params if isinstance(params, dict) else {}), sort_keys=True, default=str)
                rows.append(dict(benchmark=bm, task=d['task']['task_id'], cfg=TRACE_MODEL[model],
                                 replicate=int(run['replicate_id']), order=i, base=base, full=full,
                                 pstep=full + '|' + canon))
    return pd.DataFrame(rows)


def edit_similarity(a, b):
    """1 - normalised edit distance between two ordered step sequences."""
    if not a and not b:
        return 1.0
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return 1 - prev[-1] / max(len(a), len(b))


def route_variant_cells(steps, r, variant):
    """Task-model similarity of the three Galaxy replicate runs under one route definition."""
    rows = []
    for (bm, task, c), g in steps.groupby(['benchmark', 'task', 'cfg']):
        runs = [x.sort_values('order') for _, x in g.groupby('replicate')]
        if len(runs) != 3:
            continue
        if variant == 'ordered':
            seqs = [[k for i, k in enumerate(x.base) if i == 0 or k != x.base.iloc[i - 1]] for x in runs]
            sims = [edit_similarity(a, b) for a, b in itertools.combinations(seqs, 2)]
        else:
            col = {'versions': 'full', 'parameters': 'pstep'}[variant]
            sets_ = [frozenset(x[col]) for x in runs]
            sims = [len(a & b) / len(a | b) for a, b in itertools.combinations(sets_, 2)]
        rows.append(dict(benchmark=bm, task=task, cfg=c, sim=float(np.mean(sims))))
    cells = pd.DataFrame(rows)
    acc = r[r.env == GAL].groupby(['benchmark', 'task', 'cfg']).agg(cluster=('cluster', 'first'), ok=('ok', 'mean'))
    cells = cells.join(acc, on=['benchmark', 'task', 'cfg'])
    return cells[cells.cluster.notna()].reset_index(drop=True)


def eligibility(calls, r):
    """Task-model cells (Galaxy) in which all three runs completed a job, of all scored cells."""
    ran = calls[calls.completed & calls.tool.isin(['run_galaxy_tool_and_wait', 'run_galaxy_udt_and_wait'])]
    n = ran.groupby(['benchmark', 'task', 'cfg']).replicate.nunique()
    scored = r[r.env == GAL].groupby(['benchmark', 'task', 'cfg']).size()
    e = (n.reindex(scored.index).fillna(0) == 3).groupby(level='benchmark').agg(['sum', 'size'])
    return e


def panel_c(cells, r):
    task = cells.groupby(['benchmark', 'task']).sim.mean().rename('sim').reset_index()
    acc = r.groupby(['benchmark', 'task']).ok.mean().rename('task_ok').reset_index()
    task = task.merge(acc, on=['benchmark', 'task'])
    task['correct'] = 100 * task.task_ok
    per = {}
    for bm, g in task.groupby('benchmark'):
        rho, p = spearman_perm(g.correct, g.sim, np.zeros(len(g)))
        per[bm] = dict(rho=rho, p=p, tasks=len(g))
    return task, per


def within_task(cells):
    """Models compared on the same task: task-centred similarity against task-centred accuracy."""
    c = cells.assign(s_dm=cells.sim - cells.groupby('task').sim.transform('mean'),
                     a_dm=cells.ok - cells.groupby('task').ok.transform('mean'))
    c = c[cells.groupby('task').sim.transform('size') > 1]
    rho, p = spearman_perm(c.s_dm, c.a_dm, c.task)
    return dict(rho=rho, p=p, cells=len(c))


def similarity_by_model(cells):
    rows, tests = [], []
    for bm in BENCH:
        d = cells[cells.benchmark == bm]
        est, draws = boot_means(d, ['cfg'], 'sim')
        for c in CFG:
            rows.append(dict(benchmark=bm, cfg=c, value=est[c], lo=np.nanpercentile(draws[c], 2.5),
                             hi=np.nanpercentile(draws[c], 97.5), n=int((d.cfg == c).sum())))
        stat, p = model_effect_p(d)
        tests.append(dict(benchmark=bm, statistic=stat, p=p, cells=len(d), tasks=d.task.nunique()))
    return pd.DataFrame(rows), pd.DataFrame(tests)


def replicate_sets(r, answers):
    d = r[r.benchmark.isin(QA)].merge(answers, on=['benchmark', 'task', 'cfg', 'env', 'replicate'], how='left')
    agg = {f'same_{k}': (f'answer_{k}', lambda s: int(s.notna().all() and s.nunique() == 1))
           for k, _ in MATCH_RULES if k != 'task'}
    sets = d.groupby(['benchmark', 'cluster', 'task', 'cfg', 'env']).agg(
        n_ok=('ok', 'sum'), missing=('answer', lambda s: int(s.isna().sum())),
        n_answers=('answer', lambda s: s.nunique()), **agg).reset_index()
    tol = task_tolerance()
    task_same = d.groupby(['benchmark', 'cluster', 'task', 'cfg', 'env']).apply(
        lambda g: answers_agree(list(g.answer_task), tol.get(g.name[2])), include_groups=False)
    sets = sets.join(task_same.rename('same_task'), on=['benchmark', 'cluster', 'task', 'cfg', 'env'])
    sets['same'] = sets.same_task                      # primary: task-aware matching
    sets['outcome'] = np.select([sets.n_ok == 3, sets.missing > 0, sets.n_ok > 0, sets.same == 1],
                                ['all_accepted', 'missing', 'mixed', 'same_rejected'], 'rejected_differ')
    # held-out difficulty: incorrect runs among the task's other 21 runs (all models, both conditions)
    tot = r.groupby(['benchmark', 'task']).ok.agg(['sum', 'size'])
    sets = sets.join(tot, on=['benchmark', 'task'])
    sets['held_out_wrong'] = (sets['size'] - 3) - (sets['sum'] - sets.n_ok)
    sets['diff_bin'] = pd.cut(sets.held_out_wrong, [b[0] - 0.5 for b in DIFF_BINS] + [21.5],
                              labels=[b[2] for b in DIFF_BINS])
    # sensitivity: difficulty from the other three models only (18 runs), so no run of the same model contributes
    own = r.groupby(['benchmark', 'task', 'cfg']).ok.agg(['sum', 'size']).rename(columns={'sum': 'm_sum',
                                                                                          'size': 'm_size'})
    sets = sets.join(own, on=['benchmark', 'task', 'cfg'])
    sets['other_models_wrong'] = (sets['size'] - sets.m_size) - (sets['sum'] - sets.m_sum)
    sets['diff_bin_models'] = pd.cut(sets.other_models_wrong, [-0.5, 0.5, 2.5, 8.5, 18.5],
                                     labels=['0', '1–2', '3–8', '9–18'])
    return sets


def panel_b(sets):
    rows, tests = [], []
    for bm in QA:
        sub = sets[sets.benchmark == bm]
        est, draws = boot_means(sub, ['cfg', 'env'], 'same')
        rows += [dict(benchmark=bm, cfg=c, env=e, value=100 * est[(c, e)], lo=100 * np.percentile(draws[(c, e)], 2.5),
                      hi=100 * np.percentile(draws[(c, e)], 97.5), n=int(((sub.cfg == c) & (sub.env == e)).sum()))
                 for c in CFG for e in ENVS]
        for env in ENVS:
            stat, p = model_effect_p(sub[sub.env == env], value='same')
            tests.append(dict(benchmark=bm, env=env, statistic=stat, p=p, sets=int((sub.env == env).sum()),
                              family='secondary: per benchmark, Holm over 4'))
    pooled = []
    for env in ENVS:                           # primary: both benchmarks, model labels permuted within tasks
        stat, p = model_effect_p(sets[sets.env == env], value='same')
        pooled.append(dict(benchmark='both', env=env, statistic=stat, p=p, sets=int((sets.env == env).sum()),
                           family='primary: both benchmarks, Holm over 2'))
    tests, pooled = pd.DataFrame(tests), pd.DataFrame(pooled)
    tests['p_holm'] = holm(tests.p)
    pooled['p_holm'] = holm(pooled.p)
    return pd.DataFrame(rows), pd.concat([pooled, tests], ignore_index=True)


def difficulty_sensitivity(sets):
    """Share of sets with the same rejected answer by held-out difficulty, defined from the task's other 21 runs or
    from the other three models' 18 runs."""
    rows = []
    for col, name, labs in (('diff_bin', 'other 21 runs', [b[2] for b in DIFF_BINS]),
                            ('diff_bin_models', 'other models (18 runs)', ['0', '1–2', '3–8', '9–18'])):
        s = sets.assign(rep=(sets.outcome == 'same_rejected').astype(int), b=sets[col].astype(str))
        est, draws = boot_means(s, ['b'], 'rep')
        for b_ in labs:
            rows.append(dict(definition=name, bin=b_, value=100 * est[b_], lo=100 * np.percentile(draws[b_], 2.5),
                             hi=100 * np.percentile(draws[b_], 97.5), sets=int((s.b == b_).sum())))
    return pd.DataFrame(rows)


def match_rules(sets):
    rows = []
    for k, lab in MATCH_RULES:
        for env in ENVS:
            s = sets[sets.env == env]
            rows.append(dict(rule=k, label=lab, env=env, value=100 * s[f'same_{k}'].mean(), sets=len(s)))
    return pd.DataFrame(rows)


def panel_d(sets):
    """Outcome composition per model and held-out difficulty bin, with a cluster-bootstrap interval for the share of
    sets that repeated the same rejected answer."""
    tab = sets.groupby(['cfg', 'diff_bin', 'outcome'], observed=False).size().unstack('outcome', fill_value=0)
    tab = tab.reindex(columns=[o for o, _, _ in OUTCOMES], fill_value=0)
    ci = []
    s = sets.assign(rep=(sets.outcome == 'same_rejected').astype(int), cb=sets.cfg + '|' + sets.diff_bin.astype(str))
    est, draws = boot_means(s, ['cb'], 'rep')
    for cb in est.index:
        c, b_ = cb.split('|')
        ci.append(dict(cfg=c, diff_bin=b_, value=100 * est[cb], lo=100 * np.percentile(draws[cb], 2.5),
                       hi=100 * np.percentile(draws[cb], 97.5)))
    pooled = sets.groupby(['diff_bin', 'outcome'], observed=False).size().unstack('outcome', fill_value=0)
    return tab, pd.DataFrame(ci), pooled.reindex(columns=[o for o, _, _ in OUTCOMES], fill_value=0)


# ---------------------------------------------------------------- drawing helpers
def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def fmt_p(p):
    if p < 0.001:
        return r'$\mathit{P}$ < 0.001'
    return rf'$\mathit{{P}}$ = {p:.2f}' if p >= 0.01 else rf'$\mathit{{P}}$ = {p:.3f}'


def signed(x, nd=2):
    return f'{x:.{nd}f}'.replace('-', '−')


# ---------------------------------------------------------------- panels: drawing
def draw_a(fig, H, pct, runs):
    label(fig, 0, 0, 'a', 'What each model ran in Galaxy', H,
          'Galaxy runs with at least one completed job in each family (%); UDTs were not offered on IWC')
    rows = FAMILIES + ['UDT (agent-written code)']
    ax = axes_mm(fig, 45.0, 13.0, 60.0, 37.0, H)
    m = pct.values
    cmap = LinearSegmentedColormap.from_list('blues', ['#FFFFFF', '#CFE3F1', style.GALAXY, '#063B5E'])
    ax.imshow(m, aspect='auto', cmap=cmap, vmin=0, vmax=100, interpolation='nearest')
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m[i, j]
            if np.isnan(v):
                continue
            ax.text(j, i, f'{v:.0f}', ha='center', va='center', fontsize=5, color='white' if v >= 45 else style.INK)
    ax.set_yticks(range(len(rows)), rows, fontsize=5)
    ax.set_xticks(range(m.shape[1]), [MODEL_SHORT[c] for _, c in pct.columns], fontsize=5, rotation=90)
    ax.tick_params(axis='x', pad=1.0)
    ax.tick_params(length=0, pad=1.5)
    for s in ax.spines.values():
        s.set_visible(False)
    for j in (4, 8):
        ax.axvline(j - 0.5, color='white', lw=1.6)
    for i in (len(DATA_FAMILIES), len(FAMILIES)):
        ax.axhline(i - 0.5, color='white', lw=1.6)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for b, bm in enumerate(BENCH):
        ax.text(b * 4 + 1.5, 1.01, BENCH_SHORT[bm], transform=tr, ha='center', va='bottom', fontsize=5.5,
                fontweight='bold')
    tr2 = blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(-0.71, (len(DATA_FAMILIES) - 1) / 2, 'Data\nhandling', transform=tr2, ha='center', va='center',
            fontsize=5.5, fontweight='bold', rotation=90, linespacing=1.0)
    ax.text(-0.71, len(DATA_FAMILIES) + (len(METHOD_FAMILIES) - 1) / 2, 'Scientific methods', transform=tr2,
            ha='center', va='center', fontsize=5.5, fontweight='bold', rotation=90)


def draw_b(fig, H, agree, tests):
    label(fig, 112.0, 0, 'b', 'Same answer in all three runs', H,
          'Replicate sets (one task, model and condition)')
    ax = axes_mm(fig, 122.0, 17.0, 57.0, 27.0, H)
    a = agree.set_index(['benchmark', 'cfg', 'env'])
    for g, bm in enumerate(QA):
        for j, c in enumerate(CFG):
            pts = []
            for k, env in enumerate(ENVS):
                t = a.loc[(bm, c, env)]
                x = g * 1.15 + (j - 1.5) * 0.24 + (k - 0.5) * 0.10
                ax.errorbar(x, t.value, yerr=[[t.value - t.lo], [t.hi - t.value]], fmt=style.ENV_MARKER[env], ms=3.0,
                            mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, elinewidth=0.8, capsize=0, zorder=3,
                            ecolor=MODEL_COLOR[c] if c != 'GPT-5.6 Luna' else '#A8994A')
                pts.append((x, t.value))
            ax.plot(*zip(*pts), color=style.NEUTRAL_MID, lw=0.4, zorder=2)
        if g:
            ax.axvline(g * 1.15 - 0.575, color=style.GRID, lw=0.6, zorder=1)
    ax.set_ylim(55, 101.5)
    ax.spines['left'].set_bounds(55, 100)
    ax.set_yticks([60, 70, 80, 90, 100])
    style.grid_y(ax)
    ax.set_xticks([g * 1.15 for g in range(len(QA))], [BENCH_NAME[b] for b in QA], fontsize=5.5)
    ax.tick_params(axis='x', length=0, pad=2)
    ax.set_xlim(-0.55, (len(QA) - 1) * 1.15 + 0.55)
    ax.set_ylabel('Sets with the same answer (%)')
    at = tests.set_index(['benchmark', 'env'])
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for g, bm in enumerate(QA):
        ax.text(g * 1.15, -0.13, f'custom code {fmt_p(at.loc[(bm, CODE), "p_holm"])}\n'
                f'Galaxy {fmt_p(at.loc[(bm, GAL), "p_holm"])}', transform=tr, ha='center', va='top', fontsize=5,
                color=style.INK2, linespacing=1.2)
    ax.text(0.5, -0.36, f'Models differ, both benchmarks: custom code {fmt_p(at.loc[("both", CODE), "p_holm"])};\n'
            f'Galaxy {fmt_p(at.loc[("both", GAL), "p_holm"])}', transform=ax.transAxes, ha='center', va='top',
            fontsize=5, color=style.INK, fontweight='bold', linespacing=1.2)
    models = [Line2D([], [], ls='', marker='o', ms=3.0, mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, label=c)
              for c in CFG]
    shapes = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.0, mfc=style.NEUTRAL_MID, mec=style.INK, mew=0.35,
                     label=style.ENV_LABEL[e]) for e in ENVS]
    ax.add_artist(ax.legend(handles=models, ncol=2, loc='lower left', bbox_to_anchor=(0.0, 1.02), fontsize=5,
                            handletextpad=0.2, columnspacing=0.6, borderaxespad=0, labelspacing=0.2))
    ax.legend(handles=shapes, ncol=1, loc='lower right', bbox_to_anchor=(1.0, 1.02), fontsize=5, handletextpad=0.2,
              borderaxespad=0, labelspacing=0.2)


def draw_c(fig, H, y0, task, per, within, elig):
    label(fig, 0, y0, 'c', 'Tool-set similarity and task accuracy', H,
          'Galaxy; 1 = the same set of tools in all three runs (any UDT counted as one item; order, versions and\n'
          f'parameters ignored). Models compared on the same task: Spearman ρ = {signed(within["rho"])}, '
          f'{fmt_p(within["p"])}')
    for j, bm in enumerate(BENCH):
        ax = axes_mm(fig, 11.0 + j * 40.5, y0 + 21.0, 35.0, 20.0, H)
        t = task[task.benchmark == bm]
        m, col = BENCH_MARK[bm]
        jitter = rng.uniform(-1.2, 1.2, len(t))
        iwc = bm == 'IWC'
        ax.scatter(t.correct + jitter, t.sim, s=9 if iwc else 7, marker=m, facecolor=col,
                   edgecolor=style.INK2 if iwc else 'white', lw=0.3, zorder=3)
        ax.set_xlim(-4, 104)
        ax.set_ylim(-0.03, 1.03)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0], ['0', '0.25', '0.5', '0.75', '1'] if j == 0 else [''] * 5)
        style.grid_y(ax)
        ax.set_xlabel('Runs correct on the task (%)', labelpad=1.5)
        if j == 0:
            ax.set_ylabel('Tool-set similarity')
        p = per[bm]
        e = elig.loc[bm]
        ax.text(0.0, 1 + 5.9 / 20.0, BENCH_NAME[bm], transform=ax.transAxes, ha='left', va='bottom', fontsize=5.5,
                fontweight='bold')
        ax.text(0.0, 1 + 1.0 / 20.0, f'ρ = {signed(p["rho"])}, {fmt_p(p["p"])}\n{p["tasks"]} tasks; {int(e["sum"])} of '
                f'{int(e["size"])} cells eligible', transform=ax.transAxes, ha='left', va='bottom', fontsize=5,
                color=style.INK2, linespacing=1.2)


VER_LABEL = [('V1', 'Counts or denominators'), ('V2', 'Second method'), ('V3', 'Sensitivity analysis'),
             ('V4', 'Input assumption'), ('V5', 'Plausibility'), ('V6', 'Domain diagnostic'), ('any', 'Any check')]


def draw_d(fig, H, y0, ver):
    """Verification checks in correct and incorrect runs (Extended Data Fig. 7a, by outcome)."""
    label(fig, 131.0, y0, 'd', 'Verification checks', H, '80 coded runs (coder blind\nto the grade); 95% intervals')
    ax = axes_mm(fig, 154.0, y0 + 17.0, 22.0, 24.0, H)
    for k, (val, lab, col, mk) in enumerate(((1, 'Correct', style.INK, 'o'), (0, 'Incorrect', '#999999', 's'))):
        d = ver[(ver.by == 'ok') & (ver.group == val)].set_index('check').reindex([c for c, _ in VER_LABEL])
        y = np.arange(len(VER_LABEL)) + (k - 0.5) * 0.3
        ax.errorbar(d.value, y, xerr=[d.value - d.lo, d.hi - d.value], fmt=mk, ms=2.6, color=col, mfc=col, mec='white',
                    mew=0.3, elinewidth=0.6, capsize=0, label=lab)
    ax.set_yticks(range(len(VER_LABEL)), [l for _, l in VER_LABEL], fontsize=5)
    ax.get_yticklabels()[-1].set_fontweight('bold')
    ax.set_ylim(len(VER_LABEL) - 0.4, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 50, 100])
    style.grid_x(ax)
    ax.tick_params(axis='y', length=0)
    ax.set_xlabel('Runs with the check (%)', labelpad=1.5)
    ax.legend(loc='lower right', bbox_to_anchor=(1.05, 1.0), ncol=2, fontsize=5, borderaxespad=0.2, handletextpad=0.1,
              columnspacing=0.6, handlelength=1.0)


def draw_e(fig, H, y0, tab, ci, counts):
    label(fig, 0, y0, 'e', 'Replicate outcomes by held-out task difficulty', H,
          'BixBench-Verified-50 and CompBioBench, both conditions; difficulty from the task\'s other 21 runs, so a '
          'set\'s own runs never define it')
    labs = [b[2] for b in DIFF_BINS]
    for j, c in enumerate(CFG):
        ax = axes_mm(fig, 11.0 + j * 33.5, y0 + 13.0, 28.0, 27.0, H)
        t = tab.loc[c].reindex(labs)
        tot = t.sum(axis=1).values
        bottom = np.zeros(len(labs))
        for code, lab, col in OUTCOMES:
            v = 100 * t[code].values / tot
            ax.bar(range(len(labs)), v, bottom=bottom, width=0.72, color=col, ec='white', lw=0.3, zorder=3)
            bottom += v
        q = ci[ci.cfg == c].set_index('diff_bin').reindex(labs)
        ax.errorbar(range(len(labs)), q.value, yerr=[q.value - q.lo, q.hi - q.value], fmt='none', ecolor=style.INK,
                    elinewidth=0.6, capsize=1.2, capthick=0.6, zorder=4)
        for x, n in enumerate(tot):
            ax.text(x, 101.5, f'{int(n)}', ha='center', va='bottom', fontsize=5, color=style.INK2)
        ax.set_xticks(range(len(labs)), labs, fontsize=5)
        ax.tick_params(axis='x', length=0, pad=1.5)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100], ['0', '25', '50', '75', '100'] if j == 0 else [''] * 5)
        ax.set_xlim(-0.55, len(labs) - 0.45)
        ax.set_title(c, fontsize=5.5, fontweight='bold', color=style.INK, pad=8.0)
        if j == 0:
            ax.set_ylabel('Replicate sets (%)')
        if j == 1:
            ax.text(1.12, -0.17, 'Incorrect runs among the task\'s other 21 runs', transform=ax.transAxes, ha='center',
                    va='top', fontsize=5.5)
    handles = [Patch(fc=col, ec=style.NEUTRAL_MID if col == '#E8E8E8' else col, lw=0.3, label=lab)
               for _, lab, col in OUTCOMES[::-1]]
    handles.append(Line2D([], [], color=style.INK, lw=0.6, marker='_', ms=2.4, label='95% interval, same rejected answer'))
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(146.0 / W, 1 - (y0 + 12.0) / H), ncol=1, fontsize=5,
               handlelength=0.9, handletextpad=0.4, labelspacing=0.45, borderaxespad=0, frameon=False,
               title='Replicate set', title_fontsize=5, alignment='left')
    fig.text(146.0 / W, 1 - (y0 + 37.5) / H, 'Numbers above bars: sets', fontsize=5, color=style.INK2, va='top')


# ---------------------------------------------------------------- Extended Data
def ed_tools(fig, H, top, per, runs):
    label(fig, 0, 0, 'a', f'Installed tools with completed jobs in the most Galaxy runs ({N_TOOLS})', H)
    x0, pw, gap = 30.0, 16.0, 1.8
    labels = [TOOL_LABEL.get(t, t.split('/')[-1]) for t in top.index]
    for j, c in enumerate(CFG):
        ax = axes_mm(fig, x0 + j * (pw + gap), 13.0, pw, 40.0, H)
        ax.barh(range(N_TOOLS), per[c].values, height=0.68, color=MODEL_COLOR[c],
                ec=style.INK if c == 'GPT-5.6 Luna' else 'none', lw=0.3, zorder=3)
        ax.set_ylim(N_TOOLS - 0.5, -0.5)
        ax.set_xlim(0, 25)
        ax.set_xticks([0, 10, 20])
        style.grid_x(ax)
        ax.tick_params(axis='y', length=0)
        if j == 0:
            ax.set_yticks(range(N_TOOLS), labels, fontsize=5)
        else:
            ax.set_yticks(range(N_TOOLS), [''] * N_TOOLS)
            ax.spines['left'].set_visible(False)
        ax.set_title(c, fontsize=5.5, fontweight='bold', pad=7.0, loc='left')
        ax.text(0.0, 1.015, f'{int(runs[c])} runs', transform=ax.transAxes, ha='left', va='bottom', fontsize=5,
                color=style.INK2)
        if j == 1:
            ax.text(1 + gap / pw / 2, -0.10, 'Galaxy runs with a completed job of the tool (%)',
                    transform=ax.transAxes, ha='center', va='top', fontsize=5.5)


def ed_similarity(fig, H, sim, sim_t, sens):
    label(fig, 108.0, 0, 'b', 'Tool-set similarity by model', H)
    ax = axes_mm(fig, 118.0, 13.0, 60.0, 26.0, H)
    for g, bm in enumerate(BENCH):
        for j, c in enumerate(CFG):
            t = sim[(sim.benchmark == bm) & (sim.cfg == c)].iloc[0]
            x = g * 1.2 + (j - 1.5) * 0.22
            ax.errorbar(x, t.value, yerr=[[t.value - t.lo], [t.hi - t.value]], fmt='o', ms=3.0, mfc=MODEL_COLOR[c],
                        mec=style.INK, mew=0.35, elinewidth=0.8, capsize=0, ecolor=MODEL_COLOR[c])
    ax.set_xticks([g * 1.2 for g in range(3)], [BENCH_NAME[b] for b in BENCH], fontsize=5)
    ax.tick_params(axis='x', length=0)
    ax.set_ylim(0, 1)
    style.grid_y(ax)
    ax.set_ylabel('Mean tool-set similarity')
    st = sim_t.set_index('benchmark')
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for g, bm in enumerate(BENCH):
        ax.text(g * 1.2, -0.17, f'models differ {fmt_p(st.loc[bm, "p"])}', transform=tr, ha='center', va='top',
                fontsize=5, color=style.INK2)
    ax.legend(handles=[Line2D([], [], ls='', marker='o', ms=3.0, mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, label=c)
                       for c in CFG], ncol=2, loc='lower left', bbox_to_anchor=(0.0, 1.02), fontsize=5,
              handletextpad=0.2, columnspacing=0.6, borderaxespad=0, labelspacing=0.2)
    # sensitivity of the panel c correlation (Spearman rho across tasks; tasks in parentheses)
    x0, y = 112.4, 52.0
    cols = [x0 + 44.0, x0 + 56.0, x0 + 66.0]
    fig.text(x0 / W, 1 - y / H, 'Task similarity against task accuracy, Spearman ρ (tasks)', fontsize=5,
             fontweight='bold', va='top')
    y += 3.4
    for xc, bm in zip(cols, BENCH):
        fig.text(xc / W, 1 - y / H, BENCH_SHORT[bm], fontsize=5, va='top', ha='right', color=style.INK2)
    names = {'primary': 'Panel c (installed tools + one UDT item)',
             'installed tools only (UDTs dropped)': 'UDT items dropped',
             'cells whose runs used installed tools only': 'Cells using installed tools only',
             'cells with any UDT': 'Cells with any UDT',
             'ordered steps (edit distance)': 'Ordered steps (edit distance)',
             'tool versions distinguished': 'Tool versions distinguished',
             'tools with identical parameters': 'Tools with identical parameters'}
    for variant in names:
        y += 3.0
        fig.text(x0 / W, 1 - y / H, names[variant], fontsize=5, va='top')
        for xc, bm in zip(cols, BENCH):
            t = sens[(sens.variant == variant) & (sens.benchmark == bm)]
            txt = f'{signed(t.rho.iloc[0])} ({int(t.tasks.iloc[0])})' if len(t) else '–'
            fig.text(xc / W, 1 - y / H, txt, fontsize=5, va='top', ha='right')


def ed_matching(fig, H, mr):
    label(fig, 0, 88.0, 'c', 'Answer agreement under four answer-matching rules', H)
    ax = axes_mm(fig, 62.0, 97.0, 40.0, 14.0, H)
    for i, (k, lab) in enumerate(MATCH_RULES):
        for env in ENVS:
            t = mr[(mr.rule == k) & (mr.env == env)].iloc[0]
            ax.plot(t.value, i, ls='', marker=style.ENV_MARKER[env], ms=3.2, mfc=style.ENV_COLOR[env], mec='white',
                    mew=0.35)
    ax.set_yticks(range(len(MATCH_RULES)), [lab for _, lab in MATCH_RULES], fontsize=5)
    ax.set_ylim(len(MATCH_RULES) - 0.5, -0.5)
    ax.set_xlim(70, 95)
    style.grid_x(ax)
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Replicate sets with the same answer in all three runs (%)')
    ax.legend(handles=[Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.2, mfc=style.ENV_COLOR[e], mec='white',
                              mew=0.35, label=style.ENV_LABEL[e]) for e in ENVS], loc='lower right',
              bbox_to_anchor=(1.0, 1.02), ncol=2, fontsize=5, borderaxespad=0)


UDT_CLASSES = ['Statistics, machine learning and enrichment', 'Single-cell and spatial analysis',
               'Variant calling and annotation', 'Peak calling and epigenomics', 'Genomic intervals and sequence features',
               'Read processing and alignment', 'Expression and differential testing', 'Phylogenetics',
               'Sequence search, taxonomy and assembly', 'Tables and text', 'Script supplied as a dataset',
               'Environment probe or set-up', 'Other methods']


def udt_methods(calls):
    """Completed UDT jobs by method class (figures/udt_methods.csv, built by make_udt_methods.py), per model and
    benchmark, as a share of that model's completed UDT jobs."""
    u = pd.read_csv(os.path.join(FIGS, 'udt_methods.csv'))
    done = calls[(calls.tool == 'run_galaxy_udt_and_wait') & calls.completed][['run_id', 'task', 'line']]
    u = u.merge(done, on=['run_id', 'task', 'line'])
    tab = u.groupby(['method_class', 'benchmark', 'cfg']).size().unstack(['benchmark', 'cfg'], fill_value=0)
    cols = pd.MultiIndex.from_product([QA, CFG])
    tab = tab.reindex(index=UDT_CLASSES, columns=cols, fill_value=0)
    return 100 * tab / tab.sum(axis=0).replace(0, np.nan), tab.sum(axis=0), u


def ed_udt(fig, H, y0, pct, n):
    label(fig, 0, y0, 'e', 'What completed UDT jobs computed', H,
          'Share of each model\'s completed UDT jobs by method class (rules on the UDT definition: code first, '
          'then a tool-specific container)')
    ax = axes_mm(fig, 58.0, y0 + 12.0, 76.0, 30.0, H)
    m = pct.values
    cmap = LinearSegmentedColormap.from_list('blues', ['#FFFFFF', '#CFE3F1', style.GALAXY, '#063B5E'])
    ax.imshow(m, aspect='auto', cmap=cmap, vmin=0, vmax=100, interpolation='nearest')
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            if not np.isnan(m[i, j]):
                ax.text(j, i, f'{m[i, j]:.0f}', ha='center', va='center', fontsize=5,
                        color='white' if m[i, j] >= 45 else style.INK)
    ax.set_yticks(range(len(UDT_CLASSES)), UDT_CLASSES, fontsize=5)
    ax.set_xticks(range(m.shape[1]), [f'{MODEL_SHORT[c]}\n({int(n[(b, c)])})' for b, c in pct.columns], fontsize=5)
    ax.tick_params(length=0, pad=1.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.axvline(3.5, color='white', lw=1.6)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for b, bm in enumerate(QA):
        ax.text(b * 4 + 1.5, 1.01, BENCH_SHORT[bm], transform=tr, ha='center', va='bottom', fontsize=5.5,
                fontweight='bold')


def ed_difficulty(fig, H, y0, ds):
    label(fig, 108.0, y0, 'd', 'Same rejected answer by held-out difficulty, two definitions', H)
    ax = axes_mm(fig, 120.0, y0 + 9.0, 58.0, 20.0, H)
    for k, (name, col, mk) in enumerate((('other 21 runs', style.INK, 'o'), ('other models (18 runs)', '#888888', 's'))):
        d = ds[ds.definition == name].reset_index(drop=True)
        x = np.arange(len(d)) + (k - 0.5) * 0.18
        ax.errorbar(x, d.value, yerr=[d.value - d.lo, d.hi - d.value], fmt=mk, ms=3.0, color=col, mfc=col if k == 0
                    else 'white', mec=col, elinewidth=0.7, capsize=0, label=f'Incorrect runs among the task\'s {name}')
    ax.set_xticks(range(4), ['None', 'Few', 'Some', 'Most'])
    ax.tick_params(axis='x', length=0)
    ax.set_ylim(0, 60)
    ax.set_yticks([0, 20, 40, 60])
    style.grid_y(ax)
    ax.set_ylabel('Replicate sets (%)')
    ax.set_xlabel('Held-out task difficulty', labelpad=1.5)
    ax.legend(loc='upper left', fontsize=5, borderaxespad=0.2, handletextpad=0.3)


# ---------------------------------------------------------------- source data and assembly
def source_data(pct, counts, runs, agree, b_t, task, per, within, elig, tab, ci, pooled, sets, ver=None):
    rows = []
    if ver is not None:
        for t in ver[ver.by == 'ok'].itertuples():
            rows.append(dict(panel='d', benchmark='BixBench50+CompBio', model='all four',
                             group='correct runs' if t.group == 1 else 'incorrect runs',
                             measure=f'pct_runs_with_check: {dict(VER_LABEL)[t.check]}', value=t.value, ci95_low=t.lo,
                             ci95_high=t.hi, n=t.n))
    for fam in pct.index:
        for bm, c in pct.columns:
            rows.append(dict(panel='a', benchmark=bm, model=c, group=fam, measure='pct_galaxy_runs_with_completed_job',
                             value=pct.loc[fam, (bm, c)], n=int(runs.get((bm, c), 0))))
    for t in agree.itertuples():
        rows.append(dict(panel='b', benchmark=t.benchmark, model=t.cfg, group=t.env,
                         measure='pct_sets_same_answer_all_three_runs', value=t.value, ci95_low=t.lo, ci95_high=t.hi,
                         n=t.n))
    for t in b_t.itertuples():
        rows.append(dict(panel='b', benchmark=t.benchmark, model='all four', group=t.env,
                         measure='model_effect_permutation (Holm over 4)', value=t.statistic, n=t.sets, p=t.p,
                         p_holm=t.p_holm))
    for t in task.itertuples():
        rows.append(dict(panel='c', benchmark=t.benchmark, model='all four', group=t.task,
                         measure='task_tool_set_similarity', value=t.sim))
        rows.append(dict(panel='c', benchmark=t.benchmark, model='all four', group=t.task,
                         measure='task_pct_runs_correct', value=t.correct))
    for bm, p in per.items():
        rows.append(dict(panel='c', benchmark=bm, model='all four', measure='spearman_rho_across_tasks',
                         value=p['rho'], n=p['tasks'], p=p['p']))
        e = elig.loc[bm]
        rows.append(dict(panel='c', benchmark=bm, model='all four', measure='eligible_task_model_cells',
                         value=int(e['sum']), n=int(e['size'])))
    rows.append(dict(panel='c', benchmark='all', model='all four', group='within task',
                     measure='spearman_rho_similarity_accuracy', value=within['rho'], n=within['cells'],
                     p=within['p']))
    for (c, b_), t in tab.iterrows():
        for code, lab, _ in OUTCOMES:
            rows.append(dict(panel='e', benchmark='BixBench50+CompBio', model=c, group=f'held-out incorrect {b_} of 21',
                             measure=f'replicate_sets: {lab}', value=int(t[code]), n=int(t.sum())))
    for t in ci.itertuples():
        rows.append(dict(panel='e', benchmark='BixBench50+CompBio', model=t.cfg,
                         group=f'held-out incorrect {t.diff_bin} of 21', measure='pct_sets_same_rejected_answer',
                         value=t.value, ci95_low=t.lo, ci95_high=t.hi))
    for b_, t in pooled.iterrows():
        for code, lab, _ in OUTCOMES:
            rows.append(dict(panel='e', benchmark='BixBench50+CompBio', model='all four',
                             group=f'held-out incorrect {b_} of 21', measure=f'replicate_sets: {lab}',
                             value=int(t[code]), n=int(t.sum())))
    rows.append(dict(panel='e', benchmark='BixBench50+CompBio', model='all four', measure='sets_with_missing_submission',
                     value=int((sets.missing > 0).sum()), n=len(sets)))
    rows.append(dict(panel='e', benchmark='BixBench50+CompBio', model='all four',
                     measure='sets_all_accepted_with_different_answers',
                     value=int(((sets.n_ok == 3) & (sets.same == 0)).sum()), n=len(sets)))
    cols = ['panel', 'benchmark', 'model', 'group', 'measure', 'value', 'ci95_low', 'ci95_high', 'n', 'p', 'p_holm']
    out = pd.DataFrame(rows).reindex(columns=cols)
    out['group'] = out.group.replace({'open_ended_code': 'custom_code'})
    out = out.sort_values('panel', kind='stable')
    out.round(4).to_csv(os.path.join(OUT, 'fig4_source_data.csv'), index=False)


def ed_source_data(top, per, runs, sim, sim_t, sens, mr, ds, udt_pct, udt_n):
    rows = []
    for rank, t in enumerate(top.index, 1):
        for c in CFG:
            rows.append(dict(panel='a', model=c, group=f'{rank}: {TOOL_LABEL.get(t, t)} ({t})',
                             measure='pct_galaxy_runs_with_completed_job', value=per.loc[t, c], n=int(runs[c])))
    for t in sim.itertuples():
        rows.append(dict(panel='b', benchmark=t.benchmark, model=t.cfg, measure='mean_tool_set_similarity',
                         value=t.value, ci95_low=t.lo, ci95_high=t.hi, n=t.n))
    for t in sim_t.itertuples():
        rows.append(dict(panel='b', benchmark=t.benchmark, model='all four', measure='model_effect_permutation',
                         value=t.statistic, n=t.cells, p=t.p))
    for t in sens.itertuples():
        rows.append(dict(panel='b', benchmark=t.benchmark, model='all four', group=t.variant,
                         measure='spearman_rho_across_tasks', value=t.rho, n=t.tasks, p=t.p))
    for t in mr.itertuples():
        rows.append(dict(panel='c', model='all four', group=t.label, measure=f'pct_sets_same_answer ({t.env})',
                         value=t.value, n=t.sets))
    for cls in udt_pct.index:
        for bm, c in udt_pct.columns:
            rows.append(dict(panel='e', benchmark=bm, model=c, group=cls, measure='pct_completed_udt_jobs',
                             value=udt_pct.loc[cls, (bm, c)], n=int(udt_n[(bm, c)])))
    for t in ds.itertuples():
        rows.append(dict(panel='d', model='all four', group=f'{t.definition}: {t.bin} incorrect',
                         measure='pct_sets_same_rejected_answer', value=t.value, ci95_low=t.lo, ci95_high=t.hi,
                         n=t.sets))
    out = pd.DataFrame(rows).reindex(columns=['panel', 'benchmark', 'model', 'group', 'measure', 'value', 'ci95_low',
                                              'ci95_high', 'n', 'p'])
    out['measure'] = out.measure.str.replace('open_ended_code', 'custom_code')
    out.round(4).to_csv(os.path.join(OUT, 'ed_fig4_source_data.csv'), index=False)


def save(fig, name, title):
    style.enforce_min_font(fig)
    fig.savefig(os.path.join(OUT, f'{name}.svg'), metadata={'Title': title})
    fig.savefig(os.path.join(OUT, f'{name}.pdf'), metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, f'{name}.png'), dpi=(600, 600))
    plt.close(fig)


def main():
    panel_io.record(globals(), 'fig4')   # with PANEL_DATA set, also write figures/panel_data/fig4.json
    global rng
    r = load_runs()
    calls, traced = load_calls()
    pct, counts, runs, book = panel_a(calls, traced)
    book.to_csv(os.path.join(OUT, 'fig4_tool_family_codebook.csv'), index=False)
    top, per_tool, runs_cfg = top_tools(calls, traced)
    cells = route_cells(calls, r)
    elig = eligibility(calls, r)
    task, per = panel_c(cells, r)
    within = within_task(cells)
    rng = np.random.default_rng(SEED + 1)
    sim, sim_t = similarity_by_model(cells)
    sens = [dict(benchmark=bm, variant='primary', rho=v['rho'], p=v['p'], tasks=v['tasks']) for bm, v in per.items()]
    inst = route_cells(calls, r, mode='installed')
    for variant, frame in (('installed tools only (UDTs dropped)', inst),
                           ('cells whose runs used installed tools only', cells[cells.route == 'installed only']),
                           ('cells with any UDT', cells[cells.route != 'installed only'])):
        t, p_ = panel_c(frame, r)
        for bm, v in p_.items():
            sens.append(dict(benchmark=bm, variant=variant, rho=v['rho'], p=v['p'], tasks=v['tasks']))
    steps = job_steps(calls)
    for variant, label in (('ordered', 'ordered steps (edit distance)'), ('versions', 'tool versions distinguished'),
                           ('parameters', 'tools with identical parameters')):
        t, p_ = panel_c(route_variant_cells(steps, r, variant), r)
        for bm, v in p_.items():
            sens.append(dict(benchmark=bm, variant=label, rho=v['rho'], p=v['p'], tasks=v['tasks']))
    sens = pd.DataFrame(sens)
    answers = load_answers()
    sets = replicate_sets(r, answers)
    rng = np.random.default_rng(SEED + 3)
    agree, b_t = panel_b(sets)
    mr = match_rules(sets)
    rng = np.random.default_rng(SEED + 4)
    tab, ci, pooled = panel_d(sets)
    rng = np.random.default_rng(SEED + 6)
    ds = difficulty_sensitivity(sets)
    print('difficulty sensitivity'); print(ds.round(2).to_string())
    print('codebook families:', book.family.value_counts().to_dict())
    for name, t in (('a: families (% runs)', pct.round(0)), ('b: agreement', agree), ('b: tests', b_t),
                    ('c: per benchmark', pd.DataFrame(per).T), ('c: eligibility', elig), ('ED: similarity', sim),
                    ('ED: model effect', sim_t), ('ED: sensitivity', sens), ('ED: matching rules', mr),
                    ('d: outcomes', tab), ('d: same rejected CI', ci), ('d: pooled', pooled)):
        print(name)
        print(t.round(3).to_string())
    print('within task:', within)

    H = 166.0
    rng = np.random.default_rng(SEED + 5)                  # jitter only
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, pct, runs)
    draw_b(fig, H, agree, b_t)
    draw_c(fig, H, 64.0, task, per, within, elig)
    import make_ed_validation as validation                # same statistics as Extended Data Fig. 7a
    ver, _, _ = validation.verification(validation.load_runs())   # result_evaluation: outcome from current grades
    draw_d(fig, H, 64.0, ver)
    draw_e(fig, H, 113.0, tab, ci, pooled)
    save(fig, 'fig4', 'Fig. 4 | Answer agreement and tool use vary across model configurations')
    source_data(pct, counts, runs, agree, b_t, task, per, within, elig, tab, ci, pooled, sets, ver)

    udt_pct, udt_n, udt_rows = udt_methods(calls)
    print('UDT methods (% of completed UDT jobs)'); print(udt_pct.round(0).to_string())
    He = 170.0
    fig = plt.figure(figsize=(W * MM, He * MM))
    ed_tools(fig, He, top, per_tool, runs_cfg)
    ed_similarity(fig, He, sim, sim_t, sens)
    ed_matching(fig, He, mr)
    ed_difficulty(fig, He, 88.0, ds)
    ed_udt(fig, He, 122.0, udt_pct, udt_n)
    save(fig, 'ed_fig4', 'Extended Data Fig. 4 | Tool inventory, tool-set similarity and answer matching')
    ed_source_data(top, per_tool, runs_cfg, sim, sim_t, sens, mr, ds, udt_pct, udt_n)


if __name__ == '__main__':
    main()
