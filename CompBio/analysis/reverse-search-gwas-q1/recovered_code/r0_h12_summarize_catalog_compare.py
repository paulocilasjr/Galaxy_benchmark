import csv
import sys


def main(in_path, out_path):
    summaries = []
    details = []
    in_detail = False
    with open(in_path, newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if not row:
                continue
            if row[0] == "section" or row[0].startswith("#"):
                continue
            if row[0] == "detail" and len(row) > 1 and row[1] == "pmid":
                in_detail = True
                continue
            if row[0] == "summary":
                summaries.append(row)
            elif row[0] == "detail" and in_detail:
                details.append(row)

    def int_field(row, idx):
        try:
            return int(row[idx])
        except Exception:
            return 0

    def float_field(row, idx):
        try:
            return float(row[idx])
        except Exception:
            return 1e99

    summaries.sort(key=lambda r: (-int_field(r, 6), -int_field(r, 7), float_field(r, 9), r[1], r[3]))
    top_pmids = {r[1] for r in summaries[:5]}

    with open(out_path, "w", newline="") as out:
        w = csv.writer(out, delimiter="\t")
        w.writerow(["section", "pmid", "accession", "trait", "n_targets", "found", "within10x", "within100x", "exact_text", "best_log10_delta"])
        for row in summaries[:25]:
            w.writerow(row[:10])
        w.writerow([])
        w.writerow(["section", "pmid", "accession", "trait", "snp", "chrom", "pos", "catalog_p", "input_p", "input_over_catalog", "abs_log10_delta", "mapped_gene"])
        selected = []
        for row in details:
            if len(row) >= 12 and row[1] in top_pmids:
                selected.append(row)
        selected.sort(key=lambda r: (r[1], r[3], float_field(r, 10), r[5], r[6]))
        for row in selected[:200]:
            w.writerow(row[:12])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
