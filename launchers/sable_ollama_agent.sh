#!/usr/bin/env bash
set -euo pipefail
BASE="$HOME/sable-agent-run/sable-agent"
cd "$BASE"
python3 "$BASE/sable_agent_full.py" "${*:-Say hello from the real Ollama backend}"
