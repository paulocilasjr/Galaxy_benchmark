import subprocess, pathlib, sys
vcf=sys.argv[1]
q=subprocess.run(['bcftools','query','-f','%CHROM\t%POS\t%POS\n',vcf], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
regions_chr=pathlib.Path('regions_chr.tsv')
regions_no=pathlib.Path('regions_no.tsv')
chrom_counts={}; n=0
with regions_chr.open('w') as a, regions_no.open('w') as b:
    for line in q.stdout.splitlines():
        c,p,_=line.split('\t')[:3]
        chrom_counts[c]=chrom_counts.get(c,0)+1
        c_no=c[3:] if c.startswith('chr') else c
        c_chr=c if c.startswith('chr') else 'chr'+c
        a.write(f'{c_chr}\t{p}\t{p}\n')
        b.write(f'{c_no}\t{p}\t{p}\n')
        n+=1
ref='https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.hgdp_tgp.chr1.vcf.bgz'
for label,reg in [('chr',regions_chr),('nochr',regions_no)]:
    cmd=['bcftools','view','-R',str(reg),'-H',ref]
    p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=600)
    count=p.stdout.count('\n')
    print(label, count, 'return', p.returncode)
    if p.stderr:
        print(label+'_stderr', p.stderr[:1000].replace('\n',' | '))
print('target_total', n)
print('target_chrom_counts', chrom_counts)
