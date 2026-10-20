import gzip
import sys
from collections import deque

opener = gzip.open if sys.argv[1].endswith((".gz", ".gzip")) else open
tail = deque(maxlen=20)
with opener(sys.argv[1], "rt", encoding="utf-8", errors="replace") as text:
    for line in text:
        if line.strip():
            tail.append(line.rstrip("\n"))
for line in tail:
    print(line)
