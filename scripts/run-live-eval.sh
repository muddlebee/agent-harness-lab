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

load_from_bashrc() {
  local name="$1"
  local value

  if [[ -n "${!name:-}" || ! -f "$HOME/.bashrc" ]]; then
    return
  fi
  value="$(bash -ic "printf %s \"\${$name:-}\"" 2>/dev/null)"
  if [[ -n "$value" ]]; then
    printf -v "$name" '%s' "$value"
    export "$name"
  fi
}

: "${FINANCIAL_AGENT_PROVIDER:=openrouter}"
: "${FINANCIAL_AGENT_MODEL:=deepseek/deepseek-chat}"
load_from_bashrc FINANCIAL_AGENT_API_KEY
: "${FINANCIAL_AGENT_API_KEY:?Set FINANCIAL_AGENT_API_KEY in ~/.bashrc or the current shell.}"
export FINANCIAL_AGENT_PROVIDER FINANCIAL_AGENT_MODEL FINANCIAL_AGENT_API_KEY
inspect_model="$FINANCIAL_AGENT_PROVIDER/$FINANCIAL_AGENT_MODEL"

if [[ -z "${FINANCIAL_AGENT_EVAL_RUN_ID:-}" ]]; then
  FINANCIAL_AGENT_EVAL_RUN_ID="financial-agent-eval-$(date -u +%Y%m%dT%H%M%SZ)-$$"
fi
export FINANCIAL_AGENT_EVAL_RUN_ID

if [[ "${LANGFUSE_TRACING_ENABLED:-false}" == "true" ]]; then
  load_from_bashrc LANGFUSE_PUBLIC_KEY
  load_from_bashrc LANGFUSE_SECRET_KEY
  : "${LANGFUSE_PUBLIC_KEY:?Set LANGFUSE_PUBLIC_KEY in ~/.bashrc or the current shell.}"
  : "${LANGFUSE_SECRET_KEY:?Set LANGFUSE_SECRET_KEY in ~/.bashrc or the current shell.}"
  : "${LANGFUSE_BASE_URL:=https://cloud.langfuse.com}"
  export LANGFUSE_BASE_URL
fi

log_dir="${INSPECT_LOG_DIR:-$repo_root/logs}"
mkdir -p "$log_dir"

args=(
  evals/financial_agent/inspect_task.py@financial_agent_eval
  --model "$inspect_model"
  --max-samples 1
  --log-dir "$log_dir"
  --log-level debug
  --log-level-transcript trace
)

printf 'Langfuse session: %s\n' "$FINANCIAL_AGENT_EVAL_RUN_ID"

if [[ -n "${INSPECT_SAMPLE_ID:-}" ]]; then
  args+=(--sample-id "$INSPECT_SAMPLE_ID")
fi

exec uv run inspect eval "${args[@]}" "$@"
