#!/usr/bin/env python3
import gzip
import heapq
import math
import sys


input_path, top_path, diagnostics_path = sys.argv[1:4]

with open(input_path, "rb") as probe:
    compressed = probe.read(2) == b"\x1f\x8b"
opener = gzip.open if compressed else open

top_n = 250
heap = []
chrom_min = {}
thresholds = [5e-8, 1e-7, 1e-6, 1e-5, 1e-4]
counts = {threshold: 0 for threshold in thresholds}
valid_rows = 0
invalid_rows = 0

with opener(input_path, "rt", encoding="utf-8", errors="replace") as handle:
    header = handle.readline().rstrip("\n\r").split("\t")
    required = {"#CHROM", "POS", "ID", "REF", "ALT", "A1", "TEST", "P"}
    if not required.issubset(header):
        raise SystemExit("Required PLINK columns are absent: " + repr(header))
    ix = {name: header.index(name) for name in required}
    for line_number, line in enumerate(handle, 2):
        fields = line.rstrip("\n\r").split("\t")
        try:
            p = float(fields[ix["P"]])
            if not math.isfinite(p) or p < 0 or p > 1:
                raise ValueError
            chrom = fields[ix["#CHROM"]]
            pos = int(fields[ix["POS"]])
        except (ValueError, IndexError):
            invalid_rows += 1
            continue
        valid_rows += 1
        for threshold in thresholds:
            if p < threshold:
                counts[threshold] += 1
        record = (p, chrom, pos, fields[ix["ID"]], fields[ix["REF"]],
                  fields[ix["ALT"]], fields[ix["A1"]], fields[ix["TEST"]])
        prior = chrom_min.get(chrom)
        if prior is None or record < prior:
            chrom_min[chrom] = record
        item = (-p, record)
        if len(heap) < top_n:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)

top = sorted(record for _, record in heap)
with open(top_path, "w", encoding="utf-8") as out:
    out.write("rank\tP\tCHROM\tPOS\tID\tREF\tALT\tA1\tTEST\n")
    for rank, record in enumerate(top, 1):
        p, chrom, pos, marker, ref, alt, a1, test = record
        out.write(f"{rank}\t{p:.17g}\t{chrom}\t{pos}\t{marker}\t{ref}\t{alt}\t{a1}\t{test}\n")

with open(diagnostics_path, "w", encoding="utf-8") as out:
    out.write("metric\tvalue\n")
    out.write(f"valid_rows\t{valid_rows}\n")
    out.write(f"invalid_rows\t{invalid_rows}\n")
    out.write(f"gzip_encoded\t{str(compressed).lower()}\n")
    for threshold in thresholds:
        out.write(f"p_lt_{threshold:g}\t{counts[threshold]}\n")
    for chrom in sorted(chrom_min, key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else x)):
        record = chrom_min[chrom]
        out.write(f"chr{chrom}_min_p\t{record[0]:.17g}|{record[3]}\n")
