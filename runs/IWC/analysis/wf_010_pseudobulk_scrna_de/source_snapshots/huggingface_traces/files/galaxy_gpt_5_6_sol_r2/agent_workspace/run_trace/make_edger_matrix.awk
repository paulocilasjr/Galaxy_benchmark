BEGIN { FS = OFS = "\t" }
NR == 1 {
    for (i = 2; i <= NF; i++) {
        gsub(/#/, "Num", $i)
    }
}
{ print }
