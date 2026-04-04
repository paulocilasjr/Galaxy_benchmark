# Evaluation

## Scoring

GalaxyAgentBench uses three components.

- `outcome`: did the agent produce the correct artifacts or reported fields
- `process`: did it choose the right workflow or tool path and handle execution correctly
- `robustness`: did performance hold across prompt levels and recovery conditions

The aggregate score is:

- `0.5 outcome + 0.3 process + 0.2 robustness`

## Failure Labels

Primary failure classes:

- task understanding
- workflow discovery
- tool discovery
- input mapping
- parameter grounding
- execution or polling
- output interpretation
- provenance or reproducibility
- knowledge retrieval
- knowledge adaptation
- unsafe defaulting or unnecessary autonomy

## Reporting

Each run should leave behind:

- a run manifest
- append-only activity and event logs
- result artifacts
- failure evidence when needed
- a score summary

The benchmark is designed to judge the route to the answer, not only the final answer.
