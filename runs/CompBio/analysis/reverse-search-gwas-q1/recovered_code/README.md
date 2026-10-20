# Recovered code

These files preserve uploaded Python/shell script bytes and the executed commands of custom Galaxy jobs. `manifest.json` connects them to the user-supplied model labels, replicates, datasets and jobs, with SHA-256 hashes. `galaxy_jobs.json` preserves the retrieved public job records, excluding account identifier fields. Commands contain Galaxy execution paths and are evidence, not portable launch scripts. Uploaded scripts with no successful consuming command still document an attempted approach.

No recovered code was run for this audit. Full installable XML/YAML tool definitions and execution containers are not necessarily recoverable from job records; do not treat a command snapshot as a complete tool export. Open a history dataset's details/job information in Galaxy to inspect its creating tool and parameters; use the job API URLs in the evidence file for commands and logs.
