# Prompt Authoring Guide

Each task must have three prompt variants:
- `vague`
- `specific`
- `very_specific`

These are different formulations of the same underlying task.

Definitions:
- `vague`: novice-like, underspecified
- `specific`: intermediate, goal-driven
- `very_specific`: expert-like, explicit tool/method guidance

Prompt authoring rules:
1. Preserve the same biomedical objective across all three prompts
2. Do not change the ground truth
3. Do not introduce extra subgoals in only one prompt
4. Make specificity the only controlled difference

See `examples/prompts.example.json`.
