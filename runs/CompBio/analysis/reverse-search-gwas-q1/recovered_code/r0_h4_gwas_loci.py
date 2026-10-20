import csv
import gzip
import math
import sys
from collections import defaultdict


TARGET_POSITIONS = {
    ("1", 161509955): "rs1801274_FCGR2A",
    ("6", 32461866): "rs9268853_HLA_UC",
    ("6", 32082981): "rs1150754_HLA_SLE",
    ("6", 32638107): "rs2187668_HLA_SLE",
    ("6", 32713854): "rs9275596_HLA_IgAN",
    ("1", 196717788): "rs6677604_CFH_IgAN",
    ("22", 30098382): "rs2412971_HORMAD2_IgAN",
    ("1", 67240275): "rs11209026_IL23R_UC",
    ("1", 19845367): "rs6426833_RNF186_UC",
    ("9", 4981602): "rs10758669_JAK2_UC",
    ("21", 39093608): "rs2836878_UC",
}


def open_text(path):
    with open(path, "rb") as raw:
        magic = raw.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", newline="")
    return open(path, "rt", newline="")


def main(in_path, out_path):
    sig_rows = []
    target_rows = []
    window_best = {}
    rows = 0

    with open_text(in_path) as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        for rec in reader:
            if len(rec) < 8:
                continue
            rows += 1
            chrom = rec[0]
            try:
                pos = int(rec[1])
                p = float(rec[7])
            except ValueError:
                continue
            if not math.isfinite(p):
                continue
            label = TARGET_POSITIONS.get((chrom, pos))
            if label:
                target_rows.append([label] + rec[:8])
            if p < 5e-8:
                sig_rows.append(rec[:8])
                win = pos // 1_000_000
                key = (chrom, win)
                if key not in window_best or p < window_best[key][0]:
                    window_best[key] = (p, rec[:8])

    leads = [v[1] for _, v in sorted(window_best.items(), key=lambda kv: (kv[0][0].zfill(2), kv[0][1]))]
    leads_by_p = sorted(leads, key=lambda r: float(r[7]))[:250]

    with open(out_path, "w", newline="") as out:
        out.write("section\tvalue\n")
        out.write("rows\t%d\n" % rows)
        out.write("genome_wide_significant_rows\t%d\n" % len(sig_rows))
        out.write("lead_1mb_windows\t%d\n" % len(leads))
        out.write("\ntarget_positions\n")
        out.write("label\t#CHROM\tPOS\tID\tREF\tALT\tA1\tTEST\tP\n")
        for rec in target_rows:
            out.write("\t".join(rec) + "\n")
        out.write("\nlead_windows_by_p\n")
        out.write("#CHROM\tPOS\tID\tREF\tALT\tA1\tTEST\tP\n")
        for rec in leads_by_p:
            out.write("\t".join(rec) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
