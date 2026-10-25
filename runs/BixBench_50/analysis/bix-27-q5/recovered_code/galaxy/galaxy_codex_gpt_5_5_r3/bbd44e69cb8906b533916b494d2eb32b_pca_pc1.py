from __future__ import print_function
import csv
import math
import sys
from collections import Counter, defaultdict

import numpy as np
from sklearn.decomposition import PCA

expr_path = sys.argv[1]
meta_path = sys.argv[2]
out_path = sys.argv[3]

with open(meta_path, 'r') as handle:
    meta_reader = csv.DictReader(handle)
    meta_rows = list(meta_reader)
    meta_fields = meta_reader.fieldnames or []
if 'projid' not in meta_fields:
    raise RuntimeError('metadata is missing projid column')
meta_counts = Counter(row['projid'] for row in meta_rows)
meta_groups = defaultdict(list)
for row in meta_rows:
    meta_groups[row['projid']].append(row)

# Complete the repeated-ID gate by checking whether repeated metadata rows
# disagree on plausible stable/invariant sample attributes.
stable_fields = [field for field in ['msex', 'educ', 'apoe_genotype'] if field in meta_fields]
stable_conflict_ids = []
for sample_id, rows in meta_groups.items():
    if len(rows) > 1:
        for field in stable_fields:
            if len(set(row.get(field, '') for row in rows)) > 1:
                stable_conflict_ids.append(sample_id)
                break

with open(expr_path, 'r') as handle:
    reader = csv.reader(handle)
    header = next(reader)
    if not header or header[0] != 'gene':
        raise RuntimeError('expression table must have gene as first column')
    sample_labels = header[1:]
    expr_counts = Counter(sample_labels)
    collided_ids = set([sid for sid, n in expr_counts.items() if n > 1])
    collided_ids.update([sid for sid, n in meta_counts.items() if n > 1])
    collided_ids.update(stable_conflict_ids)

    keep_indices = []
    keep_samples = []
    for idx, sample_id in enumerate(sample_labels):
        if expr_counts[sample_id] == 1 and meta_counts.get(sample_id, 0) == 1 and sample_id not in collided_ids:
            keep_indices.append(idx)
            keep_samples.append(sample_id)
    if len(keep_samples) < 101:
        raise RuntimeError('fewer than 101 resolved samples remain for 100-component PCA')

    gene_labels = []
    rows = []
    for row in reader:
        if len(row) != len(header):
            raise RuntimeError('ragged expression row for gene %s' % (row[0] if row else '<empty>'))
        gene_labels.append(row[0])
        vals = []
        for idx in keep_indices:
            x = float(row[idx + 1])
            if x < -1.0:
                raise RuntimeError('value less than -1 encountered before log10 pseudocount transform')
            vals.append(math.log10(x + 1.0))
        rows.append(vals)

if not rows:
    raise RuntimeError('no expression rows read')
if len(set(gene_labels)) != len(gene_labels):
    raise RuntimeError('duplicate gene labels present; feature identity is unresolved')

matrix = np.asarray(rows, dtype=float).T  # samples x genes
if not np.all(np.isfinite(matrix)):
    raise RuntimeError('non-finite values after log10 pseudocount transform')

variances = np.var(matrix, axis=0, ddof=1)
nonzero = variances > 0.0
matrix = matrix[:, nonzero]
if matrix.shape[1] < 1:
    raise RuntimeError('no nonzero-variance genes remain')

pca = PCA(n_components=100, svd_solver='full')
pca.fit(matrix)
pc1_percent = float(pca.explained_variance_ratio_[0] * 100.0)

with open(out_path, 'w') as out:
    out.write('metric\tvalue\n')
    out.write('pc1_percent\t%.12g\n' % pc1_percent)
    out.write('input_genes\t%d\n' % len(gene_labels))
    out.write('fitted_genes_nonzero_variance\t%d\n' % matrix.shape[1])
    out.write('input_expression_columns\t%d\n' % len(sample_labels))
    out.write('unique_expression_ids\t%d\n' % len(expr_counts))
    out.write('metadata_rows\t%d\n' % len(meta_rows))
    out.write('unique_metadata_ids\t%d\n' % len(meta_counts))
    out.write('excluded_collided_primary_ids\t%d\n' % len(collided_ids))
    out.write('fitted_samples\t%d\n' % matrix.shape[0])
    out.write('n_components\t100\n')
    out.write('centered\ttrue\n')
    out.write('scaled\tfalse\n')
