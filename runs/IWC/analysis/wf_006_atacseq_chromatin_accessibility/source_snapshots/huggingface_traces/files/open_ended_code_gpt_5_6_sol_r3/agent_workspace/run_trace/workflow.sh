#!/usr/bin/env bash
set -euo pipefail

export PATH=/opt/conda/envs/atac/bin:/opt/conda/bin:/usr/bin:/bin

workspace=/workspace
read1="$workspace/data/inputs/pe_fastq_input/srr891269/forward/forward.fastqsanger.gz"
read2="$workspace/data/inputs/pe_fastq_input/srr891269/reverse/reverse.fastqsanger.gz"
index="$workspace/work/reference/hg19"
trim1="$workspace/work/trimmed_R1.fastq.gz"
trim2="$workspace/work/trimmed_R2.fastq.gz"

if [[ ! -s "$trim1" || ! -s "$trim2" || ! -s "$workspace/run_trace/fastp.json" ]]; then
  fastp \
    --in1 "$read1" \
    --in2 "$read2" \
    --out1 "$trim1" \
    --out2 "$trim2" \
    --detect_adapter_for_pe \
    --qualified_quality_phred 20 \
    --unqualified_percent_limit 70 \
    --length_required 15 \
    --thread 8 \
    --json "$workspace/run_trace/fastp.json" \
    --html "$workspace/work/fastp.html" \
    2> "$workspace/run_trace/fastp.log"
fi

bowtie2 \
  --very-sensitive \
  --no-mixed \
  --no-discordant \
  --no-unal \
  --maxins 2000 \
  --threads 8 \
  -x "$index" \
  -1 "$trim1" \
  -2 "$trim2" \
  2> "$workspace/run_trace/bowtie2.log" \
  | samtools view -u - \
  | samtools sort -n -@ 1 -m 256M -T "$workspace/work/name_sort" -o "$workspace/work/aligned.name.bam" -

/opt/conda/bin/python "$workspace/run_trace/pair_filter.py" \
  "$workspace/work/aligned.name.bam" \
  "$workspace/work/filtered.name.bam" \
  "$workspace/run_trace/pair_filter.json" \
  --min-mapq 30 \
  --mitochondrial-contig chrM

samtools fixmate -m -@ 4 \
  "$workspace/work/filtered.name.bam" \
  "$workspace/work/filtered.fixmate.bam"

samtools sort -@ 2 -m 512M -T "$workspace/work/coordinate_sort" \
  -o "$workspace/work/filtered.coordinate.bam" \
  "$workspace/work/filtered.fixmate.bam"

samtools markdup -r -s -@ 4 \
  -f "$workspace/run_trace/markdup.log" \
  "$workspace/work/filtered.coordinate.bam" \
  "$workspace/work/filtered.dedup.bam"
samtools index -@ 4 "$workspace/work/filtered.dedup.bam"
samtools flagstat -@ 4 "$workspace/work/filtered.dedup.bam" \
  > "$workspace/run_trace/final_flagstat.txt"

mkdir -p "$workspace/work/macs2"
macs2 callpeak \
  --treatment "$workspace/work/filtered.dedup.bam" \
  --format BAMPE \
  --gsize hs \
  --name atac \
  --outdir "$workspace/work/macs2" \
  --qvalue 0.05 \
  --keep-dup all \
  > "$workspace/run_trace/macs2.log" 2>&1

mkdir -p "$workspace/final_answer"
cut -f 1-3 "$workspace/work/macs2/atac_peaks.narrowPeak" \
  > "$workspace/final_answer/peaks.bed"
