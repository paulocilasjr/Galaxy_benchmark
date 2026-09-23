2026-08-28

Assigned Galaxy history: bbd44e69cb8906b501a7a335c9e540c9

Input:
- Collection of Pacbio Data: Galaxy collection 8f829820b253800a, element ERR13917223.

Galaxy analysis:
- Inspected assigned history only.
- MitoHiFi 3.2.3+galaxy2 reference-finder first submission failed because nested API parameters were not passed to Galaxy; no assembly was run from that failed job.
- Resubmitted MitoHiFi reference-finder with flat Galaxy conditional parameters:
  - species: Agrius convolvuli
  - organelle_type: mitochondrion
  - job: bbd44e69cb8906b5d1dea8335e1f1ae0, state ok
  - outputs used: reference FASTA f9cad7b01a472135b6393a6c265fe35d and GenBank f9cad7b01a472135b9e7c46e2373c8fe.
- Ran MitoHiFi assembly in PacBio HiFi mode:
  - input_reads: assigned PacBio collection 8f829820b253800a
  - bloom_filter: 0
  - organism_selection: animal
  - genetic_code: 5 (invertebrate mitochondrial code)
  - optional QC outputs requested: potential_contigs, contigs_circularization, final_mitogenome_alignment
  - job: bbd44e69cb8906b51cd5c4d17c7b24ac, state ok

Assembly evidence:
- Final FASTA dataset: f9cad7b01a472135ca7f71dd66e57c37.
- Contigs stats reported final_mitogenome length 15449 bp, 37 genes, circular True, no frameshift found.

Deliverable:
- Wrote final_answer/mitogenome.fasta.gz from the Galaxy final mitogenome FASTA.
- Final validation: gzip ok; FASTA records=1; length=15449; non-empty sequence; alphabet A/C/G/T/N only.
