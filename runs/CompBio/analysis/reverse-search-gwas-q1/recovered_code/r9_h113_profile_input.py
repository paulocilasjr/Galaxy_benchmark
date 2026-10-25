import gzip
import re
import sys
from collections import Counter

counts = Counter()
id_types = Counter()
headers = []
opener = gzip.open if sys.argv[1].endswith((".gz", ".gzip")) else open
with opener(sys.argv[1], "rt", encoding="utf-8", errors="replace") as text:
    for line in text:
        if line.startswith("#"):
            headers.append(line.rstrip("\n"))
            continue
        fields = re.split(r"\s+", line.strip())
        if len(fields) < 3:
            continue
        counts[fields[0]] += 1
        marker = fields[2]
        if marker.startswith("rs"):
            id_types["rs"] += 1
        elif marker.startswith(fields[0] + ":"):
            id_types["coordinate"] += 1
        else:
            id_types["other"] += 1
print("headers\t%d" % len(headers))
for key in sorted(counts, key=lambda value: (not value.isdigit(), int(value) if value.isdigit() else value)):
    print("chrom\t%s\t%d" % (key, counts[key]))
for key in sorted(id_types):
    print("id_type\t%s\t%d" % (key, id_types[key]))
