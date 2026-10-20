import csv
import gzip
import math
import sys
from collections import defaultdict


def open_text(path):
    with open(path, "rb") as raw:
        magic = raw.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", newline="")
    return open(path, "rt", newline="")


def parse_p(value):
    try:
        p = float(value)
        if math.isfinite(p):
            return p
    except ValueError:
        return None
    return None


def main(gwas_path, target_path, out_path):
    targets = {}
    target_rows = []
    with open_text(target_path) as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = (row["chrom"], int(row["pos"]))
            row["catalog_p_float"] = parse_p(row["catalog_p"])
            target_rows.append(row)
            targets.setdefault(key, []).append(row)

    found = {}
    with open_text(gwas_path) as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for rec in reader:
            try:
                key = (rec["#CHROM"], int(rec["POS"]))
            except (KeyError, ValueError):
                continue
            if key in targets:
                found[key] = rec

    summary = defaultdict(lambda: {"n": 0, "found": 0, "within10x": 0, "within100x": 0, "exact_text": 0, "best_log10_delta": None})
    detail = []
    for row in target_rows:
        key = (row["chrom"], int(row["pos"]))
        rec = found.get(key)
        s = summary[(row["pmid"], row["accession"], row["trait"])]
        s["n"] += 1
        input_p = None
        ratio = ""
        log_delta = ""
        if rec:
            s["found"] += 1
            input_p = parse_p(rec["P"])
            cat_p = row["catalog_p_float"]
            if input_p is not None and cat_p and cat_p > 0 and input_p > 0:
                log_delta_value = abs(math.log10(input_p) - math.log10(cat_p))
                log_delta = "%.6g" % log_delta_value
                ratio = "%.6g" % (input_p / cat_p)
                if log_delta_value <= 1:
                    s["within10x"] += 1
                if log_delta_value <= 2:
                    s["within100x"] += 1
                best = s["best_log10_delta"]
                if best is None or log_delta_value < best:
                    s["best_log10_delta"] = log_delta_value
            if rec["P"].lower() == row["catalog_p"].lower():
                s["exact_text"] += 1
        detail.append([
            row["pmid"], row["accession"], row["trait"], row["snp"],
            row["chrom"], row["pos"], row["catalog_p"],
            "" if input_p is None else "%.8g" % input_p,
            ratio, log_delta, row["mapped_gene"],
        ])

    with open(out_path, "w", newline="") as out:
        w = csv.writer(out, delimiter="\t")
        w.writerow(["section", "pmid", "accession", "trait", "n_targets", "found", "within10x", "within100x", "exact_text", "best_log10_delta"])
        for (pmid, accession, trait), s in sorted(summary.items(), key=lambda kv: (-kv[1]["within10x"], -kv[1]["within100x"], kv[0][1], kv[0][2])):
            w.writerow(["summary", pmid, accession, trait, s["n"], s["found"], s["within10x"], s["within100x"], s["exact_text"], "" if s["best_log10_delta"] is None else "%.6g" % s["best_log10_delta"]])
        w.writerow([])
        w.writerow(["detail", "pmid", "accession", "trait", "snp", "chrom", "pos", "catalog_p", "input_p", "input_over_catalog", "abs_log10_delta", "mapped_gene"])
        for rec in detail:
            w.writerow(["detail"] + rec)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
