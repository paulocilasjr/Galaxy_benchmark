import csv
import sys
from scipy.stats import pearsonr

counts_path, meta_path, sample_path, answer_path, details_path = sys.argv[1:6]

with open(sample_path, newline='') as f:
    reader = csv.DictReader(f)
    cd14_samples = [row['sample'] for row in reader if row.get('celltype') == 'CD14']
cd14_set = set(cd14_samples)
if not cd14_samples:
    raise SystemExit('No CD14 samples found')

meta = {}
with open(meta_path, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        gene = row.get('Geneid') or row.get('')
        if not gene:
            continue
        try:
            length = float(row['Length'])
        except Exception:
            continue
        meta[gene] = {'length': length, 'gene_biotype': row.get('gene_biotype', '')}

lengths = []
means = []
protein_coding_seen = 0
matched_rows = 0
with open(counts_path, newline='') as f:
    reader = csv.reader(f)
    header = next(reader)
    cd14_indices = [i for i, sample in enumerate(header) if sample in cd14_set]
    cd14_order = [header[i] for i in cd14_indices]
    if len(cd14_indices) != len(cd14_samples):
        missing = sorted(cd14_set - set(cd14_order))
        raise SystemExit('Missing CD14 samples in count matrix: ' + ','.join(missing[:20]))
    for row in reader:
        if not row:
            continue
        gene = row[0]
        info = meta.get(gene)
        if info is None:
            continue
        matched_rows += 1
        if info['gene_biotype'] != 'protein_coding':
            continue
        protein_coding_seen += 1
        vals = []
        for idx in cd14_indices:
            if idx >= len(row) or row[idx] == '':
                value = 0.0
            else:
                value = float(row[idx])
            vals.append(value)
        total = sum(vals)
        if total >= 10.0:
            lengths.append(info['length'])
            means.append(total / len(vals))

if len(lengths) < 3:
    raise SystemExit('Fewer than three expressed protein-coding genes after filtering')

r, p = pearsonr(lengths, means)
with open(answer_path, 'w', newline='') as out:
    out.write(format(float(r), '.17g') + '\n')
with open(details_path, 'w', newline='') as out:
    writer = csv.writer(out, delimiter='\t')
    writer.writerow(['metric', 'value'])
    writer.writerow(['cd14_samples', len(cd14_samples)])
    writer.writerow(['count_matrix_cd14_columns', len(cd14_indices)])
    writer.writerow(['metadata_genes', len(meta)])
    writer.writerow(['matched_count_rows', matched_rows])
    writer.writerow(['protein_coding_matched_rows', protein_coding_seen])
    writer.writerow(['expressed_protein_coding_rows_total_counts_ge_10', len(lengths)])
    writer.writerow(['pearson_r', format(float(r), '.17g')])
    writer.writerow(['pearson_p_value', format(float(p), '.17g')])
