#!/usr/bin/env bash
set -euo pipefail

test ! -e /workspace/private
mkdir -p [REDACTED LOCAL PATH]
# docker cp preserves a remapped host owner. Codex may drop root privileges, so
# grant access only inside this disposable, non-bind-mounted container.
chmod -R a+rwX /workspace /codex_home 2>/dev/null || true

python3 -c 'import base64, os, pathlib; pathlib.Path("[REDACTED LOCAL PATH]").write_bytes(base64.b64decode(os.environ["CODEX_PROMPT_B64"]))'
chmod a+r [REDACTED LOCAL PATH]
unset CODEX_PROMPT_B64
export CODEX_PROMPT_INPUT=[REDACTED LOCAL PATH]

if [[ -n "${GALAXY_API_KEY_B64:-}" ]]; then
  python3 -c 'import base64, os, pathlib; p=pathlib.Path("[REDACTED LOCAL PATH]"); p.write_bytes(base64.b64decode(os.environ["GALAXY_API_KEY_B64"])); p.chmod(0o644)'
  unset GALAXY_API_KEY_B64
  export GALAXY_API_KEY_FILE=[REDACTED LOCAL PATH]
fi

codex exec \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  --cd /workspace \
  --json \
  -o /workspace/answer.txt \
  --model "$CODEX_MODEL_NAME" \
  -c "model_reasoning_effort=\"$CODEX_REASONING_EFFORT_VALUE\"" \
  -c "service_tier=\"$CODEX_SERVICE_TIER_VALUE\"" \
  "$@" \
  < "$CODEX_PROMPT_INPUT" \
  | python3 -c 'from pathlib import Path; import os, sys; p=os.environ.get("GALAXY_API_KEY_FILE"); s=Path(p).read_text().strip() if p and Path(p).exists() else ""; r="[REDACTED_GALAXY_API_KEY]"; [sys.stdout.write(line.replace(s, r) if s else line) for line in sys.stdin]' \
  | tee [REDACTED LOCAL PATH]
