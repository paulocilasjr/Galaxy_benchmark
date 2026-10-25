import gzip
import sys

path = sys.argv[1]
opener = gzip.open if path.endswith((".gz", ".gzip")) else open
with opener(path, "rt", encoding="utf-8", errors="replace") as text:
    count = 0
    for line in text:
        if line.strip():
            count += 1
    print("nonempty_lines\t%d" % count)
