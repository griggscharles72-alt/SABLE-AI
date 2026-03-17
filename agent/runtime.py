#!/usr/bin/env python3
import json
import re
from pathlib import Path

from interfaces.ai_interface import query_ai
from tools.workspace_index import index_workspace
from tools.repo_audit import list_repo_files
from tools.report_io import write_json, utc_now, read_json

PROFILE_PATH = Path("config/model_profiles.json")
OUTPUT_JSON = Path("output/agent_run_latest.json")
OUTPUT_MD = Path("output/agent_run_latest.md")
MEMORY_JSON = Path("state/agent_memory.json")
STATE_DIR = Path("state")

DANGEROUS_PATTERNS = [
    r"\bsudo\s+mv\b",
    r"\bsudo\s+rm\b",
    r"\brm\s+-rf\b",
    r"\bdd\b",
    r"\bmkfs\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bpoweroff\b",
    r"\bkillall\b",
    r"\bpkill\b",
    r"\bsystemctl\s+stop\b",
    r"/var/lib/sable-agent",
]

SECTION_TEMPLATE = """SUMMARY
PLAN
FILES
COMMANDS
RISKS
NEXT STEPS"""

def load_profiles():
    if not PROFILE_PATH.exists():
        return {
            "fast": {"model": "llama3.2:1b"},
            "main": {"model": "qwen2.5-coder:7b"},
        }
    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("config/model_profiles.json must be a JSON object")
    return data

def resolve_model(profile="main", model=None):
    if model:
        return model
    profiles = load_profiles()
    entry = profiles.get(profile, {})
    if isinstance(entry, dict) and entry.get("model"):
        return entry["model"]
    return "llama3.2:1b"

def repo_files_clean():
    files = list_repo_files()
    clean = []
    for f in files:
        if not isinstance(f, str):
            continue
        if f.startswith(".git/"):
            continue
        if "__pycache__" in f:
            continue
        clean.append(f)
    return sorted(set(clean))

def workspace_summary():
    try:
        data = index_workspace()
    except Exception as exc:
        return {"root": "workspace", "file_count": 0, "files": [], "error": str(exc)}

    if isinstance(data, dict):
        files = data.get("files")
        if not isinstance(files, list):
            files = []
        return {
            "root": data.get("root", "workspace"),
            "file_count": data.get("file_count", len(files)),
            "files": [str(x) for x in files if isinstance(x, str)],
        }

    return {"root": "workspace", "file_count": 0, "files": []}

def state_summary():
    summary = {}
    if not STATE_DIR.exists():
        return summary
    for p in sorted(STATE_DIR.glob("*.json")):
        data = read_json(str(p), default={})
        if isinstance(data, dict):
            summary[p.name] = {
                "status": data.get("status"),
                "timestamp": data.get("timestamp"),
                "keys": sorted(list(data.keys()))[:20],
            }
        else:
            summary[p.name] = {"type": type(data).__name__}
    return summary

def build_system_prompt():
    return (
        "You are SABLE, a local repo agent. "
        "Be concrete, grounded, and brief. "
        "Use only repo files or workspace files explicitly provided in context. "
        "If you mention a file that does not already exist, prefix it exactly with PROPOSED NEW FILE:. "
        "Never suggest moving the repo, deleting system files, sudo mv, sudo rm, rm -rf, dd, mkfs, shutdown, reboot, killall, pkill, or relocating to /var/. "
        "Do not give generic project-management filler. "
        "Return sections in this exact order: SUMMARY, PLAN, FILES, COMMANDS, RISKS, NEXT STEPS."
    )

def build_user_prompt(goal, repo_files, workspace, states):
    payload = {
        "goal": goal,
        "required_sections": SECTION_TEMPLATE,
        "repo_files": repo_files[:120],
        "workspace_root": workspace.get("root"),
        "workspace_files": workspace.get("files", [])[:120],
        "state_summary": states,
        "rules": [
            "Only reference files listed in repo_files or workspace_files unless marked PROPOSED NEW FILE:",
            "Do not suggest dangerous commands",
            "Prefer edits to real existing repo files over invented files",
            "Keep commands local to the current repo path",
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)

def extract_response_text(result):
    if not isinstance(result, dict):
        raise RuntimeError("AI backend returned non-dict result")
    if result.get("ok") is False:
        raise RuntimeError(result.get("error") or "AI backend returned failure")
    text = result.get("response")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("AI returned empty or missing response text")
    return text.strip(), result

def sanitize_file_refs(line, known_files):
    refs = re.findall(r"`([^`]+)`", line)
    updated = line
    for ref in refs:
        looks_like_file = (
            "/" in ref
            or ref.endswith((".py", ".json", ".md", ".sh", ".txt", ".yaml", ".yml"))
        )
        if looks_like_file and ref not in known_files and not ref.startswith("PROPOSED NEW FILE:"):
            updated = updated.replace(f"`{ref}`", f"`PROPOSED NEW FILE: {ref}`")
    bullet_match = re.match(r"^(\s*[-*]\s+)([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)(.*)$", updated)
    if bullet_match:
        prefix, ref, suffix = bullet_match.groups()
        if ref not in known_files and not ref.startswith("PROPOSED NEW FILE:"):
            updated = f"{prefix}PROPOSED NEW FILE: {ref}{suffix}"
    return updated

def sanitize_response(text, known_files):
    cleaned = []
    removed = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        dangerous = False
        for pat in DANGEROUS_PATTERNS:
            if re.search(pat, line, flags=re.IGNORECASE):
                dangerous = True
                break

        if dangerous:
            removed.append(line)
            continue

        line = sanitize_file_refs(line, known_files)
        cleaned.append(line)

    safe_text = "\n".join(cleaned).strip()

    if not safe_text:
        safe_text = (
            "SUMMARY\nNo safe grounded output was produced.\n\n"
            "PLAN\n- Review the repo manually.\n\n"
            "FILES\n- None.\n\n"
            "COMMANDS\n- None.\n\n"
            "RISKS\n- Prior response violated guardrails.\n\n"
            "NEXT STEPS\n- Retry with a narrower goal."
        )

    if removed:
        safe_text += "\n\nGUARDRAILS\n- Removed unsafe command suggestions from the model output."

    return safe_text

def write_markdown(timestamp, goal, profile, model_name, repo_count, workspace_count, result_text):
    md = "\n".join([
        "# SABLE Agent Run",
        "",
        f"**Timestamp:** {timestamp}",
        f"**Goal:** {goal}",
        f"**Profile:** {profile}",
        f"**Model:** {model_name}",
        f"**Repo files seen:** {repo_count}",
        f"**Workspace files seen:** {workspace_count}",
        "",
        "## Result",
        "",
        result_text,
        "",
    ])
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(md, encoding="utf-8")

def update_memory(record):
    data = read_json(str(MEMORY_JSON), default={"runs": []})
    if not isinstance(data, dict):
        data = {"runs": []}
    runs = data.get("runs")
    if not isinstance(runs, list):
        runs = []
    runs.append(record)
    runs = runs[-25:]
    data["runs"] = runs
    data["run_count"] = len(runs)
    data["latest_goal"] = record.get("goal")
    data["latest_model"] = record.get("model")
    data["latest_timestamp"] = record.get("timestamp")
    write_json(str(MEMORY_JSON), data)

def run(goal, profile="main", model=None, system=None):
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("goal must be a non-empty string")

    timestamp = utc_now()
    model_name = resolve_model(profile=profile, model=model)
    repo_files = repo_files_clean()
    workspace = workspace_summary()
    states = state_summary()

    known_files = set(repo_files) | set(workspace.get("files", []))

    prompt_system = system or build_system_prompt()
    prompt_user = build_user_prompt(goal.strip(), repo_files, workspace, states)

    ai_result = query_ai(prompt=prompt_user, model=model_name, system=prompt_system)
    raw_text, raw_backend = extract_response_text(ai_result)
    safe_text = sanitize_response(raw_text, known_files)

    artifact = {
        "ok": True,
        "timestamp": timestamp,
        "goal": goal.strip(),
        "profile": profile,
        "model": model_name,
        "repo_file_count": len(repo_files),
        "workspace_file_count": workspace.get("file_count", 0),
        "repo_files": repo_files[:120],
        "workspace_files": workspace.get("files", [])[:120],
        "state_summary": states,
        "result": safe_text,
        "backend_result": raw_backend,
    }

    write_json(str(OUTPUT_JSON), artifact)
    write_markdown(
        timestamp=timestamp,
        goal=goal.strip(),
        profile=profile,
        model_name=model_name,
        repo_count=len(repo_files),
        workspace_count=workspace.get("file_count", 0),
        result_text=safe_text,
    )

    update_memory({
        "timestamp": timestamp,
        "goal": goal.strip(),
        "profile": profile,
        "model": model_name,
        "artifact_json": str(OUTPUT_JSON),
        "artifact_md": str(OUTPUT_MD),
    })

    return {
        "ok": True,
        "goal": goal.strip(),
        "profile": profile,
        "model": model_name,
        "artifact_json": str(OUTPUT_JSON),
        "artifact_md": str(OUTPUT_MD),
        "repo_file_count": len(repo_files),
        "workspace_file_count": workspace.get("file_count", 0),
        "response_preview": safe_text[:500],
    }

if __name__ == "__main__":
    print(json.dumps(run(goal="Create a grounded roadmap for this repo."), indent=2))
