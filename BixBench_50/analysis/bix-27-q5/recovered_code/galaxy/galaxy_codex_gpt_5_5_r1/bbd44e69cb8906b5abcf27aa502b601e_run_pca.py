import csv
import math
import sys
from collections import Counter, defaultdict

import numpy as np

exp_path, meta_path, out_path = sys.argv[1:4]

with open(meta_path, newline='') as f:
    meta_rows = list(csv.DictReader(f))
if not meta_rows or 'projid' not in meta_rows[0]:
    raise SystemExit('metadata must contain projid')
meta_ids = [r['projid'] for r in meta_rows]
meta_by_id = defaultdict(list)
for r in meta_rows:
    meta_by_id[r['projid']].append(r)

with open(exp_path, newline='') as f:
    reader = csv.reader(f)
    header = next(reader)
    if not header or header[0] != 'gene':
        raise SystemExit('expression table must have gene as first column')
    sample_ids = header[1:]
    sample_counts = Counter(sample_ids)
    if sample_counts != Counter(meta_ids):
        raise SystemExit('expression sample IDs and metadata projid values do not match as multisets')

    repeated_ids = {sid for sid, n in sample_counts.items() if n > 1}
    # Required identity gate: repeated primary labels lack a secondary sample key.
    # The complete repeated groups are excluded before fitting sample-level PCA.
    keep_indices = [i for i, sid in enumerate(sample_ids) if sample_counts[sid] == 1]
    keep_sample_ids = [sample_ids[i] for i in keep_indices]
    if len(keep_sample_ids) < 101:
        raise SystemExit('not enough resolved observations for 100 PCA components')

    genes = []
    gene_vectors = []
    for line_no, row in enumerate(reader, start=2):
        if len(row) != len(header):
            raise SystemExit(f'row {line_no} has {len(row)} fields, expected {len(header)}')
        gene = row[0]
        vals = []
        for i in keep_indices:
            try:
                x = float(row[i + 1])
            except ValueError as e:
                raise SystemExit(f'non-numeric value at row {line_no}, sample {sample_ids[i]}') from e
            if x + 1.0 <= 0.0:
                raise SystemExit(f'log10 pseudocount transform invalid at row {line_no}, sample {sample_ids[i]}')
            vals.append(math.log10(x + 1.0))
        genes.append(gene)
        gene_vectors.append(vals)

if not gene_vectors:
    raise SystemExit('no gene rows found')

X = np.asarray(gene_vectors, dtype=np.float64).T
if not np.isfinite(X).all():
    raise SystemExit('transformed matrix contains non-finite values')

# Remove zero-variance features after the requested transform.
feature_var = X.var(axis=0, ddof=1)
feature_mask = feature_var > 0.0
X = X[:, feature_mask]
if X.shape[1] == 0:
    raise SystemExit('no nonzero-variance genes remain')

# PCA on samples as rows and genes as columns: center features, do not scale.
Xc = X - X.mean(axis=0)
total_ss = float(np.sum(Xc * Xc))
if total_ss <= 0.0:
    raise SystemExit('total fitted variance is zero')

# Exact SVD gives ordinary covariance-style PCA. n_components is 100 as requested.
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
n_components = 100
if len(S) < n_components:
    raise SystemExit('SVD returned fewer components than requested')
explained_variance_ratio = (S[:n_components] ** 2) / total_ss
pc1_percent = float(explained_variance_ratio[0] * 100.0)

# Diagnostics are included to validate output semantics; local extraction reads pc1_percent only.
with open(out_path, 'w', newline='') as out:
    w = csv.writer(out, delimiter='\t')
    w.writerow(['metric', 'value'])
    w.writerow(['pc1_percent_total_variance', format(pc1_percent, '.15g')])
    w.writerow(['requested_components', n_components])
    w.writerow(['original_sample_columns', len(sample_ids)])
    w.writerow(['unique_primary_sample_ids', len(sample_counts)])
    w.writerow(['excluded_repeated_primary_ids', len(repeated_ids)])
    w.writerow(['fitted_samples', X.shape[0]])
    w.writerow(['original_genes', len(genes)])
    w.writerow(['fitted_nonzero_variance_genes', X.shape[1]])
