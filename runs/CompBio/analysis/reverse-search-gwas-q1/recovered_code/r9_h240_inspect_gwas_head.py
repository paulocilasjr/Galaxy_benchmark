import gzip
import sys

source = sys.argv[1]
out_path = sys.argv[2]

opener = gzip.open if source.endswith(".gz") else open
with opener(source, "rt", encoding="utf-8", errors="replace") as src, open(out_path, "wt", encoding="utf-8") as out:
    for i, line in enumerate(src):
        out.write(f"{i+1}\t{line}")
        if i >= 9:
            break
