#!/bin/sh
# Rebuild both narrative manuscripts from the archived evidence: figures, Source Data, numbers, Supplementary Tables
# and the .docx files. Run from anywhere; paths are resolved from this script.
#
#   python3.12 -m venv .venv-narrative && .venv-narrative/bin/pip install -r manuscript/manuscript_narrative/requirements.txt
#   (cd manuscript_narrative && npm install)
#   PYTHON=.venv-narrative/bin/python sh manuscript/manuscript_narrative/build_all.sh
#
# No agent code is run and no server is contacted. CompBioBench grades are read from the archived on-demand Source Data
# (manuscript/manuscript_material/on_demand/Source_Data_OD_Fig4.xlsx); regenerating those grades needs the private reference key
# (COMPBIO_KEY_DIR; see manuscript/manuscript_material/on_demand/README.md). The call and design tables under derived/ are archived
# outputs; their extraction scripts need the raw run snapshots and are not re-run here.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$(dirname "$HERE")")
cd "$ROOT"
PY=${PYTHON:-python3}
NARRATIVE_NODE=${NODE_BINARY:-node}
NODE_PATH=${NODE_PATH:-$HERE/node_modules}
export NODE_PATH

"$PY" manuscript/manuscript_narrative/user-oriented/scripts/make_figures.py
"$PY" manuscript/manuscript_narrative/galaxy-oriented/scripts/make_figures.py
"$PY" manuscript/manuscript_narrative/scripts/make_supplement.py
"$PY" manuscript/manuscript_narrative/galaxy-oriented/conformance/build_fixtures.py
"$PY" manuscript/manuscript_narrative/galaxy-oriented/conformance/selftest.py

"$NARRATIVE_NODE" manuscript/manuscript_narrative/build_docx.js manuscript/manuscript_narrative/user-oriented \
  manuscript/manuscript_narrative/user-oriented/Galaxy_agents_user_oriented_manuscript.docx
"$NARRATIVE_NODE" manuscript/manuscript_narrative/build_docx.js manuscript/manuscript_narrative/user-oriented \
  manuscript/manuscript_narrative/user-oriented/supplementary/Supplementary_Note_1_prospective_validation.docx \
  supplementary/Supplementary_Note_1_prospective_validation.md
"$NARRATIVE_NODE" manuscript/manuscript_narrative/build_docx.js manuscript/manuscript_narrative/galaxy-oriented \
  manuscript/manuscript_narrative/galaxy-oriented/Galaxy_agents_workbench_oriented_manuscript.docx
"$NARRATIVE_NODE" manuscript/manuscript_narrative/build_docx.js manuscript/manuscript_narrative/galaxy-oriented \
  manuscript/manuscript_narrative/galaxy-oriented/supplementary/Supplementary_Note_1_interventions_and_conformance.docx \
  supplementary/Supplementary_Note_1_interventions_and_conformance.md

"$PY" manuscript/manuscript_narrative/scripts/validate_package.py
