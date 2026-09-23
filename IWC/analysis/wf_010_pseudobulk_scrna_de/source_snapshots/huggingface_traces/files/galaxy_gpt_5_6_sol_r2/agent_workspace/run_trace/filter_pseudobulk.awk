BEGIN { FS = OFS = "\t" }

# First pass: derive every sample's total directly from the count matrix.
FNR == NR {
    if (FNR == 1) {
        n = NF - 1
        for (i = 2; i <= NF; i++) {
            header[i] = $i
        }
        next
    }
    for (i = 2; i <= NF; i++) {
        total[i] += $i
    }
    next
}

# Second pass header: derive M and S once, then emit the required header.
FNR == 1 {
    for (i = 2; i <= n + 1; i++) {
        sorted[i - 1] = total[i]
    }
    for (i = 1; i <= n; i++) {
        for (j = i + 1; j <= n; j++) {
            if (sorted[j] < sorted[i]) {
                tmp = sorted[i]
                sorted[i] = sorted[j]
                sorted[j] = tmp
            }
        }
    }
    if (n % 2 == 1) {
        median = sorted[(n + 1) / 2]
    } else {
        median = (sorted[n / 2] + sorted[n / 2 + 1]) / 2
    }
    raw_s = 10 + 0.7 * (n - 10)
    s = (raw_s == int(raw_s)) ? raw_s : int(raw_s) + 1

    printf "gene"
    for (i = 2; i <= n + 1; i++) {
        printf "%s%s", OFS, header[i]
    }
    printf "\n"
    next
}

{
    summed = 0
    qualifying_samples = 0
    for (i = 2; i <= NF; i++) {
        value = $i + 0
        summed += value
        # CPM >= (10 / M) * 1e6 is equivalent to count * M >= 10 * sample total.
        if (value * median >= 10 * total[i]) {
            qualifying_samples++
        }
    }
    if (qualifying_samples >= s && summed >= 1000) {
        printf "%s", $1
        for (i = 2; i <= NF; i++) {
            printf "%s%.0f", OFS, $i
        }
        printf "\n"
        retained++
    }
}

END {
    printf "N=%d\nM=%.10g\nS=%d\nCPM_cutoff=%.12g\nretained_genes=%d\n", n, median, s, 10 / median * 1000000, retained > "/dev/stderr"
}
