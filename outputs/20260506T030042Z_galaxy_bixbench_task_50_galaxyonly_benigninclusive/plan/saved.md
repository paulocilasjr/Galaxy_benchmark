# BixBench/task_50 Initial Plan

Objective: What is the median saturation value for fungal genes?

Inputs: Animals_Cele.busco.zip, Animals_Cele.faa, Animals_Ggal.busco.zip, Animals_Ggal.faa, Animals_Mmus.busco.zip, Animals_Mmus.faa, Animals_Xlae.busco.zip, Animals_Xlae.faa, Fungi_Ncra.busco.zip, Fungi_Ncra.faa, Fungi_Scer.busco.zip, Fungi_Scer.faa, Fungi_Spom.busco.zip, Fungi_Spom.faa, Fungi_Umay.busco.zip, Fungi_Umay.faa, busco_downloads.zip, eukaryota_odb10.2024-01-08.tar.gz, scogs_animals.zip, scogs_fungi.zip

Plan: upload format-normalized inputs to usegalaxy.org and run Galaxy Text reformatting (awk) for all filtering and scalar computation. For CHIP tasks, use VAF < 0.3, non-reference calls, In_CHIP true, exclude intronic/intergenic/UTR/upstream/downstream annotations, and count ClinVar classifications containing benign, including Likely Benign, as benign classifications. For task 50, upload raw concatenated fungal IQ-TREE reports and parse parsimony-informative-site percentages as saturation values inside Galaxy.

Expected result: one Galaxy awk scalar output preserved as results/galaxy_awk_answer.tsv, then fixed in results/result.json before ground-truth access.

Risks: usegalaxy.org does not expose an xlsx reader, so xlsx-to-TSV conversion is upload preparation only; scientific filters and arithmetic are inside Galaxy.
