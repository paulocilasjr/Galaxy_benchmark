NR % 4 == 1 {
    records++
    if (substr($0, 1, 1) != "@") bad_headers++
}
NR % 4 == 2 {
    seq_len = length($0)
    bases += seq_len
}
NR % 4 == 3 {
    if (substr($0, 1, 1) != "+") bad_plus++
}
NR % 4 == 0 {
    if (length($0) != seq_len) bad_lengths++
}
END {
    if (NR % 4 != 0) incomplete = 1
    printf "%d\t%d\t%d\t%d\t%d\t%d\n", records, bases, bad_headers, bad_plus, bad_lengths, incomplete
}
