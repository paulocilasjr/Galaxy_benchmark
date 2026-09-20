import sys
from pathlib import Path

def rewrite(source, target):
    with Path(source).open("r") as src, Path(target).open("w") as dst:
        header = src.readline().rstrip("\r\n")
        if header.split("\t") != ["gene_id", "gene_length"] and header.split("\t") != ["gene_id", "mean_expression"]:
            raise ValueError("Unexpected input header: " + header)
        dst.write("gene_id\tvalue\n")
        for line in src:
            dst.write(line)

rewrite(sys.argv[1], "gene_lengths_common.tsv")
rewrite(sys.argv[2], "gene_means_common.tsv")

