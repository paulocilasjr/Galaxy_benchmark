import gzip
import sys

src, n = sys.argv[1], int(sys.argv[2])
with gzip.open(src, "rt", errors="replace") as fh:
    for i, line in enumerate(fh):
        if i >= n:
            break
        print(line.rstrip("\n"))
