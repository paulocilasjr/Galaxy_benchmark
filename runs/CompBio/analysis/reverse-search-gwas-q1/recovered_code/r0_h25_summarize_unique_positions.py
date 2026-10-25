import csv
import sys
from collections import defaultdict


def safe_float(value, default=1e99):
    try:
        return float(value)
    except Exception:
        return default


def main(in_path, out_path):
    best = {}
    in_detail = False
    with open(in_path, newline="") as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if not row:
                continue
            if row[0] == "detail" and len(row) > 1 and row[1] == "pmid":
                in_detail = True
                continue
            if not in_detail or row[0] != "detail" or len(row) < 12:
                continue
            # row: detail, pmid, accession, trait, snp, chrom, pos, catalog_p, input_p,
            # input_over_catalog, abs_log10_delta, mapped_gene
            key = (row[1], row[2], row[3], row[5], row[6])
            delta = safe_float(row[10])
            if key not in best or delta < safe_float(best[key][10]):
                best[key] = row

    grouped = defaultdict(list)
    for row in best.values():
        grouped[(row[1], row[2], row[3])].append(row)

    summaries = []
    for key, rows in grouped.items():
        deltas = [safe_float(r[10]) for r in rows]
        within10 = sum(d <= 1 for d in deltas)
        within100 = sum(d <= 2 for d in deltas)
        summaries.append((key, rows, len(rows), within10, within100, min(deltas), sum(deltas) / len(deltas)))

    summaries.sort(key=lambda x: (-x[3], -x[4], -x[2], x[5], x[6], x[0][0], x[0][2]))

    top_keys = {s[0] for s in summaries[:10]}
    with open(out_path, "w", newline="") as out:
        w = csv.writer(out, delimiter="\t")
        w.writerow(["section", "pmid", "accession", "trait", "unique_positions", "within10x", "within100x", "best_log10_delta", "mean_best_log10_delta"])
        for key, rows, n, within10, within100, best_delta, mean_delta in summaries[:50]:
            w.writerow(["summary", key[0], key[1], key[2], n, within10, within100, "%.6g" % best_delta, "%.6g" % mean_delta])
        w.writerow([])
        w.writerow(["section", "pmid", "accession", "trait", "snp", "chrom", "pos", "catalog_p", "input_p", "input_over_catalog", "abs_log10_delta", "mapped_gene"])
        for key, rows, *_ in summaries:
            if key not in top_keys:
                continue
            for row in sorted(rows, key=lambda r: (safe_float(r[10]), r[5], r[6]))[:20]:
                w.writerow(row[:12])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
