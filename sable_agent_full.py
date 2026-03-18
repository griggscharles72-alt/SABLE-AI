#!/usr/bin/env python3
"""
SABLE Agent – Real Ollama Runtime
- Single real backend: workspace/ollama_backend.py
- Real goal handoff
- Memory persistence
- JSON + Markdown artifacts
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.resolve()
WORKSPACE_DIR = BASE_DIR / "workspace"
STATE_DIR = BASE_DIR / "state"
OUTPUT_DIR = BASE_DIR / "output"

MEMORY_JSON = STATE_DIR / "agent_memory.json"
OUTPUT_JSON = OUTPUT_DIR / "agent_run_latest.json"
OUTPUT_MD = OUTPUT_DIR / "agent_run_latest.md"
BACKEND_PATH = WORKSPACE_DIR / "ollama_backend.py"

STATE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def append_run(run_entry: dict) -> dict:
    memory = read_json(MEMORY_JSON, default={"runs": []})
    if "runs" not in memory or not isinstance(memory["runs"], list):
        memory = {"runs": []}
    if "timestamp" not in run_entry:
        run_entry["timestamp"] = utc_now()
    memory["runs"].append(run_entry)
    write_json(MEMORY_JSON, memory)
    return {"runs": len(memory["runs"])}

def list_workspace_files():
    files = []
    for path in sorted(WORKSPACE_DIR.rglob("*")):
        if path.is_file():
            files.append(str(path.relative_to(BASE_DIR)))
    return files

def run_ollama_backend(goal: str) -> dict:
    if not BACKEND_PATH.exists():
        return {
            "ok": False,
            "backend": "ollama",
            "error": f"missing backend: {BACKEND_PATH}",
            "timestamp": utc_now()
        }

    result = subprocess.run(
        [sys.executable, str(BACKEND_PATH), goal],
        capture_output=True,
        text=True
    )

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()

    if not stdout:
        return {
            "ok": False,
            "backend": "ollama",
            "error": stderr or "empty backend output",
            "timestamp": utc_now()
        }

    try:
        payload = json.loads(stdout)
    except Exception:
        payload = {
            "ok": False,
            "backend": "ollama",
            "error": "backend did not return valid json",
            "raw_stdout": stdout,
            "raw_stderr": stderr,
            "timestamp": utc_now()
        }

    if stderr and "stderr" not in payload:
        payload["stderr"] = stderr

    return payload

def main():
    goal = " ".join(sys.argv[1:]).strip() or "No goal specified"
    backend_result = run_ollama_backend(goal)

    artifact = {
        "ok": bool(backend_result.get("ok")),
        "goal": goal,
        "summary": backend_result.get("response", "")[:500],
        "model": backend_result.get("model"),
        "files": list_workspace_files(),
        "artifacts": {
            "ollama_backend": backend_result
        },
        "timestamp": utc_now()
    }

    artifact["memory"] = append_run({
        "goal": goal,
        "ok": artifact["ok"],
        "model": artifact.get("model"),
        "conversation_json": backend_result.get("conversation_json"),
        "conversation_md": backend_result.get("conversation_md")
    })

    write_json(OUTPUT_JSON, artifact)

    md = (
        "# SABLE Agent Run\n\n"
        f"**Timestamp:** {artifact['timestamp']}\n\n"
        f"**Goal:** {goal}\n\n"
        f"**OK:** {artifact['ok']}\n\n"
        f"**Model:** {artifact.get('model')}\n\n"
        "## Response\n\n"
        f"{backend_result.get('response', '')}\n\n"
        "## Workspace Files\n\n" +
        "\n".join(f"- {item}" for item in artifact["files"]) +
        "\n\n## Conversation Logs\n\n"
        f"- JSON: {backend_result.get('conversation_json')}\n"
        f"- Markdown: {backend_result.get('conversation_md')}\n"
    )
    OUTPUT_MD.write_text(md, encoding="utf-8")

    print(json.dumps(artifact, indent=2))

if __name__ == "__main__":
    main()
