import re
import sys

TARGET_IDS = {
    "rs7554873", "rs143596860", "rs34562254", "rs4273077",
    "rs4561508", "rs4985726", "rs2647032", "rs3763321",
}
TARGET_COORDS = {
    "chr1:161625940", "chr1:161642443", "chr6:32438927",
    "chr6:32662128", "chr17:16939677", "chr17:16945825",
    "chr17:16945436", "chr17:16960324",
}

def is_target(line):
    fields = re.split(r"\s+", line.strip())
    return any(field in TARGET_IDS or field in TARGET_COORDS for field in fields)

out_path = sys.argv[-1]
paths = sys.argv[1:-1]
with open(out_path, "wt", encoding="utf-8") as out:
    for label, path in zip(
        ["A-G", "A-M", "AG-M", "AG", "AGM", "G-M", "IgA", "IgG", "IgM"],
        paths,
    ):
        out.write("sheet\t%s\n" % label)
        with open(path, "rt", encoding="utf-8", errors="replace") as src:
            for line in src:
                if is_target(line):
                    out.write("row\t%s\t%s" % (label, line if line.endswith("\n") else line + "\n"))
