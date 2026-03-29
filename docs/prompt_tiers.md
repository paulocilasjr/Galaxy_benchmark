# Prompt Tiers

## Purpose

Every task should exist as semantic-equivalent prompt variants so the benchmark can measure prompt robustness rather than a single lucky phrasing.

## Prompt Tiers

- `novice`: vague, natural-language, incomplete, potentially imprecise terminology
- `intermediate`: correct task framing with some constraints but limited parameter detail
- `expert`: tool or workflow hints, critical assumptions, and explicit expected outputs

## Prompt Formats

- `prose`
- `bullets`
- `structured`
- `json_like`

## Prompt Rules

- keep task meaning semantically identical across tiers and formats
- vary wording, structure, explicitness, and detail only
- store templates under `benchmark/prompts/templates/`
- generate deterministic variants under `benchmark/prompts/<tier>/`
