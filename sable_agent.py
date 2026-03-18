#!/usr/bin/env python3
"""
SABLE Agent – Full Runtime + Reflection + Safe Artifacts
- Multi-artifact grounding: workspace + repo files
- Memory persistence with timestamps
- JSON + Markdown artifact output
- Dangerous command validation
- Fallback deterministic plan if AI backend unavailable
"""

import json, re
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

STATE_DIR = Path("state")
WORKSPACE_DIR = Path("workspace")
OUTPUT_JSON = STATE_DIR / "agent_run_latest.json"
OUTPUT_MD = STATE_DIR / "agent_run_latest.md"
MEMORY_JSON = STATE_DIR / "agent_memory.json"

DANGEROUS_PATTERNS = [
    r"\bsudo\s+rm\b", r"\brm\s+-rf\b", r"\bdd\b", r"\bmkfs\b",
    r"\bshutdown\b", r"\breboot\b", r"\bpoweroff\b", r"\bkillall\b",
    r"\bpkill\b", r"\bsystemctl\s+stop\b"
]

def read_json(path: str, default=None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def utc_now() -> str:
    return datetime.utcnow().isoformat() + "+00:00"

def append_run(run_entry: dict) -> dict:
    memory = read_json(str(MEMORY_JSON), default={"runs": []})
    if "runs" not in memory or not isinstance(memory["runs"], list):
        memory["runs"] = []
    if "timestamp" not in run_entry:
        run_entry["timestamp"] = utc_now()
    memory["runs"].append(run_entry)
    write_json(MEMORY_JSON, memory)
    return memory

def reflect_latest() -> dict:
    memory = read_json(str(MEMORY_JSON), default={"runs": []})
    runs = memory.get("runs", [])
    return runs[-1] if runs else {}

def memory_status() -> dict:
    memory = read_json(str(MEMORY_JSON), default={"runs": []})
    return {"runs": len(memory.get("runs", []))}

def safe_artifact_write(data: Dict[str, Any]):
    STATE_DIR.mkdir(exist_ok=True)
    write_json(OUTPUT_JSON, data)
    md_content = f"# Agent Run Artifact\n\n**Goal:** {data.get('goal')}\n\n**Summary:** {data.get('summary')}\n\n**Plan:**\n"
    for step in data.get("plan", []):
        md_content += f"- {step}\n"
    md_content += "\n**Files:**\n"
    for f in data.get("files", []):
        md_content += f"- {f}\n"
    md_content += f"\n**Timestamp:** {data.get('timestamp')}\n"
    OUTPUT_MD.write_text(md_content, encoding="utf-8")

def index_workspace():
    return [str(p) for p in WORKSPACE_DIR.glob("*")]

def list_repo_files(path: str) -> List[str]:
    return [str(p) for p in Path(path).rglob("*") if p.is_file()]

def fallback_plan(goal: str) -> dict:
    files = list(set(index_workspace() + list_repo_files(".")))
    return {
        "ok": True,
        "goal": goal,
        "summary": "Fallback deterministic plan executed.",
        "plan": ["Ensure runtime stability", "Use only verified repo files", "Reject unsafe commands"],
        "files": files,
        "timestamp": utc_now()
    }

def query_ai(goal: str, profile: str, files: List[str]) -> dict:
    installed_models = ["qwen2.5-coder:7b", "llama3.2:1b"]
    return {
        "ok": False,
        "backend": "ollama",
        "model": profile,
        "prompt": goal,
        "error": "model_not_installed",
        "installed_models": installed_models,
        "timestamp": utc_now()
    }

def run(goal: str, profile: str = "fast") -> dict:
    try:
        files_indexed = index_workspace()
        repo_files = list_repo_files(".")
        artifact = query_ai(goal, profile, repo_files)
        if any(re.search(pat, json.dumps(artifact)) for pat in DANGEROUS_PATTERNS):
            artifact = {"ok": False, "error": "dangerous patterns detected; artifact blocked."}
        safe_artifact_write(artifact)
        append_run(artifact)
        return artifact
    except Exception:
        fallback = fallback_plan(goal)
        safe_artifact_write(fallback)
        append_run(fallback)
        return fallback

if __name__ == "__main__":
    goal = "Create a grounded roadmap for this repo"
    artifact = run(goal, profile="fast")
    print(json.dumps(artifact, indent=2))
