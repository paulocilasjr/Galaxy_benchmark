import sys
from collections import Counter

def read_fastq(path):
    out=[]
    with open(path) as h:
        while True:
            n=h.readline().rstrip('\n')
            if not n: break
            s=h.readline().rstrip('\n')
            p=h.readline().rstrip('\n')
            q=h.readline().rstrip('\n')
            out.append((n,s,q))
    return out

def inter(a,b):
    return sum((Counter(a)&Counter(b)).values())

def prefix_eq(a,b,key=lambda x:x):
    m=min(len(a),len(b)); c=0
    for i in range(m):
        if key(a[i])==key(b[i]): c+=1
        else: break
    return c

mix=read_fastq(sys.argv[1]); endo=read_fastq(sys.argv[2]); exo=read_fastq(sys.argv[3])
sets={'full':lambda r:r,'seqqual':lambda r:(r[1],r[2]),'seq':lambda r:r[1]}
lines=['metric\tvalue']
for name,fn in sets.items():
    M=[fn(r) for r in mix]; E=[fn(r) for r in endo]; X=[fn(r) for r in exo]
    lines.append(f'{name}_inter_mix_endo\t{inter(M,E)}')
    lines.append(f'{name}_inter_mix_exo\t{inter(M,X)}')
    lines.append(f'{name}_inter_endo_exo\t{inter(E,X)}')
    lines.append(f'{name}_prefix_mix_endo\t{prefix_eq(mix,endo,fn)}')
    lines.append(f'{name}_prefix_mix_exo\t{prefix_eq(mix,exo,fn)}')
    lines.append(f'{name}_prefix_endo_exo\t{prefix_eq(endo,exo,fn)}')
    lines.append(f'{name}_mix_equals_endo_plus_exo_multiset\t{Counter(M)==Counter(E)+Counter(X)}')
    lines.append(f'{name}_mix_equals_exo_plus_nonoverlap_resid\t{sum((Counter(M)-Counter(X)).values())}')
    lines.append(f'{name}_mix_equals_endo_plus_nonoverlap_resid\t{sum((Counter(M)-Counter(E)).values())}')
# exact index ranges where mix matches endo/exo by seqqual
for label, arr in [('endo',endo),('exo',exo)]:
    fn=lambda r:(r[1],r[2])
    hits=sum(1 for i,r in enumerate(arr) if i < len(mix) and fn(mix[i])==fn(r))
    lines.append(f'seqqual_same_index_mix_{label}\t{hits}')
open(sys.argv[4],'w').write('\n'.join(lines)+'\n')
