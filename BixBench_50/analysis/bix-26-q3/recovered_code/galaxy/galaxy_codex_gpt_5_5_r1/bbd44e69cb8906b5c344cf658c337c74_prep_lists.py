import csv
import math
import sys

infile = sys.argv[1]
fg_out = 'foreground.tsv'
bg_out = 'background.tsv'
summary_out = 'prep_summary.tsv'
lfc_cutoff = 1.5
padj_cutoff = 0.05

with open(infile, newline='') as handle:
    reader = csv.DictReader(handle, delimiter='\t')
    required = {'rowname', 'log2FoldChange', 'padj'}
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise SystemExit('Missing required columns: ' + ','.join(sorted(missing)))
    foreground = []
    background = []
    total_rows = 0
    nonmissing_padj = 0
    for row in reader:
        total_rows += 1
        gene = (row.get('rowname') or '').strip()
        if not gene:
            continue
        background.append(gene)
        padj_s = (row.get('padj') or '').strip()
        lfc_s = (row.get('log2FoldChange') or '').strip()
        if padj_s in {'', 'NA', 'NaN', 'nan'} or lfc_s in {'', 'NA', 'NaN', 'nan'}:
            continue
        padj = float(padj_s)
        lfc = float(lfc_s)
        if math.isfinite(padj):
            nonmissing_padj += 1
        if math.isfinite(lfc) and math.isfinite(padj) and lfc > lfc_cutoff and padj <= padj_cutoff:
            foreground.append(gene)

with open(fg_out, 'w', newline='') as handle:
    writer = csv.writer(handle, delimiter='\t')
    writer.writerow(['gene_id'])
    for gene in foreground:
        writer.writerow([gene])
with open(bg_out, 'w', newline='') as handle:
    writer = csv.writer(handle, delimiter='\t')
    writer.writerow(['gene_id'])
    for gene in background:
        writer.writerow([gene])
with open(summary_out, 'w', newline='') as handle:
    writer = csv.writer(handle, delimiter='\t')
    writer.writerow(['metric', 'value'])
    writer.writerow(['lfc_rule', 'log2FoldChange > 1.5'])
    writer.writerow(['padj_rule', 'padj <= 0.05'])
    writer.writerow(['total_rows', total_rows])
    writer.writerow(['background_genes', len(background)])
    writer.writerow(['nonmissing_padj', nonmissing_padj])
    writer.writerow(['foreground_genes', len(foreground)])
