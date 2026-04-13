# Notes: Instructions, Formats, and Gaps Across Selected Agent-Eval Sources

Generated: 2026-03-30

Sources covered:
- [New Paper: Towards a science of AI agent reliability](https://www.normaltech.ai/p/new-paper-towards-a-science-of-ai)
- [BioAgent Bench: An AI Agent Evaluation Suite for Bioinformatics](https://arxiv.org/pdf/2601.21800)
- [AGENTIF: Benchmarking Instruction Following of Large Language Models in Agentic Scenarios](https://arxiv.org/pdf/2505.16944)
- [AgentIF-OneDay: A Task-level Instruction-Following Benchmark for General AI Agents in Daily Scenarios](https://arxiv.org/pdf/2601.20613)
- [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://arxiv.org/pdf/2602.12670)

## Cross-paper synthesis

### What kinds of instructions these sources collectively cover
- Long, specification-heavy agent prompts rather than short synthetic instructions.
- Instructions with multiple simultaneous constraints.
- Explicit workflow instructions where the user lays out a procedure to follow.
- Implicit or latent instructions that must be inferred from files, examples, or attachments.
- Tool-use instructions, including function/tool restrictions and parameter constraints.
- Artifact-oriented instructions where the agent must create files, directories, reports, presentations, websites, or domain outputs rather than only text answers.
- Iterative refinement instructions where the agent must modify prior outputs without breaking existing constraints.
- Domain-procedural instructions, especially bioinformatics pipelines and reusable agent skills.
- Reliability-oriented instructions for how agent evaluation itself should be run.

### What formats recur across the sources
- Structured output formats: JSON, Markdown, tables, bullet lists, tagged output, directory-based deliverables.
- Benchmark task packages: instruction files, config files, environments, oracle/reference solutions, tests/verifiers.
- Attachment-rich tasks: PDF, PNG, JPG, PPTX, XLSX, HTML, CSV, SVG, ZIP, subtitle/media files.
- Evaluation formats: deterministic programmatic tests, LLM judges, hybrid code-plus-LLM grading, rubric scoring, pass/fail task completion, multi-run reliability profiles.
- Modular procedural artifacts: `SKILL.md` plus optional scripts, references, templates, and examples.

### Main gaps these sources collectively target
- Average accuracy is a weak proxy for deployable reliability.
- Existing benchmarks are often too short, synthetic, text-only, or single-turn.
- Many evaluations underweight tool constraints, attachment understanding, latent instruction inference, and file-based outcomes.
- Existing suites often miss robustness testing under perturbations, long contexts, and real workflow noise.
- Benchmark coverage is often poor for privacy-sensitive domains, day-to-day user tasks, and skill augmentation.

## 1. NormalTech reliability article

Source:
- [New Paper: Towards a science of AI agent reliability](https://www.normaltech.ai/p/new-paper-towards-a-science-of-ai)

### Instructions covered
- Guidance for deployers:
  - Distinguish automation from augmentation.
  - Require higher reliability for unattended or customer-facing automation.
  - Build internal evaluations tailored to the deployment context and dataset.
  - Consider release thresholds before moving agents from sandbox to production.
  - Build an incident-reporting culture around agent failures.
- Guidance for researchers and developers:
  - Measure reliability separately from raw accuracy.
  - Re-run tasks multiple times to measure variance.
  - Evaluate under changed conditions, not only a single clean run.
  - Re-test continuously as models and environments change.
  - Improve weak dimensions directly, especially consistency and predictability/calibration.
  - Build agents that recognize likely failure and recover gracefully.

### Formats covered
- Reliability is framed as a profile, not a single score.
- Core reliability dimensions:
  - Consistency
  - Robustness
  - Calibration or predictability
  - Safety
- Evaluation format used in the article:
  - Multiple benchmark runs per task
  - Paraphrased instructions across runs
  - Fault injection in tools and environments
  - Explicit confidence elicitation from agents
  - Reporting reliability alongside accuracy
- Benchmark framing:
  - Two complementary benchmarks
  - 14 models
  - 18 months of releases
  - 500 benchmark runs total

### Gaps addressed
- Industry reliance on average success rate as the main deployment signal.
- Lack of a clear shared definition of agent reliability.
- Failure to distinguish capability progress from reliability progress.
- Lack of deployment-oriented thresholds for autonomous systems.
- Lack of systematic measurement for human-agent collaboration in multi-step tasks.

### Remaining gaps or caveats called out
- The proposed metrics still involve subjectivity.
- Safety measurement is not fully settled yet.
- The authors argue reliability may improve much more slowly than accuracy, but treat that as a tentative claim.

## 2. BioAgent Bench

Source:
- [BioAgent Bench: An AI Agent Evaluation Suite for Bioinformatics](https://arxiv.org/pdf/2601.21800)

### Instructions covered
- End-to-end bioinformatics task prompts rather than isolated QA/code tasks.
- Exact benchmark task names include:
  - `alzheimer`
  - `comparative-genomics`
  - `cystic-fibrosis`
  - `deseq`
  - `evolution`
  - `giab`
  - `metagenomics`
  - `single-cell`
  - `transcript-quant`
  - `viral-metagenomics`
- These tasks collectively cover workflows such as RNA-seq differential expression, variant calling, comparative genomics, transcript quantification, metagenomics, and single-cell analysis.
- Prompts specify concrete final artifacts so outputs can be graded.
- The system prompt instructs the agent to produce per-step artifacts and a final result artifact.
- Robustness instructions are stress-tested with:
  - Prompt bloat
  - Corrupted input data
  - Decoy reference data

### Formats covered
- Agent input bundle:
  - Task prompt
  - Input data
  - Reference data, when applicable
- Expected deliverable format:
  - File artifacts produced across named pipeline stages or directories
  - A final requested result artifact
- Evaluation inputs to the grader:
  - Input data
  - Reference data
  - Processing tree
  - Results
  - Truth
  - Original task prompt
- Grader return format:
  - `steps completed`
  - `steps to completion`
  - `final result reached`
  - `notes`
  - `results match`
- Optional task-specific metric:
  - `f1 score` where applicable
- The paper explicitly says these metrics are returned as a JSON object conforming to an `EvaluationResults` schema.
- Evaluation style:
  - LLM judge for flexible workflow grading
  - Rubric-based result matching
  - Completion-rate primary metric
  - Manual inspection for perturbation failure analysis

### Gaps addressed
- Existing bioinformatics evaluations collapse rich workflows into simplified QA or code generation.
- Strict pass/fail labeling is often unrealistic because multiple valid pipelines exist.
- Practical deployment in bioinformatics often has privacy, IP, and governance constraints that make closed hosted models unsuitable.
- Prior evaluations under-test robustness to corrupted data, decoy files, and instruction overload.

### Remaining gaps or limitations called out
- LLM grading can be subjective and can reward plausible-looking but wrong reasoning.
- Resource caps improve reproducibility but reduce fidelity to large, messy, real bioinformatics workloads.
- Robustness testing is narrow and sampled lightly.
- Inference from benchmark scope: external literature search, reference curation, and best-practice justification appear less represented than execution-heavy pipeline work.

## 3. AGENTIF

Source:
- [AGENTIF: Benchmarking Instruction Following of Large Language Models in Agentic Scenarios](https://arxiv.org/pdf/2505.16944)

### Instructions covered
- 707 human-annotated instructions from 50 real-world agentic applications.
- Instructions are long and specification-heavy, with an average length around 1,723 words and an average of 11.9 constraints.
- Constraint types covered:
  - Formatting constraints
  - Semantic constraints
  - Tool constraints
- Constraint presentation types covered:
  - Vanilla constraints
  - Conditional constraints
  - Example-implied constraints
- Meta-constraints covered:
  - Constraint selection
  - Constraint detailing
  - Constraint prioritization
- Examples of covered instruction behavior:
  - Output in JSON or Markdown
  - Use bullet points, tables, paragraph limits, or symbol conventions
  - Wrap filenames in backticks
  - Explain content in a prescribed step structure
  - Restrict tool usage to specific functions
  - Forbid internet access
  - Enforce parameter formats for tool calls

### Formats covered
- Instruction source format:
  - Real agent system prompts plus human-rewritten user queries
- Annotation format:
  - Instructions segmented into semantic blocks such as task description, tool configuration, and output specification
  - Constraint extraction performed block-wise with cross-block validation
- Evaluation formats:
  - Code-based verification
  - LLM-based verification
  - Hybrid verification
- Hybrid evaluation examples include extracting relevant spans such as JSON tool calls before validating them with code.
- Appendix coverage includes prompt templates for:
  - Instruction collection
  - Constraint annotation
  - Conditional checks
  - Evaluation generation
- Constraint taxonomy format in the appendix makes the dataset reusable as a typed instruction/constraint benchmark.

### Gaps addressed
- Prior instruction-following benchmarks are usually short and synthetic.
- Prior benchmarks under-cover realistic system prompts and tool specifications.
- Prior instruction-following work misses conditional, example-based, and tool-specific constraints common in real agent systems.
- Existing evaluation setups overlook realistic agent instruction compliance under long context.

### Remaining gaps or limitations called out
- Construction is still semi-automated and requires heavy manual verification.
- Coverage is limited to English and Chinese.
- Experiments are zero-shot only and do not study prompt-engineering interventions.
- Longer instructions degrade performance.
- Condition constraints, tool constraints, and meta-constraint selection remain especially difficult.
- The paper suggests future work on post-training with long instructions and on safer prioritization of meta-constraints.

## 4. AgentIF-OneDay

Source:
- [AgentIF-OneDay: A Task-level Instruction-Following Benchmark for General AI Agents in Daily Scenarios](https://arxiv.org/pdf/2601.20613)

### Instructions covered
- General-user daily tasks spanning work, life, and study rather than narrow professional-only domains.
- Three core instruction families:
  - Open Workflow Execution
  - Latent Instruction Inference
  - Iterative Refinement
- Covered behaviors include:
  - Following explicit multi-step workflows
  - Inferring hidden rules from attachments
  - Editing or extending prior artifacts without breaking them
  - Delivering tangible file-based outputs
- Human annotation guidelines require tasks to be:
  - Difficult
  - Objective
  - Search resistant
- Synthetic generation pipeline preserves workflow structure from seed tasks while changing domain/context.

### Formats covered
- Multimodal task format:
  - Text instructions
  - Attachments
  - File-based deliverables
- Attachment/file formats explicitly present in the benchmark statistics:
  - CSV
  - DOC
  - DOCX
  - GZ
  - HTML
  - JPEG
  - JSON
  - MD
  - PDF
  - PNG
  - JPG
  - PY
  - PPTX
  - SRT
  - SVG
  - TEX
  - TXT
  - XLS
  - XLSX
  - ZIP
- Rubric format:
  - Positive criteria
  - Negative criteria
  - Categorized into Content, Form, and Execution
- Appendix prompt formats for benchmark generation include:
  - Workflow extraction prompt returning JSON with `task`, `task_type`, and ordered `workflow` steps
  - Attachment-search prompt for finding realistic supporting files
  - Query-generation prompt returning JSON with `original_task`, `workflow_pattern`, and `generated_questions`
  - Rubric-generation prompt returning JSON with `evaluation_rubric`, `bonus_criteria`, `penalty_criteria`, `max_possible_score`, and `min_possible_score`
- The generation pipeline also enforces:
  - Clear input/output requirements per workflow step
  - Dependency links between steps
  - Verifiable final artifacts instead of scoring intermediate browsing actions
  - Binary rubric checks over independently verifiable criteria
  - Web search grounding for time-sensitive factual checks
  - HTML rendering when scoring HTML-writing tasks

### Gaps addressed
- Current evaluations over-focus on hard vertical tasks and under-cover everyday tasks ordinary users care about.
- Existing general-agent evaluations do not sufficiently test attachment understanding or file-based outputs.
- Many benchmarks miss latent instructions where the real format/spec is encoded in an attachment instead of the text prompt.
- Existing suites underrepresent iterative collaboration and revision over previous outputs.

### Remaining gaps or limitations exposed by results
- Implicit instruction inference from attachments is the weakest capability across tested agents.
- Agents often get either the content right or the format right, but not both together.
- LLM judging still diverges materially from human judgment, especially on abstract criteria such as conciseness, completeness, and design sense.
- Case studies expose weaknesses in multimodal reasoning, style transfer, and attachment-derived formatting.

## 5. SkillsBench

Source:
- [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://arxiv.org/pdf/2602.12670)

### Instructions covered
- Skill-augmented agent tasks across 11 domains.
- Skills are defined as reusable procedural packages, not one-off solutions.
- A valid Skill must provide:
  - Procedural content
  - Task-class applicability
  - Structured components
  - Filesystem portability
- Skill contents covered:
  - Workflows
  - SOPs
  - Domain conventions
  - Scripts
  - Templates
  - Examples
  - Reference docs
- Task instructions are human-written and must not name the specific Skill to use.
- Contributor instructions emphasize:
  - Human authorship
  - Skill generality
  - Deterministic verification
  - Realistic professional workflows
  - Stronger-than-baseline benefit from Skills
  - No explicit reference to which Skill the agent should use
  - No task-specific leakage inside the Skill package

### Formats covered
- Benchmark task package layout:
  - `instruction.md`
  - `task.toml`
  - `environment/Dockerfile`
  - `environment/skills/<skill-name>/SKILL.md`
  - optional `scripts/`
  - optional `references/`
  - `solution/solve.sh`
  - `tests/test.sh`
  - `tests/test_outputs.py`
- `task.toml` is used for metadata and resource configuration.
- Evaluation conditions:
  - No Skills
  - Curated Skills
  - Self-generated Skills
- Verification format:
  - Deterministic programmatic tests
  - Main metric is pass/fail with no partial credit
- Quality-control formats:
  - Structural validation
  - Oracle execution
  - AI-detection screening
  - Leakage audit
  - Benchmark report with pass rates and failure analysis
- Automated instruction-quality checks include:
  - explicit output paths
  - structured requirements
  - success criteria
  - listed constraints
  - context-first ordering
- Failure taxonomy format includes:
  - Timeout
  - Execution failures
  - Specification violation
  - Domain knowledge gap
  - Incorrect implementation
  - Tool/environment failure

### Gaps addressed
- Existing agent benchmarks measure raw agent capability but not whether Skills actually help.
- Practitioners lack a standard way to compare no-Skill, curated-Skill, and self-generated-Skill conditions.
- There was no paired benchmark for measuring augmentation efficacy rather than only model strength.
- Existing evaluation practice underexplains what makes a Skill effective or ineffective.
- Existing benchmarks also lack explicit leakage-prevention rules separating reusable procedural guidance from hidden task solutions.

### Remaining gaps or limitations called out
- Results are mostly for terminal-based, containerized tasks and may not transfer directly to GUI or multimodal agents.
- Gains from Skills may partly reflect added context length, not only procedural structure.
- Containerization does not remove all nondeterminism or contamination risk.
- The benchmark uses relatively high-quality curated Skills, so real-world Skill ecosystems may perform worse.
- Skill efficacy varies by harness, and some harnesses retrieve or apply Skills better than others.
- Too many Skills or overly comprehensive Skills can hurt performance.

## Reusable patterns worth carrying forward

### Strong instruction patterns
- Prefer explicit workflow steps when evaluating execution fidelity.
- Add hidden or latent constraints through attachments when evaluating real-world inference.
- Separate tool constraints from plain formatting constraints.
- Score final artifacts, not just conversational plausibility.
- Include iterative revision tasks to test state maintenance.

### Strong format patterns
- Use typed config or output files such as JSON or TOML whenever possible.
- Package each task with an instruction file, environment, oracle/reference solution, and verifier.
- For open-ended domains, pair deterministic checks with rubric-based or LLM-assisted grading.
- For reliability work, report multi-run profiles instead of a one-shot accuracy number.
- For procedural augmentation, store reusable guidance as modular skill packages rather than hidden system-prompt text.

### Strong gap coverage patterns
- Test robustness under paraphrase, prompt bloat, corrupted files, decoys, and tool failures.
- Measure whether agents can infer format requirements from examples or attachments.
- Measure domain privacy and deployability constraints, not only raw task success.
- Compare augmentation against a true no-augmentation baseline.
- Separate capability gains from reliability gains.
