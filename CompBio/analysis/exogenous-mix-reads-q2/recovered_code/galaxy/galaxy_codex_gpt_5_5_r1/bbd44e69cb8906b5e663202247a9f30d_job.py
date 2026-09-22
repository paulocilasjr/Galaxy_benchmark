import sys
from collections import Counter

def readfq(p):
    r=[]
    with open(p) as h:
        while True:
            n=h.readline().rstrip('\n')
            if not n: break
            s=h.readline().rstrip('\n').upper(); h.readline(); q=h.readline().rstrip('\n')
            r.append((n,s,q))
    return r

def kmers(seq,k):
    return [seq[i:i+k] for i in range(len(seq)-k+1) if 'N' not in seq[i:i+k]]

def kset(rs,k):
    z=set()
    for _,s,_ in rs: z.update(kmers(s,k))
    return z

mix=readfq(sys.argv[1]); endo=readfq(sys.argv[2]); exo=readfq(sys.argv[3])
lines=['segment\tn\tk\texo_private_reads\tendo_private_reads\tboth\tneither']
segments=[('mix_1_395',mix[:395]),('mix_396_592',mix[395:592]),('mix_593_691',mix[592:]),('exo_all',exo),('endo_all',endo)]
for k in [23,31,41,47]:
    xp=kset(exo,k)-kset(endo,k)
    dp=kset(endo,k)-kset(exo,k)
    for name,rs in segments:
        xc=dc=bc=nc=0
        for _,s,_ in rs:
            x=any(t in xp for t in kmers(s,k)); d=any(t in dp for t in kmers(s,k))
            if x and d: bc+=1
            elif x: xc+=1
            elif d: dc+=1
            else: nc+=1
        lines.append(f'{name}\t{len(rs)}\t{k}\t{xc}\t{dc}\t{bc}\t{nc}')
open(sys.argv[4],'w').write('\n'.join(lines)+'\n')
