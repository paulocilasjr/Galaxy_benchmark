import csv
import math
import sys
from collections import OrderedDict

import numpy as np
from scipy import stats

crispr_path, expr_path, model_path, out_path = sys.argv[1:5]
threshold = 0.6
min_pairs = 3
missing = set(['', 'NA', 'NaN', 'nan', 'NAN', 'null', 'NULL', 'None'])

def parse_float(value):
    if value in missing:
        return np.nan
    try:
        return float(value)
    except Exception:
        return np.nan

def read_header(path):
    with open(path, 'r', newline='') as handle:
        return next(csv.reader(handle))

def check_duplicate_labels(labels, label):
    seen = set()
    dupes = []
    for item in labels:
        if item in seen:
            dupes.append(item)
        seen.add(item)
    if dupes:
        raise RuntimeError('%s has duplicate feature labels, examples: %s' % (label, ', '.join(dupes[:5])))

cell_line_ids = set()
with open(model_path, 'r', newline='') as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        if row.get('ModelType') == 'Cell Line':
            mid = row.get('ModelID')
            if mid:
                cell_line_ids.add(mid)
if not cell_line_ids:
    raise RuntimeError('No ModelType == Cell Line rows found in Model.csv')

crispr_header = read_header(crispr_path)
expr_header = read_header(expr_path)
crispr_features = crispr_header[1:]
expr_features = expr_header[1:]
check_duplicate_labels(crispr_features, 'CRISPRGeneEffect')
check_duplicate_labels(expr_features, 'Expression')
expr_index = {name: i + 1 for i, name in enumerate(expr_features)}
common_features = [name for name in crispr_features if name in expr_index]
if not common_features:
    raise RuntimeError('No shared feature labels between CRISPR and expression matrices')
crispr_cols = [crispr_header.index(name) for name in common_features]
expr_cols = [expr_index[name] for name in common_features]

crispr_by_id = OrderedDict()
crispr_total_rows = 0
crispr_cell_line_rows = 0
with open(crispr_path, 'r', newline='') as handle:
    reader = csv.reader(handle)
    next(reader)
    for row in reader:
        crispr_total_rows += 1
        if not row:
            continue
        model_id = row[0]
        if model_id not in cell_line_ids:
            continue
        crispr_cell_line_rows += 1
        if model_id in crispr_by_id:
            raise RuntimeError('Duplicate CRISPR ModelID: %s' % model_id)
        vals = np.empty(len(common_features), dtype=np.float64)
        for out_i, col_i in enumerate(crispr_cols):
            vals[out_i] = parse_float(row[col_i]) if col_i < len(row) else np.nan
        crispr_by_id[model_id] = vals

expr_rows = []
crispr_rows = []
paired_ids = []
expr_total_rows = 0
expr_cell_line_rows = 0
seen_expr = set()
with open(expr_path, 'r', newline='') as handle:
    reader = csv.reader(handle)
    next(reader)
    for row in reader:
        expr_total_rows += 1
        if not row:
            continue
        model_id = row[0]
        if model_id not in cell_line_ids:
            continue
        expr_cell_line_rows += 1
        if model_id in seen_expr:
            raise RuntimeError('Duplicate expression ModelID: %s' % model_id)
        seen_expr.add(model_id)
        dep_vals = crispr_by_id.get(model_id)
        if dep_vals is None:
            continue
        vals = np.empty(len(common_features), dtype=np.float64)
        for out_i, col_i in enumerate(expr_cols):
            vals[out_i] = parse_float(row[col_i]) if col_i < len(row) else np.nan
        expr_rows.append(vals)
        crispr_rows.append(dep_vals)
        paired_ids.append(model_id)

if not paired_ids:
    raise RuntimeError('No paired cell-line ModelIDs between expression and CRISPR matrices')
expr = np.vstack(expr_rows)
# Convert negative-going gene effect to positive-going essentiality/dependency strength.
essentiality = -np.vstack(crispr_rows)

count = 0
tested = 0
nan_or_low_pairs = 0
max_rho = None
max_gene = None
for j, gene in enumerate(common_features):
    x = expr[:, j]
    y = essentiality[:, j]
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < min_pairs:
        nan_or_low_pairs += 1
        continue
    x_valid = x[mask]
    y_valid = y[mask]
    if np.all(x_valid == x_valid[0]) or np.all(y_valid == y_valid[0]):
        nan_or_low_pairs += 1
        continue
    rho, pvalue = stats.spearmanr(x_valid, y_valid)
    if rho is None or not np.isfinite(rho):
        nan_or_low_pairs += 1
        continue
    tested += 1
    rho = float(rho)
    if max_rho is None or rho > max_rho:
        max_rho = rho
        max_gene = gene
    if rho >= threshold:
        count += 1

with open(out_path, 'w', newline='') as handle:
    writer = csv.writer(handle, delimiter='\t')
    writer.writerow(['field', 'value'])
    writer.writerow(['strong_positive_count', count])
    writer.writerow(['rho_threshold', threshold])
    writer.writerow(['method', 'spearman'])
    writer.writerow(['essentiality_coordinate', '-CRISPRGeneEffect'])
    writer.writerow(['model_filter', 'ModelType == Cell Line'])
    writer.writerow(['id_alignment', 'ModelID intersection'])
    writer.writerow(['feature_pairing', 'exact shared gene labels'])
    writer.writerow(['min_pairs', min_pairs])
    writer.writerow(['model_cell_line_count', len(cell_line_ids)])
    writer.writerow(['crispr_total_rows', crispr_total_rows])
    writer.writerow(['crispr_cell_line_rows', crispr_cell_line_rows])
    writer.writerow(['expression_total_rows', expr_total_rows])
    writer.writerow(['expression_cell_line_rows', expr_cell_line_rows])
    writer.writerow(['paired_cell_line_rows', len(paired_ids)])
    writer.writerow(['common_features', len(common_features)])
    writer.writerow(['tested_features', tested])
    writer.writerow(['not_tested_low_pairs_or_constant', nan_or_low_pairs])
    writer.writerow(['max_rho', '' if max_rho is None else repr(max_rho)])
    writer.writerow(['max_rho_gene', '' if max_gene is None else max_gene])
