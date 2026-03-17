#!/usr/bin/env python3
import json
import re
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

DANGEROUS_PATTERNS = [
    r"\bsudo\s+mv\b",
    r"\bsudo\s+rm\b",
    r"\brm\s+-rf\b",
    r"\bmv\s+-r\b",
    r"\bdd\b",
    r"\bmkfs\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bpoweroff\b",
    r"\bkillall\b",
    r"\bpkill\b",
    r"\bsystemctl\s+stop\b",
    r"\bmv\s+.+/sable-agent\s+/var/",
]

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
            summary[p.name] = {"size": p.stat().st_size}
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
        "repo_files": important_files[:250],
        "workspace": workspace,
        "state_summary": summarize_state(),
        "output_summary": summarize_output(),
    }

def extract_code_blocks(text: str):
    return re.findall(r"```(?:bash|sh)?\n(.*?)```", text, flags=re.DOTALL)

def extract_backtick_items(text: str):
    return re.findall(r"`([^`\n]+)`", text)

def looks_like_path(token: str):
    if "/" in token:
        return True
    if token.endswith((".py", ".md", ".json", ".txt", ".sh", ".db", ".yaml", ".yml")):
        return True
    return False

def validate_response(text: str, context: dict):
    repo_files = set(context.get("repo_files", []))
    workspace_files = set(context.get("workspace", {}).get("files", []))
    known_files = set(repo_files)

    for wf in workspace_files:
        known_files.add(f"workspace/{wf}")
        known_files.add(wf)

    referenced = []
    for item in extract_backtick_items(text):
        if looks_like_path(item):
            referenced.append(item)

    unknown_paths = sorted({
        p for p in referenced
        if p not in known_files
        and not p.startswith("PROPOSED NEW FILE:")
        and not p.startswith("/home/pc-1/sable-agent-run/sable-agent/")
    })

    bad_commands = []
    for block in extract_code_blocks(text):
        for pat in DANGEROUS_PATTERNS:
            if re.search(pat, block, flags=re.IGNORECASE):
                bad_commands.append(block.strip())
                break

    return {
        "unknown_paths": unknown_paths,
        "bad_commands": bad_commands,
        "ok": not unknown_paths and not bad_commands,
    }

def render_markdown(timestamp, goal, profile, model_name, context, final_text, validation, corrected):
    md = []
    md.append("# SABLE Agent Run")
    md.append("")
    md.append(f"**Timestamp:** {timestamp}")
    md.append(f"**Goal:** {goal}")
    md.append(f"**Profile:** {profile}")
    md.append(f"**Model:** {model_name}")
    md.append(f"**Repo files seen:** {context.get('repo_file_count', 0)}")
    md.append(f"**Workspace files seen:** {context.get('workspace', {}).get('file_count', 0)}")
    md.append(f"**Correction pass used:** {'yes' if corrected else 'no'}")
    md.append("")
    md.append("## Validation")
    md.append("")
    md.append(f"- Unknown paths: {len(validation.get('unknown_paths', []))}")
    md.append(f"- Dangerous command blocks: {len(validation.get('bad_commands', []))}")
    if validation.get("unknown_paths"):
        md.append(f"- Unknown path list: {', '.join(validation['unknown_paths'][:20])}")
    md.append("")
    md.append("## Result")
    md.append("")
    md.append(final_text)
    Path(OUTPUT_MD).write_text("\n".join(md), encoding="utf-8")

def run(goal, profile="main", model=None):
    model_name = resolve_model(profile=profile, model=model)
    context = build_context()
    timestamp = utc_now()

    system = (
        "You are SABLE, a grounded local repo agent. "
        "Be direct, technical, and file-aware. "
        "Use only the provided repo context. "
        "Do not invent files that are not listed. "
        "If you recommend a file that does not exist yet, write it exactly as "
        "'PROPOSED NEW FILE: path/to/file'. "
        "Do not suggest destructive or repo-relocation commands. "
        "Return these exact sections: SUMMARY, PLAN, FILES, COMMANDS, RISKS."
    )

    prompt = (
        f"GOAL:\n{goal}\n\n"
        f"PROFILE: {profile}\n"
        f"MODEL: {model_name}\n\n"
        f"REPO CONTEXT:\n{json.dumps(context, indent=2)}\n\n"
        "Rules:\n"
        "1. Use only listed real files unless explicitly marked PROPOSED NEW FILE.\n"
        "2. Prefer commands that inspect or edit the current repo in place.\n"
        "3. Do not move the repo root.\n"
        "4. Avoid sudo unless absolutely required.\n"
        "5. If context is thin, say so explicitly.\n"
    )

    first = query_ai(prompt=prompt, model=model_name, system=system)

    final_result = first
    final_text = first.get("response", "") if isinstance(first, dict) else ""
    validation = validate_response(final_text, context)
    corrected = False

    if first.get("ok") and not validation.get("ok"):
        correction_prompt = (
            "Revise the following draft so it is strictly grounded.\n\n"
            f"KNOWN REPO FILES:\n{json.dumps(context.get('repo_files', []), indent=2)}\n\n"
            f"KNOWN WORKSPACE FILES:\n{json.dumps(context.get('workspace', {}).get('files', []), indent=2)}\n\n"
            f"PROBLEMS DETECTED:\n{json.dumps(validation, indent=2)}\n\n"
            "Draft to correct:\n"
            f"{final_text}\n\n"
            "Instructions:\n"
            "- Replace invented file references with real ones, or mark them as PROPOSED NEW FILE.\n"
            "- Remove dangerous commands.\n"
            "- Keep sections exactly: SUMMARY, PLAN, FILES, COMMANDS, RISKS.\n"
        )
        second = query_ai(prompt=correction_prompt, model=model_name, system=system)
        second_text = second.get("response", "") if isinstance(second, dict) else ""
        second_validation = validate_response(second_text, context)

        if second.get("ok"):
            final_result = second
            final_text = second_text
            validation = second_validation
            corrected = True

    artifact = {
        "timestamp": timestamp,
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "context": {
            "repo_file_count": context.get("repo_file_count", 0),
            "workspace_file_count": context.get("workspace", {}).get("file_count", 0),
            "state_files": sorted(list(context.get("state_summary", {}).keys())),
            "output_files": sorted(list(context.get("output_summary", {}).keys())),
        },
        "validation": validation,
        "correction_pass_used": corrected,
        "ai_result": final_result,
    }

    write_json(OUTPUT_JSON, artifact)
    render_markdown(timestamp, goal, profile, model_name, context, final_text, validation, corrected)

    append_run({
        "timestamp": timestamp,
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "repo_file_count": context.get("repo_file_count", 0),
        "workspace_file_count": context.get("workspace", {}).get("file_count", 0),
        "response_preview": final_text[:300],
        "ok": bool(final_result.get("ok")),
        "error": final_result.get("error"),
        "validation_ok": validation.get("ok"),
    })

    if not final_result.get("ok"):
        return {
            "ok": False,
            "goal": goal,
            "profile": profile,
            "model": model_name,
            "artifact_json": OUTPUT_JSON,
            "artifact_md": OUTPUT_MD,
            "error": final_result.get("error"),
            "detail": final_result.get("detail"),
        }

    return {
        "ok": True,
        "goal": goal,
        "profile": profile,
        "model": model_name,
        "artifact_json": OUTPUT_JSON,
        "artifact_md": OUTPUT_MD,
        "repo_file_count": context.get("repo_file_count", 0),
        "workspace_file_count": context.get("workspace", {}).get("file_count", 0),
        "correction_pass_used": corrected,
        "validation_ok": validation.get("ok"),
        "unknown_paths": validation.get("unknown_paths", []),
        "dangerous_command_blocks": len(validation.get("bad_commands", [])),
        "response_preview": final_text[:500],
    }

if __name__ == "__main__":
    print(json.dumps(run("Create a grounded roadmap for this repo."), indent=2))
