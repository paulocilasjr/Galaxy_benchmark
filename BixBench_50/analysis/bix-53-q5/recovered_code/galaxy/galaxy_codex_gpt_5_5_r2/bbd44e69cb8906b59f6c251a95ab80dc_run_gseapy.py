import sys
import time
import html
import urllib.parse
import urllib.request
import pandas as pd
import gseapy as gp

input_path, answer_path, top_path, summary_path = sys.argv[1:5]

df = pd.read_csv(input_path, sep='\t')
for col in ['baseMean', 'log2FoldChange', 'pvalue']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
fg = df[(df['pvalue'] < 0.05) & (df['log2FoldChange'].abs() > 1) & (df['baseMean'] > 10)].copy()
ids = [str(x).split('.')[0] for x in fg['geneID'].dropna().tolist()]
ids = list(dict.fromkeys(ids))
if not ids:
    raise SystemExit('No foreground genes after requested filters')

# Enrichr mouse WikiPathways libraries use gene symbols. Query Ensembl BioMart
# inside Galaxy to keep identifier conversion in the analysis job.
xml_query = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query virtualSchemaName="default" formatter="TSV" header="0" uniqueRows="1" count="" datasetConfigVersion="0.6">
  <Dataset name="mmusculus_gene_ensembl" interface="default">
    <Filter name="ensembl_gene_id" value="{ids}"/>
    <Attribute name="ensembl_gene_id"/>
    <Attribute name="external_gene_name"/>
  </Dataset>
</Query>'''.format(ids=','.join(html.escape(x) for x in ids))
encoded = urllib.parse.urlencode({'query': xml_query}).encode('utf-8')
last_err = None
mapping_text = None
for attempt in range(3):
    try:
        req = urllib.request.Request('https://www.ensembl.org/biomart/martservice', data=encoded, headers={'User-Agent': 'codex-galaxy-gseapy'})
        with urllib.request.urlopen(req, timeout=120) as resp:
            mapping_text = resp.read().decode('utf-8')
        break
    except Exception as exc:
        last_err = exc
        time.sleep(5 * (attempt + 1))
if mapping_text is None:
    raise RuntimeError(f'BioMart mapping failed: {last_err}')

mapped = []
seen = set()
for line in mapping_text.splitlines():
    parts = line.rstrip('\n').split('\t')
    if len(parts) >= 2:
        symbol = parts[1].strip()
        if symbol and symbol not in seen:
            seen.add(symbol)
            mapped.append(symbol)
if not mapped:
    raise SystemExit('No Ensembl IDs mapped to mouse gene symbols')

enr = gp.enrichr(gene_list=mapped, gene_sets='WikiPathways_2019_Mouse', organism='mouse', outdir=None, cutoff=1.0, no_plot=True)
res = enr.results.copy()
if res.empty:
    raise SystemExit('gseapy returned no enriched terms')
for col in ['P-value', 'Adjusted P-value', 'Combined Score']:
    if col in res.columns:
        res[col] = pd.to_numeric(res[col], errors='coerce')
required = ['Term', 'P-value', 'Adjusted P-value', 'Combined Score']
missing = [c for c in required if c not in res.columns]
if missing:
    raise SystemExit('Missing gseapy columns: ' + ','.join(missing))
res = res.sort_values(['P-value', 'Adjusted P-value', 'Combined Score'], ascending=[True, True, False], kind='mergesort')
top = res.head(20).copy()
if len(top) != 20:
    raise SystemExit(f'Expected at least 20 enriched terms, observed {len(top)}')
oxidative = top['Term'].str.contains('oxidative', case=False, na=False).sum()
fraction = oxidative / 20.0
with open(answer_path, 'w') as handle:
    handle.write(f'{fraction:.1f}\n')
top.to_csv(top_path, sep='\t', index=False)
with open(summary_path, 'w') as handle:
    handle.write(f'gseapy_version\t{gp.__version__}\n')
    handle.write('library\tWikiPathways_2019_Mouse\n')
    handle.write('organism\tmouse\n')
    handle.write('ranking\tP-value,Adjusted P-value,Combined Score(desc)\n')
    handle.write(f'foreground_ensembl\t{len(ids)}\n')
    handle.write(f'mapped_symbols\t{len(mapped)}\n')
    handle.write(f'enriched_terms\t{len(res)}\n')
    handle.write(f'oxidative_top20\t{int(oxidative)}\n')
    handle.write(f'fraction\t{fraction:.1f}\n')
