BEGIN { FS = OFS = "\t" }
NR == 1 { next }
{
    n++
    gene[n] = $1
    logfc[n] = $2
    pvalue[n] = $5
}
END {
    running_min = 1
    for (i = n; i >= 1; i--) {
        adjusted = pvalue[i] * n / i
        if (adjusted > 1) adjusted = 1
        if (adjusted > running_min) adjusted = running_min
        running_min = adjusted
        fdr[i] = adjusted
    }

    print "gene", "log2_fold_change", "p_value", "fdr"
    for (i = 1; i <= n; i++) {
        printf "%s%s%.15g%s%.15g%s%.15g\n", gene[i], OFS, logfc[i], OFS, pvalue[i], OFS, fdr[i]
    }
}
