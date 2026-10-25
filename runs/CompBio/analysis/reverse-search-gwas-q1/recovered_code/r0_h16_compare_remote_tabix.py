import csv
import gzip
import math
import subprocess
import sys
from collections import defaultdict


LEAD_TARGETS = {
    ("1", 161530617),
    ("6", 32067917),
    ("6", 31614248),
    ("17", 16939677),
    ("6", 30931873),
    ("19", 49525049),
    ("4", 3445429),
    ("6", 29686923),
    ("4", 102486185),
    ("2", 111471251),
    ("13", 108308037),
    ("2", 27508073),
    ("6", 33546790),
}


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
    except Exception:
        return None
    return None


def main(gwas_path, candidates_path, out_path):
    targets = {}
    first_needed = 5
    with open_text(gwas_path) as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for rec in reader:
            key = (rec["#CHROM"], int(rec["POS"]))
            if len(targets) < first_needed or key in LEAD_TARGETS:
                targets[key] = rec
            if len(targets) >= first_needed + len(LEAD_TARGETS):
                break

    candidates = []
    with open_text(candidates_path) as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            candidates.append(row)

    with open(out_path, "w", newline="") as out:
        w = csv.writer(out, delimiter="\t")
        w.writerow(["section", "pmid", "accession", "trait", "targets", "found", "within10x", "within100x", "best_log10_delta", "mean_log10_delta"])
        detail_rows = []
        for cand in candidates:
            url = cand["url"]
            found = 0
            deltas = []
            for chrom, pos in sorted(targets, key=lambda x: (int(x[0]) if x[0].isdigit() else 999, x[1])):
                region = f"{chrom}:{pos}-{pos}"
                proc = subprocess.run(["tabix", url, region], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if proc.returncode not in (0, 1):
                    detail_rows.append(["error", cand["pmid"], cand["accession"], cand["trait"], chrom, pos, proc.stderr.strip()[:200]])
                    continue
                if not proc.stdout.strip():
                    detail_rows.append(["detail", cand["pmid"], cand["accession"], cand["trait"], chrom, pos, targets[(chrom, pos)]["P"], "", "", "not_found"])
                    continue
                for line in proc.stdout.splitlines():
                    fields = line.rstrip("\n").split("\t")
                    # GWAS Catalog harmonised files place hm_* columns first and p_value later.
                    remote_p = fields[20] if len(fields) > 20 else ""
                    remote_pos = fields[3] if len(fields) > 3 else ""
                    input_p = parse_p(targets[(chrom, pos)]["P"])
                    rp = parse_p(remote_p)
                    delta = ""
                    ratio = ""
                    if input_p is not None and rp and input_p > 0 and rp > 0:
                        d = abs(math.log10(input_p) - math.log10(rp))
                        delta = "%.6g" % d
                        ratio = "%.6g" % (input_p / rp)
                        deltas.append(d)
                    found += 1
                    detail_rows.append(["detail", cand["pmid"], cand["accession"], cand["trait"], chrom, pos, targets[(chrom, pos)]["P"], remote_p, ratio, delta])
                    break
            within10 = sum(d <= 1 for d in deltas)
            within100 = sum(d <= 2 for d in deltas)
            w.writerow(["summary", cand["pmid"], cand["accession"], cand["trait"], len(targets), found, within10, within100, "" if not deltas else "%.6g" % min(deltas), "" if not deltas else "%.6g" % (sum(deltas) / len(deltas))])
        w.writerow([])
        w.writerow(["section", "pmid", "accession", "trait", "chrom", "pos", "input_p", "remote_p", "input_over_remote", "abs_log10_delta"])
        for row in detail_rows:
            w.writerow(row)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
