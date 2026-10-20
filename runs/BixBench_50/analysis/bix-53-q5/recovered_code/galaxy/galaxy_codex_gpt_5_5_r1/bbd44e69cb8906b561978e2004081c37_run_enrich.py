import sys
import pandas as pd
import mygene
import gseapy as gp

fg = pd.read_csv('filtered_de_genes.tsv', sep='\t')
ids = [str(x).split('.')[0] for x in fg['geneID'].dropna().tolist()]
mg = mygene.MyGeneInfo()
records = mg.querymany(ids, scopes='ensembl.gene', fields='symbol', species='mouse', as_dataframe=False, verbose=False)
symbol_by_id = {}
for rec in records:
    q = str(rec.get('query', '')).split('.')[0]
    sym = rec.get('symbol')
    if q and sym and not rec.get('notfound') and q not in symbol_by_id:
        symbol_by_id[q] = sym
symbols = []
seen = set()
for gid in ids:
    sym = symbol_by_id.get(gid)
    if sym and sym not in seen:
        seen.add(sym)
        symbols.append(sym)
with open('filtered_mouse_symbols.txt', 'w') as handle:
    for sym in symbols:
        handle.write(sym + '\n')
if not symbols:
    raise RuntimeError('No filtered Ensembl IDs mapped to mouse symbols')
enr = gp.enrichr(gene_list=symbols, gene_sets='WikiPathways_2019_Mouse', organism='mouse', outdir=None, cutoff=1.0)
res = enr.results.copy()
if res is None or res.empty:
    raise RuntimeError('GSEApy returned no enrichment results')
# Match the Galaxy GSEApy wrapper default ranking: P-value, adjusted P-value, then combined score.
ascending = [True, True, False]
res = res.sort_values(['P-value', 'Adjusted P-value', 'Combined Score'], ascending=ascending, kind='mergesort')
res.to_csv('gseapy_enrichr_results.tsv', sep='\t', index=False)
top20 = res.head(20).copy()
top20.to_csv('top20_pathways.tsv', sep='\t', index=False)
oxidative = top20['Term'].astype(str).str.contains('oxidative', case=False, regex=False).sum()
fraction = oxidative / 20.0
with open('answer.txt', 'w') as handle:
    handle.write(f'{fraction:.1f}\n')
with open('workflow_summary.tsv', 'w') as handle:
    handle.write('metric\tvalue\n')
    handle.write(f'filtered_de_gene_rows\t{len(fg)}\n')
    handle.write(f'mapped_unique_symbols\t{len(symbols)}\n')
    handle.write(f'enrichment_terms\t{len(res)}\n')
    handle.write(f'oxidative_top20_count\t{oxidative}\n')
    handle.write(f'fraction\t{fraction:.1f}\n')
