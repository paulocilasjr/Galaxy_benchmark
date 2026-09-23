# IWC Recovery Summary

The source workbook was matched to all task-scoped audit packages. Retrieval was read-only and preserved source URLs, retrieval timestamps, local paths, byte hashes, and explicit unavailable/metadata-only states.

- Workbook rows matched: **240**.
- Task packages: **10**.
- Distinct analytical Galaxy jobs: **1352**.
- Fully detailed Galaxy histories: **118**.
- Metadata-only Galaxy histories: **2**.
- Selected text outputs retained: **1278**.
- Outputs skipped because binary, oversized, or otherwise ineligible: **190**.

All source manifests record `tls_certificate_verified: false` for this collection because the environment's CA certificate failed Python verification. Hashes authenticate retained local bytes, not remote-server identity.
