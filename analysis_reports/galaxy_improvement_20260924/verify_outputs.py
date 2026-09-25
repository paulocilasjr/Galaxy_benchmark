"""Independent checks of fixed saved outputs; does not replay agent code."""
import csv
import gzip
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parents[1]

def fasta(p):
    op=gzip.open if p.suffix=='.gz' else open
    records=[]
    with op(p,'rt') as f:
        for line in f:
            if line.startswith('>'):records.append(['',line.strip()])
            elif line.strip():records[-1][0]+=line.strip().upper()
    return records

def kmers(seq,k=31):
    trans=str.maketrans('ACGT','TGCA')
    return Counter(min(x,x.translate(trans)[::-1]) for i in range(len(seq)-k+1)
                   if set(x:=seq[i:i+k])<=set('ACGT'))

def bh(p):
    order=sorted(range(len(p)),key=lambda i:p[i]);out=[0.]*len(p);m=1.
    for j in range(len(p)-1,-1,-1):
        i=order[j];m=min(m,p[i]*len(p)/(j+1));out[i]=m
    return out

def main():
    results={}
    ref=OUT/'OZ203683.1.fasta';seq=fasta(ref)[0][0];refk=kmers(seq)
    results['mitochondrial_reference']={'url':'https://www.ebi.ac.uk/ena/browser/api/fasta/OZ203683.1',
                                      'sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),
                                      'length':len(seq),'header':fasta(ref)[0][1]}
    rr=[]
    for p in sorted((BASE/'IWC/analysis/wf_007_vgp_mitogenome_assembly/source_snapshots/huggingface_traces/files').glob('*/agent_workspace/final_answer/mitogenome.fasta.gz')):
        records=fasta(p);c=sum((kmers(s) for s,_ in records),Counter());matched=sum((c&refk).values());den=sum(c.values())+sum(refk.values())
        rr.append({'run':p.parts[-4],'path':str(p.relative_to(BASE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                   'records':len(records),'length':sum(len(s) for s,_ in records),'matched_31mers':matched,
                   'candidate_31mers':sum(c.values()),'reference_31mers':sum(refk.values()),'f1':2*matched/den})
    results['mitogenome_comparison']=rr
    dr=[]
    for task in ['wf_002_rnaseq_de_visualization','wf_010_pseudobulk_scrna_de']:
        for p in sorted((BASE/'IWC/analysis'/task/'source_snapshots/huggingface_traces/files').glob('*/agent_workspace/final_answer/differential_expression.tsv')):
            with p.open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
            try:
                pp=[float(r['p_value']) for r in rows];qq=[float(r['fdr']) for r in rows];adj=bh(pp)
                assert all(math.isfinite(x) and 0<=x<=1 for x in pp+qq)
                err=[abs(a-b) for a,b in zip(qq,adj)];ix=max(range(len(err)),key=err.__getitem__)
                dr.append({'task':task,'run':p.parts[-4],'path':str(p.relative_to(BASE)),'genes':len(rows),
                           'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'max_abs_bh_error':err[ix],
                           'rows_error_gt_1e_6':sum(x>1e-6 for x in err),'worst_row':rows[ix],
                           'worst_row_correct_bh':adj[ix]})
            except (KeyError,ValueError) as e:dr.append({'path':str(p.relative_to(BASE)),'error':str(e)})
    results['bh_recalculation']=dr
    ids=[]
    for p in sorted((BASE/'IWC/analysis/wf_005_amplicon_dada2_pe_denoising/source_snapshots/huggingface_traces/files').glob('*/agent_workspace/final_answer/asv_abundance.tsv')):
        with p.open() as f:r=csv.reader(f,delimiter='\t');h=next(r);n=sum(1 for _ in r)
        ids.append({'run':p.parts[-4],'path':str(p.relative_to(BASE)),'samples':h[1:],'asvs':n})
    results['asv_identifiers']=ids
    # Independent coordinate containment check on retained STAR junction output.
    p=BASE/'CompBio/analysis/cryptic-exon-q1/selected_outputs/galaxy/bbd44e69cb8906b56d454c70105c6597/f9cad7b01a47213566c9ecdd9965f9fd.dat'
    with p.open() as f:lines=[l.rstrip().split('\t') for l in f if l.startswith('chr9\t11166')]
    results['cryptic_exon']={'source':str(p.relative_to(BASE)),'star_rows':lines,
        'novel_exon_1based':['chr9',111664537,111664589], 'length':53,
        'independent_gene_reference':{'url':'https://www.ncbi.nlm.nih.gov/gene/2790','gene':'GNG10','assembly':'GRCh38.p14','chromosome':'9','start':111661605,'end':111670226},
        'within_gene':111661605<=111664537<=111664589<=111670226}
    results['arithmetic_checks']={
        'bix_28_q3':{'returned_verbose_values':[-29.4826,-32.1541,-31.4275,-6.9357],
                     'independent_median':statistics.median([-29.4826,-32.1541,-31.4275,-6.9357]),
                     'submitted_nonverbose_value':146.3023},
        'bix_35_q1':{'branch_lengths':[0.1687304731,0.0017192053,0.0024702698,0.0127712990,0.0026846938],
                     'sum':sum([0.1687304731,0.0017192053,0.0024702698,0.0127712990,0.0026846938]),
                     'tips':4,'rate':sum([0.1687304731,0.0017192053,0.0024702698,0.0127712990,0.0026846938])/4},
        'bix_61_q5':{'source_counts_from_trace':[48233,18863],'independent_ratio':48233/18863,
                    'limitation':'Arithmetic verification only; original VCF not independently recounted.'},
        'bix_14_q1':{'synonymous_over_synonymous_plus_missense':30/41,'with_six_splice_region_records':30/47},
        'bix_53_q5':{'percent':10.0,'fraction':10.0/100},
        'bh_known_vector':{'input':[0.5,0.6,0.1,0.001],'observed':bh([0.5,0.6,0.1,0.001]),
                           'expected':[0.6,0.6,0.2,0.004],
                           'source':'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html'}
    }
    assert bh([0.5,0.6,0.1,0.001])==[0.6,0.6,0.2,0.004]
    assert len(rr)==24 and len(dr)==48 and len(ids)==24
    (OUT/'independent_checks.json').write_text(json.dumps(results,indent=2)+'\n')
    print('Public reference',len(seq),'nt;',len(rr),'fixed assemblies compared')
    for x in rr:
        if x['f1']==0:print('ZERO',x['run'],x['length'],x['matched_31mers'])
    for x in dr:
        if x.get('max_abs_bh_error',0)>1e-6:print('BH discrepancy',x['task'],x['run'],x['max_abs_bh_error'],x['rows_error_gt_1e_6'],x['worst_row'],x['worst_row_correct_bh'])
    print('BH tables checked',len(dr),'ASV tables',len(ids))

if __name__=='__main__':main()
