#!/usr/bin/env python3
import json
from pathlib import Path

from interfaces.ai_interface import query_ai
from tools.workspace_index import index_workspace
from tools.report_io import write_json, utc_now
from agent.reflection import append_run

PROFILE_PATH = Path("config/model_profiles.json")
OUTPUT_JSON = "output/agent_run_latest.json"
OUTPUT_MD = "output/agent_run_latest.md"

def load_profiles():
    if not PROFILE_PATH.exists():
        return {
            "fast": {"model": "qwen2.5-coder:1.5b"},
            "main": {"model": "qwen2.5-coder:7b"},
        }
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

def resolve_model(profile="main", model=None):
    if model:
        return model
    return load_profiles().get(profile, {}).get("model", "qwen2.5-coder:1.5b")

def run(goal, profile="main", model=None):
    model_name = resolve_model(profile=profile, model=model)
    workspace = index_workspace()

    system = (
        "You are SABLE, a local offline-capable repo agent. "
        "Be direct, technical, and execution-focused. "
        "Return plain text with these sections: SUMMARY, PLAN, FILES, COMMANDS, RISKS."
    )
    prompt = f"GOAL:\\n{goal}\\n\\nMODEL PROFILE: {profile}\\n\\nWORKSPACE MANIFEST:\\n{json.dumps(workspace, indent=2)}\\n"
    result = query_ai(prompt=prompt, model=model_name, system=system)

    artifact = {
        "timestamp": utc_now(),
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "workspace_file_count": workspace.get("file_count", 0),
        "ai_result": result,
    }
    write_json(OUTPUT_JSON, artifact)

    md = [
        "# SABLE Agent Run",
        "",
        f"**Timestamp:** {artifact['timestamp']}",
        f"**Goal:** {goal}",
        f"**Profile:** {profile}",
        f"**Model:** {model_name}",
        "",
        "## Response",
        "",
        result.get("response", ""),
    ]
    Path(OUTPUT_MD).write_text("\\n".join(md), encoding="utf-8")

    append_run({
        "timestamp": artifact["timestamp"],
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "workspace_file_count": workspace.get("file_count", 0),
        "response_preview": (result.get("response", "")[:300] if isinstance(result, dict) else ""),
    })

    return {
        "ok": True,
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "artifact_json": OUTPUT_JSON,
        "artifact_md": OUTPUT_MD,
        "response_preview": (result.get("response", "")[:400] if isinstance(result, dict) else ""),
    }
