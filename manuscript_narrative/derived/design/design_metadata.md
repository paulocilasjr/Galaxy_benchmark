# Design differences between the open-ended-code and Galaxy arms

Compiled 2026-10-02 from the archived Galaxy_benchmark repository. 4,240 archived runs: BixBench50 1,500; CompBio 2,500; IWC 240. Read-only extraction; ground_truth/, evaluation.json and result.json contents, .env and credentials were not read; no agent code run; no server contacted. Machine-readable tables, with the exact source fields, are in `design_metadata.json`; `per_run_design_metadata.csv` lists one row per run. 'Not recorded' means no field holding the value was found; nothing is imputed. One public Galaxy username and two account tokens are redacted, as the archive itself does elsewhere.

## Key differences

- **IWC time budgets differ within matched replicate pairs.** Each IWC run had a 6 h (21,600 s) or 12 h (43,200 s) wall-clock ceiling (`codex_invocation.json` `wall_clock_timeout_seconds`, identical to `iwc_scientific_audit.json` `wall_timeout_seconds` for 240/240). The budget depends only on start time: all runs started up to 2026-08-28 13:44 UTC had 6 h, and all runs started from 13:49 UTC had 12 h. Of 120 same-task, same-model, same-replicate Galaxy/code pairs, **73 have matching budgets** and 47 do not (26 with 12 h Galaxy and 6 h code; 21 with 6 h Galaxy and 12 h code).
- **Run budgets elsewhere are asymmetric or absent.** CompBio code prompts state "You have 120 minutes" for 1,294/1,300 runs (240 or 480 min for 6 single-item recovery runs). No budget is recorded for CompBio Galaxy runs or for any BixBench50 run.
- **Prompts always differ between arms.** No task/model/replicate pair shares a prompt file (0 identical of 2,070 compared). BixBench and CompBio Galaxy prompts add execution policy: compute on Galaxy only, copy or use the assigned history, banned tools, a local-code allowlist, route selection and UDT rules, MCP tool names and blocking-call timeouts. By median they are longer: 702 vs 368 words in BixBench50 and 938 vs 227 in CompBio. IWC prompts differ in only two lines plus the logging instruction: 55 code prompts (the 12 h code runs) require structured `analysis_steps.jsonl` records, and all Galaxy prompts ask for a concise log. Prompt versions also vary within arms: BixBench uses two versions per arm (Galaxy: GPT models vs DeepSeek; code: GPT-5.5 and DeepSeek vs GPT-5.6), and CompBio Galaxy uses an older and a newer (`promptv2`) version.
- **Harnesses and containers are not constant within configurations.** BixBench GPT-5.5 Galaxy runs used 4 image tags, mostly `full-blocking-20260715`, while its code runs mostly used `no-static-udt-resolver-20260714`. CompBio Galaxy runs ran in Docker (`galaxy-eval-agent:latest`), while CompBio code runs ran in a host conda clone with no container. IWC used one image digest for both arms, the same digest as the CompBio Galaxy image.
- **CompBio vectors are composite campaigns, mostly in the Galaxy arm.** 387/1,200 Galaxy runs and 101/1,300 code runs come from a campaign other than the largest one in their replicate vector. 86 Galaxy runs and 0 code runs come from campaigns whose names reference wrong answers or target scores (`wrong19`, `wrongset`, `fastwrong`, `target84`, `near84`). Of the 2,400 archived paired runs, 2,399 match the registry's source campaign for that item.
- **Reruns and replacements exist in all benchmarks.** BixBench50 has 13 non-primary iteration settings, and IWC has 27 Galaxy and 11 code runs from rerun roots, both detailed under Q7.
- **Other arm-specific conditions.** BixBench DeepSeek Galaxy runs (both harnesses, 300) had no local input files, while GPT Galaxy runs and all code runs did. Galaxy-only skills (`galaxy-tool-submission`, `galaxy-udt-authoring`) were removed from code runs. BixBench DeepSeek-via-Codex code runs still mounted a Galaxy API key. Some CompBio Galaxy histories were tagged `training`. Galaxy-arm registry campaigns carry two redacted account labels.

## Q1. Agent harness and container

Source: analysis.json runs[].model_metadata.harness (mm_harness); docker image from run_trace/docker_invocation.json image (fallback evidence runs[].environment.docker_image); image_id from docker_invocation.json image_id or IWC docker_isolation.json image_id; execution_backend from CompBio task.json execution_backend / conda_invocation.json execution_backend, or presence of a docker invocation/isolation record; agent_runtime from attempt.json agent_runtime / docker_invocation.json agent_runtime / conda_invocation.json codex_executable.

| Benchmark | Model | Arm | analysis.json harness | Docker image | Image ID | Backend | Agent runtime | Runs |
|---|---|---|---|---|---|---|---|---|
| BixBench50 | GPT-5.5 | Galaxy | bixbench-galaxy-agent:adaptive-search-20260715 | bixbench-galaxy-agent:adaptive-search-20260715 | not recorded | docker (docker_invocation.json) | not recorded | 6 |
| BixBench50 | GPT-5.5 | Galaxy | bixbench-galaxy-agent:full-blocking-20260715 | bixbench-galaxy-agent:full-blocking-20260715 | not recorded | docker (docker_invocation.json) | not recorded | 96 |
| BixBench50 | GPT-5.5 | Galaxy | bixbench-galaxy-agent:mcp-hardening-20260715 | bixbench-galaxy-agent:mcp-hardening-20260715 | not recorded | docker (docker_invocation.json) | not recorded | 6 |
| BixBench50 | GPT-5.5 | Galaxy | bixbench-galaxy-agent:no-static-udt-resolver-20260714 | bixbench-galaxy-agent:no-static-udt-resolver-20260714 | not recorded | docker (docker_invocation.json) | not recorded | 42 |
| BixBench50 | GPT-5.5 | Code | bixbench-galaxy-agent:full-blocking-20260715 | bixbench-galaxy-agent:full-blocking-20260715 | not recorded | docker (docker_invocation.json) | not recorded | 3 |
| BixBench50 | GPT-5.5 | Code | bixbench-galaxy-agent:no-static-udt-resolver-20260714 | bixbench-galaxy-agent:no-static-udt-resolver-20260714 | not recorded | docker (docker_invocation.json) | not recorded | 147 |
| BixBench50 | GPT-5.6 Luna | Galaxy | bixbench-galaxy-agent:codex-0.146.0-20260729 | bixbench-galaxy-agent:codex-0.146.0-20260729 | not recorded | docker (docker_invocation.json) | not recorded | 150 |
| BixBench50 | GPT-5.6 Luna | Code | bixbench-galaxy-agent:codex-0.146.0-20260729 | bixbench-galaxy-agent:codex-0.146.0-20260729 | not recorded | docker (docker_invocation.json) | not recorded | 150 |
| BixBench50 | GPT-5.6 Sol | Galaxy | bixbench-galaxy-agent:codex-0.146.0-20260729 | bixbench-galaxy-agent:codex-0.146.0-20260729 | not recorded | docker (docker_invocation.json) | not recorded | 150 |
| BixBench50 | GPT-5.6 Sol | Code | bixbench-galaxy-agent:codex-0.146.0-20260729 | bixbench-galaxy-agent:codex-0.146.0-20260729 | not recorded | docker (docker_invocation.json) | not recorded | 150 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | bixbench-claude-agent:deepseek-v4pro-latest-20260716 | bixbench-claude-agent:deepseek-v4pro-latest-20260716 | not recorded | docker (docker_invocation.json) | claude_code | 150 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Code | bixbench-claude-agent:deepseek-v4pro-latest-20260716 | bixbench-claude-agent:deepseek-v4pro-latest-20260716 | not recorded | docker (docker_invocation.json) | claude_code | 150 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Galaxy | bixbench-codex-agent:deepseek-v4pro-formal-20260813 | bixbench-codex-agent:deepseek-v4pro-formal-20260813 | not recorded | docker (docker_invocation.json) | codex_cli_0.146.0 | 150 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Code | bixbench-codex-agent:deepseek-v4pro-formal-20260813 | bixbench-codex-agent:deepseek-v4pro-formal-20260813 | not recorded | docker (docker_invocation.json) | codex_cli_0.146.0 | 150 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Galaxy | docker | galaxy-eval-agent:latest | sha256:57082a89e748... | docker | not recorded | 300 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Code | conda | not recorded | not recorded | host_conda_clone | codex_cli_0146_x64_runtime | 300 |
| CompBio | GPT-5.5 | Galaxy | docker | galaxy-eval-agent:latest | sha256:57082a89e748... | docker | not recorded | 244 |
| CompBio | GPT-5.5 | Galaxy | not recorded | not recorded | not recorded | docker | not recorded | 56 |
| CompBio | GPT-5.5 | Code | not recorded | not recorded | not recorded | host_conda_clone | not recorded | 300 |
| CompBio | GPT-5.6 Luna | Galaxy | docker | galaxy-eval-agent:latest | sha256:57082a89e748... | docker | not recorded | 300 |
| CompBio | GPT-5.6 Luna | Code | not recorded | not recorded | not recorded | host_conda_clone | not recorded | 300 |
| CompBio | GPT-5.6 Sol | Galaxy | docker | galaxy-eval-agent:latest | sha256:57082a89e748... | docker | not recorded | 270 |
| CompBio | GPT-5.6 Sol | Galaxy | not recorded | not recorded | not recorded | docker | not recorded | 30 |
| CompBio | GPT-5.6 Sol | Code | not recorded | not recorded | not recorded | host_conda_clone | not recorded | 300 |
| CompBio | GPT-6 Astra | Code | conda | not recorded | not recorded | host_conda_clone | ChatGPT.app | 100 |
| IWC | DeepSeek V4 Pro (Codex) | Galaxy | not recorded | not recorded | sha256:57082a89e748... | docker (docker_isolation.json) | not recorded | 30 |
| IWC | DeepSeek V4 Pro (Codex) | Code | not recorded | not recorded | sha256:57082a89e748... | docker (docker_isolation.json) | not recorded | 30 |
| IWC | GPT-5.5 | Galaxy | not recorded | not recorded | sha256:57082a89e748... | docker (docker_isolation.json) | not recorded | 30 |
| IWC | GPT-5.5 | Code | not recorded | not recorded | sha256:57082a89e748... | docker (docker_isolation.json) | not recorded | 30 |
| IWC | GPT-5.6 Luna | Galaxy | not recorded | not recorded | sha256:57082a89e748... | docker (docker_isolation.json) | not recorded | 30 |
| IWC | GPT-5.6 Luna | Code | not recorded | not recorded | sha256:57082a89e748... | docker (docker_isolation.json) | not recorded | 30 |
| IWC | GPT-5.6 Sol | Galaxy | not recorded | not recorded | sha256:57082a89e748... | docker (docker_isolation.json) | not recorded | 30 |
| IWC | GPT-5.6 Sol | Code | not recorded | not recorded | sha256:57082a89e748... | docker (docker_isolation.json) | not recorded | 30 |

Null image/image_id means no invocation record was archived for that run (CompBio open-ended GPT-5.5/Sol/Luna runs, 56 CompBio Galaxy GPT-5.5 runs and 30 CompBio Galaxy Sol runs). The IWC image is recorded only as a content digest (no tag).

## Q2. Runtime model IDs and reasoning settings

Source: analysis.json runs[].model_metadata (supplied_label, verified_runtime_id, reasoning_setting, verification_status; IWC verified_runtime_id/reasoning are filled by analysis.json from IWC/iwc_scientific_audit.json runtime); invocation_* columns re-read from docker_invocation.json (model, reasoning_effort|effort, service_tier, model_provider|provider), conda_invocation.json, IWC codex_invocation.json runtime.

| Benchmark | Model | Arm | Verified runtime ID | Reasoning | Status | Invocation model | Invocation reasoning | Service tier | Provider | Runs |
|---|---|---|---|---|---|---|---|---|---|---|
| BixBench50 | GPT-5.5 | Galaxy | gpt-5.5 | high | runtime_verified | gpt-5.5 | high | fast | not recorded | 150 |
| BixBench50 | GPT-5.5 | Code | gpt-5.5 | high | runtime_verified | gpt-5.5 | high | fast | not recorded | 150 |
| BixBench50 | GPT-5.6 Luna | Galaxy | gpt-5.6-luna | max | runtime_verified | gpt-5.6-luna | max | fast | not recorded | 150 |
| BixBench50 | GPT-5.6 Luna | Code | gpt-5.6-luna | max | runtime_verified | gpt-5.6-luna | max | fast | not recorded | 150 |
| BixBench50 | GPT-5.6 Sol | Galaxy | gpt-5.6-sol | high | runtime_verified | gpt-5.6-sol | high | fast | not recorded | 150 |
| BixBench50 | GPT-5.6 Sol | Code | gpt-5.6-sol | high | runtime_verified | gpt-5.6-sol | high | fast | not recorded | 150 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | deepseek-v4-pro[1m] | high | runtime_verified | deepseek-v4-pro[1m] | high | not recorded | deepseek_anthropic_compat | 150 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Code | deepseek-v4-pro[1m] | high | runtime_verified | deepseek-v4-pro[1m] | high | not recorded | deepseek_anthropic_compat | 150 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Galaxy | deepseek-v4-pro | high | runtime_verified | deepseek-v4-pro | high | not recorded | deepseek | 150 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Code | deepseek-v4-pro | high | runtime_verified | deepseek-v4-pro | high | not recorded | deepseek | 150 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Galaxy | deepseek-v4-pro | high | runtime_verified | deepseek-v4-pro | high | not recorded | deepseek | 300 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Code | deepseek-v4-pro | high | runtime_verified | deepseek-v4-pro | high | not recorded | deepseek | 300 |
| CompBio | GPT-5.5 | Galaxy | gpt-5.5 | high | runtime_verified | gpt-5.5 | high | fast | not recorded | 244 |
| CompBio | GPT-5.5 | Galaxy | not recorded | not recorded | user_supplied_only | not recorded | not recorded | not recorded | not recorded | 56 |
| CompBio | GPT-5.5 | Code | not recorded | not recorded | user_supplied_only | not recorded | not recorded | not recorded | not recorded | 300 |
| CompBio | GPT-5.6 Luna | Galaxy | gpt-5.6-luna | max | runtime_verified | gpt-5.6-luna | max | fast | not recorded | 300 |
| CompBio | GPT-5.6 Luna | Code | not recorded | not recorded | user_supplied_only | not recorded | not recorded | not recorded | not recorded | 300 |
| CompBio | GPT-5.6 Sol | Galaxy | gpt-5.6-sol | high | runtime_verified | gpt-5.6-sol | high | fast | not recorded | 270 |
| CompBio | GPT-5.6 Sol | Galaxy | not recorded | not recorded | user_supplied_only | not recorded | not recorded | not recorded | not recorded | 30 |
| CompBio | GPT-5.6 Sol | Code | not recorded | not recorded | user_supplied_only | not recorded | not recorded | not recorded | not recorded | 300 |
| CompBio | GPT-6 Astra | Code | gpt-6-astra | high | runtime_verified | gpt-6-astra | high | fast | not recorded | 100 |
| IWC | DeepSeek V4 Pro (Codex) | Galaxy | deepseek-v4-pro | high | user_supplied_only | deepseek-v4-pro | high | not recorded | deepseek | 30 |
| IWC | DeepSeek V4 Pro (Codex) | Code | deepseek-v4-pro | high | user_supplied_only | deepseek-v4-pro | high | not recorded | deepseek | 30 |
| IWC | GPT-5.5 | Galaxy | gpt-5.5 | high | user_supplied_only | gpt-5.5 | high | fast | not recorded | 30 |
| IWC | GPT-5.5 | Code | gpt-5.5 | high | user_supplied_only | gpt-5.5 | high | fast | not recorded | 30 |
| IWC | GPT-5.6 Luna | Galaxy | gpt-5.6-luna | max | user_supplied_only | gpt-5.6-luna | max | fast | not recorded | 30 |
| IWC | GPT-5.6 Luna | Code | gpt-5.6-luna | max | user_supplied_only | gpt-5.6-luna | max | fast | not recorded | 30 |
| IWC | GPT-5.6 Sol | Galaxy | gpt-5.6-sol | high | user_supplied_only | gpt-5.6-sol | high | fast | not recorded | 30 |
| IWC | GPT-5.6 Sol | Code | gpt-5.6-sol | high | user_supplied_only | gpt-5.6-sol | high | fast | not recorded | 30 |

Verification counts (status from task evidence; "invocation record" means a model ID was re-read from an invocation file):

| Benchmark | Arm | Evidence status | Invocation record | Runs |
|---|---|---|---|---|
| BixBench50 | Galaxy | runtime_verified | yes | 750 |
| BixBench50 | Code | runtime_verified | yes | 750 |
| CompBio | Galaxy | runtime_verified | yes | 1,114 |
| CompBio | Galaxy | user_supplied_only | no | 86 |
| CompBio | Code | runtime_verified | yes | 400 |
| CompBio | Code | user_supplied_only | no | 900 |
| IWC | Galaxy | user_supplied_only | yes | 120 |
| IWC | Code | user_supplied_only | yes | 120 |

IWC task evidence labels all 240 runs 'user_supplied_only', but each IWC run has codex_invocation.json runtime.model and model_reasoning_effort (the IWC README treats these as verification). GPT runs record no model-provider override (default provider). CompBio has no runtime model record for 900 open-ended GPT-5.5/Sol/Luna runs, 56 Galaxy GPT-5.5 runs and 30 Galaxy Sol runs. The campaign registry gives only descriptive settings ('high reasoning / fast processing' for GPT-5.5, Sol and Luna; Luna Galaxy campaign names contain 'luna_max_fast'). service_tier is 'fast' for GPT runs and empty for DeepSeek via Codex. The superseded BixBench DeepSeek harness ran Claude Code with deepseek_anthropic_compat and subagent/haiku model deepseek-v4-flash (provider_config.json).

## Q3. Prompts

Source: prompt.txt in each run snapshot (sha256 recomputed from bytes; equals evidence runs[].prompt_sha256 and analysis.json prompt_sha256 for 4,240/4,240 runs); word counts use the generator regex \b\w+\b; analysis.json prompt_words counts the task-level question for BixBench/CompBio (evidence task.prompt) and the archived prompt.txt for IWC.

Distinct prompt-file hashes per task and arm, across all models and replicates:

| Benchmark | Arm | Min | Median | Max | Tasks by number of distinct hashes |
|---|---|---|---|---|---|
| BixBench50 | Galaxy | 2 | 2 | 2 | 2: 50 |
| BixBench50 | Code | 2 | 2 | 2 | 2: 50 |
| CompBio | Galaxy | 1 | 2 | 3 | 1: 7; 2: 76; 3: 17 |
| CompBio | Code | 2 | 2 | 4 | 2: 98; 3: 1; 4: 1 |
| IWC | Galaxy | 1 | 1 | 1 | 1: 10 |
| IWC | Code | 2 | 2 | 3 | 2: 6; 3: 4 |

Galaxy and code prompt identity:

| Benchmark | Pairs compared (task, model, replicate) | Identical prompt hash | Tasks sharing any hash across arms |
|---|---|---|---|
| BixBench50 | 750 | 0 | 0 |
| CompBio | 1,200 | 0 | 0 |
| IWC | 120 | 0 | 0 |

Prompt length (words in the archived `prompt.txt`). `analysis.json` `prompt_words` counts only the task question for BixBench and CompBio, so it is the same in both arms:

| Benchmark | Arm | Runs | Median words (prompt.txt) | IQR | Median analysis.json prompt_words |
|---|---|---|---|---|---|
| BixBench50 | Galaxy | 750 | 702 | 684-737 | 24.5 |
| BixBench50 | Code | 750 | 368 | 347-433 | 24.5 |
| CompBio | Galaxy | 1,200 | 937.5 | 909-968 | 66 |
| CompBio | Code | 1,300 | 227 | 209-259 | 66 |
| IWC | Galaxy | 120 | 333 | 272-367 | 333 |
| IWC | Code | 120 | 344 | 267-409 | 344 |

| Benchmark | Model | Arm | Median words | Range |
|---|---|---|---|---|
| BixBench50 | GPT-5.5 | Galaxy | 717 | 670-1260 |
| BixBench50 | GPT-5.5 | Code | 368.5 | 329-910 |
| BixBench50 | GPT-5.6 Luna | Galaxy | 717 | 670-1260 |
| BixBench50 | GPT-5.6 Luna | Code | 364.5 | 325-906 |
| BixBench50 | GPT-5.6 Sol | Galaxy | 717 | 670-1260 |
| BixBench50 | GPT-5.6 Sol | Code | 364.5 | 325-906 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | 688 | 661-743 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Code | 368.5 | 329-910 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Galaxy | 688 | 661-743 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Code | 368.5 | 329-910 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Galaxy | 940 | 879-1068 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Code | 227 | 167-356 |
| CompBio | GPT-5.5 | Galaxy | 929 | 600-1068 |
| CompBio | GPT-5.5 | Code | 226 | 162-356 |
| CompBio | GPT-5.6 Luna | Galaxy | 940 | 879-1068 |
| CompBio | GPT-5.6 Luna | Code | 227 | 167-356 |
| CompBio | GPT-5.6 Sol | Galaxy | 929 | 600-1068 |
| CompBio | GPT-5.6 Sol | Code | 227 | 167-356 |
| CompBio | GPT-6 Astra | Code | 227 | 167-356 |
| IWC | DeepSeek V4 Pro (Codex) | Galaxy | 333 | 196-586 |
| IWC | DeepSeek V4 Pro (Codex) | Code | 350.5 | 248-640 |
| IWC | GPT-5.5 | Galaxy | 333 | 196-586 |
| IWC | GPT-5.5 | Code | 350.5 | 248-640 |
| IWC | GPT-5.6 Luna | Galaxy | 333 | 196-586 |
| IWC | GPT-5.6 Luna | Code | 331 | 186-576 |
| IWC | GPT-5.6 Sol | Galaxy | 333 | 196-586 |
| IWC | GPT-5.6 Sol | Code | 323 | 186-576 |

Per task and model, the median Galaxy prompt length minus the median code prompt length:

| Benchmark | Median difference (words) | Min | Max | Task-model cells |
|---|---|---|---|---|
| BixBench50 | 346 | -210 | 357 | 250 |
| CompBio | 713 | 712 | 718 | 400 |
| IWC | 10 | -60 | 10 | 40 |

Prompt content flags (runs whose prompt contains the phrase; definitions in JSON):

| Benchmark | Model | Arm | Runs | "Galaxy is not required" | No local inputs | Skills | UDT | start_timeout 300 | CompBio old Galaxy prompt | CompBio promptv2 | No wall-clock limit on calls | IWC analysis_steps.jsonl | IWC concise log | Internet | Stated minutes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BixBench50 | GPT-5.5 | Galaxy | 150 | 0 | 0 | 150 | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 0 | none: 150 |
| BixBench50 | GPT-5.5 | Code | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 150 | none: 150 |
| BixBench50 | GPT-5.6 Luna | Galaxy | 150 | 0 | 0 | 150 | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 0 | none: 150 |
| BixBench50 | GPT-5.6 Luna | Code | 150 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 150 | none: 150 |
| BixBench50 | GPT-5.6 Sol | Galaxy | 150 | 0 | 0 | 150 | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 0 | none: 150 |
| BixBench50 | GPT-5.6 Sol | Code | 150 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 150 | none: 150 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | 150 | 0 | 150 | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none: 150 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Code | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 150 | none: 150 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Galaxy | 150 | 0 | 150 | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none: 150 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Code | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 150 | none: 150 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Galaxy | 300 | 0 | 0 | 300 | 300 | 0 | 0 | 300 | 0 | 0 | 0 | 300 | none: 300 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Code | 300 | 0 | 0 | 300 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 300 | 120: 298; 240: 1; 480: 1 |
| CompBio | GPT-5.5 | Galaxy | 300 | 0 | 0 | 300 | 300 | 0 | 79 | 221 | 79 | 0 | 0 | 300 | none: 300 |
| CompBio | GPT-5.5 | Code | 300 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 300 | 120: 299; 240: 1 |
| CompBio | GPT-5.6 Luna | Galaxy | 300 | 0 | 0 | 300 | 300 | 0 | 0 | 300 | 0 | 0 | 0 | 300 | none: 300 |
| CompBio | GPT-5.6 Luna | Code | 300 | 0 | 0 | 300 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 300 | 120: 297; 480: 2; 240: 1 |
| CompBio | GPT-5.6 Sol | Galaxy | 300 | 0 | 0 | 300 | 300 | 0 | 81 | 219 | 81 | 0 | 0 | 300 | none: 300 |
| CompBio | GPT-5.6 Sol | Code | 300 | 0 | 0 | 300 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 300 | 120: 300 |
| CompBio | GPT-6 Astra | Code | 100 | 0 | 0 | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 100 | 120: 100 |
| IWC | DeepSeek V4 Pro (Codex) | Galaxy | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 | 0 | none: 30 |
| IWC | DeepSeek V4 Pro (Codex) | Code | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 7 | 0 | none: 30 |
| IWC | GPT-5.5 | Galaxy | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 | 0 | none: 30 |
| IWC | GPT-5.5 | Code | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 7 | 0 | none: 30 |
| IWC | GPT-5.6 Luna | Galaxy | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 | 0 | none: 30 |
| IWC | GPT-5.6 Luna | Code | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 25 | 0 | none: 30 |
| IWC | GPT-5.6 Sol | Galaxy | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 | 0 | none: 30 |
| IWC | GPT-5.6 Sol | Code | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 26 | 0 | none: 30 |

Prompt versions (models that share one prompt file for a task):

- BixBench50: each arm has two versions for all 50 tasks. Galaxy: the GPT family shares one version, and both DeepSeek harnesses share the other (no local inputs, different blocking-call text). Code: GPT-5.5 and both DeepSeek harnesses share one version, which includes "Galaxy is not required"; GPT-5.6 Sol and Luna use a version without that sentence.
- CompBio: in 62/100 tasks, GPT-5.5 r1 and Sol r1 share an older Galaxy prompt, and all other Galaxy runs share `promptv2`. Galaxy prompt versions follow campaign names exactly: `promptv2` appears in the campaign name of every run with the new text. In code, GPT-5.5 r1 (campaign `no_project_skills`) differs from all other runs in 98/100 tasks.
- IWC: all 12 Galaxy runs per task share one prompt (10/10 tasks). Code prompts take 2-3 versions per task, mainly the `analysis_steps.jsonl` requirement, which tracks start date and budget.

## Q4. Time and resource budgets

Source: IWC: agent_workspace/run_trace/codex_invocation.json wall_clock_timeout_seconds (identical to IWC/iwc_scientific_audit.json runs[].wall_timeout_seconds for 240/240); CompBio: evidence runs[].budgets.time (timeout_minutes/timeout_seconds) <- task.json timeout_minutes, conda_invocation.json timeout_seconds, and prompt text 'You have N minutes'; BixBench50: evidence runs[].budgets {time,tokens,retry_policy} all null and no run-level timeout field found in docker_invocation.json, attempt.json, run_record.json or runner.log.

| Benchmark | Arm | Run budget | Note |
|---|---|---|---|
| BixBench50 | both | not recorded (1,500/1,500 evidence budgets null) | Galaxy prompts instruct a per-job blocking-call timeout (normally 5400 s); this is a Galaxy job wait, not a run budget. Open-ended prompts say only "within the active runtime limits". |
| CompBio | open_ended_code | 120 min for 1,294/1,300 runs; 240 min for 3; 480 min for 3 (prompt "You have N minutes" = task.json timeout_minutes for all 1,300; conda_invocation timeout_seconds 7,200/14,400/28,800 also recorded for the 400 DeepSeek and Astra runs) | The longer budgets belong to single-item recovery campaigns (campaign names contain encode_retry_240m, timeout240, t480, recovery480, timeout480). |
| CompBio | galaxy | not recorded (task.json timeout_minutes null for 1,200/1,200; prompts state no minutes) | 81 Sol and 79 GPT-5.5 Galaxy prompts (older prompt version) say "do not set a wall-clock time limit" on blocking Galaxy calls. |
| IWC | both | 21,600 s (6 h) or 43,200 s (12 h) per run | All runs started up to 2026-08-28T13:44:15Z had 6 h; all runs started from 2026-08-28T13:49:53Z had 12 h. Token and retry budgets: not recorded. |

IWC budgets by configuration (runs; matches IWC/result_section_iwc.md Table 1):

| Model | Arm | 6 h | 12 h |
|---|---|---|---|
| DeepSeek V4 Pro (Codex) | Galaxy | 10 | 20 |
| DeepSeek V4 Pro (Codex) | Code | 7 | 23 |
| GPT-5.5 | Galaxy | 15 | 15 |
| GPT-5.5 | Code | 7 | 23 |
| GPT-5.6 Luna | Galaxy | 17 | 13 |
| GPT-5.6 Luna | Code | 25 | 5 |
| GPT-5.6 Sol | Galaxy | 18 | 12 |
| GPT-5.6 Sol | Code | 26 | 4 |

IWC budget by start time (`codex_invocation.json` `started_at_utc`):

| Budget (h) | First start | Last start | Runs |
|---|---|---|---|
| 6 | 2026-08-27T08:15:24Z | 2026-08-28T13:44:15Z | 125 |
| 12 | 2026-08-28T13:49:53Z | 2026-09-03T04:01:19Z | 115 |

IWC matched-budget pairs (pair = same IWC task, model configuration and replicate label (1-3) in galaxy and open_ended_code; replicate labels are not matched seeds): **73/120 matched**.

| Model | Pairs | Matched | 12h Galaxy / 12h code | 12h Galaxy / 6h code | 6h Galaxy / 12h code | 6h Galaxy / 6h code |
|---|---|---|---|---|---|---|
| DeepSeek V4 Pro (Codex) | 30 | 21 | 17 | 3 | 6 | 4 |
| GPT-5.5 | 30 | 22 | 15 | 0 | 8 | 7 |
| GPT-5.6 Luna | 30 | 14 | 1 | 12 | 4 | 13 |
| GPT-5.6 Sol | 30 | 16 | 1 | 11 | 3 | 15 |

| Task | Pairs | Matched |
|---|---|---|
| wf_001_short_read_qc_trim | 12 | 8 |
| wf_002_rnaseq_de_visualization | 12 | 11 |
| wf_003_host_contamination_removal | 12 | 10 |
| wf_005_amplicon_dada2_pe_denoising | 12 | 7 |
| wf_006_atacseq_chromatin_accessibility | 12 | 8 |
| wf_007_vgp_mitogenome_assembly | 12 | 9 |
| wf_008_amr_gene_detection | 12 | 7 |
| wf_009_clinicalmp_peptide_verification | 12 | 6 |
| wf_010_pseudobulk_scrna_de | 12 | 6 |
| wf_011_bioproject_metadata_sequence_retrieval | 12 | 1 |

IWC code-arm prompt variant against budget:

| Prompt requires analysis_steps.jsonl | Budget (h) | Runs |
|---|---|---|
| False | 6 | 65 |
| True | 12 | 55 |

CompBio budget fields:

| Model | Arm | task.json timeout_minutes | conda timeout_seconds | Prompt minutes | Runs |
|---|---|---|---|---|---|
| DeepSeek V4 Pro 0813 (Codex) | Galaxy | not recorded | not recorded | not recorded | 300 |
| DeepSeek V4 Pro 0813 (Codex) | Code | 120 | 7,200 | 120 | 298 |
| DeepSeek V4 Pro 0813 (Codex) | Code | 240 | 14,400 | 240 | 1 |
| DeepSeek V4 Pro 0813 (Codex) | Code | 480 | 28,800 | 480 | 1 |
| GPT-5.5 | Galaxy | not recorded | not recorded | not recorded | 300 |
| GPT-5.5 | Code | 120 | not recorded | 120 | 299 |
| GPT-5.5 | Code | 240 | not recorded | 240 | 1 |
| GPT-5.6 Luna | Galaxy | not recorded | not recorded | not recorded | 300 |
| GPT-5.6 Luna | Code | 120 | not recorded | 120 | 297 |
| GPT-5.6 Luna | Code | 240 | not recorded | 240 | 1 |
| GPT-5.6 Luna | Code | 480 | not recorded | 480 | 2 |
| GPT-5.6 Sol | Galaxy | not recorded | not recorded | not recorded | 300 |
| GPT-5.6 Sol | Code | 120 | not recorded | 120 | 300 |
| GPT-6 Astra | Code | 120 | 7,200 | 120 | 100 |

Recorded resource limits: IWC containers only (both arms identical): 8 GiB memory, 4 CPUs, pids limit 512, bridge network (`docker_isolation.json`). No CPU or memory limits are recorded for BixBench or CompBio. Token and retry budgets are not recorded in any benchmark.

## Q5. Dates

Source: run_record.json prepared_at_utc (workspace preparation, not execution start); CompBio task.json created_at and campaign-directory timestamp in run_record.json agent_workspace path; completion.json started_at/finished_at (BixBench DeepSeek runs); usage.json written_at_utc (end-of-run usage write); IWC codex_invocation.json started_at_utc and docker_postrun.json started_at/finished_at; evidence runs[].timestamps.history_create_time; Galaxy history.json create_time/update_time; evidence sources[].retrieval_time_utc and audit.timestamp_utc for collection dates.

| Benchmark | Model | Arm | Workspace prepared (run_record) | Recorded run start | Recorded run end | Galaxy history created (evidence) | CompBio campaign-name timestamps |
|---|---|---|---|---|---|---|---|
| BixBench50 | GPT-5.5 | Galaxy | 2026-07-07 03:11 to 2026-07-08 21:55 | not recorded | 2026-07-15 03:34 to 2026-07-16 06:34 | 2026-07-15 03:31 to 2026-07-16 06:30 | not recorded |
| BixBench50 | GPT-5.5 | Code | 2026-07-07 03:11 to 2026-07-07 03:37 | not recorded | 2026-07-15 03:46 to 2026-07-15 21:58 | not recorded | not recorded |
| BixBench50 | GPT-5.6 Luna | Galaxy | 2026-08-01 03:02 to 2026-08-01 03:02 | not recorded | 2026-08-01 11:30 to 2026-08-03 23:27 | 2026-08-01 10:50 to 2026-08-03 23:21 | not recorded |
| BixBench50 | GPT-5.6 Luna | Code | 2026-07-31 21:47 to 2026-08-01 02:41 | not recorded | 2026-07-31 21:50 to 2026-08-01 10:48 | not recorded | not recorded |
| BixBench50 | GPT-5.6 Sol | Galaxy | 2026-08-01 03:02 to 2026-08-01 03:02 | not recorded | 2026-08-01 10:59 to 2026-08-02 21:32 | 2026-08-01 10:49 to 2026-08-02 20:28 | not recorded |
| BixBench50 | GPT-5.6 Sol | Code | 2026-07-31 21:10 to 2026-07-31 23:58 | not recorded | 2026-07-31 21:16 to 2026-08-01 07:00 | not recorded | not recorded |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | 2026-07-16 15:47 to 2026-07-16 15:47 | 2026-07-16 15:48 to 2026-07-17 20:21 | 2026-07-16 15:59 to 2026-07-17 21:42 | 2026-07-16 15:49 to 2026-07-17 20:22 | not recorded |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Code | 2026-07-16 15:47 to 2026-07-16 15:47 | 2026-07-16 15:51 to 2026-07-17 18:02 | 2026-07-16 15:53 to 2026-07-17 19:14 | not recorded | not recorded |
| BixBench50 | DeepSeek V4 Pro (Codex) | Galaxy | 2026-08-15 02:12 to 2026-08-21 14:28 | 2026-08-15 12:46 to 2026-08-21 14:32 | 2026-08-15 12:50 to 2026-08-21 17:52 | 2026-08-15 12:47 to 2026-08-17 11:54 | not recorded |
| BixBench50 | DeepSeek V4 Pro (Codex) | Code | 2026-08-15 02:12 to 2026-08-15 02:12 | 2026-08-15 02:42 to 2026-08-15 21:20 | 2026-08-15 02:49 to 2026-08-15 21:23 | not recorded | not recorded |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Galaxy | 2026-08-13 17:43 to 2026-08-26 01:42 | not recorded | not recorded | 2026-08-14 23:41 to 2026-08-26 16:15 | 2026-08-13 17:37 to 2026-08-26 01:20 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Code | 2026-08-13 17:43 to 2026-08-23 19:47 | not recorded | not recorded | not recorded | 2026-08-13 17:37 to 2026-08-23 19:38 |
| CompBio | GPT-5.5 | Galaxy | 2026-08-03 11:00 to 2026-08-25 14:19 | not recorded | not recorded | 2026-08-03 11:00 to 2026-08-25 14:31 | 2026-08-03 11:00 to 2026-08-25 14:20 |
| CompBio | GPT-5.5 | Code | 2026-07-30 04:41 to 2026-08-05 15:08 | not recorded | not recorded | not recorded | 2026-07-30 04:41 to 2026-08-05 15:08 |
| CompBio | GPT-5.6 Luna | Galaxy | 2026-08-20 04:14 to 2026-08-28 02:33 | not recorded | not recorded | 2026-08-21 04:17 to 2026-08-28 03:24 | 2026-08-20 04:05 to 2026-08-28 02:30 |
| CompBio | GPT-5.6 Luna | Code | 2026-08-03 22:12 to 2026-08-11 03:20 | not recorded | not recorded | not recorded | 2026-08-03 22:12 to 2026-08-11 03:19 |
| CompBio | GPT-5.6 Sol | Galaxy | 2026-08-09 11:31 to 2026-08-24 01:34 | not recorded | not recorded | 2026-08-09 11:37 to 2026-08-24 01:44 | 2026-08-09 11:31 to 2026-08-24 01:35 |
| CompBio | GPT-5.6 Sol | Code | 2026-08-05 01:54 to 2026-08-09 23:43 | not recorded | not recorded | not recorded | 2026-08-05 01:54 to 2026-08-09 23:42 |
| CompBio | GPT-6 Astra | Code | 2026-09-10 02:00 to 2026-09-10 14:01 | not recorded | not recorded | not recorded | 2026-09-10 02:00 to 2026-09-10 14:00 |
| IWC | DeepSeek V4 Pro (Codex) | Galaxy | not recorded | 2026-08-28 11:45 to 2026-09-02 12:55 | 2026-08-28 11:51 to 2026-09-02 14:12 | 2026-08-28 11:45 to 2026-09-02 12:55 | not recorded |
| IWC | DeepSeek V4 Pro (Codex) | Code | not recorded | 2026-08-28 11:43 to 2026-09-02 05:25 | 2026-08-28 11:48 to 2026-09-02 05:32 | not recorded | not recorded |
| IWC | GPT-5.5 | Galaxy | not recorded | 2026-08-28 12:30 to 2026-09-02 05:22 | 2026-08-28 12:36 to 2026-09-02 13:56 | 2026-08-28 12:30 to 2026-09-02 05:22 | not recorded |
| IWC | GPT-5.5 | Code | not recorded | 2026-08-28 12:30 to 2026-09-02 02:52 | 2026-08-28 12:32 to 2026-09-02 05:06 | not recorded | not recorded |
| IWC | GPT-5.6 Luna | Galaxy | not recorded | 2026-08-27 08:15 to 2026-09-02 13:57 | 2026-08-27 08:30 to 2026-09-02 14:20 | 2026-08-27 08:15 to 2026-09-02 13:57 | not recorded |
| IWC | GPT-5.6 Luna | Code | not recorded | 2026-08-27 08:15 to 2026-08-29 16:27 | 2026-08-27 08:19 to 2026-08-30 04:02 | not recorded | not recorded |
| IWC | GPT-5.6 Sol | Galaxy | not recorded | 2026-08-27 13:38 to 2026-09-03 04:01 | 2026-08-27 13:47 to 2026-09-03 04:12 | 2026-08-27 13:38 to 2026-09-03 04:01 | not recorded |
| IWC | GPT-5.6 Sol | Code | not recorded | 2026-08-27 13:38 to 2026-08-31 11:51 | 2026-08-27 13:40 to 2026-08-31 12:02 | not recorded | not recorded |

Run start: IWC `codex_invocation.json` started_at_utc, or BixBench DeepSeek `completion.json` started_at. Run end: IWC `docker_postrun.json` finished_at, BixBench DeepSeek `completion.json` finished_at, or `usage.json` written_at_utc (BixBench GPT and Claude runs). CompBio campaign timestamps are parsed from campaign directory names and converted to UTC (names ending in ET are taken as US Eastern daylight time, UTC-4).

Galaxy history snapshot times (`history.json`):

| Benchmark | Unique histories | create_time range | update_time range |
|---|---|---|---|
| BixBench50 | 747 | 2026-07-15T03:31 to 2026-08-17T11:54 | 2026-07-17T23:58 to 2026-08-25T11:22 |
| CompBio | 1,200 | 2026-08-03T11:00 to 2026-08-28T03:24 | 2026-08-12T21:42 to 2026-08-28T19:55 |
| IWC | 120 | 2026-08-27T08:15 to 2026-09-03T04:01 | 2026-08-29T13:24 to 2026-09-10T12:27 |

| Benchmark | Model | Links | Unique | history.json present | create_time range | update_time range |
|---|---|---|---|---|---|---|
| BixBench50 | GPT-5.5 | 150 | 150 | 150 | 2026-07-15T03:31 to 2026-07-16T06:30 | 2026-07-17T23:58 to 2026-07-23T10:21 |
| BixBench50 | GPT-5.6 Luna | 150 | 150 | 150 | 2026-08-01T10:50 to 2026-08-03T23:21 | 2026-08-04T01:03 to 2026-08-11T13:22 |
| BixBench50 | GPT-5.6 Sol | 150 | 149 | 150 | 2026-08-01T10:49 to 2026-08-02T20:28 | 2026-08-04T01:03 to 2026-08-10T12:20 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | 150 | 148 | 150 | 2026-07-16T15:49 to 2026-07-17T20:22 | 2026-07-18T00:00 to 2026-07-25T10:22 |
| BixBench50 | DeepSeek V4 Pro (Codex) | 150 | 150 | 146 | 2026-08-15T12:47 to 2026-08-17T11:54 | 2026-08-19T22:07 to 2026-08-25T11:22 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | 300 | 300 | 300 | 2026-08-14T23:41 to 2026-08-26T16:15 | 2026-08-26T21:16 to 2026-08-28T15:18 |
| CompBio | GPT-5.5 | 300 | 300 | 300 | 2026-08-03T11:00 to 2026-08-25T14:31 | 2026-08-12T21:42 to 2026-08-28T15:18 |
| CompBio | GPT-5.6 Luna | 300 | 300 | 300 | 2026-08-21T04:17 to 2026-08-28T03:24 | 2026-08-28T19:37 to 2026-08-28T19:55 |
| CompBio | GPT-5.6 Sol | 300 | 300 | 300 | 2026-08-09T11:37 to 2026-08-24T01:44 | 2026-08-12T21:45 to 2026-08-28T15:18 |
| IWC | DeepSeek V4 Pro (Codex) | 30 | 30 | 30 | 2026-08-28T11:45 to 2026-09-02T12:55 | 2026-08-29T13:24 to 2026-09-10T12:27 |
| IWC | GPT-5.5 | 30 | 30 | 30 | 2026-08-28T12:30 to 2026-09-02T05:22 | 2026-08-29T13:24 to 2026-09-10T12:27 |
| IWC | GPT-5.6 Luna | 30 | 30 | 30 | 2026-08-27T08:15 to 2026-09-02T13:57 | 2026-08-29T13:24 to 2026-09-09T12:49 |
| IWC | GPT-5.6 Sol | 30 | 30 | 30 | 2026-08-27T13:38 to 2026-09-03T04:01 | 2026-08-29T13:24 to 2026-09-10T12:27 |

Evidence collection (retrospective audit):

| Benchmark | Source retrieval (sources[].retrieval_time_utc) | Evidence audit timestamp |
|---|---|---|
| BixBench50 | 2026-09-20T17:33 to 2026-09-20T19:58 UTC | 2026-09-20T19:58 to 2026-09-20T20:00 UTC |
| CompBio | 2026-09-21T20:02 to 2026-09-21T23:35 UTC | 2026-09-21T23:39 to 2026-09-21T23:41 UTC |
| IWC | 2026-09-23T14:11 to 2026-09-23T14:30 UTC | 2026-09-23T14:39 to 2026-09-23T14:39 UTC |

Galaxy update_time reflects the last server-side change (for example publication or later tagging), not run end. Galaxy job create_time values in evidence include jobs inherited from copied seed histories and are not used as run dates. Open-ended BixBench GPT-5.6 and DeepSeek-via-Codex runs, and all CompBio open-ended runs, have no recorded execution start; only preparation/creation or usage-write times. CompBio aggregate registry files were retrieved 2026-09-22; the IWC scientific audit was generated 2026-09-23.

## Q6. Tools offered

Source: analysis.json runs[].galaxy_helpers_exposed (non-null only for IWC; copied from IWC codex_invocation.json runtime.galaxy_mcp_tools); docker_invocation.json galaxy_execute_mcp_enabled / galaxy_wait_mcp_enabled / galaxy_api_key_mode / mcp_config_mode; prompt.txt tool names; analysis.json runs[].interface_calls (tools actually called, from traces); evidence runs[].environment.galaxy_server.

| Benchmark | Model | Arm | Galaxy server | Execute MCP enabled | Claude MCP config | API key mode | IWC key mounted | Recorded MCP list | UDT helper in list | Prompt names run_galaxy_udt_and_wait | Runs calling it |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BixBench50 | GPT-5.5 | Galaxy | https://usegalaxy.org | True: 150 | - | read_only_secret_file: 150 | - | not recorded | n/a | 150 | 100 |
| BixBench50 | GPT-5.5 | Code | - | False: 150 | - | not_set: 150 | - | not recorded | n/a | 0 | 0 |
| BixBench50 | GPT-5.6 Luna | Galaxy | https://usegalaxy.org | True: 150 | - | read_only_secret_file: 150 | - | not recorded | n/a | 150 | 59 |
| BixBench50 | GPT-5.6 Luna | Code | - | False: 150 | - | not_set: 150 | - | not recorded | n/a | 0 | 0 |
| BixBench50 | GPT-5.6 Sol | Galaxy | https://usegalaxy.org | True: 150 | - | read_only_secret_file: 150 | - | not recorded | n/a | 150 | 52 |
| BixBench50 | GPT-5.6 Sol | Code | - | False: 150 | - | not_set: 150 | - | not recorded | n/a | 0 | 0 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | https://usegalaxy.org | not recorded: 150 | strict: 150 | read_only_secret_file: 150 | - | not recorded | n/a | 150 | 42 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Code | - | not recorded: 150 | none: 150 | not_set: 150 | - | not recorded | n/a | 0 | 0 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Galaxy | https://usegalaxy.org | True: 150 | - | read_only_secret_file: 150 | - | not recorded | n/a | 150 | 14 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Code | - | False: 150 | - | read_only_secret_file: 150 | - | not recorded | n/a | 0 | 0 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Galaxy | https://usegalaxy.org | True: 300 | - | container_temp_secret_file: 300 | - | not recorded | n/a | 0 | 130 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Code | - | not recorded: 300 | - | not recorded: 300 | - | not recorded | n/a | 0 | 0 |
| CompBio | GPT-5.5 | Galaxy | https://usegalaxy.org | True: 244; not recorded: 56 | - | container_temp_secret_file: 244; not recorded: 56 | - | not recorded | n/a | 0 | 263 |
| CompBio | GPT-5.5 | Code | - | not recorded: 300 | - | not recorded: 300 | - | not recorded | n/a | 0 | 0 |
| CompBio | GPT-5.6 Luna | Galaxy | https://usegalaxy.org | True: 300 | - | container_temp_secret_file: 300 | - | not recorded | n/a | 0 | 176 |
| CompBio | GPT-5.6 Luna | Code | - | not recorded: 300 | - | not recorded: 300 | - | not recorded | n/a | 0 | 0 |
| CompBio | GPT-5.6 Sol | Galaxy | https://usegalaxy.org | True: 270; not recorded: 30 | - | container_temp_secret_file: 270; not recorded: 30 | - | not recorded | n/a | 0 | 239 |
| CompBio | GPT-5.6 Sol | Code | - | not recorded: 300 | - | not recorded: 300 | - | not recorded | n/a | 0 | 0 |
| CompBio | GPT-6 Astra | Code | - | not recorded: 100 | - | not recorded: 100 | - | not recorded | n/a | 0 | 0 |
| IWC | DeepSeek V4 Pro (Codex) | Galaxy | https://usegalaxy.org | not recorded: 30 | - | not recorded: 30 | 30 | yes (7 tools) | 0 | 0 | 0 |
| IWC | DeepSeek V4 Pro (Codex) | Code | - | not recorded: 30 | - | not recorded: 30 | 0 | not recorded | n/a | 0 | 0 |
| IWC | GPT-5.5 | Galaxy | https://usegalaxy.org | not recorded: 30 | - | not recorded: 30 | 30 | yes (7 tools) | 0 | 0 | 0 |
| IWC | GPT-5.5 | Code | - | not recorded: 30 | - | not recorded: 30 | 0 | not recorded | n/a | 0 | 0 |
| IWC | GPT-5.6 Luna | Galaxy | https://usegalaxy.org | not recorded: 30 | - | not recorded: 30 | 30 | yes (7 tools) | 0 | 0 | 0 |
| IWC | GPT-5.6 Luna | Code | - | not recorded: 30 | - | not recorded: 30 | 0 | not recorded | n/a | 0 | 0 |
| IWC | GPT-5.6 Sol | Galaxy | https://usegalaxy.org | not recorded: 30 | - | not recorded: 30 | 30 | yes (7 tools) | 0 | 0 | 0 |
| IWC | GPT-5.6 Sol | Code | - | not recorded: 30 | - | not recorded: 30 | 0 | not recorded | n/a | 0 | 0 |

A recorded list of exposed Galaxy MCP tools exists only for IWC (7 tools: stage_workspace_file, search_galaxy_tools, inspect_galaxy_history, inspect_archive_inventory, inspect_galaxy_tool, run_galaxy_tool_and_wait, wait_for_galaxy_jobs); it omits run_galaxy_udt_and_wait and no IWC run called it. BixBench and CompBio exposure lists are not recorded; Galaxy-arm prompts name run_galaxy_udt_and_wait (BixBench) or permit UDTs (CompBio), and Galaxy-arm traces call it. CompBio Galaxy traces also call peek_galaxy_dataset, which is absent from the IWC list. Galaxy server in every Galaxy-arm run with a recorded server: https://usegalaxy.org (IWC containers also receive IWC_GALAXY_URL, value not recorded). `analysis.json` `galaxy_helpers_exposed` is non-null only for the 240 IWC runs (120 Galaxy lists with 7 tools; 120 empty code lists). Per-configuration counts of runs calling each interface are in the JSON (`q6_tools.rows[].runs_calling_each_interface`).

## Q7. CompBio campaign selection, and BixBench/IWC reruns

Source: Per-run campaign = runs/<campaign>/ directory in run_record.json agent_workspace (CompBio); cross-checked against CompBio/compBio_overview_audit.json score_vectors[].source_campaigns (from paper_site_runs.json roots) and replicates/<campaign>/provenance.tsv source_run_id; BixBench: evidence runs[].iteration_setting and attempt.json experiment/attempt; IWC: codex_invocation.json run_root.

Archive-to-registry check over the 2,400 paired runs: 2,322 identical campaign names and 77 identical after the archive's account redaction. 1 differs: DeepSeek Galaxy r3 `finding-geo-q1`, where the vector uses an `operator_na` final-disposition campaign and the archived trace comes from `finding_geo_strict_retry2`.

| Model | Arm | Rep | Vector (campaign_id) | Score type | Campaigns | Runs from largest | From other campaigns | Outcome-named | Consensus/top10 | Other-replicate-labelled | Account labels (registry) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GPT-5.5 | Galaxy | 1 | galaxy-gpt55 | official_labelled | 8 | 33 | 67 | 19 | 0 | 0 | - |
| GPT-5.5 | Galaxy | 2 | galaxy-gpt55-r2 | official_labelled | 6 | 33 | 67 | 0 | 10 | 0 | [account-A]: 5; [account-B]: 5 |
| GPT-5.5 | Galaxy | 3 | galaxy-gpt55-r3 | predicted | 6 | 47 | 53 | 0 | 3 | 0 | [account-B]: 46; [account-A]: 51 |
| GPT-5.5 | Code | 1 | gpt55-anycode-jul30 | official_labelled | 2 | 99 | 1 | 0 | 0 | n/a | - |
| GPT-5.5 | Code | 2 | gpt55-anycode-r1 | official_labelled | 2 | 90 | 10 | 0 | 10 | n/a | - |
| GPT-5.5 | Code | 3 | gpt55-anycode-r2 | official_labelled | 1 | 100 | 0 | 0 | 0 | n/a | - |
| GPT-5.6 Sol | Galaxy | 1 | sol-galaxy-r1 | official_labelled | 3 | 65 | 35 | 19 | 0 | 0 | - |
| GPT-5.6 Sol | Galaxy | 2 | sol-galaxy-r2 | predicted | 6 | 63 | 37 | 5 | 0 | 0 | - |
| GPT-5.6 Sol | Galaxy | 3 | sol-galaxy-r3 | official_labelled | 6 | 76 | 24 | 5 | 0 | 0 | - |
| GPT-5.6 Sol | Code | 1 | sol-anycode-r1 | official_labelled | 1 | 100 | 0 | 0 | 0 | 0 | - |
| GPT-5.6 Sol | Code | 2 | sol-anycode-r2 | official_labelled | 1 | 100 | 0 | 0 | 0 | 0 | - |
| GPT-5.6 Sol | Code | 3 | sol-anycode-r3 | official_labelled | 2 | 99 | 1 | 0 | 0 | 0 | - |
| DeepSeek V4 Pro 0813 (Codex) | Galaxy | 1 | codex-ds-v4pro-galaxy-r1 | predicted | 3 | 96 | 4 | 0 | 0 | 0 | - |
| DeepSeek V4 Pro 0813 (Codex) | Galaxy | 2 | codex-ds-v4pro-galaxy-r2 | predicted | 2 | 86 | 14 | 0 | 0 | 0 | - |
| DeepSeek V4 Pro 0813 (Codex) | Galaxy | 3 | codex-ds-v4pro-galaxy-r3 | predicted | 4 | 93 | 7 | 0 | 0 | 0 | - |
| DeepSeek V4 Pro 0813 (Codex) | Code | 1 | codex-ds-v4pro-anycode-r1 | predicted | 4 | 92 | 8 | 0 | 0 | 0 | - |
| DeepSeek V4 Pro 0813 (Codex) | Code | 2 | codex-ds-v4pro-anycode-r2 | official_labelled | 5 | 95 | 5 | 0 | 0 | 0 | - |
| DeepSeek V4 Pro 0813 (Codex) | Code | 3 | codex-ds-v4pro-anycode-r3 | official_labelled | 5 | 76 | 24 | 0 | 0 | 0 | - |
| GPT-5.6 Luna | Galaxy | 1 | luna-galaxy-r1 | predicted | 10 | 52 | 48 | 11 | 0 | 1 | [account-B]: 45; [account-A]: 45 |
| GPT-5.6 Luna | Galaxy | 2 | luna-galaxy-r2 | predicted | 7 | 81 | 19 | 17 | 0 | 1 | [account-B]: 3 |
| GPT-5.6 Luna | Galaxy | 3 | luna-galaxy-r3 | predicted | 6 | 88 | 12 | 10 | 0 | 2 | [account-A]: 3 |
| GPT-5.6 Luna | Code | 1 | luna-anycode-r1 | official_labelled | 2 | 99 | 1 | 0 | 0 | 0 | - |
| GPT-5.6 Luna | Code | 2 | luna-anycode-r2 | official_labelled | 3 | 57 | 43 | 0 | 0 | 0 | - |
| GPT-5.6 Luna | Code | 3 | luna-anycode-r3 | predicted | 5 | 94 | 6 | 0 | 0 | 0 | - |
| GPT-6 Astra | Code | 1 | codex_gpt_6_astra | official_labelled | 2 | 98 | 2 | 0 | 0 | 0 | - |

| Arm | Runs from largest campaign | From other campaigns | Outcome-named | Consensus/top10 |
|---|---|---|---|---|
| Galaxy | 813 | 387 | 86 | 13 |
| Code | 1,199 | 101 | 0 | 10 |

CompBio final vectors are composites. 'Largest campaign' is the campaign contributing most items to a vector; other campaigns include recoveries, continuations, completions, retries, repeats and fresh-history reruns. Campaign names containing 'wrong', 'wrongset', 'fastwrong', 'target84' or 'near84' (outcome_named) suggest item selection informed by earlier answers or scores; names containing 'consensus' or 'top10' indicate other selective reruns whose criterion is not stated. The selection rules are not recorded in the archive. Registry campaign names carry two account-like tokens that the archive redacts as [REDACTED ACCOUNT]; they are shown here as [account-A]/[account-B]. Cross-replicate counts compare the _rN token in the campaign name with the archived replicate label and are not computed for open-ended GPT-5.5, whose registry labels are offset (gpt55-anycode-jul30 = R1, gpt55-anycode-r1 = R2, gpt55-anycode-r2 = R3).

Galaxy-arm prompt and harness tokens in CompBio campaign names: older prompt (no `promptv2`) for 79 GPT-5.5 and 81 Sol Galaxy runs. The names also carry `_agents_` (21 GPT-5.5 r2, 24 Sol r2), `noagents`, or `waitagents` (8 GPT-5.5 r3, 1 DeepSeek r3, 44 Luna). These tokens presumably encode the Codex agents/subagent setting, which is not otherwise recorded for CompBio. Per-vector counts are in `q7_campaign_selection.compbio_vectors.rows[].runs_agents_noagents_waitagents`. Code campaign names carry no prompt-version tokens.

BixBench50 iteration settings (evidence `iteration_setting`, `attempt.json` experiment):

| Model | Arm | iteration_setting | experiment | Runs |
|---|---|---|---|---|
| GPT-5.5 | Galaxy | primary | domain_skill_full_rerun_20260714 | 147 |
| GPT-5.5 | Galaxy | primary_submission_order_fix | domain_skill_full_rerun_20260714 | 3 |
| GPT-5.5 | Code | authorized_targeted_replacement | domain_skill_full_rerun_20260714 | 3 |
| GPT-5.5 | Code | primary | domain_skill_full_rerun_20260714 | 147 |
| GPT-5.6 Luna | Galaxy | not recorded | not recorded | 150 |
| GPT-5.6 Luna | Code | not recorded | not recorded | 150 |
| GPT-5.6 Sol | Galaxy | not recorded | not recorded | 150 |
| GPT-5.6 Sol | Code | not recorded | not recorded | 150 |
| DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | primary | claude_ds_v4pro_full_20260716 | 150 |
| DeepSeek V4 Pro (Claude Code, superseded) | Code | primary | claude_ds_v4pro_full_20260716 | 147 |
| DeepSeek V4 Pro (Claude Code, superseded) | Code | primary_replacement_for_invalid_infrastructure_run | claude_ds_v4pro_full_20260716 | 3 |
| DeepSeek V4 Pro (Codex) | Galaxy | history_recovery_rerun | codex_deepseek_v4pro_bix32_history_recovery_20260820 | 3 |
| DeepSeek V4 Pro (Codex) | Galaxy | primary | codex_deepseek_v4pro_formal_20260815 | 146 |
| DeepSeek V4 Pro (Codex) | Galaxy | requested_second_rerun | codex_deepseek_v4pro_bix55q1_r3_second_rerun_20260821 | 1 |
| DeepSeek V4 Pro (Codex) | Code | primary | codex_deepseek_v4pro_formal_20260815 | 150 |

IWC run roots (`codex_invocation.json` run_root); "primary" means a `*-formal` root or the DeepSeek Galaxy main root:

| Model | Arm | Run root | Primary | Runs |
|---|---|---|---|---|
| DeepSeek V4 Pro (Codex) | Galaxy | deepseek-formal | True | 5 |
| DeepSeek V4 Pro (Codex) | Galaxy | deepseek-galaxy-[galaxy-user] | True | 18 |
| DeepSeek V4 Pro (Codex) | Galaxy | deepseek-galaxy-failed-reruns-20260828 | False | 3 |
| DeepSeek V4 Pro (Codex) | Galaxy | galaxy-wf009-diagnostic-reruns-20260828 | False | 1 |
| DeepSeek V4 Pro (Codex) | Galaxy | usage-complete-reruns-20260902 | False | 3 |
| DeepSeek V4 Pro (Codex) | Code | deepseek-formal | True | 29 |
| DeepSeek V4 Pro (Codex) | Code | usage-complete-reruns-20260902 | False | 1 |
| GPT-5.5 | Galaxy | gpt55-formal | True | 28 |
| GPT-5.5 | Galaxy | gpt55-galaxy-failed-reruns-20260828 | False | 1 |
| GPT-5.5 | Galaxy | usage-complete-reruns-20260902 | False | 1 |
| GPT-5.5 | Code | gpt55-formal | True | 29 |
| GPT-5.5 | Code | gpt55-wf006-r1-clean-rerun-20260901 | False | 1 |
| GPT-5.6 Luna | Galaxy | galaxy-missing-artifact-reruns-20260829 | False | 1 |
| GPT-5.6 Luna | Galaxy | galaxy-missing-artifact-reruns-20260829-round2 | False | 2 |
| GPT-5.6 Luna | Galaxy | galaxy-timeout-reruns-12h-20260828 | False | 1 |
| GPT-5.6 Luna | Galaxy | galaxy-wf009-diagnostic-reruns-20260828 | False | 1 |
| GPT-5.6 Luna | Galaxy | luna-formal | True | 21 |
| GPT-5.6 Luna | Galaxy | usage-complete-reruns-20260902 | False | 4 |
| GPT-5.6 Luna | Code | anycode-eligible-reruns-20260829-queue | False | 1 |
| GPT-5.6 Luna | Code | anycode-step-evidence-v1-reruns | False | 4 |
| GPT-5.6 Luna | Code | luna-formal | True | 25 |
| GPT-5.6 Sol | Galaxy | galaxy-missing-artifact-reruns-20260829 | False | 1 |
| GPT-5.6 Sol | Galaxy | galaxy-missing-artifact-reruns-20260830-wf010-round4 | False | 1 |
| GPT-5.6 Sol | Galaxy | galaxy-timeout-reruns-12h-20260828 | False | 1 |
| GPT-5.6 Sol | Galaxy | sol-formal | True | 21 |
| GPT-5.6 Sol | Galaxy | sol-gap-wf002-r2-12h | False | 1 |
| GPT-5.6 Sol | Galaxy | usage-complete-reruns-20260902 | False | 5 |
| GPT-5.6 Sol | Code | anycode-eligible-reruns-20260829-queue | False | 2 |
| GPT-5.6 Sol | Code | anycode-wf011-sol-reruns-20260831-round1 | False | 2 |
| GPT-5.6 Sol | Code | sol-formal | True | 26 |

## Q8. Other differences between arms

| Item | Galaxy arm | Open-ended-code arm | Counts | Source |
|---|---|---|---|---|
| Execution substrate (CompBio) | Docker image galaxy-eval-agent:latest (image_id sha256:57082a89...; docker_cp workspace transport) | host_conda_clone (macOS host conda env compbio-benchmark; no container) | 1,200 Galaxy runs docker per task.json; 1,300 open-ended runs host_conda_clone | task.json execution_backend; docker_invocation.json; conda_invocation.json |
| Execution substrate (IWC) | Docker, same image digest as open-ended; 8 GiB memory, 4 CPUs, pids 512, bridge network; Galaxy key mounted at /run/secrets; IWC_GALAXY_URL set | Docker, same digest and resource limits; no Galaxy key or Galaxy URL | 120 / 120 | run_trace/docker_isolation.json |
| Execution substrate (BixBench50) | Docker images per harness (table Q1) | Same image family; GPT-5.5 open-ended mostly no-static-udt-resolver-20260714 vs Galaxy mostly full-blocking-20260715 | see Q1 | docker_invocation.json image |
| Skills bundled | BixBench: 8 skills incl. galaxy-tool-submission, galaxy-udt-authoring; CompBio: only galaxy-tool-submission, galaxy-udt-authoring (where inventory recorded); IWC: 5 domain skills, rev 03e9f1b9, result_verification excluded | BixBench: same 6 domain skills, '^galaxy-' excluded; CompBio: no skill inventory recorded (prompts of 1,200/1,300 runs allow installed skill instructions; GPT-5.5 replicate-1 campaign named no_project_skills); IWC: identical 5 skills | table q8.skills | skill_inventory.json; IWC codex_invocation.json skills_bundle |
| Local input files (BixBench50 DeepSeek) | No local input files staged for both DeepSeek harnesses (inputs only in Galaxy seed history); GPT Galaxy runs had local inputs | Local inputs staged for all runs | 300/300 DeepSeek Galaxy runs with empty inputs_manifest and prompt "No local input files were staged" | inputs_manifest.json; prompt.txt |
| Galaxy credentials in open-ended arm | API key as read-only secret file / container temp secret | BixBench DeepSeek-via-Codex open-ended runs record galaxy_api_key_mode 'read_only_secret_file' (MCP disabled); other open-ended runs 'not_set' or no record | 150 BixBench DeepSeek-via-Codex open-ended runs | docker_invocation.json galaxy_api_key_mode |
| Network | Unrestricted in BixBench/IWC records; CompBio Galaxy containers list blocked Hugging Face hosts in 291/1,200 runs | BixBench prompts explicitly allow internet access; CompBio DeepSeek/Astra conda runs record an HTTP CONNECT proxy filter blocking Hugging Face in 102 runs; IWC bridge network | table q8.network | docker_invocation.json blocked_hosts; conda_invocation.json blocked_host_suffixes/network_filter_mode; prompt.txt |
| Prompt-required logging (IWC) | All 120 prompts: 'Keep a concise execution log in run_trace/' | 55 prompts require structured run_trace/analysis_steps.jsonl records (exactly the 55 runs with 12 h budgets); 65 have the concise-log line | 55 / 65 | prompt.txt |
| Galaxy history routing tag (CompBio) | history_routing_tags.json applied tag 'training' to some Galaxy histories (verified 2026-08-21..25); purpose not documented | n/a | table q8.routing | run_trace/history_routing_tags.json, history_routing_tags_disabled.json |
| Extra MCP connectors (CompBio Galaxy) | 3 GPT-5.5 and 2 Luna CompBio Galaxy runs called github.* or hugging_face.* MCP tools (connectors present in those runtimes) | No such calls in any benchmark | 5 runs | analysis.json interface_calls |
| Internet in prompt text (BixBench50) | Galaxy prompts do not mention internet access | All 750 code prompts state that internet access may be used | 0 / 750 | prompt.txt |
| Agent harness for superseded DeepSeek (BixBench) | Claude Code, provider deepseek_anthropic_compat, mcp_config_mode 'strict' | Claude Code, mcp_config_mode 'none' | 150 / 150 | docker_invocation.json; provider_config.json |
| Interrupted/resumed or relabelled runs | - | CompBio Astra: 2 runs resumed after host interruption (resume_invocation.json); CompBio DeepSeek: 2 false-positive wall-clock timeouts documented (TIMEOUT_FALSE_POSITIVE.md) | 2 + 2 | run_trace/resume_invocation.json; run_trace/TIMEOUT_FALSE_POSITIVE.md |
| Shared Galaxy histories | 3 BixBench history IDs are each linked to two runs (Sol bix-11-q1 r2/r3; DeepSeek-Claude bix-16-q3 r2/r3 and bix-61-q5 r1/r3) | n/a | 3 | evidence runs[].source_ids |
| Galaxy account identity | Not recorded (history user/username redacted; CompBio seed owners and several campaign names redacted as [REDACTED ACCOUNT]); BixBench seed histories owned by one public Galaxy user; one IWC DeepSeek Galaxy run root is named after that user | n/a | - | history.json; seed_history.json; run_record.json; codex_invocation.json run_root |
| Authentication (IWC) | auth_mode 'chatgpt' for all runs incl. DeepSeek (model_provider deepseek) | same | 240 | codex_invocation.json auth_mode, runtime.model_provider |

Local inputs staged (`inputs_manifest.json`; IWC mounts data read-only at /workspace/data instead and has no manifest):

| Benchmark | Model | Arm | Runs | Manifest present | Runs with local inputs |
|---|---|---|---|---|---|
| BixBench50 | GPT-5.5 | Galaxy | 150 | 150 | 150 |
| BixBench50 | GPT-5.5 | Code | 150 | 150 | 150 |
| BixBench50 | GPT-5.6 Luna | Galaxy | 150 | 150 | 150 |
| BixBench50 | GPT-5.6 Luna | Code | 150 | 150 | 150 |
| BixBench50 | GPT-5.6 Sol | Galaxy | 150 | 150 | 150 |
| BixBench50 | GPT-5.6 Sol | Code | 150 | 150 | 150 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | 150 | 150 | 0 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Code | 150 | 150 | 150 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Galaxy | 150 | 150 | 0 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Code | 150 | 150 | 150 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Galaxy | 300 | 300 | 219 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Code | 300 | 300 | 219 |
| CompBio | GPT-5.5 | Galaxy | 300 | 300 | 219 |
| CompBio | GPT-5.5 | Code | 300 | 300 | 219 |
| CompBio | GPT-5.6 Luna | Galaxy | 300 | 300 | 219 |
| CompBio | GPT-5.6 Luna | Code | 300 | 300 | 219 |
| CompBio | GPT-5.6 Sol | Galaxy | 300 | 300 | 219 |
| CompBio | GPT-5.6 Sol | Code | 300 | 300 | 219 |
| CompBio | GPT-6 Astra | Code | 100 | 100 | 73 |
| IWC | DeepSeek V4 Pro (Codex) | Galaxy | 30 | 0 | 0 |
| IWC | DeepSeek V4 Pro (Codex) | Code | 30 | 0 | 0 |
| IWC | GPT-5.5 | Galaxy | 30 | 0 | 0 |
| IWC | GPT-5.5 | Code | 30 | 0 | 0 |
| IWC | GPT-5.6 Luna | Galaxy | 30 | 0 | 0 |
| IWC | GPT-5.6 Luna | Code | 30 | 0 | 0 |
| IWC | GPT-5.6 Sol | Galaxy | 30 | 0 | 0 |
| IWC | GPT-5.6 Sol | Code | 30 | 0 | 0 |

CompBio Galaxy history routing tag (`history_routing_tags.json`):

| Model | Galaxy runs | Tag 'training' applied | Tag-disabled record |
|---|---|---|---|
| DeepSeek V4 Pro 0813 (Codex) | 300 | 64 | 1 |
| GPT-5.5 | 300 | 146 | 3 |
| GPT-5.6 Luna | 300 | 113 | 189 |
| GPT-5.6 Sol | 300 | 18 | 0 |

Network-related records:

| Benchmark | Model | Arm | Runs | Hugging Face blocked | Conda network filter | IWC network | Prompt mentions internet |
|---|---|---|---|---|---|---|---|
| BixBench50 | GPT-5.5 | Galaxy | 150 | 0 | 0 | - | 0 |
| BixBench50 | GPT-5.5 | Code | 150 | 0 | 0 | - | 150 |
| BixBench50 | GPT-5.6 Luna | Galaxy | 150 | 0 | 0 | - | 0 |
| BixBench50 | GPT-5.6 Luna | Code | 150 | 0 | 0 | - | 150 |
| BixBench50 | GPT-5.6 Sol | Galaxy | 150 | 0 | 0 | - | 0 |
| BixBench50 | GPT-5.6 Sol | Code | 150 | 0 | 0 | - | 150 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | 150 | 0 | 0 | - | 0 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | Code | 150 | 0 | 0 | - | 150 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Galaxy | 150 | 0 | 0 | - | 0 |
| BixBench50 | DeepSeek V4 Pro (Codex) | Code | 150 | 0 | 0 | - | 150 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Galaxy | 300 | 1 | 0 | - | 300 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | Code | 300 | 2 | 2 | - | 300 |
| CompBio | GPT-5.5 | Galaxy | 300 | 22 | 0 | - | 300 |
| CompBio | GPT-5.5 | Code | 300 | 0 | 0 | - | 300 |
| CompBio | GPT-5.6 Luna | Galaxy | 300 | 258 | 0 | - | 300 |
| CompBio | GPT-5.6 Luna | Code | 300 | 0 | 0 | - | 300 |
| CompBio | GPT-5.6 Sol | Galaxy | 300 | 10 | 0 | - | 300 |
| CompBio | GPT-5.6 Sol | Code | 300 | 0 | 0 | - | 300 |
| CompBio | GPT-6 Astra | Code | 100 | 100 | 100 | - | 100 |
| IWC | DeepSeek V4 Pro (Codex) | Galaxy | 30 | 0 | 0 | bridge | 0 |
| IWC | DeepSeek V4 Pro (Codex) | Code | 30 | 0 | 0 | bridge | 0 |
| IWC | GPT-5.5 | Galaxy | 30 | 0 | 0 | bridge | 0 |
| IWC | GPT-5.5 | Code | 30 | 0 | 0 | bridge | 0 |
| IWC | GPT-5.6 Luna | Galaxy | 30 | 0 | 0 | bridge | 0 |
| IWC | GPT-5.6 Luna | Code | 30 | 0 | 0 | bridge | 0 |
| IWC | GPT-5.6 Sol | Galaxy | 30 | 0 | 0 | bridge | 0 |
| IWC | GPT-5.6 Sol | Code | 30 | 0 | 0 | bridge | 0 |

## Not recorded

- BixBench50: per-run time, token and retry budgets (evidence budgets null; no timeout field in invocation records).
- CompBio Galaxy arm: per-run wall-clock budget (task.json timeout_minutes null; prompts state none).
- All benchmarks: token budgets, retry policies and random seeds (seed null in all evidence records).
- Execution start/end for BixBench GPT runs (only workspace-preparation time, Galaxy history creation and usage-write time) and for all CompBio runs (only task creation/preparation and campaign-directory timestamps).
- Runtime model ID and reasoning for 900 CompBio open-ended GPT-5.5/Sol/Luna runs and 86 CompBio Galaxy runs (56 GPT-5.5, 30 Sol): no invocation record.
- Recorded list of exposed Galaxy MCP tools for BixBench50 and CompBio (only IWC records one).
- Codex CLI version for GPT runs outside the codex-0.146.0 image tag / codex_cli_0146 paths; IWC image tag (digest only).
- CompBio open-ended skill inventory (no skill_inventory.json in conda runs).
- Galaxy account(s) used to execute runs (redacted), and the purpose of the CompBio 'training' history routing tag.
- The rule used to select items for CompBio recovery/continuation/retry campaigns (only campaign names are recorded).
- Value of IWC_GALAXY_URL inside IWC containers (variable name recorded; evidence lists https://usegalaxy.org as the Galaxy server).

## Files

- `design_metadata.json`: all tables above, plus IWC per-run budgets (`q4_budgets.iwc_per_run.rows`), the 120 pair details (`q4_budgets.iwc_pair_matching.pairs_detail.rows`), per-campaign CompBio run counts, provenance.tsv summaries and the interface-call counts.
- `per_run_design_metadata.csv`: 4,240 runs with the extracted fields, redacted as described.
