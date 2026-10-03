// One journal Source Data workbook; statistical calculations are owned by Python.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';
const require=createRequire(import.meta.url);
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const paper=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const data=JSON.parse(await fs.readFile(path.join(paper,'source_data/figure_source_data.json'),'utf8'));
const wb=Workbook.create();
const ink='#263746',header='#E7EDF2';
const previewDir=path.join(paper,'analysis/workbook_previews');
await fs.mkdir(previewDir,{recursive:true});
const sourceMap={F1_design:'scripts/make_figures.py, fig1()',F1_prompts:'analysis/accuracy_prompt_design.csv',F2_scores:'analysis/accuracy_benchmark_configuration.csv',
 F2_sensitivity:'analysis/accuracy_sensitivities.csv',F3_repeatability:'analysis/accuracy_repeatability.csv',
 F3_UDT_usage:'analysis/accuracy_udt_usage.csv',F3_UDT_association:'analysis/accuracy_udt_accuracy_association.csv',
 F4_census:'analysis/rigor_census_categories.csv',F4_tags:'analysis/rigor_tag_overlap.csv',F4_persistence:'analysis/rigor_persistence.csv',
 F4_transitions:'analysis/accuracy_cross_arm_error_transitions.csv',F4_overlap:'analysis/accuracy_persistent_failure_overlap.csv',F4_cases:'analysis/rigor_cases.csv',
 F5_model_tradeoffs:'analysis/token_model_pareto_common_tasks.csv, input_tokens',F5_arm_totals:'analysis/token_arm_total_ratios.csv, primary_endpoint',
 F5_arm_ratios:'analysis/token_paired_arm_ratios.csv, primary_endpoint',F5_outcome:'analysis/token_outcome_sibling_summary.csv, pooled',F5_IWC_tasks:'analysis/token_iwc_task_inputs.csv',
 F6_operations:'analysis/token_operation_volume.csv, four_primary_configurations',F6_discovery:'scripts/make_figures.py, fig6() search+tool-inspect sums; analysis/token_interface_friction.csv',
 F6_failure_classes:'analysis/token_failure_classes.csv',F6_udt_outcomes:'analysis/token_udt_call_breakdown.csv',F6_friction:'analysis/token_interface_friction.csv',
 F6_interventions:'scripts/make_figures.py, fig6(); prospective statements, no results',Scored_runs:'analysis/accuracy_primary_runs.csv',
 Replicate_sets:'analysis/accuracy_replicate_sets.csv',Token_runs:'analysis/token_run_observations.csv, model_primary and primary_endpoint',
 Token_cells:'analysis/token_cell_eligibility_and_ratios.csv, primary_endpoint',Audit_tasks:'analysis/rigor_task_cases.csv',Trace_locators:'analysis/rigor_evidence.csv'};
const readme=[['Item','Definition'],['Title',data.title],['Scope',data.scope],
 ['Primary endpoints','3,816 assigned endpoint runs: 50 BixBench, 100 CompBioBench and nine IWC tasks; four shared configurations, three repeats per arm.'],
 ['Endpoint meaning','BixBench original evaluator acceptance; CompBio reconstructed-key agreement, not official-key validation; IWC continuous workflow-output agreement.'],
 ['Intervals','95% percentile cluster bootstrap, 20,000 resamples, seed 20261002. BixBench capsules; otherwise tasks. Model/frontier comparisons exploratory.'],
 ['Token ratio','Primary: total Galaxy tokens divided by total code tokens over eligible paired task–configuration cells (F5_arm_totals). Secondary: median across cells of Galaxy/code three-run medians (F5_arm_ratios).'],
 ['Token units','Recorded input includes cached reads; uncached=input minus cached. Tokens are neither returned characters nor monetary cost.'],
 ['Model-resource cohort','Complete scores and input in all eight configuration–arm groups: 50 BixBench, 86 CompBioBench, nine IWC tasks.'],
 ['Repeatability','Binary mixed acceptance; IWC within-set score range >0.05. All-three-correct is binary only; exact text stability is separate.'],
 ['Interface scope','66,316 calls in the four primary configurations across all 160 tasks; 1,908 available Galaxy traces among 1,920 assignments.'],
 ['Audit scope','93 audited tasks: every BixBench task with a rejected run and every CompBioBench task with a key-deviating run in any archived configuration, plus seven IWC workflows. Census analyses use the 73 binary-benchmark tasks with a rejected primary run. AI-assisted labels; non-exclusive tags; blinded expert review pending.'],
 ['UDTs','Calls, observed attempts, eventual ok jobs, ok interface returns and accepted answers are distinct denominators. Missing traces mean unknown use.'],
 ['Missing cells','Blank/null means unavailable or not applicable, never a silently substituted zero. Eligibility fields determine analysis inclusion.'],
 ['Private answers','CompBioBench submitted and reference answers are withheld. Trace paths are locators, not a release of private files.'],
 ['Prospective panel','RESULTS PENDING: Fig. 6f is a placeholder until intervention results are confirmed and finalized. Proposed interventions are text, not measured effects.'],
 ['Build','sh manuscript_narrative/original_layout/build_all.sh; exact input source hashes and versions in release_manifest.json.'],
 ['Values','Unrounded typed statistical outputs. Calculations live in the supplied Python analysis scripts; this workbook is a Source Data snapshot.'],
 ['Sources','Paths below are relative to manuscript_narrative/original_layout unless otherwise stated. Source file hashes appear in release_manifest.json.'],
 ...Object.entries(sourceMap).map(([n,s])=>[n,s])];
function colLetter(i){let out='';while(i>=0){out=String.fromCharCode(65+i%26)+out;i=Math.floor(i/26)-1;}return out;}
const info=[];
function addSheet(name,columns,rows){
 const sh=wb.worksheets.add(name);sh.showGridLines=false;
 const values=[columns,...rows],all=sh.getRangeByIndexes(0,0,values.length,columns.length);
 all.values=values;all.format={font:{name:'Arial',size:10,color:ink},verticalAlignment:'center',rowHeight:22,columnWidth:18};
 all.format.numberFormat='0.0000';
 sh.getRangeByIndexes(0,0,1,columns.length).format={fill:header,font:{name:'Arial',size:10,bold:true,color:ink},wrapText:true,verticalAlignment:'center',horizontalAlignment:'center',rowHeight:68};
 const widths=[];
 columns.forEach((c,j)=>{
  const range=sh.getRangeByIndexes(1,j,Math.max(1,rows.length),1);
  const isText=rows.some(r=>typeof r[j]==='string');
  if(isText){range.format.numberFormat='@';range.format.horizontalAlignment='left';range.format.wrapText=true;}
  else {range.format.horizontalAlignment='right';if(rows.every(r=>r[j]===null||typeof r[j]==='boolean'||Number.isInteger(r[j])))range.format.numberFormat='0';}
  let width=18;
  if(/^(benchmark|task|cfg|env|run_id|cluster|population|trajectory|label|measure|operation|token_kind|endpoint)$/.test(c))width=30;
  if(/(path|source|mechanism|evidence|opportunity|definition|caveat|interpretation|description|intervention|guardrail|finding|contrast|heading|inference|dominated_by|status)/.test(c))width=64;
  widths.push(width);
  sh.getRangeByIndexes(0,j,values.length,1).format.columnWidth=width;
 });
 if(name==='README'){sh.getRange('A1:A42').format.columnWidth=28;sh.getRange('B1:B42').format.columnWidth=108;sh.getRangeByIndexes(1,1,rows.length,1).format.wrapText=true;sh.getRangeByIndexes(1,0,rows.length,2).format.rowHeight=46;sh.tabColor='#6D8795';}
 else if(name==='Column_dictionary'){sh.getRangeByIndexes(0,0,values.length,1).format.columnWidth=28;sh.getRangeByIndexes(0,1,values.length,1).format.columnWidth=34;sh.getRangeByIndexes(0,2,values.length,1).format.columnWidth=104;sh.getRangeByIndexes(1,2,rows.length,1).format.wrapText=true;sh.getRangeByIndexes(1,0,rows.length,3).format.rowHeight=56;}
 else {
  rows.forEach((row,i)=>{
   const lines=Math.max(1,...row.map((v,j)=>typeof v==='string'?Math.ceil(v.length/(widths[j]*1.1)):1));
   if(lines>1)sh.getRangeByIndexes(i+1,0,1,columns.length).format.rowHeight=lines*16+10;
  });
  if(name.startsWith('F'))sh.tabColor='#385A76';
 }
 sh.freezePanes.freezeRows(1);
 info.push({name,rows:rows.length,columns:columns.length,preview_range:`A1:${colLetter(columns.length-1)}${Math.min(values.length,5)}`});
 return sh;
}
addSheet('README',readme[0],readme.slice(1));
for(const [name,t]of Object.entries(data.tables))addSheet(name,t.columns,t.rows);
addSheet('Column_dictionary',['Sheet','Column','Definition'],data.dictionary);
await wb.recalculate();
const checks=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},maxChars:1500});
await fs.writeFile(path.join(paper,'analysis/workbook_inspection.json'),JSON.stringify({formula_error_scan:checks,sheets:info},null,2)+'\n');
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(path.join(paper,'Source_Data.xlsx'));
console.log(`Source_Data.xlsx: ${info.length} sheets; typed archive values and strict column dictionary`);
for(const entry of info){
 const png=await wb.render({sheetName:entry.name,range:entry.preview_range,scale:1,format:'png'});
 await fs.writeFile(path.join(previewDir,entry.name+'.png'),new Uint8Array(await png.arrayBuffer()));
 console.log(`preview ${entry.name}`);
}
