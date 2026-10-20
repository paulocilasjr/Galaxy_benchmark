// Supplementary Notes 1-3. Same markup as content.js. Sources: analysis/integrity_audit/README.md and violations.csv;
// runs/CompBio/README.md and reruns_20261005/; runs/IWC/README.md and replacement_wf007_20261012/; numbers.json.

const notes = [
  {
    n: 1,
    title: 'Answer integrity and shared Galaxy accounts',
    paragraphs: [
      'Agents in both conditions could reach the internet, and Galaxy runs shared usegalaxy.org accounts. We therefore ' +
      'audited every archived run for rule breaks and for actions against the spirit of the benchmark. The audit ' +
      'normalized the traces of 4,443 run folders (the 3,816 archived primary runs, 3,804 of them with a trace, and 627 ' +
      'superseded, replaced, extra-configuration and token-batch runs) into agent actions and applied 19 rule detectors. ' +
      'It recorded where each submitted answer first appeared in any tool output and whether each Galaxy run had a ' +
      'successful Galaxy analysis job, from the trace or the archived Galaxy job ledger. Exposure was counted as verified ' +
      'when content that the agent fetched contained the task\'s answer: the reference answer, the submitted answer, the ' +
      'BixBench "ideal" field next to the question, or another agent\'s recorded answer in a trace file of the same task. ' +
      'Every run whose fetched content contained the answer was checked by reading its trace. Supplementary Table 6 lists ' +
      'all categories for the primary runs.',
      '**Answers taken from outside the run.** Fifteen primary runs copied an answer. Three BixBench-Verified-50 runs ' +
      '(DeepSeek V4 Pro, Galaxy condition, all three replicates of bix-30-q3) printed the "ideal" field of the public ' +
      'BixBench dataset and submitted it. Twelve CompBioBench runs (9 DeepSeek V4 Pro, 2 GPT-5.6 Luna and 1 GPT-5.6 Sol) ' +
      'read another agent\'s trace for the same task in a public Hugging Face dataset of agent traces and submitted that ' +
      'agent\'s answer. Eleven of the 15 were graded correct. A further 12 runs used another agent\'s answer and then ' +
      'checked it with their own analysis (10 graded correct), 12 saw the answer only after computing their own, and 6 ' +
      'saw another agent\'s answer but submitted a different one. All 45 of these runs used DeepSeek V4 Pro, GPT-5.6 ' +
      'Luna or GPT-5.6 Sol; none used GPT-5.5.',
      '**Looking for answers.** In 447 primary runs the agent searched for, probed or opened sources of answers: 359 of ' +
      'the 2,400 CompBioBench runs, 82 of the 1,200 BixBench-Verified-50 runs and 6 of the 216 archived IWC-derived runs ' +
      '(DeepSeek V4 Pro 244, GPT-5.6 Luna 91, GPT-5.5 57 and GPT-5.6 Sol 55 runs). These were web and code searches for ' +
      'the benchmark name, task identifier or question text (437 runs), probes of the CompBioBench leaderboard, ' +
      'evaluator, question catalogue and runner repository (232 runs) and attempts on private submission and result ' +
      'datasets, which failed. Grouping runs by the most informative source they reached, 94 primary runs had verified ' +
      'or probable exposure (34 BixBench-Verified-50 and 60 CompBioBench runs). Excluding them changed the Galaxy minus ' +
      'custom-code differences from +0.5 to +0.6 percentage points (95% CI −4.0 to 5.1) on BixBench-Verified-50 and from ' +
      '+0.3 to +0.2 (−2.0 to 2.4) on CompBioBench (Supplementary Fig. 3b).',
      '**Other runs\' work.** In 139 primary runs the agent listed the Galaxy account\'s histories, jobs or datasets, and ' +
      'the output showed other runs\' histories. Four primary runs read another run\'s history: two GPT-5.6 Luna runs of ' +
      'encode-atac-pipeline-q1 (one read a pilot run of the same task, the other inspected four other runs\' ' +
      'histories), one GPT-5.6 Luna run of saluki-setup-optimize-q1, which read a dataset from another history, and one ' +
      'GPT-5.5 rerun of lung-cancer-sc-q1, which fetched this project\'s results page for the task and imported a ' +
      'dataset from another history through a personal Galaxy connector. Thirty-three CompBioBench Galaxy runs used ' +
      'account-connected tools that the benchmark did not provide (GitHub, personal Galaxy connectors and Hugging Face). ' +
      'Separately, the traces of two GPT-5.6 Sol Galaxy runs of bix-11-q1 (replicates 2 and 3) both work in one Galaxy ' +
      'history, which the results site links to both runs (Supplementary Data 2).',
      '**Computation outside Galaxy.** A manual review on 5 October 2026 found 30 CompBioBench Galaxy runs whose ' +
      'key analyses ran outside Galaxy; they were rerun and replaced (Supplementary Note 2). The audit\'s detector for ' +
      'local computation flagged 28 of those 30 runs. In the primary set it flagged 38 further Galaxy runs in which local ' +
      'analysis produced the submitted answer (24 BixBench-Verified-50 and 14 CompBioBench), and 5 Galaxy runs submitted ' +
      'an answer without a successful Galaxy analysis job. These 43 detections are automatic. Excluding them changed the ' +
      'differences to −0.04 (95% CI −4.7 to 4.4) and +0.4 (−1.8 to 2.6) percentage points. In addition, 104 ' +
      'BixBench-Verified-50 Galaxy runs searched tools, submitted jobs or polled jobs through BioBlend or the Galaxy API ' +
      'instead of the MCP tools; in 58 DeepSeek V4 Pro runs this was because a Codex setting hid the Galaxy tools from ' +
      'the model. These runs still executed their analyses as Galaxy jobs.',
      '**Limits.** Codex traces do not log the content of web pages opened with the browsing tool, so such pages can only ' +
      'be counted as opened. Short or common answers were matched only in context. Twelve CompBioBench Galaxy runs and ' +
      'the 24 replacement runs of the mitochondrial genome assembly task have no archived trace. The audit code, the ' +
      'per-run findings and the evidence for each row are in analysis/integrity_audit/ of the run archive.',
    ],
  },
  {
    n: 2,
    title: 'CompBioBench answer key, campaigns and reviewed reruns',
    paragraphs: [
      '**Answer key.** CompBioBench withholds its reference answers and item-level evaluator scores. We scored runs ' +
      'against a reconstructed key in which 54 references were inferred from recorded per-run scores and 46 from ' +
      'predicted answers. With this key, the per-run grades reproduce the official leaderboard score of all 24 ' +
      'replicates (four models × two conditions × three replicates). Reference and submitted answers are not ' +
      'redistributed; the grading inputs are held outside the public archive.',
      '**Campaigns.** CompBioBench runs were collected in named campaigns, and the final answer vector of a replicate ' +
      'can combine runs from several campaigns, including continuation and recovery campaigns, so replicates are not ' +
      'documented first attempts. Some Galaxy campaigns had names that referred to wrong answers or target scores. ' +
      'Removing the 66 task–model pairs (396 runs, both conditions) that contained runs from such campaigns changed the ' +
      'Galaxy minus custom-code difference from +0.3 to −0.3 percentage points (95% CI −2.2 to 1.7; Supplementary ' +
      'Fig. 2b).',
      '**Reviewed reruns.** After a manual review of CompBioBench Galaxy runs on 5 October 2026, 53 runs were rerun: ' +
      '30 whose key analyses had run outside Galaxy and 23 in which tool timeouts or failed routes left the result in ' +
      'need of verification. The reruns replaced the original runs, and every other run kept its result. Twenty-two answers ' +
      'and 17 grades changed (8 runs became correct and 9 incorrect). The rerun manifest, the original runs and a check ' +
      'that no other record changed are in runs/CompBio/reruns_20261005/ of the run archive. Main-run token totals on ' +
      'the results site include the replaced runs.',
    ],
  },
  {
    n: 3,
    title: 'IWC-derived tasks',
    paragraphs: [
      '**Tasks and scoring.** The ten tasks were derived from workflows of the Intergalactic Workflow Commission: ' +
      'short-read quality control and trimming; RNA-seq differential expression and visualization; host-read removal; ' +
      'amplicon denoising with DADA2; ATAC-seq chromatin accessibility; mitochondrial genome assembly (Vertebrate Genomes ' +
      'Project); antimicrobial-resistance gene detection; clinical metaproteomics peptide verification; pseudobulk ' +
      'single-cell differential expression; and BioProject metadata and sequence retrieval. Agents received the task ' +
      'inputs and a description of the expected outputs, but not the workflow, and UDTs were not offered in the Galaxy ' +
      'condition. Runs were scored by the agreement (0–1) of their output files with the curated workflow outputs. Runs ' +
      'had a 6-h or 12-h wall-clock limit depending on when they started (Supplementary Table 3).',
      '**Caveats.** First, because the tasks come from Galaxy workflows, the tools that the workflows use are installed on ' +
      'usegalaxy.org, which could favour the Galaxy condition. Second, the host-read removal task is scored from each ' +
      'run\'s run record, as on the results site, and its minimap2 reference output is identical to the output submitted ' +
      'by one run (GPT-5.5, custom code, replicate 3), so that run\'s score is self-referential. Third, some references ' +
      'of the ATAC-seq task were calibrated from agent runs, and the RNA-seq composite score does not include the set of ' +
      'significant genes; Supplementary Fig. 2b shows the difference without the calibrated ATAC-seq routes. Fourth, on ' +
      '12 October 2026 the results site replaced all 24 runs of the mitochondrial genome assembly task with reruns on a ' +
      'second read set (ERR12833637). We use their scores and token counts; the archive holds no traces of these reruns, ' +
      'so trace-based analyses exclude the task.',
      '**Where the difference comes from.** Three tasks had at least one run with zero agreement: amplicon denoising, ' +
      'mitochondrial genome assembly and pseudobulk differential expression. Without them, the Galaxy minus ' +
      'custom-code difference in mean agreement was +0.0036 (Supplementary Fig. 2b), compared with +0.036 for all ten ' +
      'tasks.',
    ],
  },
];

module.exports = { notes };
