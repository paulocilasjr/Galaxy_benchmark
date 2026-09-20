import csv
import sys
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA

input_path = sys.argv[1]

with open(input_path, "r", encoding="utf-8", newline="") as handle:
    rows = list(csv.reader(handle, delimiter="\t"))

if not rows:
    raise RuntimeError("Input matrix is empty")
header = rows[0]
if not header or header[0] != "gene":
    raise RuntimeError("Expected first column header 'gene'")
if any(len(row) != len(header) for row in rows[1:]):
    raise RuntimeError("Inconsistent tabular row width")

gene_labels = [row[0] for row in rows[1:]]
if len(set(gene_labels)) != len(gene_labels):
    raise RuntimeError("Duplicate gene labels are unresolved")

try:
    matrix = np.asarray([[float(value) for value in row[1:]] for row in rows[1:]], dtype=np.float64)
except ValueError as exc:
    raise RuntimeError("Expression matrix contains a non-numeric value") from exc

if matrix.size == 0:
    raise RuntimeError("Expression matrix has no numeric values")
if not np.isfinite(matrix).all():
    raise RuntimeError("Expression matrix contains missing or non-finite values")
if (matrix < 0).any():
    raise RuntimeError("Expression matrix contains negative values")

# Rows are samples and columns are genes after the explicit transpose.
X = np.log10(matrix + 1.0).T

# Remove features with no variance after the requested transform.
feature_variance = np.var(X, axis=0)
X = X[:, feature_variance > 0.0]

if X.shape[0] != 178:
    raise RuntimeError("Unexpected resolved sample count")
if X.shape[1] == 0 or 100 > min(X.shape):
    raise RuntimeError("Invalid PCA dimensions")

# sklearn PCA centers each feature and does not scale it.
pca = PCA(n_components=100, svd_solver="full")
pca.fit(X)

percent = float(pca.explained_variance_ratio_[0] * 100.0)
if not np.isfinite(percent) or not (0.0 <= percent <= 100.0):
    raise RuntimeError("Invalid explained-variance percentage")

Path("pc1_percent.txt").write_text("{:.15g}\n".format(percent), encoding="utf-8")
