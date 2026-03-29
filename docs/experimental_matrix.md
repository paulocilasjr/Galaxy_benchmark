# Experimental Matrix

## Independent Axes

### Agent Type

- external general agent
- external general agent with Galaxy wrapper
- internal Galaxy-connected agent
- internal Galaxy-connected agent with MCP

### Access Mode

- browser/UI only
- API/BioBlend only
- hybrid UI + API
- MCP-exposed tools, resources, and prompts

### Knowledge Condition

- prompt only
- raw web
- GTN
- IWC
- GTN + IWC
- GTN + IWC via MCP

## Benchmark Hypotheses

- `H1`: structured Galaxy access improves correctness and recovery
- `H2`: prompt tier and format materially affect performance
- `H3`: GTN and IWC help only when the agent adapts the retrieved material correctly
- `H4`: internal-vs-external gains should be decomposed into access, grounding, state visibility, and retry quality
