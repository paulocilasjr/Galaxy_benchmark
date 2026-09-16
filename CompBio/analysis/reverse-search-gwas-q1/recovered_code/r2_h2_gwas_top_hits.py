#!/usr/bin/env python3
import gzip
import heapq
import math
import sys
from collections import Counter


def open_maybe_gzip(path):
    with open(path, "rb") as raw:
        magic = raw.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "rt", encoding="utf-8", errors="replace")


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: gwas_top_hits.py INPUT TOP_OUT DIAG_OUT")
    input_path, top_out, diag_out = sys.argv[1:]

    keep_n = 500
    top_heap = []
    threshold_counts = Counter()
    chr_sig_counts = Counter()
    chr_counts = Counter()
    row_count = 0
    bad_p = 0
    header = None
    min_p = math.inf

    with open_maybe_gzip(input_path) as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.rstrip("\n")
            if not line:
                continue
            fields = line.split("\t")
            if line_number == 1 and fields[0] == "#CHROM":
                header = fields
                continue
            if len(fields) < 8:
                bad_p += 1
                continue
            try:
                p_value = float(fields[7])
            except ValueError:
                bad_p += 1
                continue
            if not math.isfinite(p_value):
                bad_p += 1
                continue

            row_count += 1
            chrom = fields[0]
            chr_counts[chrom] += 1
            min_p = min(min_p, p_value)
            if p_value < 5e-8:
                threshold_counts["p_lt_5e-8"] += 1
                chr_sig_counts[chrom] += 1
            if p_value < 1e-10:
                threshold_counts["p_lt_1e-10"] += 1
            if p_value < 1e-20:
                threshold_counts["p_lt_1e-20"] += 1

            row_key = (p_value, line_number, fields[:8])
            heap_item = (-p_value, -line_number, row_key)
            if len(top_heap) < keep_n:
                heapq.heappush(top_heap, heap_item)
            elif heap_item > top_heap[0]:
                heapq.heapreplace(top_heap, heap_item)

    top_rows = [item[2] for item in top_heap]
    top_rows.sort(key=lambda item: (item[0], item[1]))

    with open(top_out, "w", encoding="utf-8") as out:
        out.write("rank\tline_number\t" + "\t".join(header or ["#CHROM", "POS", "ID", "REF", "ALT", "A1", "TEST", "P"]) + "\n")
        for rank, (p_value, line_number, fields) in enumerate(top_rows, start=1):
            out.write(f"{rank}\t{line_number}\t" + "\t".join(fields) + "\n")

    with open(diag_out, "w", encoding="utf-8") as out:
        out.write("metric\tvalue\n")
        out.write(f"row_count\t{row_count}\n")
        out.write(f"bad_p_or_short_rows\t{bad_p}\n")
        out.write(f"min_p\t{min_p:.17g}\n")
        for key in ["p_lt_5e-8", "p_lt_1e-10", "p_lt_1e-20"]:
            out.write(f"{key}\t{threshold_counts[key]}\n")
        out.write("chromosome_counts\t" + ";".join(f"{k}:{chr_counts[k]}" for k in sorted(chr_counts, key=lambda x: (len(x), x))) + "\n")
        out.write("chromosome_sig_counts\t" + ";".join(f"{k}:{chr_sig_counts[k]}" for k in sorted(chr_sig_counts, key=lambda x: (len(x), x))) + "\n")


if __name__ == "__main__":
    main()
