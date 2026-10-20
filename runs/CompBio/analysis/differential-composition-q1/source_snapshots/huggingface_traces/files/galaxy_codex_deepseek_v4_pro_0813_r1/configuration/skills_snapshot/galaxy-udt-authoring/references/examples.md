# Examples

These are optional implementation examples, not required steps for every UDT.

## RDS And S4 Inspection

Use the validated image below when a UDT needs R, S4, or sparse `Matrix`
support:

```text
quay.io/chiujunhao24/udt:rds-sparse-r4.5.3-matrix1.7.5-r1
```

Stage `scripts/inspect_rds.R` as a typed script input. First produce a bounded
JSON structure report without choosing a metadata member:

```sh
Rscript "$(inputs.script.path)" \
  "$(inputs.input.path)" \
  rds_report.json \
  metadata.tsv
```

Inspect `rds_report.json`. If it identifies a tabular member needed by the
analysis, run the script again with that exact member name:

```sh
Rscript "$(inputs.script.path)" \
  "$(inputs.input.path)" \
  rds_report.json \
  metadata.tsv \
  meta.data
```

Declare both outputs with `from_work_dir`. The first run records that metadata
extraction was not requested; the second exports the selected table with a
`row_id` column. This example inspects what the object contains. It does not
authorize inventing missing annotations or replacing source metadata with an
expression-derived classifier.
