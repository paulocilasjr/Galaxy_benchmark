// Text of the Brief Communication. Markup: **bold**, *italic*, {cite:key1,key2} (numbered in order of first citation:
// main text, figure legends, then Methods), [[...]] = item the authors must supply (highlighted in the document).
// Every number traces to numbers.json (scripts/compute_numbers.py).

const title = 'AI agents can perform accurate bioinformatics analyses through a computational workbench';

const front = {
  authors: '[[Authors: author list]]',
  affiliations: '[[Authors: affiliations]]',
  correspondence: '[[Authors: corresponding author and e-mail]]',
};

const abstract =
  'Artificial intelligence (AI) agents can perform bioinformatics analyses, but benchmarks test only agents that ' +
  'write their own code. To address this gap, we connected agents to the Galaxy workbench and compared them with ' +
  'agents writing custom code on 160 tasks from three benchmarks with four models. Accuracy was similar, Galaxy ' +
  'recorded every tool, parameter and dataset, and agent traces guided interface improvements that more than halved' +
  ' Galaxy\'s token use.';

const main = [
  // P1 - the gap
  'Artificial intelligence (AI) agents that plan and run analyses are increasingly used in biomedical ' +
  'research{cite:gao2024,biomni2026,cellvoyager2026,paper2agent2026}, and benchmarks now test whether they can ' +
  'complete whole bioinformatics analyses{cite:bixbench2025,compbiobench}. These benchmarks evaluate agents as ' +
  'programmers: each agent writes and runs its own code. However, custom code often lacks a structured record of ' +
  'the software versions and parameters used, which makes analyses difficult to review and ' +
  'reproduce{cite:sandve2013,gruning2018cs}. Scientific workbenches such as Galaxy{cite:goecks2010,galaxy2024} ' +
  'address this problem for scientists by providing versioned tools, managed compute and histories that record the ' +
  'inputs, parameters and outputs of every step and can be shared, turned into workflows and ' +
  'rerun{cite:wratten2021}. Whether agents can use a workbench to complete bioinformatics tasks as accurately as ' +
  'they write code has not been tested.',
  // P2 - the tool and the study
  'To address this gap, we connected AI agents to Galaxy through Model Context Protocol (MCP) servers and compared ' +
  'them with agents writing custom code (Fig. 1a). The MCP servers give agents access to Galaxy\'s main ' +
  'capabilities: tool search, parameter descriptions, history inspection, job submission and monitoring, and ' +
  'user-defined tools (UDTs) for operations that no installed tool covers. In the Galaxy condition, all scientific ' +
  'computation had to run as Galaxy jobs on usegalaxy.org; in the custom-code condition, which served as the ' +
  'baseline, the agent installed software and wrote its own code. Four model configurations in the Codex agent ' +
  'harness attempted each of 160 tasks three times per condition, for 3,840 runs: 50 tasks from ' +
  'BixBench-Verified-50{cite:bixbench2025}, 100 from CompBioBench{cite:compbiobench} and 10 derived from workflows ' +
  'of the Intergalactic Workflow Commission (IWC; https://github.com/galaxyproject/iwc). Because the IWC-derived ' +
  'tasks come from Galaxy workflows and could favour Galaxy, we report them separately.',
  // P3 - accuracy
  'Agents were similarly accurate in the two conditions on the two platform-neutral benchmarks. On ' +
  'BixBench-Verified-50, 87.2% of custom-code runs and 87.7% of Galaxy runs were accepted (Fig. 1b), a difference ' +
  'of +0.5 percentage points (95% confidence interval (CI) −3.9 to 4.8). On CompBioBench, 86.7% and 87.0% of runs ' +
  'agreed with the answer key (Fig. 1c; +0.3; 95% CI −1.8 to 2.5). For both benchmarks, the 90% CI of the ' +
  'difference lay within ±5 percentage points, a margin set after the analysis (Methods). No per-model difference ' +
  'was significant after Holm adjustment (smallest adjusted *P* = 0.19), although 4 of the 8 per-model intervals ' +
  'extended beyond ±5 points (Supplementary Fig. 1). The pooled differences stayed within one point of zero after ' +
  'we removed tasks with audited benchmark-side problems, questionable CompBioBench campaigns, runs exposed to ' +
  'benchmark answers or Galaxy runs that computed outside Galaxy (Supplementary Figs. 2 and 3). On the IWC-derived ' +
  'tasks, mean output agreement was 0.95 with custom code and 0.99 with Galaxy (+0.036; 95% CI 0.006 to 0.073; ' +
  'exact paired *P* = 0.055), and three tasks with a zero-scored run accounted for most of this difference (Fig. ' +
  '1d).',
  // P4 - why runs failed
  'Next, we asked why runs failed. An audit of the execution traces of all 151 incorrect BixBench-Verified-50 runs ' +
  'found that Galaxy itself caused 3 failures (Fig. 2a). Most failures, 107 (71%), came from the benchmark: an ' +
  'under-specified task or reference answer (94) or a scorer that rejected a valid answer (13). The agent caused ' +
  '37, and 4 runs submitted no answer. The two main causes were linked, because in 74 of the 94 under-specified ' +
  'runs the agent also did not validate its answer. Under-specification was systematic: 85 of the 94 runs were in ' +
  'replicate groups in which all three runs were wrong. In contrast, missing validation, the main agent-side cause,' +
  ' was largely random: 16 of its 32 cases occurred in groups whose other two replicates were correct. Notably, at ' +
  'least one replicate was correct in 85–94% of replicate groups, yet a majority vote added at most 2.3 points ' +
  '(Fig. 2b, Supplementary Fig. 4 and Supplementary Table 1). Thus, a validation step that selects a correct replicate could' +
  ' recover more errors than voting.',
  // P5 - what Galaxy records and what it costs
  'Galaxy also recorded each analysis in a structured form that can be audited (Fig. 2c and Supplementary Fig. 5). ' +
  'All 37,498 analysis steps in Galaxy runs recorded the tool and its version, the parameters and the output ' +
  'datasets, and the Galaxy history was retrieved for 1,871 of 1,908 runs. In contrast, custom-code runs retained ' +
  'the 55,380 commands that they ran but no structured record of software versions, parameters or outputs. This ' +
  'record came at a cost: across the main runs, Galaxy used 4.2, 2.7 and 0.92 times the tokens of custom code on ' +
  'BixBench-Verified-50, CompBioBench and the IWC-derived tasks (Supplementary Table 2 and Supplementary Fig. 6). ' +
  'Agent traces showed that, in the first-round GPT-5.5 batch, Galaxy runs took 2.66 times as many steps as ' +
  'custom-code runs, and each step reread 2.2 times as much context (Methods). Treating the agents as virtual ' +
  'users, we changed the interface to reduce these overheads and reran BixBench-Verified-50 (Fig. 2d). Combining ' +
  'job submission, waiting and checking into one MCP call, among other changes, reduced Galaxy tokens by 55.2% (95%' +
  ' CI 44.9–62.8%) with GPT-5.5. Compact replies and longer waits between checks reduced them by a further 55.6% ' +
  '(46.4–63.0%) with GPT-5.6 Sol, to 1.53 times custom code, while 137 of 150 runs remained correct (136 before). ' +
  'Thus, much of Galaxy\'s token cost came from its interface, and agent traces showed how to reduce it.',
  // P6 - implications, limitations and future work
  'Together, these results show that AI agents can perform bioinformatics analyses through a computational ' +
  'workbench with accuracy similar to that of custom code, while leaving a record that people can inspect and ' +
  'rerun. Galaxy could also make rigor-improving practices inexpensive for agents, such as comparing several ' +
  'methods for one step or validating results before reporting them, but we did not test this here. This study has ' +
  'several limitations. First, it covers four model configurations and three benchmarks, and models change quickly.' +
  ' Second, prompts, time limits and runtime environments differed between conditions, so we compared the ' +
  'conditions as deployed (Supplementary Table 3). Third, the IWC comparison rests on ten Galaxy-derived tasks, the' +
  ' cause audit covers BixBench-Verified-50 only, and the interface rounds were not a controlled ablation. Future ' +
  'work will add a validation layer to the agent interface and test whether it improves accuracy. More broadly, ' +
  'agent traces could become a routine source of usability evidence for scientific software.',
];

const legends = [
  {
    file: 'Fig1_300dpi.png',
    title: 'Fig. 1 | Agents performed with similar accuracy in Galaxy and with custom code.',
    body:
      '**a**, Study design: four model configurations attempted each of 160 tasks three times in each condition. ' +
      '**b**–**d**, Galaxy minus custom code for each model (open circles) and pooled (filled diamonds) on ' +
      'BixBench-Verified-50 (**b**; accepted runs), CompBioBench (**c**; agreement with the answer key) and the ' +
      'IWC-derived tasks (**d**; mean output agreement); condition values above each panel. Grey bands, ±5 percentage ' +
      'points. Error bars, 95% cluster-bootstrap CIs (clusters: BixBench source capsules or tasks); *n* = 150 (**b**), ' +
      '300 (**c**) and 30 (**d**) runs per model and condition. With ten IWC-derived tasks the interval is too narrow; ' +
      'the exact paired *P* of the pooled difference is 0.055.',
  },
  {
    file: 'Fig2_300dpi.png',
    title: 'Fig. 2 | Most errors came from the benchmark, voting recovered few of them, and interface changes reduced ' +
      'Galaxy\'s token use.',
    body:
      '**a**, Primary causes of the 151 incorrect BixBench-Verified-50 runs (both conditions), from execution traces, by ' +
      'the number of correct sibling replicates (the other two runs of the same task, model and condition). **b**, ' +
      'Accuracy of a single run, a majority of 3 replicates, a majority of all 12 runs of a task and at least 1 of 3 ' +
      'correct (the ceiling for selecting a correct replicate), four models pooled; IWC-derived runs are correct at ' +
      'output agreement ≥ 0.99. A vote on the submitted answers is in Supplementary Table 1. **c**, One analysis step ' +
      'as recorded by the Galaxy job and by the custom-code trace; both runs answered correctly. **d**, Galaxy ÷ ' +
      'custom-code tokens per 50-task BixBench-Verified-50 run across interface rounds, with the percentage of Galaxy ' +
      'runs correct. Error bars, 95% cluster-bootstrap CIs; open circle, a single replicate.',
  },
];

// Online Methods: [heading, paragraphs]
const methods = [
  ['Benchmarks', [
    'We evaluated agents on 160 tasks from three benchmarks that each require a complete bioinformatics analysis ' +
    '(Supplementary Table 3). BixBench-Verified-50 is a curated ' +
    'subset of 50 questions from 33 data capsules of BixBench{cite:bixbench2025}, reviewed with domain experts for the ' +
    'correctness of the ground truth, the sufficiency of the supplied context and the clarity of the expected answer; ' +
    '17 of the 50 questions were revised relative to the original release. Each question comes with a data capsule and ' +
    'an evaluation mode (17 string, 13 range and 20 language-model verifiers). Agents received the question and input ' +
    'data but not the reference notebook or answer. The inputs were frozen before evaluation and archived on Zenodo ' +
    '(record 21115010). CompBioBench v1 comprises 100 computational biology tasks with objectively gradable answers in ' +
    'genomics, transcriptomics, epigenomics, single-cell analysis, human genetics and machine learning{cite:compbiobench}; ' +
    'agents received the question and input files, and the analytical route was not prescribed. The IWC-derived tasks ' +
    'are ten analyses derived from workflows of the Intergalactic Workflow Commission, the Galaxy community\'s ' +
    'collection of reviewed workflows; agents received the task inputs and a description of the expected outputs, but ' +
    'not the workflow.',
  ]],
  ['Galaxy interface', [
    'In the Galaxy condition, agents worked through MCP servers (https://modelcontextprotocol.io) that we wrote as ' +
    'Python wrappers around the Galaxy application programming interface (API). For each run, the servers were ' +
    'launched locally inside the run\'s Docker container, communicated with the agent over standard input and output ' +
    '(stdio) and were configured through the run\'s Codex configuration file (config.toml). They called the API of ' +
    'usegalaxy.org (Galaxy 26.1.2.dev0) with an API key, through BioBlend{cite:bioblend2013} and REST requests, and ' +
    'exposed Galaxy operations as agent tools: searching installed tools, retrieving a tool\'s parameter descriptions, ' +
    'inspecting histories and datasets, submitting jobs and waiting for them, and defining and running UDTs, which run ' +
    'agent-written code as Galaxy jobs in a declared container. Some runs also called the Galaxy API directly through ' +
    'BioBlend or REST instead of the MCP tools (Supplementary Note 1). Analyses used tools from the Galaxy ' +
    'ToolShed{cite:toolshed2014}. Task inputs were preloaded into seed histories, and each run ' +
    'copied its seed history into a new history before it started, so independent runs began from identical datasets. ' +
    'The main runs used the second-round interface, in which one call submits a job, waits for it, checks the resolved ' +
    'inputs and parameters against the request and returns a compact result. UDTs were not offered on the IWC-derived ' +
    'tasks. [[Authors: repository URL, version and licence of the Galaxy MCP servers and agent skills]].',
  ]],
  ['Models and agent harness', [
    'We ran four model configurations in the Codex agent harness: GPT-5.5, GPT-5.6 Sol and DeepSeek V4 Pro at high ' +
    'reasoning effort, and GPT-5.6 Luna at maximum reasoning effort. The GPT models used the fast service tier, and ' +
    'DeepSeek V4 Pro was served through the DeepSeek API as a Codex model provider. Settings were identical in the two ' +
    'conditions for each model. The main runs used the Codex command-line interface (CLI) version 0.146.0: the ' +
    'BixBench-Verified-50 runs of GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro, and all CompBioBench and IWC-derived ' +
    'runs [[Authors: Codex CLI version of the BixBench-Verified-50 GPT-5.5 runs]]. The third-round interface runs used ' +
    'version 0.156.0 (Token accounting and interface rounds). [[Authors: reason for maximum reasoning effort on GPT-5.6 ' +
    'Luna]].',
  ]],
  ['Execution conditions', [
    'We ran every task in two execution conditions. In the custom-code condition, the agent could write and run code, ' +
    'use command-line programs, install software and ' +
    'retrieve external resources. In the Galaxy condition, the prompt added an execution policy: scientific computation ' +
    'had to run in Galaxy, local code was limited to orchestrating Galaxy, staging inputs and extracting the answer from ' +
    'Galaxy outputs, and the prompt specified history use, permitted tools, UDT rules and interface timeouts. Galaxy ' +
    'prompts were therefore longer than custom-code prompts on BixBench-Verified-50 (median 707 versus 366 words) and ' +
    'CompBioBench (938 versus 227), but not on the IWC-derived tasks (333 versus 344). Runtime environments and time ' +
    'limits also differed. CompBioBench Galaxy runs executed in containers and custom-code runs in a host conda ' +
    'environment; IWC runs had a 6-h or 12-h wall-clock limit depending on start time; CompBioBench custom-code prompts ' +
    'stated a 120-min budget; and no budget was recorded for the other runs (Supplementary Table 3). Agents in both ' +
    'conditions could reach the internet. Galaxy runs shared usegalaxy.org accounts, so agents could see other runs\' ' +
    'histories (Supplementary Note 1). We therefore compare the conditions as deployed, not as an isolated effect of the ' +
    'workbench.',
  ]],
  ['Experimental design', [
    'Each model configuration attempted each task three times in each condition: 160 tasks × 4 configurations × 2 ' +
    'conditions × 3 replicates = 3,840 runs (1,200 on BixBench-Verified-50, 2,400 on CompBioBench and 240 on the ' +
    'IWC-derived tasks). Replicates were independent runs that began from a fresh workspace or history, and replicate ' +
    'indices were not matched between conditions. Comparisons between conditions were paired by task, the unit that both ' +
    'conditions share. Runs that ended without a scoreable answer were scored as incorrect.',
  ]],
  ['Answer evaluation', [
    'We kept each benchmark\'s own endpoint and did not pool scores across benchmarks. We used the per-run scores ' +
    'displayed on the project\'s public results site (https://goeckslab.github.io/galaxy-agent-benchmark/) and ' +
    'confirmed on 14 October 2026 that every score and answer used here matched the site. Accuracy per benchmark, ' +
    'model and condition is in ' +
    'Supplementary Table 4. BixBench-Verified-50 runs were scored by the benchmark\'s verifiers [[Authors: model, version ' +
    'and provider of the language-model verifier]]. The results site corrected the scoring of two questions after the ' +
    'original evaluation (bix-53-q2, accepting equivalent statements of an increase, and bix-43-q2, with ' +
    'platform-dependent numerical results under a two-decimal rule), which regraded 27 runs. CompBioBench withholds its ' +
    'reference answers, so runs were scored against a reconstructed answer key in which 54 references were inferred from ' +
    'recorded scores and 46 from predicted answers; the per-run grades reproduce the official leaderboard score of every ' +
    'replicate. After a review on 5 October 2026, 53 CompBioBench Galaxy runs whose key analyses had run outside Galaxy ' +
    'or whose tool timeouts needed verification were rerun, and the reruns replaced the original runs (Supplementary ' +
    'Note 2). The IWC-derived tasks were scored by the agreement (0–1) of the output files with the curated workflow ' +
    'outputs; we report mean agreement and, for counts of correct runs, treat agreement ≥ 0.99 as correct. Two ' +
    'IWC-derived tasks need care (Supplementary Note 3). The host-read removal task is scored from each run\'s run ' +
    'record, and its reference output is identical to the output of one run. On 12 October 2026, the results site ' +
    'replaced all 24 runs of the mitochondrial genome assembly task with reruns on a second read set (ERR12833637); we ' +
    'use their scores and token counts, and the trace-based analyses exclude the task because the archive holds no ' +
    'traces of the reruns.',
  ]],
  ['Failure-cause audit', [
    'We assigned each of the 151 incorrect BixBench-Verified-50 runs one primary cause and, where present, one ' +
    'secondary cause from its execution trace, outputs and Galaxy history: an under-specified task or reference ' +
    'answer; a scorer that ' +
    'rejected a valid answer; no validation of the answer; wrong biological or statistical knowledge; a fault of Galaxy ' +
    'itself; or no answer submitted. We assigned causes with AI assistance. An independent AI-assisted second rater ' +
    'agreed with the primary cause for 35 of 45 sampled runs (κ = 0.56). [[Authors: describe the human review of the ' +
    'audit: who reviewed which cases and how disagreements were resolved]]. Four bix-43-q2 runs regraded as incorrect by ' +
    'the results site after the audit take the cause of the task-level audit. CompBioBench and the IWC-derived tasks have ' +
    'no trace-based cause audit. Supplementary Figs. 7–11 summarize how Galaxy runs used Galaxy, execution errors, ' +
    'answer agreement between replicates, tool use and recovery from failed steps.',
  ]],
  ['Replicate agreement and consensus', [
    'A replicate group is the three replicates of one task, model and condition. From the existing runs we estimated the ' +
    'accuracy of three strategies: a majority vote (a group is correct if at least two replicates are correct, which ' +
    'assumes that correct answers agree), selection of a correct replicate whenever one exists (at least one of three ' +
    'correct) and a majority over all 12 runs of a task in a condition (ties counted as incorrect). A vote on the ' +
    'submitted answers, compared as normalized text, is reported in Supplementary Table 1. None of these strategies was ' +
    'run.',
  ]],
  ['What each condition records', [
    'We counted the elements that the archived run evidence retains for each analysis step. Galaxy analysis steps are ' +
    'Galaxy jobs; custom-code analysis steps are the agent\'s shell commands that the run evidence labels as analysis. ' +
    'For each step we recorded whether its command, tool and version, parameters and output datasets were retained, and ' +
    'for each Galaxy run whether its history contents were retrieved. Software versions that custom-code runs printed ' +
    'in their logs are not counted as structured records.',
  ]],
  ['Token accounting and interface rounds', [
    'Token counts are those that the model provider reported for each run and that the Codex harness recorded at the end ' +
    'of the run: input, including cached context, plus output, with reasoning counted in output. Main-run totals per ' +
    'benchmark and model are those published on the results site; for CompBioBench they include the 53 runs that the ' +
    'reruns replaced, and 14 CompBioBench runs have no usage record. In the July first-round batch, cached input was 95% ' +
    'of Galaxy tokens and output under 1.5%; Galaxy runs took 2.66 times as many agent steps (37.9 versus 14.2 per run), ' +
    'each carrying 2.2 times as much cached context.',
    'The interface rounds used BixBench-Verified-50 (Supplementary Table 5). In July 2026, with GPT-5.5, we compared runs ' +
    'with the first-round interface (shorter skill text and prompt guidance; 150 runs per condition) with the archived ' +
    'runs of the second-round interface (one call to submit a job, wait and check the resolved inputs and parameters; ' +
    'automatic record keeping and parameter checks; live tool search). In October 2026, with GPT-5.6 Sol, we compared ' +
    'the archived second-round runs with a third-round interface (replies capped at 4 KiB per output and 8 KiB per reply, ' +
    'an \'unchanged\' notice instead of repeated content, parameter templates, fewer false parameter warnings and ' +
    'pre-submission checks for UDTs), run once over the 50 tasks, and with the third-round interface plus instructions ' +
    'to wait 5–30 min before rechecking a running job (three replicates; 150 runs). Tokens are reported per complete ' +
    '50-task run, averaged over replicates; ratios are Galaxy over custom-code totals, and the change in Galaxy tokens is ' +
    'paired by task. The rounds changed several features at once, the model changed between July and October and the ' +
    'Codex command-line interface changed for round 3 (0.156.0 versus 0.146.0), so the stages are not a controlled ' +
    'ablation. Earlier single-run measurements of the original interface are not reported because their run records are ' +
    'not archived.',
  ]],
  ['Answer integrity', [
    'Because benchmark answers can leak into evaluations{cite:kapoor2023}, we scanned the traces of all 4,443 archived ' +
    'run folders with 19 rule detectors and read the trace of every case in which fetched content contained the ' +
    'task\'s answer (Supplementary Note 1 and Supplementary Table 6). ' +
    'In the primary set, 15 runs copied an answer: 3 BixBench-Verified-50 runs printed the answer field of the public ' +
    'benchmark dataset, and 12 CompBioBench runs submitted another agent\'s answer from a public trace dataset; 11 of the ' +
    '15 were graded correct. Exposure tiers based on what each run fetched identified 94 runs with verified or probable ' +
    'exposure; excluding them changed the BixBench-Verified-50 and CompBioBench differences to +0.6 and +0.2 points ' +
    '(Supplementary Fig. 3). The audit also flagged 43 Galaxy runs whose traces show that local analysis produced the ' +
    'submitted answer or that had no successful Galaxy job (automatic detections); excluding them changed the ' +
    'differences to −0.04 (95% CI −4.7 to 4.4) and +0.4 (−1.8 to 2.6) points.',
  ]],
  ['Statistics and reproducibility', [
    'We computed differences as Galaxy minus custom code for each benchmark. Intervals are 95% percentile cluster-bootstrap ' +
    'intervals (20,000 resamples; seed 20261002){cite:davison1997} that resample BixBench source capsules, whose ' +
    'questions share data, or tasks, with all their models, replicates and conditions. *P* values come from paired ' +
    'cluster sign-flip tests on each cluster\'s summed difference (200,000 random sign vectors, or exact enumeration for ' +
    '16 or fewer clusters, as for the IWC-derived tasks) and were Holm-adjusted{cite:holm1979} across the 12 benchmark × ' +
    'model comparisons. The equivalence check was defined after the analysis: we report the 90% cluster-bootstrap ' +
    'interval of each pooled difference, which corresponds to two one-sided tests at α = 0.05, against a ±5-percentage-' +
    'point margin. With ten IWC-derived tasks, bootstrap intervals are too narrow, so we report exact *P* values. ' +
    'Sensitivity populations were defined retrospectively. All tests were two-sided. No statistical method was used to ' +
    'predetermine sample size. Analyses used Python 3.12 with NumPy 2.5.3, pandas 3.0.6 and SciPy 1.18.1; the figure ' +
    'scripts record every value they draw, so each figure can be regenerated from the archive.',
  ]],
  ['Use of AI tools', [
    'AI coding assistants were used during this study to assist with analysis and figure code and with drafting and ' +
    'editing the text [[Authors: name the assistants, models and versions]]. Every number in the paper was computed by ' +
    'archived scripts and checked against the source tables. [[Authors: confirm or edit: The authors determined the ' +
    'study design, performed and validated the reported analyses, interpreted the results, and reviewed and verified ' +
    'all AI-assisted outputs.]] The agents evaluated in this study are its subject and did not contribute to the ' +
    'analysis or the writing.',
  ]],
];

const reporting = 'Further information on research design is available in the Nature Portfolio Reporting Summary linked ' +
  'to this article.';

const dataAvailability = 'Supplementary Data 2 lists every run with links to its agent trace, its page on the results ' +
  'site (https://goeckslab.github.io/galaxy-agent-benchmark/) and, for Galaxy runs, its usegalaxy.org history: the ' +
  '3,840 primary runs, the 77 runs replaced by reruns and the 450 interface-round runs of Fig. 2d. The agent traces of ' +
  'both conditions, with prompts, submitted answers, token usage and evaluation records, are in the Hugging Face ' +
  'dataset goeckslab/galaxy-agent-benchmark-run-traces [[Authors: the dataset currently requires authorization; make ' +
  'it public or state how readers obtain access, and deposit a snapshot with a DOI]]. On 20 October 2026, 2,281 of the ' +
  '2,285 Galaxy histories opened without an account; the other 4, of DeepSeek V4 Pro runs on BixBench-Verified-50, ' +
  'are not shared [[Authors: make these four histories importable]]. Per-run scores and token counts are also on the ' +
  'results site. BixBench-Verified-50 inputs are archived on Zenodo (record 21115010). The run archive and analysis ' +
  'tables are at https://github.com/paulocilasjr/Galaxy_benchmark [[Authors: release DOI]]. CompBioBench reference ' +
  'answers are not redistributed. Source data are provided with this paper.';

const codeAvailability = 'Analysis and figure code are at https://github.com/paulocilasjr/Galaxy_benchmark and ' +
  'https://github.com/goeckslab/agent-galaxy-benchmark-manuscript [[Authors: tagged release, DOI and licence]]. The ' +
  'Galaxy MCP servers and agent skills are at [[Authors: repository URL, version and licence]].';

const endMatter = [
  ['Acknowledgements', '[[Authors: funding and acknowledgements]]'],
  ['Author contributions', '[[Authors: contributions]]'],
  ['Competing interests', '[[Authors: competing interests]]'],
  ['Additional information', 'Supplementary information is available for this paper. Correspondence and requests for ' +
    'materials should be addressed to [[Authors: corresponding author]].'],
];

module.exports = { title, front, abstract, main, legends, methods, reporting, dataAvailability, codeAvailability,
                   endMatter };
