import sys,json
from collections import Counter
import h5py, numpy as np
from scipy import sparse
markers={"Basal": ["KRT5", "KRT6A", "KRT6B", "KRT14", "KRT15", "KRT17", "TP63", "DSG3", "SOX2"], "AT2": ["SFTPA1", "SFTPA2", "SFTPB", "SFTPC", "SLC34A2", "NAPSA", "ABCA3"], "AT1": ["AGER", "PDPN", "AQP5", "CAV1", "EMP2"], "Cilia": ["FOXJ1", "TPPP3", "PIFO", "CAPS", "DNAH5"], "Club": ["SCGB1A1", "SCGB3A1", "SCGB3A2", "MUC5B"], "EC": ["PECAM1", "VWF", "CLDN5", "KDR", "RAMP2"], "Fib": ["COL1A1", "COL1A2", "DCN", "LUM", "PDGFRA", "COL3A1"], "NE": ["CHGA", "CHGB", "ASCL1", "GRP", "CALCA"], "T": ["CD3D", "CD3E", "TRAC", "IL7R"], "CD8": ["CD8A", "CD8B", "GZMK"], "NK": ["NKG7", "GNLY", "KLRD1", "KLRF1"], "B": ["MS4A1", "CD79A", "CD79B", "BANK1"], "DC": ["FCER1A", "CD1C", "CLEC10A", "LILRA4", "CLEC4C", "IRF8", "LAMP3", "CCR7"], "Mac": ["C1QA", "C1QB", "C1QC", "MARCO", "CD68", "APOE"], "Mast": ["TPSAB1", "TPSB2", "CPA3", "MS4A2"], "Gran": ["S100A8", "S100A9", "FCGR3B", "CSF3R"]}
patients=set(['Patient_005','Patient_006','Patient_007','Patient_018','Patient_040'])
nonimmune=set(['Basal','AT2','AT1','Cilia','Club','EC','Fib','NE'])
path,out=sys.argv[1],sys.argv[2]
def dec(x): return x.decode('utf-8','replace') if isinstance(x,bytes) else str(x)
def read_cat(g):
    cats=[dec(x) for x in g['categories'][()]]; codes=g['codes'][()]
    return np.array([cats[int(c)] if int(c)>=0 else '' for c in codes], dtype=object)
with h5py.File(path,'r') as f:
    samples=read_cat(f['obs/sampleID'])
    genes=[dec(x) for x in f['var/symbol'][()]]; gi={g:i for i,g in enumerate(genes)}
    X=sparse.csr_matrix((f['X/data'][()],f['X/indices'][()],f['X/indptr'][()]), shape=tuple(f['X'].attrs['shape']))
lib=np.asarray(X.sum(axis=1)).ravel().astype(float); lib[lib==0]=1
names=[]; sc=[]
for n,gs in markers.items():
    names.append(n); cols=[gi[g] for g in gs if g in gi]
    if cols:
        vals=X[:,cols].astype(float).multiply(10000.0/lib[:,None])
        sc.append(np.asarray(np.log1p(vals).mean(axis=1)).ravel())
    else: sc.append(np.zeros(X.shape[0]))
S=np.vstack(sc).T; labels=np.array([names[i] for i in np.argmax(S,axis=1)], dtype=object); labels[S.max(axis=1)<=0]='Unassigned'
basal=S[:,names.index('Basal')]; at2=S[:,names.index('AT2')]
# sample LUSC rule from epithelial signatures
sample_lusc={s for s in sorted(set(samples)) if basal[samples==s].mean()>at2[samples==s].mean() and basal[samples==s].mean()>0.05}
# malignant basal marker normalized expression
extra=['KPNA2','PPT1','MKI67','TOP2A','MCM2','PCNA']
extra_cols=[gi[g] for g in extra if g in gi]
E=X[:,extra_cols].astype(float).multiply(10000.0/lib[:,None]) if extra_cols else sparse.csr_matrix((X.shape[0],0))
Elog=np.log1p(E.toarray()) if extra_cols else np.zeros((X.shape[0],0))
extra_names=[g for g in extra if g in gi]
base_mask=np.array([(s in sample_lusc) for s in samples]) & (labels=='Basal')
nonimmune_mask=np.array([lab in nonimmune for lab in labels])
with open(out,'w') as fh:
    fh.write('sample_lusc\t%s\n' % json.dumps(sorted(sample_lusc)))
    fh.write('candidate_lusc_dc\t%s\n' % json.dumps({s:float(((samples==s)&(labels=='DC')).sum()/max(1,(samples==s).sum())) for s in patients if s in sample_lusc}, sort_keys=True))
    fh.write('nonimmune_total\t%d\n' % int(nonimmune_mask.sum()))
    fh.write('basal_lusc_all\t%d\t%.6f\n' % (int(base_mask.sum()), 100*base_mask.sum()/nonimmune_mask.sum()))
    fh.write('extra_names\t%s\n' % json.dumps(extra_names))
    for thr in [0,0.1,0.25,0.5,0.75,1.0,1.25,1.5]:
        if Elog.shape[1]:
            m=base_mask & (Elog.max(axis=1)>thr)
        else: m=base_mask
        pct=100*m.sum()/nonimmune_mask.sum()
        fh.write('malig_thr_max_extra_gt\t%.2f\t%d\t%.6f\tnearest20_%d\n' % (thr,int(m.sum()),pct,int(round(pct/20)*20)))
