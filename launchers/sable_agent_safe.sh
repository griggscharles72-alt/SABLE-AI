#!/usr/bin/env bash
set -u
set -o pipefail

REPO_DIR="$HOME/sable-agent-run/sable-agent"
LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"

PROFILE="${1:-fast}"
GOAL="${2:-Create a roadmap for this repo.}"
LOG_FILE="$LOG_DIR/sable_agent_safe_$(date +%Y%m%d_%H%M%S).log"
TMP_OUT="$(mktemp)"

cleanup() {
  rm -f "$TMP_OUT"
}
trap cleanup EXIT

cd "$REPO_DIR" || { echo "Repo directory not found: $REPO_DIR"; exit 1; }

{
  echo "============================================================"
  echo "SABLE SAFE AGENT RUN"
  echo "============================================================"
  echo "Profile : $PROFILE"
  echo "Goal    : $GOAL"
  echo "Log     : $LOG_FILE"
  echo
} | tee "$LOG_FILE"

python3 run_sable.py agent.run "{\"goal\":\"$GOAL\",\"profile\":\"$PROFILE\"}" >"$TMP_OUT" 2>&1 &
AGENT_PID=$!

while kill -0 "$AGENT_PID" 2>/dev/null; do
  TS="$(date -Iseconds)"
  echo "[$TS] heartbeat: agent.run still executing..." | tee -a "$LOG_FILE"
  sleep 10
done

wait "$AGENT_PID"
RC=$?

cat "$TMP_OUT" | tee -a "$LOG_FILE"

LOGICAL_RC=0
if grep -q '"ok": false' "$TMP_OUT"; then
  LOGICAL_RC=1
fi

FINAL_RC="$RC"
if [ "$LOGICAL_RC" -ne 0 ]; then
  FINAL_RC="$LOGICAL_RC"
fi

{
  echo
  echo "Process exit code : $RC"
  echo "Logical exit code : $LOGICAL_RC"
  echo "Final exit code   : $FINAL_RC"
  echo "Latest markdown artifact: $REPO_DIR/output/agent_run_latest.md"
  echo "Latest json artifact    : $REPO_DIR/output/agent_run_latest.json"
} | tee -a "$LOG_FILE"

exit "$FINAL_RC"
