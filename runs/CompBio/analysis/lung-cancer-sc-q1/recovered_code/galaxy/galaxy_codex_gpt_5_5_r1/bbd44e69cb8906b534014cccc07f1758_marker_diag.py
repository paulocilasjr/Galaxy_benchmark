import sys, json, math
from collections import Counter, defaultdict
import h5py
import numpy as np
from scipy import sparse
markers = {"Basal": ["KRT5", "KRT6A", "KRT6B", "KRT14", "KRT15", "KRT17", "TP63", "DSG3", "SOX2"], "AT2": ["SFTPA1", "SFTPA2", "SFTPB", "SFTPC", "SLC34A2", "NAPSA", "ABCA3"], "AT1": ["AGER", "PDPN", "AQP5", "CAV1", "EMP2"], "Cilia": ["FOXJ1", "TPPP3", "PIFO", "CAPS", "DNAH5"], "Club": ["SCGB1A1", "SCGB3A1", "SCGB3A2", "MUC5B"], "EC": ["PECAM1", "VWF", "CLDN5", "KDR", "RAMP2"], "Fib": ["COL1A1", "COL1A2", "DCN", "LUM", "PDGFRA", "COL3A1"], "NE": ["CHGA", "CHGB", "ASCL1", "GRP", "CALCA"], "T": ["CD3D", "CD3E", "TRAC", "IL7R"], "CD8": ["CD8A", "CD8B", "GZMK"], "NK": ["NKG7", "GNLY", "KLRD1", "KLRF1"], "B": ["MS4A1", "CD79A", "CD79B", "BANK1"], "DC": ["FCER1A", "CD1C", "CLEC10A", "LILRA4", "CLEC4C", "IRF8", "LAMP3", "CCR7"], "Mac": ["C1QA", "C1QB", "C1QC", "MARCO", "CD68", "APOE"], "Mast": ["TPSAB1", "TPSB2", "CPA3", "MS4A2"], "Gran": ["S100A8", "S100A9", "FCGR3B", "CSF3R"]}
patients=set(['Patient_005','Patient_006','Patient_007','Patient_018','Patient_040'])
nonimmune=set(['Basal','AT2','AT1','Cilia','Club','EC','Fib','NE'])
immune=set(markers)-nonimmune
path,out=sys.argv[1],sys.argv[2]
def dec(x): return x.decode('utf-8','replace') if isinstance(x,bytes) else str(x)
def read_cat(g):
    cats=[dec(x) for x in g['categories'][()]]; codes=g['codes'][()]
    return np.array([cats[int(c)] if int(c)>=0 else '' for c in codes], dtype=object)
with h5py.File(path,'r') as f:
    samples=read_cat(f['obs/sampleID'])
    genes=[dec(x) for x in f['var/symbol'][()]]
    gene_to_idx={g:i for i,g in enumerate(genes)}
    data=f['X/data'][()]
    indices=f['X/indices'][()]
    indptr=f['X/indptr'][()]
    X=sparse.csr_matrix((data,indices,indptr), shape=tuple(f['X'].attrs['shape']))
lib=np.asarray(X.sum(axis=1)).ravel().astype(float)
lib[lib==0]=1.0
found={k:[g for g in v if g in gene_to_idx] for k,v in markers.items()}
score_cols=[]; names=[]
for name,gs in found.items():
    names.append(name)
    if gs:
        sub=X[:,[gene_to_idx[g] for g in gs]].astype(float)
        # normalize selected marker counts by total library size and average log1p CPM/10k.
        vals=sub.multiply(10000.0/lib[:,None])
        score=np.asarray(np.log1p(vals).mean(axis=1)).ravel()
    else:
        score=np.zeros(X.shape[0])
    score_cols.append(score)
S=np.vstack(score_cols).T
max_idx=np.argmax(S,axis=1)
max_score=S[np.arange(S.shape[0]), max_idx]
second=np.partition(S, -2, axis=1)[:,-2]
labels=np.array([names[i] for i in max_idx], dtype=object)
# low-confidence fallback only for completely marker-negative cells
labels[max_score <= 0] = 'Unassigned'
with open(out,'w') as fh:
    fh.write('found_markers\t%s\n' % json.dumps(found, sort_keys=True))
    fh.write('overall_label_counts\t%s\n' % json.dumps(Counter(labels).most_common(), sort_keys=True))
    fh.write('sample\tn\tBasal_mean\tAT2_mean\tAT1_mean\tDC_mean\tPTPRC_present_marker_note\tlabel_counts\tDC_calls\tDC_prop\tnonimmune_calls\tbasal_calls\tbasal_nonimmune_prop\n')
    for smp in sorted(set(samples)):
        mask=(samples==smp)
        n=int(mask.sum())
        cnt=Counter(labels[mask])
        dc=int(cnt.get('DC',0))
        ni=sum(cnt.get(x,0) for x in nonimmune)
        basal=int(cnt.get('Basal',0))
        fh.write('%s\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%s\t%s\t%d\t%.6f\t%d\t%d\t%.6f\n' % (smp,n,S[mask,names.index('Basal')].mean(),S[mask,names.index('AT2')].mean(),S[mask,names.index('AT1')].mean(),S[mask,names.index('DC')].mean(),'none',json.dumps(cnt.most_common(12)),dc,dc/n if n else 0,ni,basal,basal/ni if ni else 0))
    fh.write('candidate_cells\n')
    for smp in sorted(patients):
        mask=(samples==smp); cnt=Counter(labels[mask]); n=int(mask.sum())
        fh.write('%s\t%d\t%s\n' % (smp,n,json.dumps(cnt.most_common(), sort_keys=True)))
