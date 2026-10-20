import gzip
import heapq
import math
import sys


def open_text(path):
    with open(path, "rb") as probe:
        magic = probe.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", errors="replace")
    return open(path, "rt", errors="replace")


def add_top(heap, value, row, limit=25):
    if not math.isfinite(value):
        return
    item = (value, row)
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif item > heap[0]:
        heapq.heapreplace(heap, item)


def rows_desc(heap):
    return [(item[0], item[1]) for item in sorted(heap, reverse=True)]


regions = {
    "FCGR_hg38": ("1", 161480000, 161680000),
    "HLA_hg38": ("6", 32000000, 33000000),
    "TACI_hg38": ("17", 16900000, 17100000),
    "FCGRT_hg38": ("19", 49300000, 49800000),
}
source_regions = {
    "FCGR_hg19": ("1", 161450000, 161650000),
    "HLA_hg19": ("6", 32000000, 33000000),
    "TACI_hg19": ("17", 16800000, 16900000),
    "FCGRT_hg19": ("19", 49300000, 49800000),
}

target_path, source_path, out_path = sys.argv[1:4]
target_heaps = {name: [] for name in regions}
source_heaps = {name: [] for name in source_regions}

with open_text(target_path) as fh:
    header = None
    pidx = None
    for line in fh:
        if not line.strip():
            continue
        if line.startswith("#"):
            header = line.rstrip("\n").split("\t")
            pidx = header.index("P")
            continue
        fields = line.rstrip("\n").split("\t")
        if pidx is None or len(fields) <= pidx:
            fields = line.rstrip("\n").split()
        try:
            chrom = fields[0].removeprefix("chr")
            pos = int(fields[1])
            p = float(fields[pidx])
        except (ValueError, IndexError):
            continue
        for name, (rchrom, start, end) in regions.items():
            if chrom == rchrom and start <= pos <= end:
                add_top(target_heaps[name], -math.log10(p), "\t".join(fields))

with open_text(source_path) as fh:
    source_header = None
    pidx = None
    vidx = None
    cidx = None
    posidx = None
    for line in fh:
        if not line.strip():
            continue
        if source_header is None:
            source_header = line.rstrip("\n").split("\t")
            lower = [x.lower() for x in source_header]
            if "variant" in lower:
                vidx = lower.index("variant")
            else:
                cidx = lower.index("chromosome")
                posidx = lower.index("base_pair_location")
            if "pval" in lower:
                pidx = lower.index("pval")
            else:
                pidx = lower.index("p_value")
            continue
        fields = line.rstrip("\n").split("\t")
        if len(fields) <= max(pidx, vidx if vidx is not None else 0, cidx if cidx is not None else 0, posidx if posidx is not None else 0):
            continue
        try:
            if vidx is not None:
                variant = fields[vidx]
                parts = variant.split(":")
                if len(parts) < 2:
                    continue
                chrom = parts[0].removeprefix("chr")
                pos = int(parts[1])
            else:
                chrom = fields[cidx].removeprefix("chr")
                pos = int(fields[posidx])
            p = float(fields[pidx])
        except (ValueError, IndexError):
            continue
        for name, (rchrom, start, end) in source_regions.items():
            if chrom == rchrom and start <= pos <= end:
                add_top(source_heaps[name], -math.log10(p), "\t".join(fields))

with open(out_path, "w") as out:
    out.write("target_header\t" + "\t".join(header or []) + "\n")
    out.write("source_header\t" + "\t".join(source_header or []) + "\n")
    for name in regions:
        out.write("TARGET_REGION\t" + name + "\n")
        for score, row in rows_desc(target_heaps[name]):
            out.write("TARGET\t" + name + "\t-log10P=" + format(score, ".8g") + "\t" + row + "\n")
    for name in source_regions:
        out.write("SOURCE_REGION\t" + name + "\n")
        for score, row in rows_desc(source_heaps[name]):
            out.write("SOURCE\t" + name + "\t-log10P=" + format(score, ".8g") + "\t" + row + "\n")
