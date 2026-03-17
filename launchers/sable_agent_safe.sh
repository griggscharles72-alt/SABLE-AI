#!/usr/bin/env bash
set -u
set -o pipefail

REPO_DIR="$HOME/sable-agent-run/sable-agent"
LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"

PROFILE="${1:-fast}"
GOAL="${2:-Create a roadmap for this repo.}"
LOG_FILE="$LOG_DIR/sable_agent_safe_$(date +%Y%m%d_%H%M%S).log"

cd "$REPO_DIR" || { echo "Repo directory not found: $REPO_DIR"; exit 1; }

echo "============================================================" | tee "$LOG_FILE"
echo "SABLE SAFE AGENT RUN" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "Profile : $PROFILE" | tee -a "$LOG_FILE"
echo "Goal    : $GOAL" | tee -a "$LOG_FILE"
echo "Log     : $LOG_FILE" | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

python3 run_sable.py agent.run "{\"goal\":\"$GOAL\",\"profile\":\"$PROFILE\"}" | tee -a "$LOG_FILE"
RC=${PIPESTATUS[0]}

echo | tee -a "$LOG_FILE"
echo "Exit code: $RC" | tee -a "$LOG_FILE"
echo "Latest markdown artifact: $REPO_DIR/output/agent_run_latest.md" | tee -a "$LOG_FILE"
echo "Latest json artifact    : $REPO_DIR/output/agent_run_latest.json" | tee -a "$LOG_FILE"

exit "$RC"
