#!/bin/sh
# Archive-only build. Requires parent pinned Python dependencies and Node libraries.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$(dirname "$HERE")")
cd "$ROOT"
ANALYSIS_PYTHON=${PYTHON:-python3}
NARRATIVE_NODE=${NODE_BINARY:-node}
NODE_PATH=${NODE_PATH:-$(dirname "$HERE")/node_modules}
MPLCONFIGDIR=${MPLCONFIGDIR:-${TMPDIR:-/tmp}/galaxy-original-layout-mpl}
export NODE_PATH MPLCONFIGDIR
"$ANALYSIS_PYTHON" "$HERE/scripts/accuracy_analysis.py"
"$ANALYSIS_PYTHON" "$HERE/scripts/rigor_analysis.py"
"$ANALYSIS_PYTHON" "$HERE/scripts/token_analysis.py"
"$ANALYSIS_PYTHON" "$HERE/scripts/make_figures.py"
"$NARRATIVE_NODE" "$HERE/scripts/build_source_data.mjs"
"$NARRATIVE_NODE" "$(dirname "$HERE")/build_docx.js" "$HERE" "$HERE/Galaxy_agents_original_layout_manuscript.docx"
"$ANALYSIS_PYTHON" "$HERE/scripts/validate_package.py"
