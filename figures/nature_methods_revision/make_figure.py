"""Redraw the supplied Fig. 1 from existing source data; no statistics recomputed.
Run from repository root. Outputs are isolated from the manuscript originals.
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/galaxy-figure-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import pandas as pd
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
INK, GREY, BLUE, ORANGE = '#202020', '#626262', '#0072B2', '#D55E00'
plt.rcParams.update({'font.family':'Arial','font.size':6,'svg.fonttype':'none','pdf.fonttype':42,
 'axes.linewidth':.5,'xtick.major.width':.5,'xtick.major.size':2.5,'xtick.labelsize':5.5,
 'axes.labelsize':6,'axes.edgecolor':GREY,'text.color':INK,'axes.labelcolor':INK})
fig=plt.figure(figsize=(183/25.4,111/25.4))
ax=fig.add_axes([0,0,1,1]); ax.set(xlim=(0,183),ylim=(111,0)); ax.axis('off')
def text(x,y,s,size=6,bold=False,**kw):
 return ax.text(x,y,s,fontsize=size,fontweight='bold' if bold else 'normal',va='top',**kw)
def box(x,y,w,h,fc='white',ec='#c8c8c8'):
 ax.add_patch(Rectangle((x,y),w,h,fc=fc,ec=ec,lw=.5))
def arr(x,y,x2,y2):
 ax.add_patch(FancyArrowPatch((x,y),(x2,y2),arrowstyle='-|>',mutation_scale=5,lw=.6,color=GREY))
text(1,1,'a',8,True); text(7,1.5,'Paired benchmark design',7,True)
# Compact four-stage schematic; black text and color keys, no decorative icons.
for x,w,title in [(7,35,'Tasks'),(49,31,'Agent'),(88,55,'Execution condition'),(151,30,'Evaluation')]:
 text(x,8,title,6.5,True); ax.plot([x,x+w],[12,12],color='#a0a0a0',lw=.5)
text(7,15,'160 tasks',7,True)
for i,(name,n) in enumerate([('BixBench-Verified-50','50'),('CompBioBench','100'),('IWC-derived','10')]):
 text(7,21+i*5,name,5.5); text(42,21+i*5,n,5.5,ha='right')
text(7,38,'Question and input data',5.5,color=GREY)
text(49,15,'Same model in both conditions',5.5,True)
for i,m in enumerate(['GPT-5.5','GPT-5.6 Sol','GPT-5.6 Luna','DeepSeek V4 Pro']): text(49,21+4.6*i,m,5.5)
text(49,42,'Codex agent harness',5.5,color=GREY)
box(88,15,55,20,'#eef5f9',BLUE); box(88,37,55,14,'#fcf1e9',ORANGE)
ax.plot([90,90],[17,20],color=BLUE,lw=2); text(92,16.5,'Galaxy',6.5,True)
text(91,22,'Galaxy jobs on usegalaxy.org',5.5)
text(91,27,'MCP: tool search, parameters, history,',5.5)
text(91,31,'job monitoring and user-defined tools',5.5)
ax.plot([90,90],[39,42],color=ORANGE,lw=2);text(92,38.5,'Custom code',6.5,True)
text(91,44,'Software and code in an isolated workspace',5.5)
arr(43,29,47,29);arr(81,28,86,24);arr(81,33,86,43)
arr(144,24,149,29);arr(144,43,149,37)
text(151,15,'3 replicates',6.5,True)
text(151,20,'per task, model and condition',5)
text(151,26,'3,840 runs',7,True)
text(151,32,'Benchmark-specific scoring',5.5)
text(151,38,'Galaxy history retains tools,',5)
text(151,42,'versions, parameters and data',5)
# Forest plots: same estimates and confidence intervals as original.
runs=pd.read_csv(ROOT/'figures/scored_runs.csv')
f2=pd.read_csv(ROOT/'figures/fig2_source_data.csv')
b=f2[(f2.panel=='b') & f2.measure.str.contains('mean_score_difference')]
models=['GPT-5.5','GPT-5.6 Sol','GPT-5.6 Luna','DeepSeek V4 Pro','All four models']
source=[]
for j,(bm,title,sub) in enumerate([('BixBench50','BixBench-Verified-50','Accepted runs'),('CompBio','CompBioBench','Answer-key agreement'),('IWC','IWC-derived tasks','Mean output agreement (0–1)')]):
 x=24+j*55
 text(x-23 if j==0 else x-4,57,'bcd'[j],8,True)
 text(x,57.5,title,6.5,True);text(x,62,sub,5.5,color=GREY)
 r=runs[runs.benchmark==bm];means=r.groupby('env').score.mean();iwc=bm=='IWC'
 vals=[f'{means[e]:.2f}' if iwc else f'{100*means[e]:.1f}%' for e in ['open_ended_code','galaxy']]
 for dx,c,mark,label,v in [(0,ORANGE,'s','Custom code',vals[0]),(25,BLUE,'o','Galaxy',vals[1])]:
  ax.plot(x+dx+.5,68,marker=mark,ms=2.6,color=c);text(x+dx+2,66.8,f'{label} {v}',5)
 plot=fig.add_axes([x/183,17/111,44/183,23/111])
 g=b[b.benchmark==bm].copy()
 if iwc:g[['value','ci95_low','ci95_high']]/=100
 lo,hi=(-.06,.27) if iwc else (-10,10)
 plot.axvline(0,color='#909090',lw=.6,zorder=0)
 plot.axhspan(3.65,4.65,color='#f1f1f1',lw=0,zorder=0)
 for i,name in enumerate(models):
  row=g[g.model==('all four' if i==4 else name)].iloc[0]
  plot.plot([row.ci95_low,row.ci95_high],[i,i],color=INK,lw=1.1 if i==4 else .7)
  plot.plot(row.value,i,marker='D' if i==4 else 'o',ms=3.3 if i==4 else 2.8,mfc=INK if i==4 else 'white',mec=INK,mew=.65)
  source.append(dict(panel='bcd'[j],benchmark=bm,model=name,value=row.value,ci95_low=row.ci95_low,ci95_high=row.ci95_high))
  if i==4:
   nd=3 if iwc else 1
   text(x,104,f'{row.value:+.{nd}f} ({row.ci95_low:.{nd}f} to {row.ci95_high:.{nd}f})'.replace('-','−'),5.5,True)
 plot.set(xlim=(lo,hi),ylim=(4.65,-.5))
 plot.set_yticks(range(5),models if j==0 else ['']*5,fontsize=5.5)
 plot.tick_params(axis='y',length=0,pad=3)
 if j==0:plot.get_yticklabels()[-1].set_fontweight('bold')
 plot.set_xticks([0,.1,.2] if iwc else [-10,-5,0,5,10])
 for spine in ('top','right','left'):plot.spines[spine].set_visible(False)
 text(x,99,'Galaxy − custom code '+('(agreement)' if iwc else '(percentage points)'),5)
text(7,109,'Points, model-specific estimates; diamonds, pooled estimates; lines, 95% confidence intervals.',5,color=GREY)
for ext in ['pdf','svg','png']:fig.savefig(OUT/f'Fig1_revised.{ext}',dpi=600,facecolor='white')
fig.savefig(OUT/'Fig1_preview.png',dpi=160,facecolor='white')
pd.DataFrame(source).to_csv(OUT/'plotted_estimates.csv',index=False)
print(OUT/'Fig1_revised.pdf')
