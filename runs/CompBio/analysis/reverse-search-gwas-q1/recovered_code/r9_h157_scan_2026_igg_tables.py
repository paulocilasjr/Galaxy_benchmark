import sys


needles = [
    "rs7554873", "rs143596860", "rs34562254", "rs4273077",
    "rs4561508", "rs4985726", "rs2647032", "rs3763321",
    "rs150420714", "rs2926468",
    "161530", "161595730", "161612233", "161625940", "161642443",
    "32406704", "32438927", "32629905", "32662128",
    "16842991", "16848750", "16849139", "16863638",
    "16939677", "16945436", "16945825", "16960324", "49525049",
    "FCGR", "HLA", "TACI", "TNFRSF13B", "FCGRT", "IGH",
]


def matches(line):
    low = line.lower()
    return any(needle.lower() in low for needle in needles)


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: scan_2026_igg_tables.py label=path ... output")
    output = sys.argv[-1]
    sources = sys.argv[1:-1]
    with open(output, "w", encoding="utf-8") as out:
        for source in sources:
            label, path = source.split("=", 1)
            out.write("TABLE\t%s\n" % label)
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    if matches(line):
                        out.write(line.rstrip("\n") + "\n")


if __name__ == "__main__":
    main()
