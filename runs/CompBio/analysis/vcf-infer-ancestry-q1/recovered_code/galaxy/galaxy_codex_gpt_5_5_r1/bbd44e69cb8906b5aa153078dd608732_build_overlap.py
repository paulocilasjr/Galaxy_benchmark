import subprocess, pathlib, sys
vcf=sys.argv[1]
q=subprocess.run(['bcftools','query','-f','%CHROM\t%POS\t%POS\n',vcf], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
lines=[]
for line in q.stdout.splitlines():
    c,p,_=line.split('\t')[:3]
    c_no=c[3:] if c.startswith('chr') else c
    lines.append((c_no,int(p)))
lines.sort(key=lambda x:x[1])
# select first 3000 evenly, write region files for 1 and chr1.
def sel(items,n):
    if len(items)<=n: return items
    return [items[round(i*(len(items)-1)/(n-1))] for i in range(n)]
selected=sel(lines,3000)
with open('regions_1.tsv','w') as a, open('regions_chr1.tsv','w') as b:
    for c,p in selected:
        a.write(f'{c}\t{p}\t{p}\n')
        b.write(f'chr{c}\t{p}\t{p}\n')
refs=[
 ('1000g37','regions_chr1.tsv','https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz'),
 ('gnomad211_37','regions_1.tsv','https://storage.googleapis.com/gcp-public-data--gnomad/release/2.1.1/vcf/genomes/gnomad.genomes.r2.1.1.sites.1.vcf.bgz'),
 ('zenodo','regions_chr1.tsv','https://zenodo.org/records/18156285/files/hgdp1kgp_chr1.shapeit5_phased.filter1_SNP_maf005.rechr.vcf.gz?download=1'),
]
print('target_total',len(lines))
print('selected',len(selected), 'first', selected[:3], 'last', selected[-3:])
for name,reg,url in refs:
    cmd=['bcftools','view','-G','-R',reg,'-H',url]
    try:
        p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
        out=p.stdout.decode('utf-8','replace')
        err=p.stderr.decode('utf-8','replace')[-500:].replace('\n',' | ')
        print(name, 'return', p.returncode, 'count', out.count('\n'), 'err', err)
    except Exception as e:
        print(name, 'EXCEPTION', repr(e))
