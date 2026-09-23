BEGIN { FS = OFS = "\t" }
NR == 1 {
    print "sample", "disease", "cell_type"
    next
}
{
    disease = $4
    cell_type = $5
    gsub(/[ -]/, "_", disease)
    gsub(/[ -]/, "_", cell_type)
    print $1, disease, cell_type
}
