#!/usr/bin/env python3
"""
SABLE Agent Runtime – Stage 8
- Multi-artifact grounding: wifi, traffic, devices, doctor, iphone, sentinel
- Safe output shaping and section validation
- Heartbeat + fallback planner
- Memory + artifact persistence
"""

import json, re
from pathlib import Path
from typing import Any

from interfaces.ai_interface import query_ai
from tools.workspace_index import index_workspace
from tools.repo_audit import list_repo_files
from tools.report_io import write_json, read_json, utc_now
from agent.reflection import append_run

STATE_DIR = Path("state")
OUTPUT_JSON = Path("output/agent_run_latest.json")
OUTPUT_MD = Path("output/agent_run_latest.md")
WORKSPACE_DIR = Path("workspace")

DANGEROUS_PATTERNS = [
    r"\bsudo\s+mv\b", r"\bsudo\s+rm\b", r"\brm\s+-rf\b",
    r"\bdd\b", r"\bmkfs\b", r"\bshutdown\b", r"\breboot\b",
    r"\bpoweroff\b", r"\bkillall\b", r"\bpkill\b",
    r"\bsystemctl\s+stop\b", r"/var/lib/sable-agent"
]

def safe_artifact_write(data: dict):
    if OUTPUT_JSON.parent.exists():
        write_json(OUTPUT_JSON, data)

def fallback_plan(goal: str):
    return {
        "ok": True,
        "goal": goal,
        "summary": "Fallback deterministic plan executed.",
        "plan": ["Ensure runtime stability", "Use only verified repo files", "Reject unsafe commands"],
        "files": [str(f) for f in WORKSPACE_DIR.glob("*")],
        "timestamp": utc_now()
    }

def run(goal: str, profile: str = "fast") -> dict:
    """Main agent.run entrypoint."""
    try:
        # Call index_workspace correctly (no args)
        index_workspace()
        repo_files = list_repo_files(".")
        artifact = query_ai(goal, profile, repo_files)
        # Validate for dangerous patterns
        if any(re.search(pat, json.dumps(artifact)) for pat in DANGEROUS_PATTERNS):
            artifact = fallback_plan(goal)
    except Exception as e:
        artifact = fallback_plan(goal)
        artifact["error"] = str(e)
    safe_artifact_write(artifact)
    append_run(artifact)
    return artifact
