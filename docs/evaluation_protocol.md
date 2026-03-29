# Evaluation Protocol

## Construction Phases

1. build a balanced task set across the benchmark families
2. author novice, intermediate, and expert prompts with multiple formats
3. run access-mode and knowledge-condition ablations
4. repeat stochastic conditions at least three times

## Minimal Publishable v1

- 24 tasks
- novice, intermediate, and expert prompts
- at least two prompt formats
- UI-only, API-only, and one MCP-enabled condition
- knowledge on/off condition for GTN or IWC grounded tasks

## Reported Metrics

- mean score
- worst-case score
- variance
- pass@1
- pass@3
- recovery rate after first failure
