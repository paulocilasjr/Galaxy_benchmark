#!/usr/bin/env bash
set -euo pipefail

HISTORY_ID=$(jq -r '.history_id' run_trace/assigned_history.json)
GALAXY_URL="${GALAXY_URL%/}"
API_KEY="${GALAXY_API_KEY}"
TOOL_ID='toolshed.g2.bx.psu.edu/repos/iuc/dada2_mergepairs/dada2_mergePairs/1.38.0+galaxy1'

mkdir -p /tmp/dada2/merge_paired_responses
: > /tmp/dada2/merge_paired_map.tsv
: > /tmp/dada2/merge_paired_jobs.tsv

while IFS=$'\t' read -r sample fwd_filt rev_filt outtab filter_job out_coll; do
  dada_fwd=$(awk -F'\t' -v s="$sample" '$1==s && $2=="forward"{print $3}' \
    /tmp/dada2/dada_paired_map.tsv)
  dada_rev=$(awk -F'\t' -v s="$sample" '$1==s && $2=="reverse"{print $3}' \
    /tmp/dada2/dada_paired_map.tsv)

  if [ -z "$dada_fwd" ] || [ "$dada_fwd" = null ] || \
     [ -z "$dada_rev" ] || [ "$dada_rev" = null ]; then
    echo "Missing DADA IDs for ${sample}" >&2
    exit 1
  fi

  payload="/tmp/dada2/merge_paired_payload_${sample}.json"
  jq -n \
    --arg history_id "$HISTORY_ID" \
    --arg tool_id "$TOOL_ID" \
    --arg dadaF "$dada_fwd" \
    --arg derepF "$fwd_filt" \
    --arg dadaR "$dada_rev" \
    --arg derepR "$rev_filt" \
    '{
      history_id: $history_id,
      tool_id: $tool_id,
      inputs: {
        dadaF: {src: "hda", id: $dadaF},
        derepF: {src: "hda", id: $derepF},
        dadaR: {src: "hda", id: $dadaR},
        derepR: {src: "hda", id: $derepR},
        minOverlap: 12,
        maxMismatch: 0,
        justConcatenate: false,
        trimOverhang: false,
        output_details: false
      }
    }' > "$payload"

  response="/tmp/dada2/merge_paired_responses/${sample}.json"
  curl -sS -X POST \
    -H "x-api-key: ${API_KEY}" \
    -H 'Content-Type: application/json' \
    --data-binary @"$payload" \
    "${GALAXY_URL}/api/tools" > "$response"

  if ! jq -e '.outputs and .jobs' "$response" >/dev/null; then
    echo "Submission error for ${sample}" >&2
    jq . "$response" >&2
    exit 1
  fi

  outid=$(jq -r '.outputs[] | select(.output_name == "merged") | .id' "$response")
  jobid=$(jq -r '.jobs[0].id' "$response")
  if [ -z "$outid" ] || [ "$outid" = null ] || \
     [ -z "$jobid" ] || [ "$jobid" = null ]; then
    echo "Missing output/job for ${sample}" >&2
    jq . "$response" >&2
    exit 1
  fi

  printf '%s\t%s\t%s\n' "$sample" "$outid" "$jobid" \
    >> /tmp/dada2/merge_paired_map.tsv
  printf '%s\n' "$jobid" >> /tmp/dada2/merge_paired_jobs.tsv
done < /tmp/dada2/paired_filter_map.tsv

echo "Submitted $(wc -l < /tmp/dada2/merge_paired_map.tsv) paired merge jobs"
echo "Map: /tmp/dada2/merge_paired_map.tsv"
echo "Jobs: /tmp/dada2/merge_paired_jobs.tsv"
