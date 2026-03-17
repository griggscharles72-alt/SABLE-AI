#!/usr/bin/env python3
import json
from pathlib import Path

from interfaces.ai_interface import query_ai
from tools.workspace_index import index_workspace
from tools.repo_audit import list_repo_files
from tools.report_io import write_json, utc_now, read_json
from agent.reflection import append_run

PROFILE_PATH = Path("config/model_profiles.json")
OUTPUT_JSON = "output/agent_run_latest.json"
OUTPUT_MD = "output/agent_run_latest.md"

STATE_DIR = Path("state")
OUTPUT_DIR = Path("output")

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

def summarize_state():
    summary = {}
    if not STATE_DIR.exists():
        return summary
    for p in sorted(STATE_DIR.glob("*.json")):
        data = read_json(str(p), default={})
        if isinstance(data, dict):
            summary[p.name] = {
                "keys": sorted(list(data.keys()))[:20],
                "status": data.get("status"),
                "timestamp": data.get("timestamp"),
                "started_at": data.get("started_at"),
                "stopped_at": data.get("stopped_at"),
            }
        else:
            summary[p.name] = {"type": type(data).__name__}
    return summary

def summarize_output():
    summary = {}
    if not OUTPUT_DIR.exists():
        return summary
    for p in sorted(OUTPUT_DIR.glob("*")):
        if p.is_file():
            summary[p.name] = {
                "size": p.stat().st_size,
            }
    return summary

def build_context():
    workspace = index_workspace()
    repo_files = list_repo_files()

    important_files = [
        f for f in repo_files
        if not f.startswith(".git/")
        and "__pycache__" not in f
        and not f.endswith(".pyc")
    ]

    return {
        "repo_root": str(Path(".").resolve()),
        "repo_file_count": len(important_files),
        "repo_files": important_files[:200],
        "workspace": workspace,
        "state_summary": summarize_state(),
        "output_summary": summarize_output(),
    }

def run(goal, profile="main", model=None):
    model_name = resolve_model(profile=profile, model=model)
    context = build_context()

    system = (
        "You are SABLE, a local repo agent. "
        "Be direct, technical, grounded, and file-aware. "
        "Use only the provided repo context. "
        "Do not invent files that are not listed. "
        "Reference real file paths when making recommendations. "
        "Return these exact sections: SUMMARY, PLAN, FILES, COMMANDS, RISKS."
    )

    prompt = (
        f"GOAL:\n{goal}\n\n"
        f"PROFILE: {profile}\n"
        f"MODEL: {model_name}\n\n"
        f"REPO CONTEXT:\n{json.dumps(context, indent=2)}\n\n"
        "Instructions:\n"
        "1. Ground recommendations in the listed repo files.\n"
        "2. Mention specific files to edit or create when appropriate.\n"
        "3. Keep COMMANDS practical for this Linux repo.\n"
        "4. If context is thin, say so explicitly instead of inventing details.\n"
    )

    result = query_ai(prompt=prompt, model=model_name, system=system)

    artifact = {
        "timestamp": utc_now(),
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "context": {
            "repo_file_count": context.get("repo_file_count", 0),
            "workspace_file_count": context.get("workspace", {}).get("file_count", 0),
            "state_files": sorted(list(context.get("state_summary", {}).keys())),
            "output_files": sorted(list(context.get("output_summary", {}).keys())),
        },
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
    md.append(f"**Repo files seen:** {artifact['context']['repo_file_count']}")
    md.append(f"**Workspace files seen:** {artifact['context']['workspace_file_count']}")
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
        "repo_file_count": artifact["context"]["repo_file_count"],
        "workspace_file_count": artifact["context"]["workspace_file_count"],
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
        "repo_file_count": artifact["context"]["repo_file_count"],
        "workspace_file_count": artifact["context"]["workspace_file_count"],
        "response_preview": response_text[:500]
    }

if __name__ == "__main__":
    print(json.dumps(run("Create a grounded roadmap for this repo."), indent=2))
