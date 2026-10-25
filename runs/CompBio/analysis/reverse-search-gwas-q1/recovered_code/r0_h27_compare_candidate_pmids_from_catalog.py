import csv
import gzip
import math
import os
import sys
import urllib.request
import zipfile
from collections import defaultdict


CATALOG_URL = "https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip"


def as_float(value):
    try:
        return float(value)
    except Exception:
        return None


def norm_chrom(value):
    value = str(value).strip()
    if value.startswith("chr"):
        value = value[3:]
    return value


def log_delta(a, b):
    if a is None or b is None or a <= 0 or b <= 0:
        return 1e99
    return abs(math.log10(a) - math.log10(b))


def read_catalog(pmids, work_dir):
    zip_path = os.path.join(work_dir, "gwas-catalog-associations-full.zip")
    urllib.request.urlretrieve(CATALOG_URL, zip_path)
    rows = []
    positions = set()
    with zipfile.ZipFile(zip_path) as archive:
        names = [name for name in archive.namelist() if name.endswith(".tsv")]
        if not names:
            raise RuntimeError("No TSV found in GWAS Catalog zip")
        with archive.open(names[0]) as raw:
            text = (line.decode("utf-8", errors="replace") for line in raw)
            reader = csv.DictReader(text, delimiter="\t")
            for row in reader:
                pmid = row.get("PUBMEDID", "").strip()
                if pmid not in pmids:
                    continue
                chrom = norm_chrom(row.get("CHR_ID", ""))
                pos = row.get("CHR_POS", "").strip()
                if not chrom.isdigit() or not pos.isdigit():
                    continue
                pval = as_float(row.get("P-VALUE", ""))
                if pval is None:
                    continue
                entry = {
                    "pmid": pmid,
                    "accession": row.get("STUDY ACCESSION", "").strip(),
                    "trait": row.get("DISEASE/TRAIT", "").strip(),
                    "snp": row.get("SNPS", "").strip(),
                    "chrom": chrom,
                    "pos": pos,
                    "catalog_p": pval,
                    "mapped_gene": row.get("MAPPED_GENE", "").strip(),
                }
                rows.append(entry)
                positions.add((chrom, pos))
    return rows, positions


def read_input_hits(input_path, positions):
    hits = {}
    opener = gzip.open if input_path.endswith(".gz") else open
    with opener(input_path, "rt", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            if len(row) < 8:
                continue
            key = (norm_chrom(row[0]), row[1])
            if key in positions:
                pval = as_float(row[7])
                if pval is not None:
                    hits[key] = pval
    return hits


def main(input_path, out_path, *pmids):
    if not pmids:
        raise RuntimeError("At least one PMID is required")
    catalog_rows, positions = read_catalog(set(pmids), os.getcwd())
    input_hits = read_input_hits(input_path, positions)

    best_by_position = {}
    details = []
    for row in catalog_rows:
        input_p = input_hits.get((row["chrom"], row["pos"]))
        if input_p is None:
            continue
        delta = log_delta(row["catalog_p"], input_p)
        detail = dict(row)
        detail["input_p"] = input_p
        detail["delta"] = delta
        detail["ratio"] = input_p / row["catalog_p"] if row["catalog_p"] > 0 else 1e99
        details.append(detail)
        key = (row["pmid"], row["accession"], row["trait"], row["chrom"], row["pos"])
        if key not in best_by_position or delta < best_by_position[key]["delta"]:
            best_by_position[key] = detail

    grouped = defaultdict(list)
    for row in best_by_position.values():
        grouped[(row["pmid"], row["accession"], row["trait"])].append(row)

    summaries = []
    for key, rows in grouped.items():
        deltas = [r["delta"] for r in rows]
        within10 = sum(d <= 1 for d in deltas)
        within100 = sum(d <= 2 for d in deltas)
        summaries.append((key, rows, len(rows), within10, within100, min(deltas), sum(deltas) / len(deltas)))

    summaries.sort(key=lambda item: (-item[3], -item[4], -item[2], item[5], item[6], item[0]))
    top_keys = {item[0] for item in summaries[:12]}

    with open(out_path, "w", newline="") as out:
        writer = csv.writer(out, delimiter="\t")
        writer.writerow(["section", "pmid", "accession", "trait", "unique_positions", "within10x", "within100x", "best_log10_delta", "mean_log10_delta"])
        for key, rows, n, within10, within100, best_delta, mean_delta in summaries[:50]:
            writer.writerow(["summary", key[0], key[1], key[2], n, within10, within100, "%.6g" % best_delta, "%.6g" % mean_delta])
        writer.writerow([])
        writer.writerow(["section", "pmid", "accession", "trait", "snp", "chrom", "pos", "catalog_p", "input_p", "input_over_catalog", "abs_log10_delta", "mapped_gene"])
        for key, rows, *_ in summaries:
            if key not in top_keys:
                continue
            for row in sorted(rows, key=lambda r: (r["delta"], r["chrom"], int(r["pos"])))[:25]:
                writer.writerow([
                    "detail",
                    row["pmid"],
                    row["accession"],
                    row["trait"],
                    row["snp"],
                    row["chrom"],
                    row["pos"],
                    "%.6g" % row["catalog_p"],
                    "%.6g" % row["input_p"],
                    "%.6g" % row["ratio"],
                    "%.6g" % row["delta"],
                    row["mapped_gene"],
                ])


if __name__ == "__main__":
    main(*sys.argv[1:])
