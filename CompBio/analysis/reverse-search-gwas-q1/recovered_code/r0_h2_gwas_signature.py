import csv
import gzip
import heapq
import io
import math
import sys
from collections import Counter


def open_text(path):
    with open(path, "rb") as raw:
        magic = raw.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", newline="")
    return open(path, "rt", newline="")


def main(in_path, out_path):
    top_n = 100
    rows = 0
    malformed = 0
    p_missing = 0
    min_p = None
    chrom_counts = Counter()
    top = []
    first_data = []
    header = None

    with open_text(in_path) as handle:
        reader = csv.reader(handle, delimiter="\t")
        for rec in reader:
            if not rec:
                continue
            if header is None:
                header = rec
                continue
            rows += 1
            if len(rec) < 8:
                malformed += 1
                continue
            if len(first_data) < 5:
                first_data.append(rec[:8])
            chrom_counts[rec[0]] += 1
            try:
                p = float(rec[7])
            except ValueError:
                p_missing += 1
                continue
            if not math.isfinite(p):
                p_missing += 1
                continue
            if min_p is None or p < min_p:
                min_p = p
            # Heap root is the largest P among retained records.
            key = (-p, rows, rec[:8])
            if len(top) < top_n:
                heapq.heappush(top, key)
            elif key > top[0]:
                heapq.heapreplace(top, key)

    top_rows = [item[2] for item in sorted(top, key=lambda x: (-x[0], x[1]))]

    with open(out_path, "w", newline="") as out:
        out.write("section\tvalue\n")
        out.write("header\t%s\n" % "\t".join(header or []))
        out.write("rows\t%d\n" % rows)
        out.write("malformed_rows\t%d\n" % malformed)
        out.write("missing_or_invalid_p\t%d\n" % p_missing)
        out.write("min_p\t%s\n" % ("" if min_p is None else format(min_p, ".17g")))
        out.write("chrom_counts\t%s\n" % ";".join(f"{k}:{chrom_counts[k]}" for k in sorted(chrom_counts, key=lambda x: (len(x), x))))
        out.write("\nfirst_rows\n")
        out.write("#CHROM\tPOS\tID\tREF\tALT\tA1\tTEST\tP\n")
        for rec in first_data:
            out.write("\t".join(rec) + "\n")
        out.write("\ntop_by_p\n")
        out.write("#CHROM\tPOS\tID\tREF\tALT\tA1\tTEST\tP\n")
        for rec in top_rows:
            out.write("\t".join(rec) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
