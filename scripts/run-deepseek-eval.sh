#!/usr/bin/env bash
set -euo pipefail

# Backward-compatible entry point. The runner supports every configured provider.
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run-live-eval.sh" "$@"
