#!/usr/bin/env bash
set -euo pipefail

HISTORY_ID=$(jq -r '.history_id' run_trace/assigned_history.json)
GALAXY_URL="${GALAXY_URL%/}"
API_KEY="${GALAXY_API_KEY}"
TOOL_ID='toolshed.g2.bx.psu.edu/repos/iuc/dada2_filterandtrim/dada2_filterAndTrim/1.38.0+galaxy1'

mkdir -p /tmp/dada2/paired_collection_responses
mkdir -p /tmp/dada2/paired_filter_responses
: > /tmp/dada2/paired_collection_map.tsv
: > /tmp/dada2/paired_filter_map.tsv
: > /tmp/dada2/paired_filter_jobs.tsv

# Build one paired collection per sample from the original raw forward/reverse
# HDAs, because this version of the filterAndTrim wrapper cannot be submitted
# directly with the nested list:paired input collection.
while IFS=$'\t' read -r sample fwd_raw rev_raw; do
  create_payload="/tmp/dada2/paired_collection_payload_${sample}.json"
  jq -n \
    --arg name "raw_pair_${sample}" \
    --arg history_id "$HISTORY_ID" \
    --arg fwd "$fwd_raw" \
    --arg rev "$rev_raw" \
    '{
      name: $name,
      history_id: $history_id,
      collection_type: "paired",
      element_identifiers: [
        {name: "forward", src: "hda", id: $fwd},
        {name: "reverse", src: "hda", id: $rev}
      ]
    }' > "$create_payload"

  create_resp="/tmp/dada2/paired_collection_responses/${sample}.json"
  curl -sS -X POST \
    -H "x-api-key: ${API_KEY}" \
    -H 'Content-Type: application/json' \
    --data-binary @"$create_payload" \
    "${GALAXY_URL}/api/dataset_collections" > "$create_resp"

  hdca_id=$(jq -r '.id' "$create_resp")
  if [ -z "$hdca_id" ] || [ "$hdca_id" = null ]; then
    echo "Collection creation error for ${sample}:" >&2
    jq . "$create_resp" >&2
    exit 1
  fi
  printf '%s\t%s\n' "$sample" "$hdca_id" >> /tmp/dada2/paired_collection_map.tsv

  filter_payload="/tmp/dada2/paired_filter_payload_${sample}.json"
  jq -n \
    --arg history_id "$HISTORY_ID" \
    --arg tool_id "$TOOL_ID" \
    --arg input_collection "$hdca_id" \
    '{
      history_id: $history_id,
      tool_id: $tool_id,
      inputs: {
        "paired_cond|paired_select": "paired",
        "paired_cond|reads": {src: "hdca", id: $input_collection},
        "trim|truncQ": 2,
        "trim|trimLeft": 0,
        "trim|trimRight": 0,
        "trim|truncLen": 240,
        "filter|maxLen": "",
        "filter|minLen": 20,
        "filter|maxN": 0,
        "filter|minQ": 0,
        "filter|maxEE": 2,
        "seprev_cond|seprev_select": "yes",
        "seprev_cond|trim|truncQ": 2,
        "seprev_cond|trim|trimLeft": 0,
        "seprev_cond|trim|trimRight": 0,
        "seprev_cond|trim|truncLen": 160,
        "seprev_cond|filter|maxLen": "",
        "seprev_cond|filter|minLen": 20,
        "seprev_cond|filter|maxN": 0,
        "seprev_cond|filter|minQ": 0,
        "seprev_cond|filter|maxEE": 2,
        "rmPhiX": true,
        "rmlowcomplex": 0,
        "orientFwd": "",
        "output_statistics": true
      }
    }' > "$filter_payload"

  filter_resp="/tmp/dada2/paired_filter_responses/${sample}.json"
  curl -sS -X POST \
    -H "x-api-key: ${API_KEY}" \
    -H 'Content-Type: application/json' \
    --data-binary @"$filter_payload" \
    "${GALAXY_URL}/api/tools" > "$filter_resp"

  if ! jq -e '.outputs and .jobs' "$filter_resp" >/dev/null; then
    echo "Submission error for paired filter ${sample}:" >&2
    jq . "$filter_resp" >&2
    exit 1
  fi

  fwd_out=$(jq -r '.outputs[] | select(.output_name == "paired_output|__part__|forward") | .id' "$filter_resp")
  rev_out=$(jq -r '.outputs[] | select(.output_name == "paired_output|__part__|reverse") | .id' "$filter_resp")
  outtab=$(jq -r '.outputs[] | select(.output_name == "outtab") | .id' "$filter_resp")
  job_id=$(jq -r '.jobs[0].id' "$filter_resp")
  out_coll=$(jq -r '.output_collections[0].id' "$filter_resp")

  if [ -z "$fwd_out" ] || [ "$fwd_out" = null ] || \
     [ -z "$rev_out" ] || [ "$rev_out" = null ] || \
     [ -z "$job_id" ] || [ "$job_id" = null ]; then
    echo "Missing outputs/job for ${sample}:" >&2
    jq . "$filter_resp" >&2
    exit 1
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$sample" "$fwd_out" "$rev_out" "$outtab" "$job_id" "$out_coll" \
    >> /tmp/dada2/paired_filter_map.tsv
  printf '%s\n' "$job_id" >> /tmp/dada2/paired_filter_jobs.tsv
done < /tmp/dada2/sample_map.tsv

echo "Created $(wc -l < /tmp/dada2/paired_collection_map.tsv) paired collections"
echo "Submitted $(wc -l < /tmp/dada2/paired_filter_map.tsv) paired filter jobs"
echo "Collection map: /tmp/dada2/paired_collection_map.tsv"
echo "Filter map: /tmp/dada2/paired_filter_map.tsv"
echo "Jobs: /tmp/dada2/paired_filter_jobs.tsv"
