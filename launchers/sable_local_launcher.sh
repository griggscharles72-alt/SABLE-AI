#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$HOME/sable-agent-run/sable-agent"
cd "$REPO_DIR" || { echo "Repo directory not found: $REPO_DIR"; exit 1; }

if [ "${1:-}" = "--ui" ]; then
  shift
  exec python3 "$REPO_DIR/run_sable.py" --ui "${1:-cli}"
fi

exec python3 "$REPO_DIR/run_sable.py" "$@"
