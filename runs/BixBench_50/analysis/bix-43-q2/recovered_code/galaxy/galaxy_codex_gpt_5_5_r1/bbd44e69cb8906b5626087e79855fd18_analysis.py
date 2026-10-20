import os
import sys
import traceback
from pathlib import Path

import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
try:
    from pydeseq2.default_inference import DefaultInference
except Exception:
    DefaultInference = None
import gseapy as gp

counts_path = sys.argv[1]
map_path = sys.argv[2]
layout_path = sys.argv[3]

related_groups = [
    'DMSO',
    'DMSO_Serum_starvation',
    'Cisplatin_IC50_CBD_IC50',
    'Cisplatin_IC50_CBD_IC50_Serum_starvation_16h',
]
case_group = 'Cisplatin_IC50_CBD_IC50'
control_group = 'DMSO'

try:
    counts_all = pd.read_csv(counts_path, index_col=0)
    counts_all.index = counts_all.index.astype(str).str.replace(r'\.\d+$', '', regex=True)
    counts_all = counts_all.apply(pd.to_numeric, errors='raise').astype(int)

    layout = pd.read_csv(layout_path)
    layout['count_col'] = layout['SampleID'].astype(str).str.replace('-', '_', regex=False)
    missing = sorted(set(layout['count_col']) - set(counts_all.columns))
    if missing:
        raise ValueError('Sample layout columns missing from counts: ' + ','.join(missing))

    keep_prefilter = (counts_all > 10).any(axis=1)
    counts_pref = counts_all.loc[keep_prefilter]

    model_layout = layout.loc[layout['Group'].isin(related_groups)].copy()
    model_layout['Group'] = pd.Categorical(model_layout['Group'], categories=related_groups)
    model_cols = model_layout['count_col'].tolist()
    metadata = model_layout.set_index('count_col')[['Group']]
    metadata.index = metadata.index.astype(str)

    counts_model = counts_pref.loc[:, model_cols].T
    counts_model.index = counts_model.index.astype(str)
    counts_model = counts_model.loc[metadata.index]

    n_cpus = int(os.environ.get('GALAXY_SLOTS') or '1')
    inference = DefaultInference(n_cpus=n_cpus) if DefaultInference is not None else None
    dds_kwargs = dict(counts=counts_model, metadata=metadata, design='~Group', refit_cooks=True)
    if inference is not None:
        dds_kwargs['inference'] = inference
    dds = DeseqDataSet(**dds_kwargs)
    dds.deseq2()

    stats_kwargs = dict(dds=dds, contrast=['Group', case_group, control_group])
    if inference is not None:
        stats_kwargs['inference'] = inference
    stat_res = DeseqStats(**stats_kwargs)
    stat_res.summary()
    res = stat_res.results_df.copy()
    res.index.name = 'ENSG'
    res.to_csv('deseq2_results.tsv', sep='\t')

    sig = res.loc[
        res['padj'].notna()
        & (res['padj'] <= 0.05)
        & (res['log2FoldChange'].abs() >= 0.5)
        & (res['baseMean'] >= 10)
    ].copy()
    sig.index.name = 'ENSG'
    sig.to_csv('significant_deseq2_results.tsv', sep='\t')

    gene_map = pd.read_csv(map_path, sep='\t', dtype=str)
    gene_map = gene_map.dropna(subset=['ENSG', 'gene_name']).drop_duplicates(subset=['ENSG'])
    ens_to_name = dict(zip(gene_map['ENSG'], gene_map['gene_name']))
    mapped = []
    seen = set()
    for ensg in sig.index.astype(str):
        name = ens_to_name.get(ensg)
        if name and name not in seen:
            mapped.append(name)
            seen.add(name)
    pd.DataFrame({'gene_name': mapped}).to_csv('significant_gene_symbols.tsv', sep='\t', index=False)

    if not mapped:
        raise ValueError('No significant mapped gene symbols available for enrichment')

    enr = gp.enrichr(
        gene_list=mapped,
        gene_sets='Reactome_2022',
        organism='human',
        outdir=None,
        cutoff=1.0,
        no_plot=True,
        verbose=False,
    )
    enrich = enr.results.copy()
    enrich.to_csv('gseapy_reactome_2022.tsv', sep='\t', index=False)

    term_col = 'Term'
    odds_col = 'Odds Ratio' if 'Odds Ratio' in enrich.columns else 'OddsRatio'
    terms = enrich[term_col].astype(str)
    lower = terms.str.lower()
    exact_phrase = lower.str.contains('p53-mediated cell cycle gene regulation', regex=False)
    tp53_cell_cycle = (lower.str.contains('tp53') | lower.str.contains('p53')) & lower.str.contains('cell cycle')
    transcription_cell_cycle = tp53_cell_cycle & lower.str.contains('transcription')
    if exact_phrase.any():
        target = enrich.loc[exact_phrase].copy()
    elif transcription_cell_cycle.any():
        target = enrich.loc[transcription_cell_cycle].copy()
    elif tp53_cell_cycle.any():
        target = enrich.loc[tp53_cell_cycle].copy()
    else:
        target = enrich.loc[lower.str.contains('p53') | lower.str.contains('tp53')].copy()
    target.to_csv('target_candidate_terms.tsv', sep='\t', index=False)
    if len(target) != 1:
        raise ValueError('Expected one target p53/cell-cycle Reactome term, found %d; inspect target_candidate_terms.tsv' % len(target))
    odds = target.iloc[0][odds_col]
    with open('answer.txt', 'w') as out:
        out.write(str(odds) + '\n')

    with open('diagnostics.txt', 'w') as out:
        out.write('pydeseq2_version=' + __import__('pydeseq2').__version__ + '\n')
        out.write('gseapy_version=' + gp.__version__ + '\n')
        out.write('all_count_genes=' + str(counts_all.shape[0]) + '\n')
        out.write('all_count_samples=' + str(counts_all.shape[1]) + '\n')
        out.write('prefiltered_genes=' + str(counts_pref.shape[0]) + '\n')
        out.write('model_samples=' + str(counts_model.shape[0]) + '\n')
        out.write('model_groups=' + ','.join(related_groups) + '\n')
        out.write('contrast=' + case_group + '_vs_' + control_group + '\n')
        out.write('significant_genes=' + str(sig.shape[0]) + '\n')
        out.write('mapped_unique_gene_symbols=' + str(len(mapped)) + '\n')
        out.write('target_term=' + str(target.iloc[0][term_col]) + '\n')
        out.write('target_odds_ratio=' + str(odds) + '\n')
except Exception:
    Path('diagnostics.txt').write_text(traceback.format_exc())
    raise
