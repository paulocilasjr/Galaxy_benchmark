# Outputs

`outputs/` is the only writable destination during benchmark execution.

## v0.3 Run Layout

Each run should create:

```text
outputs/<timestamp>_<level>_<experiment>/
|-- plan/
|-- reasoning/
|-- errors/
|-- traces/
|-- evaluations/
`-- results/
```

## Policy

- keep this directory tracked as a placeholder
- do not commit live run artifacts in publication or blind-release branches
- never overwrite a previous run directory
- preserve attempt versions rather than replacing old files
