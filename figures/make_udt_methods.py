"""Method classes of user-defined tools (UDTs): the code agents ran as Galaxy jobs.

Every run_galaxy_udt_and_wait request in the traced Galaxy runs of the four primary configurations is read from the
archived trace. Each UDT is classified by rules on its container image and its shell command (libraries, functions and
programs called), with scientific methods taking precedence over data handling. The rules are deterministic and listed
below; scripts are classified, never executed. Writes figures/udt_methods.csv: one row per UDT request with the run,
trace line, UDT identifier, container, whether the container carries a version tag, the method class and the rule that
matched (scripts themselves are not written).
"""
import gzip
import json
import os
import re

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'figures')
SUMMARIES = os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz')
PRIMARY = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
           'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
           'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}
# Classification, in order: (1) an environment probe or set-up job (versions, help text, installs, file tests) is its own
# class; (2) rules on the command, when it contains the analysis code; (3) rules on the container when it names a specific
# tool (general images such as python, busybox or multi-tool toolboxes are skipped); (4) data handling if the command
# only reshapes tables or text; otherwise 'Other methods'. Classes follow the Fig. 4a families, plus the probe class.
PROBE = re.compile(r'--version|__version__|--help|\bwhich\b|pip (install|show|list|download)|conda (list|install)|'
                   r'sessionInfo|packageVersion|^\s*set [-+]eu?\s*test -r', re.I)
RULES = [
    ('Phylogenetics', r'phykit|iqtree|raxml|mafft|newick|treeness|ete3|dendropy|Bio\.Phylo'),
    ('Variant calling and annotation', r'bcftools|freebayes|snpeff|pysam\.VariantFile|\.vcf\b|vcfpy|cyvcf2|genotype|plink'),
    ('Expression and differential testing', r'deseq|edger|limma|pydeseq2|featurecounts|salmon|kallisto|'
                                            r'differential expression|log2foldchange|padj'),
    ('Single-cell and spatial analysis', r'scanpy|anndata|\.h5ad|seurat|squidpy|leiden|vireo|cellsnp'),
    ('Peak calling and epigenomics', r'macs2|macs3|encode-atac|chromvar|peak'),
    ('Read processing and alignment', r'samtools|bwa |bowtie|minimap2|hisat2|pysam\.AlignmentFile|\.bam\b|fastp|'
                                      r'cutadapt'),
    ('Genomic intervals and sequence features', r'bedtools|pybedtools|pyranges|\.bed\b|\.gtf\b|\.gff|SeqIO|biopython|'
                                                r'\.fa(sta)?\b'),
    ('Sequence search, taxonomy and assembly', r'blast|kraken|diamond|hmmer|mmseqs|busco|spades'),
    ('Statistics, machine learning and enrichment', r'scipy\.stats|statsmodels|mannwhitneyu|ttest|wilcox|fisher_exact|'
                                                    r'chi2|kruskal|pearsonr|spearmanr|sklearn|gseapy|enrich|goatools|'
                                                    r'multipletests|p\.adjust|glm\(|cor\.test|t\.test|tensorflow|'
                                                    r'torch|keras|borzoi|caduceus|enformer'),
]
DATA = r'pandas|read_csv|read_table|csv\.|openpyxl|xlsx|awk|sed |sort |cut |grep |\bcat\b|head |wc '
GENERIC = re.compile(r'sequence-toolbox|/python:|python:\d|busybox|r-base|ubuntu|debian|alpine', re.I)


def classify(container, command):
    if command and len(command) < 1500 and PROBE.search(command):
        return 'Environment probe or set-up', PROBE.search(command).group(0)
    for name, rx in RULES:
        m = re.search(rx, command or '', flags=re.I)
        if m:
            return name, m.group(0)
    if container and not GENERIC.search(container):
        for name, rx in RULES:
            m = re.search(rx, container, flags=re.I)
            if m:
                return name, 'container: ' + m.group(0)
    m = re.search(r'\$\(inputs\.\w*(script|code|program|py|r)\w*\.path\)', command or '', flags=re.I)
    if m:                                   # the code is an input dataset, kept in the history, not in the request
        return 'Script supplied as a dataset', m.group(0)
    m = re.search(DATA, command or '', flags=re.I)
    if m:
        return 'Tables and text', m.group(0)
    return 'Other methods', ''


def main():
    rows = []
    for raw in gzip.open(SUMMARIES, 'rt'):
        s = json.loads(raw)
        if s['condition'] != 'galaxy' or s['model'] not in PRIMARY or not s.get('trace'):
            continue
        path = s['trace'] if os.path.exists(s['trace']) else s['trace'] + '.gz'
        if not os.path.exists(path):
            continue
        op = gzip.open if path.endswith('.gz') else open
        with op(path, 'rt', newline='\n') as f:
            for line_no, line in enumerate(f, 1):
                if '"run_galaxy_udt_and_wait"' not in line or '"item.completed"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                it = e.get('item') or {}
                if it.get('tool') != 'run_galaxy_udt_and_wait':
                    continue
                rep = (it.get('arguments') or {}).get('representation') or {}
                if isinstance(rep, str):
                    try:
                        rep = json.loads(rep)
                    except ValueError:
                        rep = {}
                container = rep.get('container') or ''
                if isinstance(container, dict):        # some definitions give {type, identifier} or similar
                    container = container.get('identifier') or container.get('image') or json.dumps(container)
                elif isinstance(container, list):
                    container = ' '.join(str(c.get('identifier', c) if isinstance(c, dict) else c) for c in container)
                command = rep.get('shell_command') or rep.get('command') or ''
                if not isinstance(command, str):
                    command = json.dumps(command)
                cls, hit = classify(container, command)
                rows.append(dict(benchmark=s['benchmark'], task=s['task'], run_id=s['run_id'], cfg=PRIMARY[s['model']],
                                 replicate=int(s['replicate']), line=line_no, udt_id=rep.get('id'),
                                 container=container, container_versioned=bool(re.search(r':[^:/]+$', container)),
                                 method_class=cls, matched=hit))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, 'udt_methods.csv'), index=False)
    print(len(out), 'UDT requests')
    print(out.method_class.value_counts().to_string())
    print('versioned container:', round(out.container_versioned.mean() * 100, 1), '%; no container:',
          int((out.container == '').sum()))
    print(out.groupby('container').size().sort_values(ascending=False).head(15).to_string())


if __name__ == '__main__':
    main()
