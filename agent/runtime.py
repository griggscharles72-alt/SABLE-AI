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
            "fast": {"model": "llama3.2:1b"},
            "main": {"model": "qwen2.5-coder:7b"}
        }
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

def resolve_model(profile="main", model=None):
    if model:
        return model
    profiles = load_profiles()
    return profiles.get(profile, {}).get("model", "llama3.2:1b")

def run(goal, profile="main", model=None):
    model_name = resolve_model(profile=profile, model=model)
    workspace = index_workspace()

    system = (
        "You are SABLE, a local offline-capable repo agent. "
        "Be direct, technical, and execution-focused. "
        "Return plain text with these sections: SUMMARY, PLAN, FILES, COMMANDS, RISKS."
    )

    prompt = (
        f"GOAL:\n{goal}\n\n"
        f"MODEL PROFILE: {profile}\n\n"
        f"WORKSPACE MANIFEST:\n{json.dumps(workspace, indent=2)}\n"
    )

    result = query_ai(prompt=prompt, model=model_name, system=system)

    artifact = {
        "timestamp": utc_now(),
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "workspace_file_count": workspace.get("file_count", 0),
        "ai_result": result
    }

    write_json(OUTPUT_JSON, artifact)

    response_text = result.get("response", "") if isinstance(result, dict) else ""
    md = []
    md.append("# SABLE Agent Run")
    md.append("")
    md.append(f"**Timestamp:** {artifact['timestamp']}")
    md.append(f"**Goal:** {goal}")
    md.append(f"**Profile:** {profile}")
    md.append(f"**Model:** {model_name}")
    md.append("")
    md.append("## Result")
    md.append("")
    if result.get("ok"):
        md.append(response_text)
    else:
        md.append(f"ERROR: {result.get('error', 'unknown_error')}")
        if result.get("detail"):
            md.append("")
            md.append(str(result.get("detail")))
    Path(OUTPUT_MD).write_text("\n".join(md), encoding="utf-8")

    append_run({
        "timestamp": artifact["timestamp"],
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "workspace_file_count": workspace.get("file_count", 0),
        "response_preview": response_text[:300],
        "ok": bool(result.get("ok")),
        "error": result.get("error"),
    })

    if not result.get("ok"):
        return {
            "ok": False,
            "goal": goal,
            "profile": profile,
            "model": model_name,
            "artifact_json": OUTPUT_JSON,
            "artifact_md": OUTPUT_MD,
            "error": result.get("error"),
            "detail": result.get("detail"),
            "installed_models": result.get("installed_models"),
        }

    return {
        "ok": True,
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "artifact_json": OUTPUT_JSON,
        "artifact_md": OUTPUT_MD,
        "response_preview": response_text[:400]
    }

if __name__ == "__main__":
    print(json.dumps(run("Describe how to improve this repo."), indent=2))
