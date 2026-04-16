# Skills Support Spec

Skills are optional procedural supports used in the `galaxy_skills` environment.

Skills may encode:

- tool selection heuristics
- preprocessing heuristics
- parameter defaults
- input/output compatibility rules
- workflow templates
- debugging hints
- common failure patterns

Requirements:

- skills must be versioned
- runs must record which skills were active
- skills should be treated as harness components, not hidden benchmark knowledge
