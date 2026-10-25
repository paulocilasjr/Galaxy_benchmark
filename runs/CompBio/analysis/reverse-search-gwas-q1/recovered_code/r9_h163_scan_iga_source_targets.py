import sys


targets = {
    "1:161530617", "1:161531006", "1:161540726", "1:161530615",
    "1:161595363", "1:161558222", "1:161533223", "1:161642443",
    "1:161513694", "1:161530922", "1:161540644", "1:161625940",
    "6:32438927", "6:32662128", "6:32406704", "6:32629905",
    "17:16939677", "17:16945436", "17:16945825", "17:16960324",
    "17:16842991", "17:16848750", "17:16849139", "17:16863638",
    "19:49525049",
}


def main():
    source = sys.argv[1]
    output = sys.argv[2]
    with open(output, "w", encoding="utf-8") as out:
        out.write("SNP\tCHR\tBP_hg19\tA1\tA2\tBETA\tSE\tP\n")
        with open(source, "r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                fields = line.rstrip("\n").split("\t")
                if fields and fields[0] in targets:
                    out.write(line.rstrip("\n") + "\n")


if __name__ == "__main__":
    main()
