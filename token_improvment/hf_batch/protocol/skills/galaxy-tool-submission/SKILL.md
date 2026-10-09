---
name: galaxy-tool-submission
description: Use only for Galaxy submissions with nested, repeated, conditional, paired, collection, or reference-selector inputs, or when raw API payload binding is uncertain. Skip simple submissions handled by a validating client.
---

# Galaxy Tool Submission

Use this skill after the scientific tool and parameters have been selected. Build
complex inputs from the selected wrapper's live schema and verify the created job
resolved the intended objects.

## Dataset Inputs

- Wait for uploaded data to reach `ok` with the expected datatype before using
  the final history dataset ID.
- Verify paired mates use distinct dataset IDs and preserve forward/reverse
  order.
- For reference-source conditionals, confirm the job resolved the intended
  history reference or built-in genome rather than a default branch.

## Nested And Repeated Payloads

- Use input format `21.01` for natural nested JSON, repeat lists, and conditional
  objects. Use legacy format only for deliberately flattened keys such as
  `group|field`.
- Do not mix nested repeats or conditionals with legacy formatting; a request
  may succeed while retaining only one repeat or a default branch.
- Include a conditional controller and fields from its active branch. Omit
  inactive branch fields.
- For repeated dataset inputs, use the live repeat names and verify every entry
  and scalar option appears in the resolved job inputs.

## Ordered Inputs

- Treat input order as part of the scientific parameters when a wrapper uses
  positions or repeat order to define a numerator and denominator, target and
  reference, case and control, or factor level 1 and factor level 2.
- Determine that direction from the selected wrapper's live help or schema.
  Do not transfer an ordering convention from another API, package, or wrapper.
- After execution, verify the reported contrast, coefficient, comparison label,
  or documented output direction before assigning signs or directional labels
  to downstream results.

## Collections

- Before submission, verify collection type, element identifiers, order, and
  child dataset IDs. Do not infer paired semantics from names alone.
- Treat output datasets and output collections as different object types. An
  output collection ID is not a child history dataset ID; resolve its elements
  through the collection API before downstream use.
- After submission, verify the job resolved the intended collection or every
  intended member, especially for merge, concatenate, compare, and joint-analysis
  tools.

If the execution client already validates and returns resolved inputs, do not
fetch the same provenance again. Otherwise inspect the created job once and
reject outputs whose resolved datasets, collections, branch, or material scalar
parameters differ from the intended payload.
