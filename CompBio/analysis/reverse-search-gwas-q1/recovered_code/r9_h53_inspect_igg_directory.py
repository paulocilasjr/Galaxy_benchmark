import gzip
import os
import sys


root = sys.argv[1]
out_path = sys.argv[2]

files = []
for dirpath, _, names in os.walk(root):
    for name in names:
        files.append(os.path.join(dirpath, name))
files.sort()

with open(out_path, "w", encoding="utf-8") as out:
    out.write("path\tsize_bytes\tfirst_lines\n")
    for path in files:
        rel = os.path.relpath(path, root)
        size = os.path.getsize(path)
        lines = []
        opener = gzip.open if path.endswith(".gz") else open
        try:
            with opener(path, "rt", encoding="utf-8", errors="replace") as handle:
                for _ in range(3):
                    line = handle.readline()
                    if not line:
                        break
                    lines.append(line.rstrip("\n").replace("\t", "<TAB>"))
        except Exception as exc:
            lines = ["ERROR:" + type(exc).__name__]
        out.write(rel + "\t" + str(size) + "\t" + "\\n".join(lines) + "\n")
