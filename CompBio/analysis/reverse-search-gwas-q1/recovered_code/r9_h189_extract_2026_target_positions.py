import re
import sys

targets = {
    "1:161530615", "1:161530617", "1:161531006", "1:161540726",
    "1:161558222", "1:161595363", "1:161625940", "1:161642443",
    "1:161649573", "6:32067917", "6:32662128", "6:32629905",
    "17:16939677", "17:16941853", "17:16945436", "17:16945825",
    "17:16960324", "19:49525049",
}
ids = {
    "rs7554873", "rs143596860", "rs34562254", "rs4273077",
    "rs4561508", "rs4985726", "rs2647032", "rs3763321",
}

def wanted(line):
    low = line.lower()
    if any(x.lower() in low for x in ids):
        return True
    for chrom, pos in re.findall(r"(?:chr)?(1|6|17|19)[: _-](161530615|161530617|161531006|161540726|161558222|161595363|161625940|161642443|161649573|32067917|32662128|32629905|16939677|16941853|16945436|16945825|16960324|49525049)", low):
        if f"{chrom}:{pos}" in targets:
            return True
    return False

src = sys.argv[1]
out = sys.argv[2]
with open(src, "rt", encoding="utf-8", errors="replace") as inp, open(out, "wt", encoding="utf-8") as dst:
    table = ""
    for line in inp:
        if line.startswith("TABLE\t"):
            table = line.rstrip("\n")
        elif wanted(line):
            dst.write(table + "\n")
            dst.write(line if line.endswith("\n") else line + "\n")
