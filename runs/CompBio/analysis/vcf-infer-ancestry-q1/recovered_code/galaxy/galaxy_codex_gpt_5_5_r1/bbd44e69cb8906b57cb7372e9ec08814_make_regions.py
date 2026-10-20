import subprocess, pathlib, sys
vcf=sys.argv[1]
q=subprocess.run(['bcftools','query','-f','%CHROM\t%POS\t%POS\n',vcf], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
chrom_counts={}; n=0
with open('regions_chr.tsv','w') as a, open('regions_no.tsv','w') as b:
    for line in q.stdout.splitlines():
        c,p,_=line.split('\t')[:3]
        chrom_counts[c]=chrom_counts.get(c,0)+1
        c_no=c[3:] if c.startswith('chr') else c
        c_chr=c if c.startswith('chr') else 'chr'+c
        a.write(f'{c_chr}\t{p}\t{p}\n')
        b.write(f'{c_no}\t{p}\t{p}\n')
        n += 1
with open('summary_start.txt','w') as out:
    out.write(f'target_total\t{n}\n')
    out.write(f'target_chrom_counts\t{chrom_counts}\n')
