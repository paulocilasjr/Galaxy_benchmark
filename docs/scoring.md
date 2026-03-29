# Scoring Model

## Benchmark-Level Formula

`GalaxyAgentScore = 0.5 * outcome + 0.3 * process + 0.2 * robustness`

## Outcome Score

Outcome measures whether the agent got the task right.

- final artifact correctness: `0.25`
- answer or report correctness: `0.10`
- metric target achieved: `0.10`
- completion under budget: `0.05`

## Process Score

Process measures whether the route taken was acceptable.

- workflow or tool selection correctness: `0.10`
- parameter correctness: `0.10`
- dependency handling and polling: `0.05`
- provenance completeness: `0.05`

## Robustness Score

Robustness measures stability across benchmark conditions.

- average prompt-tier score: `0.08`
- worst-case prompt-tier score: `0.04`
- consistency across repeated runs: `0.04`
- recovery after initial failure: `0.04`

## Scoring Rules

- scoring must be deterministic
- scoring functions must be side-effect free
- schema normalization happens before scoring
- scoring consumes structured results and artifacts, not ad hoc string inspection
- process and robustness evidence must be trace-linked
