#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -z "${DEEPSEEK_API_KEY:-}" && -f "$HOME/.bashrc" ]]; then
  DEEPSEEK_API_KEY="$(bash -ic 'printf %s "${DEEPSEEK_API_KEY:-}"' 2>/dev/null)"
  export DEEPSEEK_API_KEY
fi

: "${DEEPSEEK_API_KEY:?Set DEEPSEEK_API_KEY in ~/.bashrc or the current shell.}"
: "${DEEPSEEK_MODEL:=deepseek-chat}"

log_dir="${INSPECT_LOG_DIR:-$repo_root/.inspect-logs}"
mkdir -p "$log_dir"

args=(
  evals/financial_agent/inspect_task.py@financial_agent_eval
  --model "deepseek/$DEEPSEEK_MODEL"
  --max-samples 1
  --log-dir "$log_dir"
  --log-level debug
  --log-level-transcript trace
)

if [[ -n "${INSPECT_SAMPLE_ID:-}" ]]; then
  args+=(--sample-id "$INSPECT_SAMPLE_ID")
fi

exec uv run inspect eval "${args[@]}" "$@"
