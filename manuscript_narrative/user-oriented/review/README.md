# Expert-review packets

`make_review_packets.py` prepares the material for Supplementary Note 1, section 4: blinded expert review of archived runs and human verification of the AI-assisted trace audit. **Status: packets generated; no review has been performed.**

## Where the packets are

The packets are written **outside this repository**, by default to `<repository parent>/Galaxy_benchmark_review_packets/user_oriented/`. Each packet holds a run's submitted answer, and the sampling design says which replicate sets were all correct, so together they reveal benchmark references. That includes the private CompBioBench key. Agents are run from this repository, so the script refuses to write packets inside it. This folder keeps only material that does not reveal answers:

| File | Content |
|---|---|
| `sampling_design.csv` | Every replicate set in the primary population (four Codex configurations; nine IWC tasks). Gives its stratum, the stratum size, the number selected, the inclusion probability and whether it was selected. |
| `audit_sample.csv` | The audited task cases: whether each was drawn in the random 20% or is Galaxy-attributed (primary cause C4 or tagged as a platform defect), with its inclusion probability. |
| `packet_manifest.json` | Seed, counts and the SHA-256 of every file written outside the repository. |

## Sample (seed 20261002)

- **Run review:** 220 replicate sets (660 runs in 95 task folders).
  - All 168 discordant sets: BixBench-Verified-50 34, CompBioBench 119, IWC 15.
  - Up to five concordant sets per benchmark × arm × concordant stratum (all of them when a stratum is smaller): all correct or none correct; for IWC, mean output agreement at or above 0.95, or below. The IWC low-agreement stratum has two Galaxy sets and no code sets.
  - A pilot of 20 discordant runs (10 per arm) checks whether reviewers can guess the arm.
  - Use `--concordant-per-stratum` to change the concordant sample.
- **Audit verification:** 30 task cases, the random 20% of the 93 cases plus all 15 Galaxy-attributed cases.

## What reviewers see

- **Task folder** (`reviewer/T##/`):
  - the task as given to the agent, without the run-condition block;
  - a rating rubric and a rating form;
  - every selected run in random order under a random identifier.
- **Run entry:**
  - the submitted answer and the names and hashes of deliverable files;
  - each recorded analysis step as an executed command line with its status and truncated output, in the same layout for both arms.
- **What is removed:** directory paths are reduced to file names; identifiers and platform or model words are masked.
- **What is never shown:** evaluator scores, references, arm labels, model names and run identifiers.
- **Arm guess:** provenance structure can still reveal the arm, so reviewers record a guess and a confidence.

Audit packets (`reviewer/audit/C##.md`) name the runs and their job ledgers but do not give the AI-assisted assignment or its narrative. For CompBioBench cases, per-run correctness is withheld until the maintainers permit its release.

## What the coordinator does

`coordinator/README.md`, written beside the packets, describes:

- the pilot;
- two independent reviewers per task, with a third to resolve disagreements;
- the stage-2 reference reveal, excluding CompBioBench references until their release is permitted;
- inverse-probability weighting;
- reporting kappa, audit agreement and arm-guess accuracy.

`coordinator/run_key.csv` and `coordinator/audit_key.csv` undo the blinding and must not reach reviewers.
