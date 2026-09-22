import gzip, subprocess, pathlib, sys
vcf=sys.argv[1]
# read target variant positions without parsing genotypes
opener=gzip.open if vcf.endswith('.gz') else open
chrom_counts={}
regions_chr=pathlib.Path('regions_chr.tsv')
regions_no=pathlib.Path('regions_no.tsv')
with opener(vcf,'rt',errors='replace') as f, regions_chr.open('w') as a, regions_no.open('w') as b:
    n=0
    for line in f:
        if not line or line[0]=='#':
            continue
        fields=line.split('\t',5)
        if len(fields)<2: continue
        c=fields[0]; p=fields[1]
        chrom_counts[c]=chrom_counts.get(c,0)+1
        c_no=c[3:] if c.startswith('chr') else c
        c_chr=c if c.startswith('chr') else 'chr'+c
        a.write(f'{c_chr}\t{p}\t{p}\n')
        b.write(f'{c_no}\t{p}\t{p}\n')
        n+=1
ref='https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.hgdp_tgp.chr1.vcf.bgz'
for label,reg in [('chr',regions_chr),('nochr',regions_no)]:
    cmd=['bcftools','view','-R',str(reg),'-H',ref]
    try:
        p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
        count=sum(1 for _ in p.stdout.splitlines())
        print(label, count, 'return', p.returncode)
        if p.stderr:
            print(label+'_stderr', p.stderr[:1000].replace('\n',' | '))
    except Exception as e:
        print(label, 'EXCEPTION', repr(e))
print('target_total', n)
print('target_chrom_counts', chrom_counts)
