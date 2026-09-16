# Recovered code and commands

`manifest.json` links each uploaded Python script or recorded command to its run index, dataset/job ID and SHA-256 hash. Runs 0–2 are Codex ChatGPT-5.5, 3–5 Codex GPT-5.6 Sol, 6–8 Codex + DeepSeek-v4-pro-0813 and 9–11 Codex GPT-5.6 Luna. Replicate = run index modulo 3 + 1.

There are four uploaded script artifacts, representing two distinct programs. The three r2 copies are byte-identical despite differing custom tool versions. The successful representative is r1_h1.py, also provided as ../ccre_query.py. Script files were preserved without executing them.

`.sh` files are recorded commands with Galaxy execution paths, not portable launchers or complete installable tool definitions. Standard Galaxy tools may require no agent-generated source code. `galaxy_jobs.json` retains public creating-job records with account identifier fields omitted. Inspect tool parameters and command lines in the job ledgers or via their Galaxy job API links; the Galaxy dataset details panel also links to the creating tool/job information.
