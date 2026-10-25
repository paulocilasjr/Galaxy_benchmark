import os
import sys
import zipfile
import subprocess


def process_zip(zip_path, group_label, out):
    with zipfile.ZipFile(zip_path) as archive:
        members = sorted(
            name for name in archive.namelist()
            if name.endswith(".faa.mafft")
        )

    for member in members:
        gene = os.path.basename(member)[: -len(".faa.mafft")]
        tmp_path = os.path.join(
            os.getcwd(),
            group_label + "_" + gene + ".faa.mafft",
        )
        with zipfile.ZipFile(zip_path) as archive, open(tmp_path, "wb") as tmp:
            tmp.write(archive.read(member))

        try:
            result = subprocess.run(
                ["phykit", "parsimony_informative_sites", tmp_path],
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        parts = result.stdout.strip().split()
        if len(parts) < 3:
            raise RuntimeError(
                "Unexpected phykit output for {}: {!r}".format(
                    member, result.stdout
                )
            )
        percentage = parts[2]
        out.write("{}\t{}\t{}\n".format(group_label, gene, percentage))


def main():
    animal_zip = sys.argv[1]
    fungi_zip = sys.argv[2]
    output_path = sys.argv[3]

    with open(output_path, "w") as out:
        out.write("group\tgene\tpercentage\n")
        process_zip(animal_zip, "animals", out)
        process_zip(fungi_zip, "fungi", out)


if __name__ == "__main__":
    main()
