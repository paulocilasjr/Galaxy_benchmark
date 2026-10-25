"""Layout revision of Brief Communication Fig. 2; reuse original data and panel builders."""
from pathlib import Path
import importlib.util
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/galaxy-figure-mpl')
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
p=ROOT/'manuscript/manuscript_narrative/original_layout/brief_communication/scripts/make_figures.py'
spec=importlib.util.spec_from_file_location('source_figure',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
plt=m.plt
fig=plt.figure(figsize=(183/25.4,142/25.4))
def head(x,y,l,title,sub=None):
 fig.text(x,y,l,fontsize=8,fontweight='bold',va='top')
 fig.text(x+.025,y-.002,title,fontsize=6.5,fontweight='bold',va='top')
 if sub:fig.text(x+.025,y-.031,sub,fontsize=5.5,color=m.INK2,va='top')
a=fig.add_axes([.145,.595,.325,.32])
b=fig.add_axes([.705,.595,.275,.28])
c=fig.add_axes([.035,.045,.465,.38])
d=fig.add_axes([.635,.105,.345,.32])
ra=m.panel_causes(a);rb=m.panel_consensus(b);rc=m.panel_provenance(c);rd=m.panel_token_steps(d)
head(.008,.982,'a','Causes of incorrect runs','BixBench-Verified-50 · 151 incorrect runs')
head(.535,.982,'b','Accuracy across replicates')
head(.008,.492,'c','What each execution record retains','bix-16-q1 · GPT-5.6 Luna · replicate 1')
head(.535,.492,'d','Token use across interface rounds')
# Quiet axes and keep consistent typography.
for ax in (a,b,d):
 ax.grid(False)
 ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
# Table headings are black, with color keys expressed by the cell background.
for t in c.texts:
 if t.get_text() in ('Galaxy job record','Custom-code trace'):t.set_color(m.INK)
 if t.get_text().startswith('The decisive choice'):
  t.set_text('Stored parameter: DeepSeek V4 Pro r3 used transform_b = none\nand answered CCND1.')
  t.set_fontsize(5.2)
# Place the cause legend in the open space above its axis, clear of the data.
a.legend(handles=[m.Patch(facecolor=m.SHADE[k], label=str(k)) for k in (0,1,2)], loc='lower right',bbox_to_anchor=(1,1.005),ncol=3,fontsize=5,
 title='Sibling replicates correct',title_fontsize=5,handlelength=.8,columnspacing=.8)
# Use two concise legend rows above the consensus plot.
b.get_legend().set_bbox_to_anchor((-.03,1.03))
# Export source rows from the same builders, without changing the manuscript files.
import pandas as pd
for panel,rows in zip('abcd',(ra,rb,rc,rd)):
 pd.DataFrame(rows).to_csv(OUT/f'Fig2_panel_{panel}_data.csv',index=False)
for ext in ('pdf','svg','png'):fig.savefig(OUT/f'Fig2_revised.{ext}',dpi=600,facecolor='white')
fig.savefig(OUT/'Fig2_preview.png',dpi=160,facecolor='white')
print(OUT/'Fig2_revised.pdf')
