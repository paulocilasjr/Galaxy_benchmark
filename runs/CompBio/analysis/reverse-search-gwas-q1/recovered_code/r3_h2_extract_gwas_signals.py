import gzip
import heapq
import sys


input_path, output_path = sys.argv[1:3]

with open(input_path, "rb") as raw:
    magic = raw.read(2)
opener = gzip.open if magic == b"\x1f\x8b" else open

top = []
row_count = 0
invalid_p = 0
threshold_counts = {5e-8: 0, 1e-10: 0, 1e-20: 0, 1e-50: 0}

with opener(input_path, "rt", encoding="utf-8", errors="replace") as handle:
    header = handle.readline().rstrip("\n\r").split("\t")
    if len(header) < 8 or header[7] != "P":
        raise ValueError(f"Unexpected header: {header!r}")
    for line in handle:
        fields = line.rstrip("\n\r").split("\t")
        if len(fields) < 8:
            continue
        row_count += 1
        try:
            p = float(fields[7])
        except ValueError:
            invalid_p += 1
            continue
        for threshold in threshold_counts:
            if p < threshold:
                threshold_counts[threshold] += 1
        item = (-p, fields[:8])
        if len(top) < 200:
            heapq.heappush(top, item)
        elif p < -top[0][0]:
            heapq.heapreplace(top, item)

with open(output_path, "w", encoding="utf-8") as out:
    out.write("metric\tvalue\n")
    out.write(f"row_count\t{row_count}\n")
    out.write(f"invalid_p\t{invalid_p}\n")
    for threshold, count in threshold_counts.items():
        out.write(f"p_lt_{threshold:g}\t{count}\n")
    out.write("rank\tCHROM\tPOS\tID\tREF\tALT\tA1\tTEST\tP\n")
    for rank, (neg_p, fields) in enumerate(sorted(top, key=lambda x: -x[0]), 1):
        out.write(str(rank) + "\t" + "\t".join(fields) + "\n")
