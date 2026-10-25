#!/usr/bin/env bash
set -euo pipefail

test ! -e /workspace/private
mkdir -p [REDACTED LOCAL PATH]
# docker cp preserves a remapped host owner. Codex may drop root privileges, so
# grant access only inside this disposable, non-bind-mounted container.
chmod -R a+rwX /workspace /codex_home 2>/dev/null || true
if [[ "${CODEX_SCIENCE_FIRST_MODE:-false}" == "true" && -d /workspace/inputs ]]; then
  chmod -R a-w /workspace/inputs
fi

python3 -c 'import base64, os, pathlib; pathlib.Path("[REDACTED LOCAL PATH]").write_bytes(base64.b64decode(os.environ["CODEX_PROMPT_B64"]))'
chmod a+r [REDACTED LOCAL PATH]
unset CODEX_PROMPT_B64
export CODEX_PROMPT_INPUT=[REDACTED LOCAL PATH]

if [[ -n "${GALAXY_API_KEY_B64:-}" ]]; then
  python3 -c 'import base64, os, pathlib; p=pathlib.Path("[REDACTED LOCAL PATH]"); p.write_bytes(base64.b64decode(os.environ["GALAXY_API_KEY_B64"])); p.chmod(0o644)'
  unset GALAXY_API_KEY_B64
  export GALAXY_API_KEY_FILE=[REDACTED LOCAL PATH]
fi

if [[ -n "${CODEX_PROVIDER_ENV_KEY_NAME:-}" ]]; then
  test -s [REDACTED LOCAL PATH]
  provider_secret="$(< [REDACTED LOCAL PATH]"
  printf -v "$CODEX_PROVIDER_ENV_KEY_NAME" '%s' "$provider_secret"
  export "$CODEX_PROVIDER_ENV_KEY_NAME"
  unset provider_secret
  export CODEX_PROVIDER_KEY_FILE=[REDACTED LOCAL PATH]
fi

CODEX_CONFIG_ARGS=(-c "model_reasoning_effort=\"$CODEX_REASONING_EFFORT_VALUE\"")
if [[ -n "$CODEX_SERVICE_TIER_VALUE" ]]; then
  CODEX_CONFIG_ARGS+=(-c "service_tier=\"$CODEX_SERVICE_TIER_VALUE\"")
fi

codex exec \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  --cd /workspace \
  --json \
  -o /workspace/answer.txt \
  --model "$CODEX_MODEL_NAME" \
  "${CODEX_CONFIG_ARGS[@]}" \
  "$@" \
  < "$CODEX_PROMPT_INPUT" \
  | python3 -c 'from pathlib import Path; import os,sys; pairs=(("GALAXY_API_KEY_FILE","[REDACTED_GALAXY_API_KEY]"),("CODEX_PROVIDER_KEY_FILE","[REDACTED_CODEX_PROVIDER_KEY]")); secrets=[(Path(p).read_text().strip(),r) for n,r in pairs if (p:=os.environ.get(n)) and Path(p).exists()]; [sys.stdout.write(__import__("functools").reduce(lambda text,pair:text.replace(*pair),secrets,line)) for line in sys.stdin]' \
  | tee [REDACTED LOCAL PATH]
